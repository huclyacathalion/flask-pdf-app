import os
import logging
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
import base64

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "supersecretkey"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def px_to_points(px, dpi=300):
    """Converte pixels para pontos do PDF (1 ponto = 1/72 polegadas)"""
    inches = px / dpi
    return inches * 72


def create_pdf_with_labels(image_file):
    try:
        # Abre a imagem
        img = Image.open(image_file)
        logger.debug(
            f"Imagem original: formato={img.format}, tamanho={img.size}")

        # Converte para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Define o tamanho da página A4
        page_width, page_height = letter

        # Obtém o tamanho original da imagem em pixels
        label_width_px, label_height_px = img.size
        logger.debug(
            f"Tamanho da imagem em pixels: {label_width_px}x{label_height_px}")

        # Converte para pontos (assumindo DPI = 300 para melhor precisão)
        label_width = px_to_points(label_width_px, dpi=300)
        label_height = px_to_points(label_height_px, dpi=300)
        logger.debug(
            f"Tamanho da imagem convertido para pontos: {label_width}x{label_height}"
        )

        # Define o espaçamento entre as imagens
        spacing = 10

        # Ajusta se a imagem for maior que a página A4
        if label_width > page_width or label_height > page_height:
            raise ValueError(
                "A imagem é muito grande para caber na página A4 sem redimensionamento."
            )

        # Calcula quantas imagens cabem na folha A4
        images_per_row = max(
            1, int((page_width - spacing) // (label_width + spacing)))
        images_per_column = max(
            1, int((page_height - spacing) // (label_height + spacing)))

        logger.debug(
            f"Número de imagens na página: {images_per_row}x{images_per_column}"
        )

        # Cria um buffer para o PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Adiciona as imagens repetidas ao PDF
        for row in range(images_per_column):
            for col in range(images_per_row):
                x = spacing + col * (label_width + spacing)
                y = page_height - ((row + 1) * (label_height + spacing))
                c.drawImage(ImageReader(img),
                            x,
                            y,
                            width=label_width,
                            height=label_height,
                            preserveAspectRatio=True)

        # Salva o PDF
        c.save()
        buffer.seek(0)
        logger.debug(
            "PDF gerado corretamente, repetindo a imagem o máximo de vezes possível"
        )

        return buffer
    except Exception as e:
        logger.error(f"Erro ao criar PDF: {str(e)}")
        raise


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato de arquivo não permitido'}), 400

        # Processa o arquivo e gera o PDF
        pdf_buffer = create_pdf_with_labels(file)

        # Converte o PDF para base64 para preview
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        logger.debug("PDF convertido para base64 com sucesso")

        return jsonify({'success': True, 'pdf_data': pdf_base64})
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            pdf_buffer = create_pdf_with_labels(file)
            return send_file(pdf_buffer,
                             mimetype='application/pdf',
                             as_attachment=True,
                             download_name='rotulos.pdf')
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        return jsonify({'error': 'Erro ao gerar PDF'}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
