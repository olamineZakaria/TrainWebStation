from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Clé secrète pour les sessions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ProjetImageWebCam')
def projet_image_webcam():
    return render_template('ProjetImageWebCam.html')

@app.route('/ProjetCSV')
def projet_csv():
    return render_template('ProjetCSV.html')

if __name__ == '__main__':
    app.run(debug=True)
