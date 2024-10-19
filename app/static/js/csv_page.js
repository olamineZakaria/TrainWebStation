let uploadedFile = null; // Variable pour stocker le fichier téléchargé

        document.getElementById('fileID').addEventListener('change', handleFileUpload);
        document.getElementById('uploadForm').addEventListener('submit', function(event) {
            event.preventDefault();
            if (!uploadedFile) {
                alert('Veuillez importer un fichier avant de soumettre.');
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
                    window.open(data.url, '_blank');
                } else {
                    alert('Erreur lors du chargement de l\'analyse: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                document.getElementById('spinner').style.display = 'none';
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
                    alert('Le fichier a été téléchargé avec succès.');

                    document.getElementById('spinner').style.display = 'none';
                    document.getElementById('fileNameDisplay').textContent = file.name;
                    displayDataInTable(csvData);
                };
                
                reader.readAsText(file);
            } else {
                alert('Veuillez importer un fichier au format CSV, TSV ou XLSX.');
            }
        }

        function displayDataInTable(data) {
            const tableHeader = document.getElementById('tableHeader');
            const tableBody = document.getElementById('tableBody');
            tableHeader.innerHTML = '';
            tableBody.innerHTML = '';

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
        }

        // Gestion de la soumission du formulaire de configuration du modèle
        document.getElementById('modelConfigForm').addEventListener('submit', function(event) {
            event.preventDefault(); // Empêcher le rechargement de la page

            const configData = {
                targetColumn: document.getElementById('targetColumn').value,
                inputColumns: document.getElementById('inputColumns').value.split(',').map(col => col.trim()),
                problemType: document.getElementById('problemType').value,
                lossFunction: document.getElementById('lossFunction').value,
                numEpochs: document.getElementById('numEpochs').value,
                numLayers: document.getElementById('numLayers').value,
                neuronsPerLayer: Array.from(document.querySelectorAll('#neuronsPerLayerContainer input')).map(input => input.value),
                activationFunction: document.getElementById('activationFunction').value
            };

            // Envoi des données au serveur
            fetch('/save_config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            })
            .then(response => response.json())
            .then(data => {
                const configAlertMessage = document.getElementById('configAlertMessage');
                if (data.success) {
                    configAlertMessage.textContent = 'Configuration sauvegardée avec succès!';
                    configAlertMessage.classList.remove('alert-danger');
                    configAlertMessage.classList.add('alert-success');
                } else {
                    configAlertMessage.textContent = 'Erreur lors de la sauvegarde de la configuration.';
                    configAlertMessage.classList.remove('alert-success');
                    configAlertMessage.classList.add('alert-danger');
                }
                configAlertMessage.style.display = 'block';
            })
            .catch(error => {
                console.error('Erreur:', error);
                const configAlertMessage = document.getElementById('configAlertMessage');
                configAlertMessage.textContent = 'Erreur lors de la sauvegarde de la configuration.';
                configAlertMessage.classList.remove('alert-success');
                configAlertMessage.classList.add('alert-danger');
                configAlertMessage.style.display = 'block';
            });
        });

        // Ajout de la logique pour gérer le nombre de couches et de neurones
        document.getElementById('numLayers').addEventListener('change', updateNeuronsPerLayer);

        function updateNeuronsPerLayer() {
            const numLayers = document.getElementById('numLayers').value;
            const neuronsPerLayerContainer = document.getElementById('neuronsPerLayerContainer');
            neuronsPerLayerContainer.innerHTML = '';

            for (let i = 0; i < numLayers; i++) {
                const layerDiv = document.createElement('div');
                layerDiv.className = 'form-group';
                const label = document.createElement('label');
                label.textContent = `Nombre de neurones dans la couche ${i + 1}`;
                const input = document.createElement('input');
                input.type = 'number';
                input.className = 'form-control';
                input.value = 10; // Valeur par défaut
                input.min = 1;

                layerDiv.appendChild(label);
                layerDiv.appendChild(input);
                neuronsPerLayerContainer.appendChild(layerDiv);
            }

            document.getElementById('neuronsPerLayerGroup').style.display = 'block';
        }