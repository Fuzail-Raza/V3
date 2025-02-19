
document.getElementById('get-started').addEventListener('click', function() {
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('upload-screen').style.display = 'block';
});

document.getElementById('uploadButton').addEventListener('click', function() {
    uploadFile();
});

function updateFileName() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];

    if (file) {
        const fileName = file.name;
        const fileSize = (file.size / (1024 * 1024)).toFixed(2);

        document.getElementById('fileSize').textContent = `File selected: ${fileName}, Size: ${fileSize} MB`;
    } else {
        document.getElementById('fileSize').textContent = 'Choose File';
    }
}

function uploadFile() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('memory_dump', file);

        // Show loading animation
        document.getElementById('upload-screen').style.display = 'none';
        document.getElementById('loading').style.display = 'block';

        fetch('/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Get CSRF token from cookie
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result-screen').style.display = 'block';
            document.getElementById('results').textContent = JSON.stringify(data.results, null, 2);
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            alert('Error: ' + error.message);
        });
    } else {
        alert('Please select a file.');
    }
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
