import flask
import json
import os
import time
from PIL import Image, ImageFile
from shutil import rmtree
from hashlib import sha1

import pytesseract
import google

DATA_DIR = 'data'
MAX_IMAGE_SIZE = 800, 600


app = flask.Flask(__name__, static_folder=DATA_DIR)

try:  # Reset saved files on each start
    rmtree(DATA_DIR, True)
    os.mkdir(DATA_DIR)
except OSError:
    pass

def safe_addr(ip_addr):
    """Strip of the trailing two octets of the IP address."""
    return '.'.join(ip_addr.split('.')[:2] + ['xxx', 'xxx'])

def save_normalized_image(path, data):
    image_parser = ImageFile.Parser()
    try:
        image_parser.feed(data)
        image = image_parser.close()
    except IOError:
        raise
        return False
    image.thumbnail(MAX_IMAGE_SIZE, Image.ANTIALIAS)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(path)
    return True

@app.route('/post', methods=['POST'])
def post():
    global start
    sha1sum = sha1(flask.request.data).hexdigest()
    target = os.path.join(DATA_DIR, '{0}.jpg'.format(sha1sum))
    message = json.dumps({'src': target,
                          'ip_addr': safe_addr(flask.request.access_route[0])})
    try:
        if save_normalized_image(target, flask.request.data):
	    print target
	    #print flask.request.data
    except Exception as e:  # Output errors
        return '{0}'.format(e)

    #need to stop this here and add image cropping

    image = Image.open(target)
    q = pytesseract.image_to_string(image)
    answer = ''
    result = google.query(q)
    for r in result:
      answer = (answer + '<a href="http://twitter.com/home/?status=' + str(r[0]) + '">' 
                + '<div class="result">'
                + str(r[1]) + '<br>' 
                + str(r[2]) + '<br>' 
                + str(r[0]) + '<br>'
                + '</div>'
                + '</a>' + '<br>')
    return answer

    
@app.route('/')
def home():
    
    return """
<!doctype html>
<title>Print Share</title>
<meta charset="utf-8" />
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/jquery-ui.min.js"></script>

<link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/themes/vader/jquery-ui.css" />
<link rel=stylesheet type=text/css href="https://raw.githubusercontent.com/davidmichaelryan/PrintShare/master/resources/jquery.Jcrop.min.css">
<script src="https://raw.githubusercontent.com/davidmichaelryan/PrintShare/master/resources/jquery.Jcrop.min.js"></script>

<style>
  body {
    max-width: 800px;
    margin: auto;
    padding: 2em;
    background:white;
    color: #318ce7;
    font: 16px/1.6 menlo, monospace;
    text-align:center;
  }

  fieldset {

  }

  #status {
    font-weight: 800;
  }

  .result {
    text-align: left;
    padding-left: 1em;
  }

  a {
    color: #318ce7;
  }

  .notice {
    font-size: 100%%;
  }


#drop {
    font-weight: bold;
    text-align: center;
    padding: 10em 0;
    margin: 5em 0;
    color: #318ce7;
    border: 2px dashed #318ce7;
    border-radius: 7px;
    cursor: default;
}

#drop.hover {
    color: #318ce7;
    border-color: #318ce7;
    border-style: solid;
    box-shadow: inset 0 10px 20px #318ce7;
}

</style>


<h3>Print Share</h3>
<p>Share the web version of a print article</p>

<noscript>Note: You must have javascript enabled in order to upload and
dynamically view new images.</noscript>
<form>
  <p id="status">Upload an image</p>
  <div id="progressbar"></div>
  <input id="file" type="file" />
</form>

<h3>Your Picture</h3>
<img src="" id='crop-image'/>
<div id="images"></div>

<script>
  function file_select_handler(to_upload) {
      var progressbar = $('#progressbar');
      var status = $('#status');
      var xhr = new XMLHttpRequest();
      xhr.upload.addEventListener('loadstart', function(e1){
          status.text('uploading image');
          progressbar.progressbar({max: e1.total});
      });
      xhr.upload.addEventListener('progress', function(e1){
          if (progressbar.progressbar('option', 'max') == 0)
              progressbar.progressbar('option', 'max', e1.total);
          progressbar.progressbar('value', e1.loaded);
      });
      xhr.onreadystatechange = function(e1) {
          if (this.readyState == 4)  {
              if (this.status == 200)
                  var text = 'Your Results' + this.responseText;
              else
                  var text = 'upload failed: code ' + this.status;
              status.html(text + '<br/>Select an image');
              progressbar.progressbar('destroy');
          }
      };
      console.log(to_upload);

      xhr.open('POST', '/post', true);
      xhr.send(to_upload);



  };
  function handle_hover(e) {
      e.originalEvent.stopPropagation();
      e.originalEvent.preventDefault();
      e.target.className = (e.type == 'dragleave' || e.type == 'drop') ? '' : 'hover';
  }

  $('#drop').bind('drop', function(e) {
      handle_hover(e);
      if (e.originalEvent.dataTransfer.files.length < 1) {
          return;
      }
      file_select_handler(e.originalEvent.dataTransfer.files[0]);
  }).bind('dragenter dragleave dragover', handle_hover);
  $('#file').change(function(e){
      file_select_handler(e.target.files[0]);
      e.target.value = '';
  });
</script>
""" 


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', threaded=True)

