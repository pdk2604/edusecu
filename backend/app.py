from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from web3 import Web3
import json
import os
from utils.qr_utils import get_file_hash, upload_file, generate_qr_code, add_qr_watermark, add_qr_watermark_to_pdf
from auth.admin import get_user

app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

# 🔐 Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

# 🔗 Connexion à Ganache
ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))
w3.eth.default_account = w3.eth.accounts[0]

# 📦 Charger et déployer le smart contract
with open("build/EduSecu.json", "r") as f:
    contract_json = json.load(f)

abi = contract_json["contracts"]["EduSecu.sol"]["EduSecu"]["abi"]
bytecode = contract_json["contracts"]["EduSecu.sol"]["EduSecu"]["evm"]["bytecode"]["object"]

contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = contract.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_instance = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

print(f"✅ Contrat déployé à l'adresse : {tx_receipt.contractAddress}")

# ======================== 🔐 AUTH ========================

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = get_user(username)
    if user and password == user.password:
        login_user(user)
        return jsonify({"message": "Connexion réussie ✅"}), 200
    else:
        return jsonify({"message": "Nom d'utilisateur ou mot de passe invalide ❌"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Déconnecté ✅"}), 200

@app.route('/admin')
@login_required
def admin_dashboard():
    return jsonify({"message": f"Bienvenue {current_user.name} 🔐"}), 200

# ======================== 📥 AJOUT ========================

@app.route('/add_document', methods=['POST'])
def add_document():
    data = request.get_json()
    hash_val = data['hash']
    full_name = data['full_name']
    doc_type = data['doc_type']

    try:
        tx_hash = contract_instance.functions.addDocument(hash_val, full_name, doc_type).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"status": "success", "message": "Document enregistré ✅"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ======================== 🔍 VERIF ========================

@app.route('/verify_document', methods=['GET'])
def verify_document():
    hash_val = request.args.get("hash")

    try:
        result = contract_instance.functions.verifyDocument(hash_val).call()
        return jsonify({
            "full_name": result[0],
            "doc_type": result[1],
            "timestamp": result[2],
            "is_valid": result[3]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ======================== 🛡️ AUTHENTIFICATION ========================

@app.route('/authenticate', methods=['POST'])
@login_required
def authenticate_document():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Aucun fichier reçu"}), 400

    file = request.files['file']
    full_name = request.form.get("full_name")
    doc_type = request.form.get("doc_type")

    if not full_name or not doc_type:
        return jsonify({"status": "error", "message": "Nom complet et type requis"}), 400

    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    try:
        hash_val = get_file_hash(filepath)
        public_link = upload_file(filepath)
        qr_path = generate_qr_code(public_link)

        # Détection PDF ou image
        if filepath.lower().endswith(".pdf"):
            output_path = add_qr_watermark_to_pdf(filepath, qr_path)
        else:
            output_path = add_qr_watermark(filepath, qr_path)

        tx_hash = contract_instance.functions.addDocument(hash_val, full_name, doc_type).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "message": "Document authentifié et enregistré ✅",
            "hash": hash_val,
            "link": public_link,
            "final_image": output_path
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ======================== ▶️ RUN ========================

if __name__ == '__main__':
    app.run(debug=True)
