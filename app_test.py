import flask
import json
import os
import time
from PIL import Image, ImageFile
from gevent.event import AsyncResult, Timeout
from gevent.queue import Empty, Queue
from shutil import rmtree
from hashlib import sha1
from stat import S_ISREG, ST_CTIME, ST_MODE


import pytesseract
import google

DATA_DIR = 'data'
KEEP_ALIVE_DELAY = 0
MAX_IMAGE_SIZE = 800, 600
MAX_IMAGES = 0
MAX_DURATION = 300
global start
start = 0

app = flask.Flask(__name__, static_folder=DATA_DIR)
broadcast_queue = Queue()


try:  # Reset saved files on each start
    rmtree(DATA_DIR, True)
    os.mkdir(DATA_DIR)
except OSError:
    pass


def broadcast(message):
    """Notify all waiting waiting gthreads of message."""
    waiting = []
    try:
        while True:
            waiting.append(broadcast_queue.get(block=False))
    except Empty:
        pass
    print('Broadcasting {0} messages'.format(len(waiting)))
    for item in waiting:
        item.set(message)


def receive():
    """Generator that yields a message at least every KEEP_ALIVE_DELAY seconds.

    yields messages sent by `broadcast`.

    """
    now = time.time()
    end = now + MAX_DURATION
    tmp = None
    # Heroku doesn't notify when client disconnect so we have to impose a
    # maximum connection duration.
    while now < end:
        if not tmp:
            tmp = AsyncResult()
            broadcast_queue.put(tmp)
        try:
            yield tmp.get(timeout=KEEP_ALIVE_DELAY)
            tmp = None
        except Timeout:
            yield ''
        now = time.time()


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


def event_stream(client):
    force_disconnect = False
    try:
        for message in receive():
            yield 'data: {0}\n\n'.format(message)
        print('{0} force closing stream'.format(client))
        force_disconnect = True
    finally:
        if not force_disconnect:
            print('{0} disconnected from stream'.format(client))


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
            broadcast(message)  # Notify subscribers of completion
    except Exception as e:  # Output errors
        return '{0}'.format(e)
    image = Image.open(target)
    return q

    q = pytesseract.image_to_string(image)
    answer = ''
    result = google.query(q)
    for r in result:
      answer = (answer + '<a href="' + str(r[0]) + '">' 
                + '<div class="result">'
                + str(r[1]) + '<br>' 
                + str(r[2]) + '<br>' 
                + str(r[0]) + '<br>'
                + '</div>'
                + '</a>' + '<br>')
    return answer

    


@app.route('/stream')
def stream():
    return flask.Response(event_stream(flask.request.access_route[0]),
                          mimetype='text/event-stream')


@app.route('/')
def home():
    # Code adapted from: http://stackoverflow.com/questions/168409/
    image_infos = []
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        file_stat = os.stat(filepath)
        if S_ISREG(file_stat[ST_MODE]):
            image_infos.append((file_stat[ST_CTIME], filepath))

    images = []
    for i, (_, path) in enumerate(sorted(image_infos, reverse=True)):
        if i >= MAX_IMAGES:
            os.unlink(path)
            continue
        images.append('<div><img alt="User uploaded image" src="{0}" /></div>'
                      .format(path))
    return """
<!doctype html>
<title>Print Share</title>
<meta charset="utf-8" />
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/jquery-ui.min.js"></script>
<link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.1/themes/vader/jquery-ui.css" />
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
<!-- <p>Only the most recent %s images are saved.</p> -->


<noscript>Note: You must have javascript enabled in order to upload and
dynamically view new images.</noscript>
<fieldset>
  <p id="status">Upload an image</p>
  <div id="progressbar"></div>
  <input id="file" type="file" />
</fieldset>
<h3>Your Picture</h3>
<div id="images">%s</div>
<script>
  function sse() {
      var source = new EventSource('/stream');
      source.onmessage = function(e) {
          if (e.data == '')
              return;
          var data = $.parseJSON(e.data);
          var upload_message = '';
          var image = $('<img>', {alt: upload_message, src: data['src']});
          var container = $('<div>').hide();
          container.append($('<div>', {text: upload_message}));
          container.append(image);
          $('#images div:last-child').remove();
          $('#images').prepend(container);
          image.load(function(){
              container.show('blind', {}, 1000);
          });
      };
  }
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
  sse();

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-510348-17']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
""" % (MAX_IMAGES, '\n'.join(images))


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', threaded=True)

