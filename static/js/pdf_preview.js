function showPdfPreview(pdfData) {
    const container = document.getElementById('pdfPreview');
    container.innerHTML = '';

    // Configurar worker do PDF.js
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js';

    // Converter base64 para array buffer
    const pdfDataArray = atob(pdfData);
    const array = new Uint8Array(pdfDataArray.length);
    for (let i = 0; i < pdfDataArray.length; i++) {
        array[i] = pdfDataArray.charCodeAt(i);
    }

    // Carregar PDF
    pdfjsLib.getDocument(array).promise.then(function(pdf) {
        // Renderizar primeira página
        pdf.getPage(1).then(function(page) {
            const scale = 1.5;
            const viewport = page.getViewport({ scale: scale });

            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            canvas.style.width = '100%';
            canvas.style.height = 'auto';

            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            page.render(renderContext).promise.then(function() {
                container.appendChild(canvas);
            });
        });
    }).catch(function(error) {
        console.error('Erro ao carregar PDF:', error);
        container.innerHTML = '<div class="alert alert-danger">Erro ao carregar preview do PDF</div>';
    });
}
