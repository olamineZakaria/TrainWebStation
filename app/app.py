from flask import Flask, render_template, redirect, url_for, session ,request, jsonify
import os
from ann_regression_model import ANNRegressionModel
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
        'filePath': file_path,
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
        f.write(f"Fichier Data : {config_data['filePath']}\n")
        f.write(f"Colonne cible: {config_data['targetColumn']}\n")
        f.write(f"Colonnes d'entree: {', '.join(config_data['inputColumns'])}\n")
        f.write(f"Type de probleme: {config_data['problemType']}\n")
        f.write(f"Fonction de cout: {config_data['lossFunction']}\n")
        f.write(f"Nombre d'epoques: {config_data['numEpochs']}\n")
        f.write(f"Nombre de couches: {config_data['numLayers']}\n")
        f.write(f"Neurones par couche: {', '.join(map(str, config_data['neuronsPerLayer']))}\n")
        f.write(f"Fonction d'activation: {config_data['activationFunction']}\n")

    return jsonify({'message': 'Configuration sauvegardee avec succès.'}), 200
@app.route('/train_model', methods=['POST'])
def train_model():
    try:
        model = ANNRegressionModel('model_config.txt')  # Changez 'config.txt' par le bon fichier
        model.load_data()
        model.build_model()
        model.train_model()
        model.evaluate_model()
        model.plot_learning_curve()
        return jsonify({'message': "Modèle entraîné avec succès"}), 200  # Return valid JSON response
    except Exception as e:
        print(f"Erreur lors de l'entraînement du modèle : {e}")
        return jsonify({'error': str(e)}), 400  # Return error in JSON format

if __name__ == '__main__':
    app.run(debug=True)
