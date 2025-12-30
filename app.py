from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import io
import zipfile
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max para múltiplos arquivos

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_single_image(img, original_filename):
    """Divide uma única imagem em partes de 1080px"""
    width, height = img.size
    
    part_width = 1080
    num_parts = (width + part_width - 1) // part_width 
    
    parts = []
    
    for i in range(num_parts):
        left = i * part_width
        right = min((i + 1) * part_width, width)
        
        cropped = img.crop((left, 0, right, height))
        
        img_buffer = io.BytesIO()
        img_format = img.format if img.format else 'PNG'
        cropped.save(img_buffer, format=img_format)
        img_buffer.seek(0)
        
        # Nome do arquivo: original_parte01.ext
        base_name = os.path.splitext(original_filename)[0]
        ext = img_format.lower()
        filename = f"{base_name}_parte{i+1:02d}.{ext}"
        
        parts.append((filename, img_buffer.getvalue()))
    
    return parts, num_parts

def split_image(image_file):
    """Função original para compatibilidade (uma imagem apenas)"""
    img = Image.open(image_file)
    filename = secure_filename(image_file.filename) if hasattr(image_file, 'filename') else 'image'
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        parts, num_parts = split_single_image(img, filename)
        for filename, data in parts:
            zip_file.writestr(filename, data)
    
    zip_buffer.seek(0)
    return zip_buffer, num_parts

def split_multiple_images(image_files):
    """Processa múltiplas imagens em lote"""
    zip_buffer = io.BytesIO()
    total_parts = 0
    processed_images = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in image_files:
            if file and allowed_file(file.filename):
                try:
                    img = Image.open(file)
                    original_filename = secure_filename(file.filename)
                    
                    # Nome da pasta: nome do arquivo sem extensão
                    folder_name = os.path.splitext(original_filename)[0]
                    
                    parts, num_parts = split_single_image(img, original_filename)
                    
                    # Adicionar cada parte dentro da pasta do carrossel
                    for filename, data in parts:
                        # Caminho completo: pasta/arquivo
                        file_path = f"{folder_name}/{filename}"
                        zip_file.writestr(file_path, data)
                    
                    total_parts += num_parts
                    processed_images += 1
                    
                except Exception as e:
                    print(f"Erro ao processar {file.filename}: {str(e)}")
                    continue
    
    zip_buffer.seek(0)
    return zip_buffer, processed_images, total_parts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/split', methods=['POST'])
def split():
    """Endpoint para processar uma única imagem"""
    if 'image' not in request.files:
        return jsonify({'error': 'Imagem não enviada'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Imagem não selecionada'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de imagem não suportado'}), 400
    
    try:
        zip_buffer, num_parts = split_image(file)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=file.filename.rsplit('.', 1)[0] + '-splited.zip'
        )
    except Exception as e:
        return jsonify({'error': f'Erro ao processar a imagem: {str(e)}'}), 500

@app.route('/split-batch', methods=['POST'])
def split_batch():
    """Endpoint para processar múltiplas imagens em lote"""
    if 'images' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    files = request.files.getlist('images')
    
    if not files or len(files) == 0:
        return jsonify({'error': 'Nenhuma imagem selecionada'}), 400
    
    # Validar se há pelo menos uma imagem válida
    valid_files = [f for f in files if f and allowed_file(f.filename)]
    
    if len(valid_files) == 0:
        return jsonify({'error': 'Nenhuma imagem com formato válido encontrada'}), 400
    
    try:
        zip_buffer, processed_images, total_parts = split_multiple_images(files)
        
        if processed_images == 0:
            return jsonify({'error': 'Nenhuma imagem pôde ser processada'}), 500
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'carrosseis-splited-{processed_images}imgs-{total_parts}parts.zip'
        )
    except Exception as e:
        return jsonify({'error': f'Erro ao processar as imagens: {str(e)}'}), 500

if __name__ == '__main__':

    #dev port:
    #app.run(host="0.0.0.0", port=3140)

    #run port:
    app.run(host="0.0.0.0", port=3100)