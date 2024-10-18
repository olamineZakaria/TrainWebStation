let uploadedFile = null; // Variable to store the uploaded file

document.getElementById('fileID').addEventListener('change', handleFileUpload);
document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Empêcher le rechargement de la page
    if (!uploadedFile) {
        alert('Veuillez importer un fichier avant de soumettre.');
        return;
    }

    // Afficher le spinner pendant le chargement
    document.getElementById('spinner').style.display = 'inline-block';

    const formData = new FormData();
    formData.append('file', uploadedFile);

    // Envoi du fichier au backend pour analyse
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Cacher le spinner après le chargement
        document.getElementById('spinner').style.display = 'none';

        if (data.url) {
            window.open(data.url, '_blank'); // Ouvrir l'URL D-Tale dans un nouvel onglet
        } else {
            alert('Erreur lors du chargement de l\'analyse: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        // Cacher le spinner en cas d'erreur
        document.getElementById('spinner').style.display = 'none';
    });
});

// Fonction pour gérer l'importation du fichier CSV
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.tsv') || file.name.endsWith('.xlsx'))) {
        uploadedFile = file; // Store the uploaded file
        const reader = new FileReader();
        
        // Afficher le spinner pendant le chargement du fichier
        document.getElementById('spinner').style.display = 'inline-block';
        
        reader.onload = function(e) {
            const csvData = e.target.result;
            console.log("Données CSV chargées:", csvData);
            alert('Le fichier a été téléchargé avec succès.');

            // Cacher le spinner après le chargement du fichier
            document.getElementById('spinner').style.display = 'none';

            // Afficher le nom du fichier
            document.getElementById('fileNameDisplay').textContent = file.name; // Display the file name
        };
        
        reader.readAsText(file);
    } else {
        alert('Veuillez importer un fichier au format CSV, TSV ou XLSX.');
    }
}
