from flask import Flask, request, send_file, render_template
from PIL import Image
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

def fit_resize(image: Image.Image) -> Image.Image:
    img_ratio = image.width / image.height
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if img_ratio > target_ratio:
        new_width = TARGET_WIDTH
        new_height = round(TARGET_WIDTH / img_ratio)
    else:
        new_height = TARGET_HEIGHT
        new_width = round(TARGET_HEIGHT * img_ratio)

    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (255, 255, 255))
    left = (TARGET_WIDTH - new_width) // 2
    top = (TARGET_HEIGHT - new_height) // 2
    canvas.paste(resized, (left, top))
    return canvas

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