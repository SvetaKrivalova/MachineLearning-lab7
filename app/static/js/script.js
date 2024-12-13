function openLoadingScreen() {
    var LoadingScreen = document.querySelector('.LoadingScreen');
    document.querySelector('.overlay').classList.add('show');
    document.querySelector('.LoadingScreen').classList.add('show');
    LoadingScreen.style.display = 'block';
}
   
function closeLoadingScreen() {
    var LoadingScreen = document.querySelector('.LoadingScreen');
    document.querySelector('.overlay').classList.remove('show');
    document.querySelector('.LoadingScreen').classList.remove('show');
    LoadingScreen.style.display = 'none';
}

document.getElementById('showUploadForm').addEventListener('click', function() {
    const uploadForm = document.getElementById('uploadForm');
    uploadForm.style.display = uploadForm.style.display === 'none' ? 'block' : 'none';
})

function updateFileLabel(files) {
    const fileLabel = document.getElementById('file-label');
    const fileCount = document.getElementById('fileCount2');
    
    if (files.length > 0) {
        const fileNames = Array.from(files).map(file => file.name).join('<br>');
        fileLabel.innerHTML = fileNames;
        fileCount.textContent = `Количество загружаемых файлов: ${files.length}`;
    } else {
        fileLabel.textContent = 'Нет загружаемых файлов';
        fileCount.textContent = `Количество загружаемых файлов: 0`;
    }
}

function validateForm1() {
    const fileInput = document.getElementById('showUploadForm');
    if (fileInput.files.length === 0) {
        alert('Пожалуйста, добавьте файлы для загрузки.');
        return false;
    } else if (fileInput.files.length > 1000) {
        alert("Вы можете загрузить разом не более 1000 файлов.");
        return false;
    }
    return true;
}

function validateForm() {
    const fileInput = document.getElementById('showUploadForm');
    if (fileInput.files.length === 0) {
        alert('Пожалуйста, добавьте файлы для загрузки.');
        return false;
    }
    return true;
}

function validateForm() {
    const trainSize = parseFloat(document.getElementById('trainSize').value);
    const valSize = parseFloat(document.getElementById('valSize').value);

    if (trainSize + valSize !== 1) {
        alert('Сумма train и val выборок должна быть равна 1.');
        return false;
    }
    alert("Датасет успешно создан. Он находится в папке datasets.");
    return true; 
    
}

