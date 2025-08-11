// Truy cập webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        document.getElementById('video').srcObject = stream;
    })
    .catch(function(error) {
        console.error("Không thể truy cập camera: ", error);
    });

// Hàm chụp ảnh
function capture() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/jpeg');
    document.getElementById('image_data').value = dataURL;
}
