from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import tenseal as ts
from utils_server import *
import threading
import json
import gzip

app = Flask(__name__)
CORS(app)

## Initialization
gm_weights_flat = []
fed_avg = False
agg_lock = threading.Lock()
data = {}

@app.route("/node/encrypt-parameter", methods=["POST"])
def encrypt_parameter():
    global data, fed_avg, agg_lock

    if agg_lock.acquire(blocking=False):

        try:
            ##decompressing
            raw = request.get_data()

            if request.headers.get("Content-Encoding", "") == "gzip":
                raw = gzip.decompress(raw)
            received = json.loads(raw)
            
            if not received:
                agg_lock.release()
                return jsonify({
                    "weights": None,
                    "hash": None,
                    "message": "No JSON data received"
                }), 400
            
            print("received")
            
            ## Validate required fields
            required_fields = ['enc_param_node', 'enc_param_global','context', 'hash', 'shapes']
            for field in required_fields:
                if field not in received:
                    agg_lock.release()
                    return jsonify({
                        "weights": None,
                        "hash": None,
                        "message": f"Missing required field: {field}"
                    }), 400
            
            node_weight_ser = [bytes.fromhex(x) for x in received["enc_param_node"]]
            global_weight_ser = [bytes.fromhex(x) for x in received["enc_param_global"]]
            server_context_ser = bytes.fromhex(received["context"])

            received_parameters_shapes = received['shapes']
            parameters_shapes = [tuple(s) for s in received_parameters_shapes]
            
            received_hash = received["hash"]

            ## serialization
            shapes_bytes = json.dumps(parameters_shapes).encode("utf-8")

            ## hashing
            print("hashing")
            data_hash = hashlib.sha256(b"".join(node_weight_ser) +b"".join(global_weight_ser) + server_context_ser + shapes_bytes).hexdigest()

            if data_hash != received_hash:
                agg_lock.release()
                return jsonify({
                    "weights": None,
                    "hash": None,
                    "message": "Hash not matched! Kindly re send it."
                }), 400

            ## deserialization
            context = ts.context_from(server_context_ser)
            lm_enc_weights = [ts.ckks_vector_from(context, w_bytes) for w_bytes in node_weight_ser]
            gm_enc_weights = [ts.ckks_vector_from(context, w_bytes) for w_bytes in global_weight_ser]

            # if fed_avg:
            #     scaled_lm_enc_weights = scaling_weight(lm_enc_weights, 0.01)  
            #     scaled_gm_enc_weights = scaling_weight(gm_enc_weights, 0.01)  
            #     avg_weight = aggregation_parameter(scaled_lm_enc_weights, scaled_gm_enc_weights, 0.5)
            # else:
            #     scaled_lm_enc_weights = scaling_weight(lm_enc_weights, 0.01)  
            #     avg_weight = aggregation_parameter(scaled_lm_enc_weights, gm_enc_weights, 0.5)
            #     fed_avg = True

            ## aggregation
            avg_weight = aggregation_parameter(lm_enc_weights, gm_enc_weights, 0.5)
            fed_avg = True

            avg_weight_ser = [w.serialize() for w in avg_weight]
            avg_weight_ser_hex = [w_bytes.hex() for w_bytes in avg_weight_ser]
            all_avg_weight_ser_bytes = b"".join(avg_weight_ser)

            avg_hash = hashlib.sha256(all_avg_weight_ser_bytes + shapes_bytes).hexdigest()

            data = {
                "weights": avg_weight_ser_hex,
                "hash": avg_hash,
                'shapes': parameters_shapes,
                "message": "aggregated weights are ready"
            }

            # return jsonify({'message' : 'aggregated weights are ready'}), 200
            return jsonify(data), 200

        except Exception as e:
            print(f"Error processing request: {e}")
            agg_lock.release()
            return jsonify({
                "weights": None,
                "hash": None,
                "message": f"Error processing request: {str(e)}"
            }), 500
        finally:
            agg_lock.release()
    else:
        return jsonify({
                "weights": None,
                "hash": None,
                "message": "Server is busy, please retry after some time"
            }), 504

@app.route("/server/aggregated-parameter", methods=["GET"])
def aggregated_parameter():
    if fed_avg:
        return jsonify(data), 200
    return jsonify({'message' : 'aggregated weights are not ready'}), 200

if __name__ == "__main__":
    app.run(debug=True, port=4313)
    # app.run(debug=True, port=9945)

#--------------------------------------------------------------------------------