document.getElementById('photoForm').onsubmit = function(event) {
    event.preventDefault();
    const numPhotos = document.getElementById('numPhotos').value;
    const destinationFolder = document.getElementById('destinationFolder').value;

    const formData = new FormData();
    formData.append('num_photos', numPhotos);
    formData.append('destination_folder', destinationFolder);

    fetch('/copy_photos', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
};

function showAlert1() {
    alert("Класс успешно создан. Он находится в папке выбранного датасета. Называется classes.txt");
    return true;
}

function showAlert2() {
    alert("train.py успешно создан. Он находится в папке выбранного датасета.");
    return true; 
}

document.querySelector('form').addEventListener('submit', function(e) {
    const imgsz = document.getElementById('imgsz').value;
    const epochs = document.getElementById('epochs').value;
    const batch = document.getElementById('batch').value;
    const savePeriod = document.getElementById('save_period').value;

    if (imgsz < 1 || epochs < 1 || batch < 1 || savePeriod < 1) {
        e.preventDefault();
        alert('Все значения должны быть больше 0.');
    }
});

document.getElementById('numPhotos').addEventListener('input', function() {
    const min = parseInt(this.min);
    const max = parseInt(this.max);
    const value = parseInt(this.value);

    if (value < min || value > max) {
        this.setCustomValidity(`Пожалуйста, введите число от ${min} до ${max}.`);
    } else {
        this.setCustomValidity('');
    }
});

function handleFlashMessages(messages) {
    messages.forEach(function(msg) {
        let title = msg.category.charAt(0).toUpperCase() + msg.category.slice(1); 
        let icon = msg.category === 'success' ? 'success' : 'error'; 

        swal({
            title: title,
            text: msg.message,
            icon: icon,
            button: "ОК",
        });
    });
}

function openCreateDataSet() {
    var LoadingScreen = document.querySelector('.CreateDataSet');
    document.querySelector('.overlayForCD').classList.add('showForCD');
    document.querySelector('.CreateDataSet').classList.add('showForCD');
    LoadingScreen.style.display = 'block';
}
   
function closeCreateDataSet() {
    var LoadingScreen = document.querySelector('.CreateDataSet');
    document.querySelector('.overlayForCD').classList.remove('showForCD');
    document.querySelector('.CreateDataSet').classList.remove('showForCD');
    LoadingScreen.style.display = 'none';
}

function openScript() {
    var LoadingScreen = document.querySelector('.Script');
    document.querySelector('.overlayForScript').classList.add('showForScript');
    document.querySelector('.Script').classList.add('showForScript');
    LoadingScreen.style.display = 'block';
}
   
function closeScript() {
    var LoadingScreen = document.querySelector('.Script');
    document.querySelector('.overlayForScript').classList.remove('showForScript');
    document.querySelector('.Script').classList.remove('showForScript');
    LoadingScreen.style.display = 'none';
}


const trainInput = document.getElementById('trainSize');
    const valInput = document.getElementById('valSize');

    trainInput.addEventListener('input', function() {
        const trainValue = parseFloat(trainInput.value);
        if (!isNaN(trainValue)) {
            valInput.value = (1 - trainValue).toFixed(2);
        }
    });

    valInput.addEventListener('input', function() {
        const valValue = parseFloat(valInput.value);
        if (!isNaN(valValue)) {
            trainInput.value = (1 - valValue).toFixed(2);
        }
    });


$(document).ready(function() {
    $('#photoForm').on('submit', function(event) {
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response.exists) {
                    alert(response.message);
                    if (confirm("Продолжить?")) {
                        $.ajax({
                            type: 'POST',
                            url: '/copy_photos', 
                            data: $(this).serialize(),
                            success: function() {
                                window.location.href = '/';
                            },
                            error: function(err) {
                                alert('Ошибка: ' + err.responseJSON.error);
                            }
                        });
                    }
                } else {
                    window.location.href = '/';
                }
            },
            error: function(err) {
                alert('Ошибка: ' + err.responseJSON.error);
            }
        });
    });
});

function updateFileCount() {
    const select = document.getElementById('datasets');
    const selectedOptions = Array.from(select.selectedOptions);
    const count = selectedOptions.length;

    console.log(`Количество выбранных файлов: ${count}`);
}

function updateImageV(selectId, canvasId, fileNameId) {
    const selectElement = document.getElementById(selectId);
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const fileNameElement = document.getElementById(fileNameId);

    fileNameElement.textContent = "/static/images/" + (selectedOption.dataset.txt).split('images/')[1];

    const img = new Image();
    img.src = "/static/images/" + (selectedOption.value).split('images/')[1]; 
    img.onload = function() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.width = img.width;
        canvas.height = img.height; 
        ctx.drawImage(img, 0, 0);

        loadCoordinates(selectedOption.dataset.txt, ctx, img.width, img.height);
    };

    img.onerror = function() {
        console.error('Ошибка загрузки изображения:', img.src);
        fileNameElement.textContent = "Ошибка загрузки изображения.";
    };
}

function loadCoordinates(txtFileName, ctx, imgWidth, imgHeight) {
    console.log("Функция loadCoordinates вызвана с файлом:", txtFileName);
    fetch("/static/images/" + txtFileName.split('images/')[1]) 
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка загрузки текстового файла: ' + response.statusText);
            }
            return response.text();
        })
        .then(data => {
            const lines = data.split('\n');
            lines.forEach(line => {
                const values = line.split(' ').map(Number);
                if (values.length === 5) {
                    const [classId, x, y, width, height] = values;

                    const left = (x - width / 2) * imgWidth;
                    const top = (y - height / 2) * imgHeight;
                    const frameWidth = width * imgWidth;
                    const frameHeight = height * imgHeight;

                    console.log(`Class ID: ${classId}, Left: ${left}, Top: ${top}, Width: ${frameWidth}, Height: ${frameHeight}`);

                    ctx.strokeStyle = 'red'; 
                    ctx.lineWidth = 6;
                    ctx.strokeRect(left, top, frameWidth, frameHeight); 
                }
            });
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
}

window.onload = function() {
    updateImage('files_selectV', 'fileImageV', 'selectedFileNameV');
};