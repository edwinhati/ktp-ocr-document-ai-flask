import os
from flask import Flask
from flask_cors import CORS

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'credential.json'

app = Flask(__name__)
CORS(app)

from app import views

