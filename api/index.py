import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(BASE_DIR, 'Tugas_porto'))

from Backend.app import create_app

app = create_app()
