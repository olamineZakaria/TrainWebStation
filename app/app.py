from flask import Flask, render_template, redirect, url_for, session ,request, jsonify
import os
app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Cle secrète pour les sessions

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

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'Aucun fichier fourni.'}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'Nom de fichier vide.'}), 400
    
#     if file:
#         # Sauvegarder le fichier
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(file_path)
#         return jsonify({'url': file_path})  # Retourner l'URL du fichier uploade
app.config['UPLOAD_FOLDER'] = 'uploads'  # Ensure this folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create the upload folder if it doesn't exist

@app.route('/save_config', methods=['POST'])
def save_config():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide.'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

    config_data = {
        'targetColumn': request.form['targetColumn'],
        'inputColumns': request.form.getlist('inputColumns'),
        'problemType': request.form['problemType'],
        'lossFunction': request.form['lossFunction'],
        'numEpochs': request.form['numEpochs'],
        'numLayers': request.form['numLayers'],
        'neuronsPerLayer': request.form.getlist('neuronsPerLayer[]'),  # Adjusted here
        'activationFunction': request.form['activationFunction']
    }

    # Write configuration to a file
    with open('model_config.txt', 'w') as f:
        f.write(f"Colonne cible: {config_data['targetColumn']}\n")
        f.write(f"Colonnes d'entree: {', '.join(config_data['inputColumns'])}\n")
        f.write(f"Type de problème: {config_data['problemType']}\n")
        f.write(f"Fonction de cout: {config_data['lossFunction']}\n")
        f.write(f"Nombre d'epoques: {config_data['numEpochs']}\n")
        f.write(f"Nombre de couches: {config_data['numLayers']}\n")
        f.write(f"Neurones par couche: {', '.join(map(str, config_data['neuronsPerLayer']))}\n")
        f.write(f"Fonction d'activation: {config_data['activationFunction']}\n")

    return jsonify({'message': 'Configuration sauvegardee avec succès.'}), 200



if __name__ == '__main__':
    app.run(debug=True)
