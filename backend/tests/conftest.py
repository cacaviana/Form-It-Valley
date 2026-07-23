import os
import sys

# Env minimo ANTES de qualquer import da app (itvalleysecurity valida no import)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-com-mais-de-32-caracteres!!")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DATABASE", "flowquote-test")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
