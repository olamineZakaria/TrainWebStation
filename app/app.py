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
if __name__ == '__main__':
    app.run(debug=True)
