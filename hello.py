import os
from flask import Flask
import Image
from pytesseract import image_to_string

__all__ = ['image_to_string']


app = Flask(__name__)

@app.route('/')
def hello():
    print image_to_string(Image.open('test.png'))
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
