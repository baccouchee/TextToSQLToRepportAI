from huggingface_hub import HfApi, HfFolder, upload_file
import os

# Remplacez par votre nom d'utilisateur et le nom du dataset
user = "omarbacc"
dataset_name = "sqlproject"

# Chemin vers votre fichier dataset.jsonl
dataset_path = r"C:\Users\omarb\Downloads\TpAPPbd\data\dataset.jsonl"

# Authentifiez-vous avec votre token
token = "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"
HfFolder.save_token(token)



# Télécharger le fichier dataset.jsonl
upload_file(
    path_or_fileobj=dataset_path,
    path_in_repo="dataset.jsonl",
    repo_id=f"{user}/{dataset_name}",
    repo_type="dataset",
    token=token
)

print("Fichier téléchargé avec succès.")