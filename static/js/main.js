document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const spinner = uploadBtn.querySelector('.spinner-border');
    const alertArea = document.getElementById('alertArea');
    const previewArea = document.getElementById('previewArea');
    const downloadBtn = document.getElementById('downloadBtn');
    
    function showAlert(message, type = 'danger') {
        alertArea.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }

    function toggleLoading(loading) {
        uploadBtn.disabled = loading;
        spinner.classList.toggle('d-none', !loading);
        uploadBtn.innerText = loading ? 'Processando...' : 'Gerar PDF';
    }

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('imageFile');
        const file = fileInput.files[0];
        
        if (!file) {
            showAlert('Por favor, selecione uma imagem.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        toggleLoading(true);
        alertArea.innerHTML = '';
        previewArea.classList.add('d-none');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro ao processar arquivo');
            }

            // Preview do PDF
            previewArea.classList.remove('d-none');
            showPdfPreview(data.pdf_data);
            
        } catch (error) {
            showAlert(error.message);
            previewArea.classList.add('d-none');
        } finally {
            toggleLoading(false);
        }
    });

    downloadBtn.addEventListener('click', async function() {
        const fileInput = document.getElementById('imageFile');
        const file = fileInput.files[0];
        
        if (!file) {
            showAlert('Por favor, selecione uma imagem novamente.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/download-pdf', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Erro ao baixar PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'rotulos.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

        } catch (error) {
            showAlert(error.message);
        }
    });
});
