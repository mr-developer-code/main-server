from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import tenseal as ts
from utils_server import *
# import fed_sec_halo2_modify
import threading

app = Flask(__name__)
CORS(app)

# Initialize variables with error handling
gm_weights_flat = []
fed_avg = False
agg_lock = threading.Lock()

@app.route("/node/encrypt-parameter", methods=["POST"])
def encrypt_parameter():
    global model_scaled

    # if agg_lock.acquire(block=True):

    try:
        received = request.get_json()
        
        if not received:
            return jsonify({
                "weights": None,
                "hash": None,
                "message": "No JSON data received"
            }), 400
        
        print("received")
        
        # Validate required fields
        required_fields = ['enc_param_node', 'enc_param_global','context', 'plain_proof', 'hash'] # 'inet_add'
        for field in required_fields:
            if field not in received:
                return jsonify({
                    "weights": None,
                    "hash": None,
                    "message": f"Missing required field: {field}"
                }), 400
        
        node_weight_ser = [bytes.fromhex(x) for x in received["enc_param_node"]]
        global_weight_ser = [bytes.fromhex(x) for x in received["enc_param_global"]]
        server_context_ser = bytes.fromhex(received["context"])
        proof_bytes = bytes.fromhex(received["plain_proof"])
        received_hash = received["hash"]

        #-----------------------------------------------------------------------
        ## here for direct communication with client

        # received_add = received["inet_add"]
        # parameters_shapes = received['shapes']

        # data_csv = [
        #     [received_add]
        # ]

        # with open("port_add_list.csv", "r")as f:
        #     new_list=[]
        #     address = False
        #     reader = csv.reader(f)
        #     for row in reader:
        #         if received_add in row:
        #             address = True
        # if address == False:
        #     with open("port_add_list.csv", "a")as f: 
        #         writer = csv.writer(f)
        #         writer.writerow(data_csv)

        # add_bytes = bytes(received_add)
        # shapes_bytes = json.dumps(parameters_shapes).encode("utf-8")
        #-----------------------------------------------------------------------    

        print("hashing")
        data_hash = hashlib.sha256(b"".join(node_weight_ser) +b"".join(global_weight_ser) + server_context_ser + proof_bytes).hexdigest() #add_bytes, shapes_bytes

        if data_hash != received_hash:
            return jsonify({
                "weights": None,
                "hash": None,
                "message": "Hash not matched! Kindly re send it."
            }), 400
        
        # proof = list(proof_bytes)
        # is_proof_valid = fed_sec_halo2_modify.verify_circuit_proof(18, weights_flat, proof)

        # if is_proof_valid == False:
        #     return {
        #     "weights": None,
        #     "hash": None,
        #     "message" : "Proof verification failed! Kinldy re send it."
        # } ,400

        context = ts.context_from(server_context_ser)
        lm_enc_weights = [ts.ckks_vector_from(context, w_bytes) for w_bytes in node_weight_ser]
        gm_enc_weights = [ts.ckks_vector_from(context, w_bytes) for w_bytes in global_weight_ser]

        if fed_avg:
            scaled_lm_enc_weights = scaling_weight(lm_enc_weights, 0.5)  
            scaled_gm_enc_weights = scaling_weight(gm_enc_weights, 0.5)  
            avg_weight = aggregation_parameter(scaled_lm_enc_weights, scaled_gm_enc_weights, 0.5)
        else:
            scaled_lm_enc_weights = scaling_weight(lm_enc_weights, 0.5)  
            avg_weight = aggregation_parameter(scaled_lm_enc_weights, gm_enc_weights, 0.5)

        avg_weight_ser = [w.serialize() for w in avg_weight]
        avg_weight_ser_hex = [w_bytes.hex() for w_bytes in avg_weight_ser]
        all_avg_weight_ser_bytes = b"".join(avg_weight_ser)

        avg_hash = hashlib.sha256(all_avg_weight_ser_bytes).hexdigest()

        data = {
            "weights": avg_weight_ser_hex,
            "hash": avg_hash,
            # 'shapes': parameters_shapes,
            "message": "Done"
        }

        #-----------------------------------------------------------------------
        ## here for direct communication with client

        # with open("port_add_list.csv", "r")as f:
        #     reader = csv.reader(f)
        #     for row in reader:
        #         node_add = row[0]

        #         while True:
        #             response = requests.post(f"http:{node_add}:7226/server/aggregated", json=data)
        #             reply = response.json()
        #             if "Hash Not Matched" in reply["message"]:
        #                 time.sleep(5)
        #                 continue
        #             if "Received" in reply["message"]:
        #                 break
        #-----------------------------------------------------------------------

        ## here for communication with client via kaggle
        return jsonify(data), 200

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({
            "weights": None,
            "hash": None,
            "message": f"Error processing request: {str(e)}"
        }), 500
    # finally:
    #     agg_lock.release()
    # else:
    #     return jsonify({
    #             "weights": None,
    #             "hash": None,
    #             "message": "Server is busy, please retry after some time"
    #         }), 504

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=2416)