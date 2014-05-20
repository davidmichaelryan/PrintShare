import flask
import json
import os
import time
from PIL import Image, ImageFile
from shutil import rmtree
from hashlib import sha1
from flask import request 

import pytesseract
import google


image = Image.open('test.png')
croppedImage = image.crop((int('0'), int('0'), int('100'), int('100')))
print 'WOO!'