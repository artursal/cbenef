from flask import Flask, request, jsonify
from flask_cors import CORS
from cbenef_engine import CbenefEngine

app = Flask(__name__)
CORS(app)

# Load engine
engine = CbenefEngine()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "db_entries": len(engine.db)})

@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    
    if not data or 'cst' not in data:
        return jsonify({"error": "Missing Required Fields (cst)"}), 400
    
    cst = data.get('cst')
    legal_text = data.get('legal_text', '')
    ncm = data.get('ncm')
    cfop = data.get('cfop')
    
    result = engine.suggest(cst, legal_text, ncm=ncm, cfop=cfop)
    return jsonify(result)

if __name__ == '__main__':
    # Running on 0.0.0.0 to allow access from local network if needed
    app.run(host='0.0.0.0', port=5000)
