from flask import Flask, render_template, request, redirect, url_for
import os
from uuid import uuid4
from barcode import Code128, EAN13
from barcode.writer import ImageWriter
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)

BARCODE_DIR = os.path.join("static", "barcodes")
os.makedirs(BARCODE_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["GET", "POST"])
def generate():
    barcode_types = ["Code128", "EAN13"]

    if request.method == "POST":
        text = request.form.get("text")
        btype = request.form.get("type")

        if not text:
            return render_template("generate.html", error="Enter text!", types=barcode_types)

        filename = f"{uuid4().hex}.png"
        filepath = os.path.join(BARCODE_DIR, filename)

        if btype == "Code128":
            barcode = Code128(text, writer=ImageWriter())
        elif btype == "EAN13":
            barcode = EAN13(text, writer=ImageWriter())
        else:
            return "Invalid type"

        barcode.save(filepath.replace(".png", ""))

        return render_template("generate.html", types=barcode_types, filename=filename)

    return render_template("generate.html", types=barcode_types)

@app.route("/read", methods=["GET", "POST"])
def read():
    if request.method == "POST":
        file = request.files.get("file")

        if not file:
            return render_template("read.html", error="Upload an image!")

        img = Image.open(file.stream)
        result = decode(img)

        if not result:
            return render_template("read.html", error="No barcode found!")

        decoded_texts = [r.data.decode("utf-8") for r in result]

        return render_template("read.html", result=decoded_texts)

    return render_template("read.html")

if __name__ == "__main__":
    app.run(debug=True)
