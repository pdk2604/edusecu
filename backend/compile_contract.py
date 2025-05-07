from solcx import compile_standard, install_solc
import json
import os

# 1. Installer la version de Solidity
install_solc("0.8.0")

# 2. Lire le contenu du contrat
with open("contract/EduSecu.sol", "r") as file:
    contract_source = file.read()

# 3. Compiler
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "EduSecu.sol": {
            "content": contract_source
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode"]
            }
        }
    }
}, solc_version="0.8.0")

# 4. Sauvegarder dans backend/build/
with open("build/EduSecu.json", "w") as f:
    json.dump(compiled_sol, f)

print("✅ Compilation réussie ! Fichier sauvegardé dans build/EduSecu.json")
