"""API Flask legada de sugestão de cBenef.

DESCONTINUADA E INATIVA desde 10/11/2026. A resolução de cBenef passou a ser
responsabilidade do galatea-api-fiscal (app/services/cbenef_resolver_service.py).
Este módulo aborta a inicialização de propósito.
"""

import sys

_MSG_INATIVO = (
    "PROJETO cbenef DESCONTINUADO E INATIVO desde 10/11/2026.\n"
    "A resolucao de cBenef foi absorvida pelo galatea-api-fiscal "
    "(app/services/cbenef_resolver_service.py).\n"
    "Nao reativar esta API."
)
print(_MSG_INATIVO, file=sys.stderr)
raise SystemExit(1)

from flask import Flask, request, jsonify  # noqa: E402
from flask_cors import CORS  # noqa: E402
from cbenef_engine import CbenefEngine  # noqa: E402

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
