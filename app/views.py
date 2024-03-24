from app import app
from flask import request, jsonify
from werkzeug.utils import secure_filename

from PIL import Image
from rembg import remove

from google.cloud import storage
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions

options = ClientOptions(api_endpoint="us-documentai.googleapis.com")
client = documentai.DocumentProcessorServiceClient(client_options=options)

name = client.processor_version_path(
    "825292908281",
    "us",
    "751f444c2d36cdb6",
    "pretrained-foundation-model-v1.0-2023-08-22",
)


@app.route("/extract", methods=["POST"])
def process_document():
    try:
        file = request.files["file"]
        if file:
            secure_filename(file.filename)
            file_stream = file.read()

            raw_document = documentai.RawDocument(
                content=file_stream, mime_type="image/jpeg"
            )
            process_request = documentai.ProcessRequest(
                name=name,
                raw_document=raw_document,
                field_mask="entities",
                process_options=None,
            )
            result = client.process_document(request=process_request)
            document = result.document

            ktp = {}

            for entity in document.entities:
                ktp[entity.type_] = entity.mention_text

            return jsonify(ktp)
        else:
            return jsonify({"error": "No file provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload-ktp", methods=["POST"])
def upload_ktp():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        client = storage.Client()
        bucket = client.get_bucket("dharmapongrekun_ktp_bucket")
        blob = bucket.blob(filename)
        blob.upload_from_file(file)

        download_url = (
            f"https://storage.googleapis.com/dharmapongrekun_ktp_bucket/{filename}"
        )

        return (
            jsonify(
                {
                    "download_url": download_url,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/remback", methods=["POST"])
def remback():
    file = request.files["file"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        rembg_img_name = filename.split(".")[0] + "_rembg.png"
        remove_background(
            UPLOAD_FOLDER + "/" + filename, UPLOAD_FOLDER + "/" + rembg_img_name
        )
        return render_template(
            "home.html", org_img_name=filename, rembg_img_name=rembg_img_name
        )


if __name__ == "__main__":
    app.run(debug=True)
