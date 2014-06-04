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
from flask import Flask, redirect, url_for
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

DATA_DIR = 'data'
MAX_IMAGE_SIZE = 800, 600

global q1
global q2
global q3
global q4
q1 = ''
q2 = ''
q3 = ''
q4 = ''

app = flask.Flask(__name__, static_folder=DATA_DIR)

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
    return target

@app.route('/crop', methods=['POST']) 
def crop_ajax():    
    
    global q1 
    q1 = request.form['q1']
    global q2 
    q2 = request.form['q2']
    global q3 
    q3 = request.form['q3']
    global q4 
    q4 = request.form['q4']
    left = request.form['left'] 
    upper = request.form['upper'] 
    right = request.form['right'] 
    lower = request.form['lower'] 
    target = request.form['target'] 


    image = Image.open(target)
    croppedImage = image.crop((int(left), int(upper), int(right), int(lower)))

    q = pytesseract.image_to_string(croppedImage)
    q = ' '+q1+' '+q2+' '+q3+' '+q4+' '+q
    q1=''
    q2=''
    q3=''
    q4=''
    answer = ''
    result = google.query(q)
    for r in result:
      answer = (answer + '<a href="' + str(r[0]) + '">'
                + '<div class="result">'
                + str(r[1]) + '<br>' 
                + str(r[0]) + '<br>'
                + '</div>'
    + '<a target="_blank" style="color:white;background-color:#318ce7;padding:5px 5px;border-radius:5px;margin-bottom:20px;display:inline-block;" href="http://twitter.com/home/?status=' +str(r[1]) + ' --> ' +str(r[0])+'">'
    + '<div class="tweet">'
    + "Tweet it" + '<br>' 
                + '</div>'
                + '</a>' + '<br>')
    return answer

    
@app.route('/', methods=['GET', 'OPTIONS'])
def home():
  try:  # Reset saved files on each start
    rmtree(DATA_DIR, True)
    os.mkdir(DATA_DIR)
  except OSError:
    pass

  return """
<!doctype html>
<head>
<title>Print Share</title>
<meta charset="utf-8" />
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/jquery-ui.min.js"></script>

<link rel="stylesheet" type="text/css" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/themes/vader/jquery-ui.css" />

<script src="https://rawgit.com/davidmichaelryan/PrintShare/master/resources/jquery.Jcrop.js"></script>
<link rel="stylesheet" href="https://rawgit.com/davidmichaelryan/PrintShare/master/resources/jquery.Jcrop.min.css" type="text/css" />


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

  #status {
    font-weight: 800;
  }

  .result {
    text-align: left;
    padding-left: 1em;
  }
  .tweet {
    text-align: right;

  }
    #status span:hover{
  cursor:pointer;
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

.waitToShow {
  text-align: left;
  display: none;
}

#q1, #q2, #q3, #q4{
    margin-left:25px;
    margin-right:20px;
}

#image-header {
  display: none;
  margin-bottom:20px;
}

h3 {
  text-align: center;

}

#title{
    font-size:48px;
  margin:0 auto;
}

#crop-submit {
  display: none;
  cursor: pointer;
  margin-top: 20px;
  margin-bottom: 20px;
  border: 1px solid #318ce7;
}

#crop-submit:hover {
  background: #ddd;
}

.jcrop-holder {
  display: block;
  margin-left: auto;
  margin-right: auto;
}

#loading{
  position:fixed;
  top:-100px;
  left:0;
  z-index:999999999999;
  width:100%;
  height:100%;
  pointer-events:none;
  display:none;
}

</style>
</head>
<body>
<div id="loading"><img src="http://sierrafire.cr.usgs.gov/images/loading.gif"/></div>

<h3 id="title">Print Share</h3>
<p style="padding-bottom: 10px;border-bottom: 1px solid rgb(49, 140, 231);margin-top: 0">Share the web version of a print article</p>
<p id="status"></p>

<h3 id="image-header">Your Picture</h3>

<form>
  <img src="" id='crop-image'/>
  <p class="waitToShow" style="margin-bottom:0">Have we not found it yet? Sorry about that! Help us narrow it down:</p>
  <p id="q1" class="waitToShow">Publication<br><input type="text" name="q1" id="text1"></input></p>
  <p id="q2" class="waitToShow">Author<br><input type="text" name="q2" id="text2"></input></p>
  <p id="q3" class="waitToShow">Date<br><input type="text" name="q3" id="text3"></input></p>
  <p id="q4" class="waitToShow">Other Keywords<br><input type="text" name="q4" id="text4"></input>
  <br>
  <div id="crop-submit">Submit</div>
</form>

<noscript>Note: You must have javascript enabled in order to upload and
dynamically view new images.</noscript>
<form id="image-upload">
  <p style="font-size:24px>Upload an image</p>
  <div id="progressbar"></div>
  <input id="file" type="file"/>
</form>
<script>
  var targetURL = ''
  function file_select_handler(to_upload) {
      var progressbar = $('#progressbar');
      var status = $('#status');
      var xhr = new XMLHttpRequest();
      xhr.upload.addEventListener('loadstart', function(e1){
          progressbar.progressbar({max: e1.total});
      });
      xhr.upload.addEventListener('progress', function(e1){
          if (progressbar.progressbar('option', 'max') == 0)
              progressbar.progressbar('option', 'max', e1.total);
          progressbar.progressbar('value', e1.loaded);
      });
      xhr.onreadystatechange = function(e1) {
          if (this.readyState == 4)  {
              if (this.status == 200){
                  targetURL = this.responseText
              }
              else
                  var text = 'upload failed: code ' + this.status;
              progressbar.progressbar('destroy');

              $('#crop-image').attr('src', targetURL);
              $('#crop-image').Jcrop({
                  onSelect: offerSubmit,
                  onChange: offerSubmit, 
                  setSelect: [0,0,9999,9999]
                });
          }
      };
      xhr.open('POST', '/post', true);
      xhr.send(to_upload);

  };

  function offerSubmit(c){
    $("#crop-submit").css('display', 'block');
    $("#image-header").css('display', 'block');

    $('#crop-submit').unbind().click(function (){
          $('#loading').show();
          var target = $('#crop-image')
          var pub = $('#text1').val();
          var author = $('#text2').val();
          var date = $('#text3').val();
          var other = $('#text4').val();

          $.post('/crop', {target: targetURL, left: c.x, upper: c.y, right: c.x2, lower: c.y2,
                            q1: pub, q2: author, q3: date, q4: other},
                            function(reply){
            $(".waitToShow").css('display', 'inline-block');
            $('#status').html(reply)
            $('#loading').hide();
            })
      })
  }

  $('#file').change(function(e){
      file_select_handler(e.target.files[0]);
      e.target.value = '';
  });

</script>
</body>
</html>
""" 

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', threaded=True)

