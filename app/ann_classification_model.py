import pandas as pd
import re
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer

class ANNClassificationModel:
    def __init__(self, config_file):
        self.model_info = self.extract_model_info(config_file)
        self.model = None
        self.history = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.num_classes = None  # Automatically determined later

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
            'activation': r'Fonction d\'activation:\s*(.*)',
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
                    model_info[key] = int(match.group(1))  # Convert to integer
                else:
                    model_info[key] = match.group(1).strip()

        return model_info

    def load_data(self):
        # Load the dataset
        df = pd.read_csv(self.model_info['data_file'])

        # Identify categorical columns
        categorical_cols = df[self.model_info['input_columns']].select_dtypes(include=['object']).columns.tolist()

        # Create a transformation pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(), categorical_cols),  # Apply One-Hot Encoding to categorical columns
            ],
            remainder='passthrough'  # Keep other columns unchanged
        )

        # Split features and target
        X = df[self.model_info['input_columns']]
        y = df[self.model_info['target_column']].values

        # Debug: Print unique values of the target column
        print("Unique values in target column:", pd.unique(y))

        # Automatically detect the number of classes
        self.num_classes = len(pd.unique(y))

        # Label encode the target variable
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)  # Convert species names to numeric labels
        
        # Debug: Print encoded target variable
        print("Encoded target variable:", y)

        # One-Hot Encode the target if multi-class classification
        if self.num_classes > 2:
            y = tf.keras.utils.to_categorical(y, num_classes=self.num_classes)

        # Apply transformations
        X_transformed = preprocessor.fit_transform(X)

        # Split data into training and test sets
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_transformed, y, test_size=0.2, random_state=42)

        # Normalize the data
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)

    def build_model(self):
        # Create the ANN model
        self.model = tf.keras.Sequential()

        # Add hidden layers
        neurons = self.model_info['neurons']

        for i in range(len(neurons)):
            if i == 0:
                # First hidden layer
                self.model.add(tf.keras.layers.Dense(units=neurons[i], activation=self.model_info['activation'], input_shape=(self.X_train.shape[1],)))
            else:
                # Subsequent hidden layers
                self.model.add(tf.keras.layers.Dense(units=neurons[i], activation=self.model_info['activation']))

        # Add output layer
        if self.num_classes > 2:
            # Multi-class classification
            self.model.add(tf.keras.layers.Dense(units=self.num_classes, activation='softmax'))
        else:
            # Binary classification
            self.model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))

        # Compile the model
        loss_function = 'categorical_crossentropy' if self.num_classes > 2 else 'binary_crossentropy'
        self.model.compile(optimizer='adam', loss=loss_function, metrics=['accuracy'])

    def train_model(self):
        # Train the model
        self.history = self.model.fit(self.X_train, self.y_train, epochs=self.model_info['epochs'], batch_size=10, verbose=1, validation_split=0.2)

    def evaluate_model(self):
        # Evaluate the model
        loss, accuracy = self.model.evaluate(self.X_test, self.y_test)
        print(f'Loss on test set: {loss}')
        print(f'Accuracy on test set: {accuracy}')

    def plot_learning_curve(self):
        # Plot learning curves
        plt.figure(figsize=(12, 6))
        plt.plot(self.history.history['loss'], label='Training Loss')
        plt.plot(self.history.history['val_loss'], label='Validation Loss')
        plt.plot(self.history.history['accuracy'], label='Training Accuracy')
        plt.plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Learning Curves')
        plt.xlabel('Epochs')
        plt.ylabel('Loss / Accuracy')
        plt.legend()
        plt.show()

    def print_model_summary(self):
        # Print the model summary
        self.model.summary()
