import os
from flask import Flask

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'credential.json'

app = Flask(__name__)

from app import views

