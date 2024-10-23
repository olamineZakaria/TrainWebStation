import pandas as pd
import re
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import os
import matplotlib
from io import StringIO


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

    matplotlib.use('Agg')
    def plot_learning_curve(self):
    # Create the 'assets/plots' directory if it doesn't exist
        plots_dir = os.path.join('static', 'assets', 'plots')
        os.makedirs(plots_dir, exist_ok=True)

        # Check if the history contains the necessary keys
        if 'loss' not in self.history.history or 'val_loss' not in self.history.history:
            print("No loss data found in history. Plotting cannot be done.")
            return

        # Plot the learning curves
        plt.figure(figsize=(12, 6))
        
        try:
            plt.plot(self.history.history['loss'], label='Perte d\'entraînement', color='blue')
            plt.plot(self.history.history['val_loss'], label='Perte de validation', color='orange')
            plt.title('Courbe d\'apprentissage')
            plt.xlabel('Époques')
            plt.ylabel('Perte')
            plt.legend()
            
            # Save the plot in the 'assets/plots' directory
            plot_path = os.path.join(plots_dir, 'learning_curve.png')
            plt.savefig(plot_path)
            print(f"Learning curve saved at {plot_path}")

        except Exception as e:
            print(f"An error occurred while plotting the learning curve: {e}")

        finally:
            # Clear the plot to free up memory
            plt.clf()


    def print_model_summary(self):
        # Capture the model summary as a string
        stream = StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        model_summary_str = stream.getvalue()

        # Create a new figure for the summary
        plt.figure(figsize=(10, 5))
        plt.text(0, 1, model_summary_str, fontsize=10, ha='left', va='top', family='monospace')
        plt.axis('off')  # Turn off the axis

        # Define the paths for saving the summary image
        plots_dir = os.path.join('static', 'assets', 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Save in the 'plots' directory
        summary_image_path = os.path.join(plots_dir, 'model_summary.png')
        plt.savefig(summary_image_path, bbox_inches='tight', pad_inches=0.1)
        plt.close()  # Close the plot to free up memory

        return summary_image_path  # Return the path to the saved image