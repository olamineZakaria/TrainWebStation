document.addEventListener("DOMContentLoaded", () => {
    const addClassBtn = document.getElementById("add-class-btn");
    const classContainer = document.getElementById("class-container");

    // Variable pour stocker les images en session
    let classImageData = {};

    // Appliquez les fonctionnalités aux classes déjà existantes
    const existingClassCards = document.querySelectorAll(".class-card");
    existingClassCards.forEach((classCard, index) => {
        setupClassCard(classCard, `Class ${index + 1}`);
    });

    // Ajouter un événement pour ajouter une nouvelle classe
    addClassBtn.addEventListener("click", () => {
        const classCount = classContainer.querySelectorAll(".class-card").length + 1;
        const newClassCard = createClassCard(classCount);
        classContainer.appendChild(newClassCard); // Ajout de la nouvelle carte au container
        setupClassCard(newClassCard, `Class ${classCount}`); // Configurez la nouvelle carte
    });

    // Fonction pour créer une nouvelle carte de classe
    function createClassCard(classCount) {
        const classCard = document.createElement("div");
        classCard.classList.add("col-md-6", "mb-4", "class-card"); // Add Bootstrap classes for layout

        classCard.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <input type="text" class="form-control class-name" value="Class ${classCount}" placeholder="Nom de la classe" />
                    <button class="btn btn-danger delete-btn"><i class="fas fa-trash-alt"></i></button>
                </div>
                <div class="card-body">
                    <p>Ajouter des échantillons d'images :</p>
                    <div class="button-group">
                        <input type="file" class="file-input" accept="image/*" multiple style="display: none;" />
                        <button class="btn btn-primary file-upload-btn"><i class="fas fa-upload"></i> Importer</button>
                        <button class="btn btn-secondary webcam-btn"><i class="fas fa-video"></i> Webcam</button>
                    </div>
                    <div class="image-preview-container"></div>
                    <p class="image-count">Nombre d'images: <span class="count">0</span></p>
                    
                    <!-- Video container for responsive webcam -->
                    <div class="video-container" style="display: none;">
                        <video class="webcam" autoplay playsinline style="width: 100%; height: auto;"></video>
                    </div>
                    
                    <canvas class="snapshot" style="display: none;"></canvas>
                    <button class="btn btn-warning stop-webcam-btn" style="display: none;"><i class="fas fa-times"></i> Arrêter Webcam</button>
                    <button class="btn btn-danger clear-images-btn" style="display: none;">Supprimer les images</button>
                </div>
            </div>
        `;

        return classCard;
    }

    // Fonction pour configurer une carte de classe
    function setupClassCard(classCard, className) {
        const deleteBtn = classCard.querySelector(".delete-btn");
        const uploadBtn = classCard.querySelector(".file-upload-btn");
        const fileInput = classCard.querySelector(".file-input");
        const webcamBtn = classCard.querySelector(".webcam-btn");
        const stopWebcamBtn = classCard.querySelector(".stop-webcam-btn");
        const clearImagesBtn = classCard.querySelector(".clear-images-btn");
        const imagePreviewContainer = classCard.querySelector(".image-preview-container");
        const imageCountSpan = classCard.querySelector(".count");
        const webcam = classCard.querySelector(".webcam");
        const snapshot = classCard.querySelector(".snapshot");

        // Initialisation de la session d'images pour cette classe
        classImageData[className] = [];

        // Suppression de la carte
        deleteBtn.addEventListener("click", () => {
            delete classImageData[className]; // Supprimer les images en session
            classCard.remove(); // Suppression directe de la carte
        });

        // Gestion de l'importation d'images à partir de fichiers
        uploadBtn.addEventListener("click", () => {
            fileInput.click();
        });

        fileInput.addEventListener("change", (event) => {
            const files = event.target.files;

            // Ajout des fichiers importés au conteneur d'aperçu
            addFilesToPreview(files, imagePreviewContainer, className, clearImagesBtn);
        });

        // Suppression des images de la classe
        clearImagesBtn.addEventListener("click", () => {
            classImageData[className] = [];
            imagePreviewContainer.innerHTML = '';
            imageCountSpan.textContent = 0;
            clearImagesBtn.style.display = "none"; // Cacher le bouton de suppression
        });

        // Gestion de la webcam et upload des images
        let captureInterval; // Variable pour stocker l'intervalle de capture

        webcamBtn.addEventListener("click", () => {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    webcam.srcObject = stream;
                    webcam.style.display = "block";
                    stopWebcamBtn.style.display = "block";

                    // Afficher le conteneur vidéo
                    const videoContainer = classCard.querySelector(".video-container");
                    videoContainer.style.display = "block"; 

                    // Commencer à capturer les images à 5 FPS
                    captureInterval = setInterval(() => {
                        const ctx = snapshot.getContext('2d');
                        snapshot.width = webcam.videoWidth; 
                        snapshot.height = webcam.videoHeight;
                        ctx.drawImage(webcam, 0, 0, snapshot.width, snapshot.height);

                        // Convertir le canvas en image
                        const imageData = snapshot.toDataURL('image/png');
                        const img = document.createElement('img');
                        img.src = imageData;
                        img.style.width = '50px'; // Taille réduite
                        img.style.height = '50px'; // Taille réduite
                        img.style.margin = '5px';

                        // Ajouter l'image à l'aperçu
                        imagePreviewContainer.appendChild(img);

                        // Ajouter l'image à la session de la classe
                        classImageData[className].push(imageData); // Stocker l'image dans la session

                        // Mise à jour du compteur d'images
                        imageCountSpan.textContent = classImageData[className].length; 
                        clearImagesBtn.style.display = "block"; // Afficher le bouton de suppression
                    }, 1000 / 2); // Capture à 5 FPS

                    stopWebcamBtn.addEventListener("click", () => {
                        const tracks = webcam.srcObject.getTracks();
                        tracks.forEach(track => track.stop());
                        webcam.style.display = "none";
                        videoContainer.style.display = "none"; // Masquer le conteneur vidéo lors de l'arrêt de la webcam
                        stopWebcamBtn.style.display = "none";
                        clearInterval(captureInterval); // Arrêter la capture d'images
                    }, { once: true });
                })
                .catch(err => console.error("Webcam non accessible", err));
        });
    }

    // Fonction pour ajouter des fichiers à l'aperçu
    function addFilesToPreview(files, imagePreviewContainer, classNameValue, clearImagesBtn) {
        // Ajout des fichiers importés au conteneur d'aperçu
        [...files].forEach(file => {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.style.width = '50px'; // Taille réduite
            img.style.height = '50px'; // Taille réduite
            img.style.margin = '5px';
            imagePreviewContainer.appendChild(img);

            // Ajouter l'image à la session de la classe
            classImageData[classNameValue].push(URL.createObjectURL(file));
        });

        // Mise à jour du compteur en temps réel
        const imageCountSpan = imagePreviewContainer.closest(".class-card").querySelector(".count");
        imageCountSpan.textContent = classImageData[classNameValue].length; // Mise à jour du compteur

        // Afficher le bouton de suppression si des images sont présentes
        if (classImageData[classNameValue].length > 0) {
            clearImagesBtn.style.display = "block"; // Afficher le bouton de suppression
        }
    }
});
