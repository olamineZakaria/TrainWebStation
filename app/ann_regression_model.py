import pandas as pd
import re
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


class ANNRegressionModel:
    def __init__(self, config_file):
        self.model_info = self.extract_model_info(config_file)
        self.model = None
        self.history = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def extract_model_info(self, config_file):
        # Define the regex patterns
        patterns = {
            'data_file': r'Fichier Data :\s*(.*)',
            'target_column': r'Colonne cible:\s*(.*)',
            'input_columns': r'Colonnes d\'entree:\s*(.*)',
            'loss_function': r'Fonction de cout:\s*(.*)',
            'epochs': r'Nombre d\'epoques:\s*(\d+)',
            'layers': r'Nombre de couches:\s*(\d+)',
            'neurons': r'Neurones par couche:\s*(.*)',
            'activation': r'Fonction d\'activation:\s*(.*)'
        }

        model_info = {}

        with open(config_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # Extract each piece of information using regex
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                if key == 'input_columns':
                    model_info[key] = [col.strip() for col in match.group(1).split(',')]
                elif key == 'neurons':
                    model_info[key] = [int(neuron.strip()) for neuron in match.group(1).split(',')]
                elif key in ['epochs', 'layers']:
                    model_info[key] = int(match.group(1))  # Convertir en entier
                else:
                    model_info[key] = match.group(1).strip()

        return model_info

    def load_data(self):
        # Charger le dataset
        df = pd.read_csv(self.model_info['data_file'])

        # Identifier les colonnes catégorielles
        categorical_cols = df[self.model_info['input_columns']].select_dtypes(include=['object']).columns.tolist()

        # Créer un pipeline de transformation
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(), categorical_cols),  # Appliquer One-Hot Encoding aux colonnes catégorielles
            ],
            remainder='passthrough'  # Garder les autres colonnes inchangées
        )

        # Séparer les caractéristiques et la cible
        X = df[self.model_info['input_columns']]
        y = df[self.model_info['target_column']].values

        # Appliquer les transformations
        X_transformed = preprocessor.fit_transform(X)

        # Diviser les données en ensembles d'entraînement et de test
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_transformed, y, test_size=0.2, random_state=42)

        # Normaliser les données
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)

    def build_model(self):
        # Créer le modèle ANN
        self.model = tf.keras.Sequential()

        # Ajouter les couches cachées
        neurons = self.model_info['neurons']

        for i in range(len(neurons)):
            if i == 0:
                # Première couche cachée
                self.model.add(tf.keras.layers.Dense(units=neurons[i], activation=self.model_info['activation'], input_shape=(self.X_train.shape[1],)))
            else:
                # Couches cachées suivantes
                self.model.add(tf.keras.layers.Dense(units=neurons[i], activation=self.model_info['activation']))

        # Ajouter la couche de sortie
        self.model.add(tf.keras.layers.Dense(units=1))  # Pour la régression, on a une sortie

        # Compiler le modèle
        self.model.compile(optimizer='adam', loss=self.model_info['loss_function'])

    def train_model(self):
        # Entraîner le modèle
        self.history = self.model.fit(self.X_train, self.y_train, epochs=self.model_info['epochs'], batch_size=10, verbose=1, validation_split=0.2)

    def evaluate_model(self):
        # Évaluer le modèle
        loss = self.model.evaluate(self.X_test, self.y_test)
        print(f'Perte sur l\'ensemble de test : {loss}')

    def plot_learning_curve(self):
        # Afficher les courbes d'apprentissage
        plt.figure(figsize=(12, 6))
        plt.plot(self.history.history['loss'], label='Perte d\'entraînement')
        plt.plot(self.history.history['val_loss'], label='Perte de validation')
        plt.title('Courbe d\'apprentissage')
        plt.xlabel('Époques')
        plt.ylabel('Perte')
        plt.legend()
        plt.show()

    def print_model_summary(self):
        # Afficher le résumé du modèle
        self.model.summary()
