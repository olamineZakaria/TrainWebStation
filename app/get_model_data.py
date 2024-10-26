import re

def extract_model_info(config_file):
        # Define the regex patterns
        patterns = {
            'data_file': r'Fichier Data :\s*(.*)',
            'target_column': r'Colonne cible:\s*(.*)',
            'input_columns': r'Colonnes d\'entree:\s*(.*)',
            'loss_function': r'Fonction de cout:\s*(.*)',
            'epochs': r'Nombre d\'epoques:\s*(\d+)',
            'problemType': r'Type de probleme:\s*(.*)',
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
