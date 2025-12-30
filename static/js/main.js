// Estado da aplicação
let selectedFileSingle = null;
let selectedFilesBatch = [];

// Elementos DOM
const dropZone = document.getElementById('dropZone');
const dropZoneBatch = document.getElementById('dropZoneBatch');
const fileInput = document.getElementById('fileInput');
const fileInputBatch = document.getElementById('fileInputBatch');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const fileName = document.getElementById('fileName');
const dimensions = document.getElementById('dimensions');
const parts = document.getElementById('parts');
const processBtn = document.getElementById('processBtn');
const processBatchBtn = document.getElementById('processBatchBtn');
const fileList = document.getElementById('fileList');
const fileCount = document.getElementById('fileCount');
const loading = document.getElementById('loading');
const loadingPlural = document.getElementById('loadingPlural');
const errorDiv = document.getElementById('error');
const successDiv = document.getElementById('success');

// ==================== TABS ====================
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remover active de todas as tabs e conteúdos
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Adicionar active na tab clicada e seu conteúdo
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
        
        // Limpar mensagens
        hideMessages();
    });
});

// ==================== SINGLE IMAGE MODE ====================

// Drag and drop - Single
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    if (e.dataTransfer.files.length > 0) {
        handleFileSingle(e.dataTransfer.files[0]);
    }
});

// File input change - Single
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSingle(e.target.files[0]);
    }
});

// Processar arquivo único
function handleFileSingle(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        return;
    }

    selectedFileSingle = file;
    
    // Mostrar preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        
        // Obter dimensões da imagem
        const img = new Image();
        img.onload = () => {
            const width = img.width;
            const height = img.height;
            const numParts = Math.ceil(width / 1080);
            
            fileName.textContent = file.name;
            dimensions.textContent = `${width} x ${height}px`;
            parts.textContent = numParts;
            
            preview.style.display = 'block';
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    hideMessages();
}

// Processar imagem única
processBtn.addEventListener('click', async () => {
    if (!selectedFileSingle) return;
    
    const formData = new FormData();
    formData.append('image', selectedFileSingle);
    
    await processRequest('/split', formData, false);
});

// ==================== BATCH MODE ====================

// Drag and drop - Batch
dropZoneBatch.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZoneBatch.classList.add('drag-over');
});

dropZoneBatch.addEventListener('dragleave', () => {
    dropZoneBatch.classList.remove('drag-over');
});

dropZoneBatch.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZoneBatch.classList.remove('drag-over');
    
    if (e.dataTransfer.files.length > 0) {
        handleFilesBatch(Array.from(e.dataTransfer.files));
    }
});

// File input change - Batch
fileInputBatch.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFilesBatch(Array.from(e.target.files));
    }
});

// Processar múltiplos arquivos
function handleFilesBatch(files) {
    // Filtrar apenas imagens
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        showError('Please select valid image files');
        return;
    }
    
    selectedFilesBatch = imageFiles;
    renderFileList();
    hideMessages();
}

// Renderizar lista de arquivos
function renderFileList() {
    fileList.innerHTML = '';
    fileCount.textContent = selectedFilesBatch.length;
    
    if (selectedFilesBatch.length === 0) {
        processBatchBtn.style.display = 'none';
        return;
    }
    
    processBatchBtn.style.display = 'block';
    
    selectedFilesBatch.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <span class="file-item-name">${file.name}</span>
            <button class="file-item-remove" onclick="removeFile(${index})">Remove</button>
        `;
        fileList.appendChild(item);
    });
}

// Remover arquivo da lista
window.removeFile = function(index) {
    selectedFilesBatch.splice(index, 1);
    renderFileList();
};

// Processar lote de imagens
processBatchBtn.addEventListener('click', async () => {
    if (selectedFilesBatch.length === 0) return;
    
    const formData = new FormData();
    selectedFilesBatch.forEach(file => {
        formData.append('images', file);
    });
    
    await processRequest('/split-batch', formData, true);
});

// ==================== REQUEST HANDLER ====================

async function processRequest(endpoint, formData, isBatch) {
    showLoading(isBatch);
    hideMessages();
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error processing image(s)');
        }
        
        // Download do arquivo
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Obter nome do arquivo do header
        const contentDisposition = response.headers.get('content-disposition');
        const fileNameMatch = contentDisposition && contentDisposition.match(/filename="?(.+)"?/);
        a.download = fileNameMatch ? fileNameMatch[1] : 'carousel-splited.zip';
        
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        showSuccess('Download started successfully!');
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// ==================== UI HELPERS ====================

function showLoading(isBatch) {
    loading.style.display = 'block';
    loadingPlural.textContent = isBatch ? 's' : '';
    processBtn.disabled = true;
    processBatchBtn.disabled = true;
}

function hideLoading() {
    loading.style.display = 'none';
    processBtn.disabled = false;
    processBatchBtn.disabled = false;
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    successDiv.style.display = 'none';
}

function showSuccess(message) {
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    errorDiv.style.display = 'none';
}

function hideMessages() {
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';
}