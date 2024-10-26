document.addEventListener("DOMContentLoaded", () => {
    const addClassBtn = document.getElementById("add-class-btn");
    const classContainer = document.getElementById("class-container");

    // Variable to store images in session
    let classImageData = {};

    // Apply features to existing classes
    const existingClassCards = document.querySelectorAll(".class-card");
    existingClassCards.forEach((classCard, index) => {
        setupClassCard(classCard, `Class ${index + 1}`);
    });

    // Add event for adding a new class
    addClassBtn.addEventListener("click", () => {
        const classCount = classContainer.querySelectorAll(".class-card").length + 1;
        const newClassCard = createClassCard(classCount);
        classContainer.appendChild(newClassCard);
        setupClassCard(newClassCard, `Class ${classCount}`);
    });

    // Function to create a new class card
    function createClassCard(classCount) {
        const classCard = document.createElement("div");
        classCard.classList.add("col-md-6", "mb-4", "class-card");

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

    // Function to set up a class card
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

        // Initialize session images for this class
        classImageData[className] = [];

        // Delete class card
        deleteBtn.addEventListener("click", () => {
            delete classImageData[className];
            classCard.remove();
        });

        // Handle file upload
        uploadBtn.addEventListener("click", () => {
            fileInput.click();
        });

        fileInput.addEventListener("change", (event) => {
            const files = event.target.files;
            addFilesToPreview(files, imagePreviewContainer, className, clearImagesBtn);
        });

        // Clear class images
        clearImagesBtn.addEventListener("click", () => {
            classImageData[className] = [];
            imagePreviewContainer.innerHTML = '';
            imageCountSpan.textContent = 0;
            clearImagesBtn.style.display = "none";
        });

        // Webcam and image upload functionality
        let captureInterval;

        webcamBtn.addEventListener("click", () => {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    webcam.srcObject = stream;
                    webcam.style.display = "block";
                    stopWebcamBtn.style.display = "block";
                    const videoContainer = classCard.querySelector(".video-container");
                    videoContainer.style.display = "block"; 

                    captureInterval = setInterval(() => {
                        const ctx = snapshot.getContext('2d');
                        snapshot.width = webcam.videoWidth; 
                        snapshot.height = webcam.videoHeight;
                        ctx.drawImage(webcam, 0, 0, snapshot.width, snapshot.height);

                        const imageData = snapshot.toDataURL('image/png');
                        addImageToPreview(imageData, imagePreviewContainer, className, clearImagesBtn);
                        saveImageToServer(imageData, className); // Save to server
                    }, 1000 / 2); // Capture at 2 FPS

                    stopWebcamBtn.addEventListener("click", () => {
                        const tracks = webcam.srcObject.getTracks();
                        tracks.forEach(track => track.stop());
                        webcam.style.display = "none";
                        videoContainer.style.display = "none";
                        stopWebcamBtn.style.display = "none";
                        clearInterval(captureInterval);
                    }, { once: true });
                })
                .catch(err => console.error("Webcam inaccessible", err));
        });
    }

    // Function to add files to preview
    function addFilesToPreview(files, imagePreviewContainer, className, clearImagesBtn) {
        [...files].forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                const imageData = reader.result;
                addImageToPreview(imageData, imagePreviewContainer, className, clearImagesBtn);
                saveImageToServer(imageData, className); // Save each file to server
            };
            reader.readAsDataURL(file);
        });
    }

    // Helper to add image to preview
    function addImageToPreview(imageData, container, className, clearBtn) {
        const img = document.createElement('img');
        img.src = imageData;
        img.style.width = '50px';
        img.style.height = '50px';
        img.style.margin = '5px';
        container.appendChild(img);

        classImageData[className].push(imageData);
        const count = container.closest(".class-card").querySelector(".count");
        count.textContent = classImageData[className].length;
        clearBtn.style.display = "block";
    }

    // Function to save image to server
    function saveImageToServer(imageData, className) {
        fetch("/upload_image", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ image: imageData, className: className })
        })
        .then(response => response.json())
        .then(data => console.log("Image saved:", data))
        .catch(err => console.error("Error saving image:", err));
    }
});
