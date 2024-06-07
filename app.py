from flask import (
    Flask,
    render_template,
    request,
    after_this_request,
    send_file,
    redirect,
    url_for,
    send_from_directory,
    abort,
)
import os
from PIL import Image
import io


import pillow_avif


def convert_to_avif(input_image_path, output_image_path):
    # Open the input image
    img = Image.open(input_image_path)

    # Convert the image to AVIF format
    img.save(output_image_path, "AVIF")


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "static/converted"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        print("File uploaded")

        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            # Construct the input and output file paths
            input_file_path = os.path.join(UPLOAD_FOLDER, filename)
            output_file_path = os.path.join(
                CONVERTED_FOLDER, os.path.splitext(filename)[0] + ".avif"
            )
            convert_to_avif(input_file_path, output_file_path)
            print("Converted to AVIF")

            NewFileName = os.path.splitext(filename)[0] + ".avif"
            try:
                os.remove(input_file_path)
            except Exception as error:
                print(f"Error deleting file: {error}")

            return redirect(url_for("view_image", filename=NewFileName))

    return "Invalid file format"


@app.route("/view/<filename>")
def view_image(filename):
    return render_template("view.html", filename=filename)


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    filepath = os.path.join(CONVERTED_FOLDER, filename)

    if not os.path.isfile(filepath):
        abort(404)  # Return 404 if the file is not found

    @after_this_request
    def remove_file(response):
        try:
            os.remove(filepath)
        except Exception as error:
            print(f"Error deleting file: {error}")
        return response

    with open(filepath, "rb") as file:
        file_data = file.read()

    return send_file(io.BytesIO(file_data), as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run()
