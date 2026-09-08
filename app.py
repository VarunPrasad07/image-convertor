from flask import Flask, request, send_file, render_template
from PIL import Image, ImageFilter, ImageEnhance
import io
import os

app = Flask(__name__)

TARGET_WIDTH = 832
TARGET_HEIGHT = 551
WHITE_THRESHOLD = 245
WHITE_PERCENTAGE = 0.95

def remove_white_borders(image: Image.Image) -> Image.Image:
    width, height = image.size

    def is_white_row(y):
        white_pixels = sum(
            1 for x in range(width)
            if all(c >= WHITE_THRESHOLD for c in image.getpixel((x, y)))
        )
        return (white_pixels / width) >= WHITE_PERCENTAGE

    top = 0
    while top < height and is_white_row(top):
        top += 1

    bottom = height - 1
    while bottom >= 0 and is_white_row(bottom):
        bottom -= 1

    if top < bottom:
        image = image.crop((0, top, width, bottom + 1))

    return image

def enhance_image(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Contrast(image).enhance(1.2)
    image = ImageEnhance.Sharpness(image).enhance(1.5)
    image = ImageEnhance.Color(image).enhance(1.1)
    image = image.filter(
        ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
    )
    return image

def fit_resize(image: Image.Image) -> Image.Image:
    resized = image.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    return resized

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return "No image uploaded", 400

    file = request.files["image"]
    if file.filename == "":
        return "No file selected", 400

    try:
        image = Image.open(file.stream).convert("RGB")
        image = remove_white_borders(image)
        image = enhance_image(image)
        result = fit_resize(image)

        output = io.BytesIO()
        result.save(output, "PNG", optimize=True)
        output.seek(0)

        return send_file(
            output,
            mimetype="image/png",
            as_attachment=True,
            download_name=f"{os.path.splitext(file.filename)[0]}_832x551.png"
        )
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)