import hashlib
import os
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)

## initialization
zip_file = "secure_gen_ai_application.zip"
txt_file = "README.pdf"

## calculate the hash
def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        return hashlib.sha256(file_bytes).hexdigest()

## encoding
def encode_file_to_base64(file_path):
    """Encode file to base64 string"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        return base64.b64encode(file_bytes).decode('utf-8')

@app.route("/api/fetch-file", methods=["GET"])
def fetch_file():
    try:
        
        if not os.path.exists(zip_file) or not os.path.exists(txt_file):
            return jsonify({
                'status': 'error',
                'message': 'Files not found on server'
            }), 404
        
        ## hashing
        zip_hash = calculate_file_hash(zip_file)
        txt_hash = calculate_file_hash(txt_file)
        
        ## encoding
        zip_data = encode_file_to_base64(zip_file)
        txt_data = encode_file_to_base64(txt_file)
        
        if zip_data is None or txt_data is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to read files'
            }), 500
        
        data = {
            'status': 'success',
            'zip_data': zip_data,
            'txt_data': txt_data,
            'zip_hash': zip_hash,
            'txt_hash': txt_hash,
            'zip_filename': 'secure_gen_ai_application.zip',
            'txt_filename': 'README.pdf'
        }
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3035, debug=True)
    # app.run(host="127.0.0.1", port=3005, debug=True)

#--------------------------------------------------------------------------------