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
    """Original function (for single image)"""
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
    """Batch images"""
    zip_buffer = io.BytesIO()
    total_parts = 0
    processed_images = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in image_files:
            if file and allowed_file(file.filename):
                try:
                    img = Image.open(file)
                    original_filename = secure_filename(file.filename)
                    
                    # folder name, file without extension
                    folder_name = os.path.splitext(original_filename)[0]
                    
                    parts, num_parts = split_single_image(img, original_filename)
                    
                    # add all parts in folder
                    for filename, data in parts:
                        # folder url complete
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
    """Endpoint for process single image"""
    if 'image' not in request.files:
        return jsonify({'error': 'Image not send'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Image not selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format not supported'}), 400
    
    try:
        zip_buffer, num_parts = split_image(file)
        
        # Nome do arquivo sem a extensão original + '-splited.zip'
        download_filename = secure_filename(file.filename.rsplit('.', 1)[0] + '-splited.zip')
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_filename
        )
    except Exception as e:
        return jsonify({'error': f'Error when process image: {str(e)}'}), 500

@app.route('/split-batch', methods=['POST'])
def split_batch():
    """Endpoint for process batch images"""
    if 'images' not in request.files:
        return jsonify({'error': 'Image not selected'}), 400
    
    files = request.files.getlist('images')
    
    if not files or len(files) == 0:
        return jsonify({'error': 'Image not selected'}), 400
    
    # Valid if have image
    valid_files = [f for f in files if f and allowed_file(f.filename)]
    
    if len(valid_files) == 0:
        return jsonify({'error': 'Invalid image extension'}), 400
    
    try:
        zip_buffer, processed_images, total_parts = split_multiple_images(files)
        
        if processed_images == 0:
            return jsonify({'error': 'Not image can be process'}), 500
        
        download_filename = secure_filename(f'carrosseis-splited-{processed_images}imgs-{total_parts}parts.zip')
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_filename
        )
    except Exception as e:
        return jsonify({'error': f'Error when process image: {str(e)}'}), 500

if __name__ == '__main__':

    #dev port:
    #app.run(host="0.0.0.0", port=3140)

    #run port:
    app.run(host="0.0.0.0", port=3100)