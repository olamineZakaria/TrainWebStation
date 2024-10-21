from flask import Flask, render_template, redirect, url_for, session ,request, jsonify
import os
app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Clé secrète pour les sessions

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ProjetImageWebCam')
def projet_image_webcam():
    return render_template('ProjetImageWebCam.html')

@app.route('/ProjetCSV')
def projet_csv():
    return render_template('ProjetCSV.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide.'}), 400
    
    if file:
        # Sauvegarder le fichier
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return jsonify({'url': file_path})  # Retourner l'URL du fichier uploadé
@app.route('/save_config', methods=['POST'])
def save_config():
    config_data = request.json
    with open('model_config.txt', 'a') as f:
        f.write(f"Colonne cible: {config_data['targetColumn']}\n")
        f.write(f"Colonnes d'entrée: {', '.join(config_data['inputColumns'])}\n")
        f.write(f"Type de problème: {config_data['problemType']}\n")
        f.write(f"Fonction de coût: {config_data['lossFunction']}\n")
        f.write(f"Nombre d'époques: {config_data['numEpochs']}\n")
        f.write(f"Nombre de couches: {config_data['numLayers']}\n")
        f.write(f"Neurones par couche: {', '.join(map(str, config_data['neuronsPerLayer']))}\n")  # Conversion en chaîne ici
        f.write(f"Fonction d'activation: {config_data['activationFunction']}\n\n")
    
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
