import pandas as pd
import re
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
import os
from io import StringIO
from sklearn.metrics import classification_report

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
        use_sigmoid_for_all = self.num_classes > 2  # Use sigmoid for all layers if it's a multi-class classification

        for i in range(len(neurons)):
            if i == 0:
                # First hidden layer
                self.model.add(tf.keras.layers.Dense(units=neurons[i], activation='sigmoid' if use_sigmoid_for_all else self.model_info['activation'], input_shape=(self.X_train.shape[1],)))
            else:
                # Subsequent hidden layers
                self.model.add(tf.keras.layers.Dense(units=neurons[i], activation='sigmoid' if use_sigmoid_for_all else self.model_info['activation']))

        # Add output layer
        if self.num_classes > 2:
            # Multi-class classification with sigmoid in the output layer
            self.model.add(tf.keras.layers.Dense(units=self.num_classes, activation='softmax'))
        else:
            # Binary classification with standard sigmoid output
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
        # Create the 'assets/plots' directory if it doesn't exist
        plots_dir = os.path.join('app','static', 'assets', 'plots')
        os.makedirs(plots_dir, exist_ok=True)

        # Check if the history contains the necessary keys
        required_keys = ['loss', 'val_loss', 'accuracy', 'val_accuracy']
        if not all(key in self.history.history for key in required_keys):
            print("Missing data in history. Ensure 'loss', 'val_loss', 'accuracy', and 'val_accuracy' are available.")
            return

        # Plot the learning curves
        plt.figure(figsize=(12, 6))

        try:
            # Plot Loss
            plt.plot(self.history.history['loss'], label='Training Loss', color='blue', linestyle='--')
            plt.plot(self.history.history['val_loss'], label='Validation Loss', color='orange', linestyle='--')

            # Plot Accuracy
            plt.plot(self.history.history['accuracy'], label='Training Accuracy', color='blue')
            plt.plot(self.history.history['val_accuracy'], label='Validation Accuracy', color='orange')

            plt.title('Learning Curves')
            plt.xlabel('Epochs')
            plt.ylabel('Loss / Accuracy')
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
        plt.axis('off')  # Turn off the axis for cleaner output

        # Define the paths for saving the summary image
        plots_dir = os.path.join('app','static', 'assets', 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Save the summary as an image in the 'plots' directory
        summary_image_path = os.path.join(plots_dir, 'model_summary.png')
        plt.savefig(summary_image_path, bbox_inches='tight', pad_inches=0.1)
        print(f"Model summary saved at {summary_image_path}")

        # Clear and close the plot to free up memory
        return summary_image_path
    
    def save_classification_report_as_image(self):
        # Generate predictions on the test set
        y_pred = (self.model.predict(self.X_test) > 0.5).astype("int32")  # Threshold for binary classification

        # If multi-class, apply argmax
        if self.num_classes > 2:
            y_pred = y_pred.argmax(axis=1)
            y_true = self.y_test.argmax(axis=1)
        else:
            y_true = self.y_test

        # Generate classification report
        report = classification_report(y_true, y_pred)
        
        # Set up the directory for saving plots
        plots_dir = os.path.join('app', 'static', 'assets', 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Plot the report
        plt.figure(figsize=(8, 6))
        plt.axis('off')
        plt.text(0.01, 1.0, report, ha='left', va='top', fontsize=10, family='monospace')

        # Save the report as an image
        report_image_path = os.path.join(plots_dir, 'classification_report.png')
        plt.savefig(report_image_path, bbox_inches='tight', pad_inches=0.5)
        plt.close()  # Close the plot to free memory

        print(f"Classification report saved at {report_image_path}")