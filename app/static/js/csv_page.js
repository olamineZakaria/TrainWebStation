let uploadedFile = null; // Variable pour stocker le fichier téléchargé

document.getElementById('fileID').addEventListener('change', handleFileUpload);
document.getElementById('uploadForm-data').addEventListener('submit', function(event) {
    event.preventDefault();
    if (!uploadedFile) {
        showAlert('Veuillez importer un fichier avant de soumettre.', 'danger', 'alertMessage');
        return;
    }

    document.getElementById('spinner').style.display = 'inline-block';

    const formData = new FormData();
    formData.append('file', uploadedFile);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('spinner').style.display = 'none';

        if (data.url) {
            showAlert('Le fichier a été téléchargé avec succès.', 'success', 'alertMessage');
            window.open(data.url, '_blank');
        } else {
            showAlert('Erreur lors du chargement de l\'analyse: ' + data.error, 'danger', 'alertMessage');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        document.getElementById('spinner').style.display = 'none';
        showAlert('Erreur lors du chargement de l\'analyse.', 'danger', 'alertMessage');
    });
});

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.tsv') || file.name.endsWith('.xlsx'))) {
        uploadedFile = file;
        const reader = new FileReader();
        document.getElementById('spinner').style.display = 'inline-block';

        reader.onload = function(e) {
            const csvData = e.target.result;
            console.log("Données CSV chargées:", csvData);
            showAlert('Le fichier a été téléchargé avec succès.', 'success', 'alertMessage');

            document.getElementById('spinner').style.display = 'none';
            document.getElementById('fileNameDisplay').textContent = file.name;
            displayDataInTable(csvData);

            // Activer les champs de configuration après le téléchargement du fichier
            document.getElementById('targetColumn').disabled = false;
            document.getElementById('inputColumns').disabled = false;
            document.getElementById('problemType').disabled = false;
            document.getElementById('lossFunction').disabled = false;
            document.getElementById('numEpochs').disabled = false;
            document.getElementById('numLayers').disabled = false;
            document.getElementById('activationFunction').disabled = false;
            document.querySelector('#modelConfigForm button[type="submit"]').disabled = false;
        };

        reader.readAsText(file);
    } else {
        showAlert('Veuillez importer un fichier au format CSV, TSV ou XLSX.', 'danger', 'alertMessage');
    }
}



function displayDataInTable(data) {
    const tableHeader = document.getElementById('tableHeader');
    const tableBody = document.getElementById('tableBody');
    const targetColumnSelect = document.getElementById('targetColumn'); // Pour la colonne cible
    const inputColumnsSelect = document.getElementById('inputColumns'); // Pour les colonnes d'entrée

    tableHeader.innerHTML = '';
    tableBody.innerHTML = '';
    targetColumnSelect.innerHTML = ''; // Réinitialiser les options
    inputColumnsSelect.innerHTML = ''; // Réinitialiser les options

    const rows = data.split('\n');
    const headers = rows[0].split(',');

    // Créer les en-têtes du tableau
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.trim();
        headerRow.appendChild(th);
    });
    tableHeader.appendChild(headerRow);

    // Remplir le corps du tableau
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i].split(',');
        if (row.length === headers.length) {
            const tableRow = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell.trim();
                tableRow.appendChild(td);
            });
            tableBody.appendChild(tableRow);
        }
    }

    // Ajouter les colonnes dans le champ de la colonne cible
    headers.forEach(header => {
        const option = document.createElement('option');
        option.value = header.trim();
        option.textContent = header.trim();
        targetColumnSelect.appendChild(option);
    });

    // Quand une colonne cible est sélectionnée, exclure cette colonne des colonnes d'entrée
    targetColumnSelect.addEventListener('change', function () {
        const selectedTargetColumn = targetColumnSelect.value;

        // Effacer les colonnes d'entrée
        inputColumnsSelect.innerHTML = '';

        // Ajouter les colonnes sauf la colonne cible
        headers.forEach(header => {
            if (header.trim() !== selectedTargetColumn) {
                const option = document.createElement('option');
                option.value = header.trim();
                option.textContent = header.trim();
                inputColumnsSelect.appendChild(option);
            }
        });
    });

    // Déclencher l'événement de changement une fois que les colonnes sont initialisées
    targetColumnSelect.dispatchEvent(new Event('change'));
}



// Ajout de la logique pour gérer le nombre de couches et de neurones

// Fonction pour afficher les alertes
function showAlert(message, type, elementId) {
    const alertDiv = document.getElementById(elementId);
    alertDiv.textContent = message;
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.style.display = 'block'; 
}



// toogle 


