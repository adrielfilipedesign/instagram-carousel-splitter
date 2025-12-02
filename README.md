# 🖼️ Instagram Carousel Image Slicer

Auto slicer for Instagram carousel images with Python and Flask. Split large images into 1080px wide vertical strips perfect for Instagram carousel posts.

## ✨ Features

- 📤 Drag & drop or select images
- ✂️ Automatic split into 1080px wide parts
- 🎯 Maintains original image height
- 📦 Downloads as ZIP with sequential naming
- 🖥️ Clean and modern web interface
- 🚀 Fast processing with PIL/Pillow

## 🛠️ Technologies

- **Backend:** Python 3.10 + Flask
- **Image Processing:** Pillow (PIL)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/adrielfilipedesign/instagram-carousel-splitter.git
cd instagram-carousel-splitter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install flask pillow
```

## 💻 Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and go to:
```
http://localhost:3100
```

3. Upload your image (drag & drop or click to select)

4. Click "Split and Download"

5. Your sliced images will be downloaded as a ZIP file

## 📁 Project Structure
```
instagram-carousel-splitter/
├── app.py                 # Flask backend
├── templates/
│   └── index.html        # Main page
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── main.js       # Frontend logic
└── README.md
```

## 🎨 How It Works

1. Upload an image of any width
2. The app calculates how many 1080px wide parts are needed
3. Splits the image horizontally maintaining the original height
4. Names each part sequentially (filename_01, filename_02, etc.)
5. Packages everything in a ZIP file for download

## 📝 Supported Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- WEBP

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.


## ⭐ Show your support

Give a ⭐️ if this project helped you!