
from app import app
from flask import request, jsonify
from werkzeug.utils import secure_filename

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



@app.route("/extract/", methods=["POST"])
def process_document():
    try:
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
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


if __name__ == "__main__":
    app.run(debug=True)
