import flask
from flask import Flask, redirect, url_for
from flask import session, flash, g, \
     render_template
from flask_oauth import OAuth
import json
import os
import time
from PIL import Image, ImageFile
from shutil import rmtree
from hashlib import sha1
from flask import request 
import pytesseract
import google
import sys

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


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
app.secret_key = os.urandom(24)
oauth = OAuth()

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):  
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator




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
                + str(r[2]) + '<br>' 
                + str(r[0]) + '<br>'
                + '</div>'
        # + '<a href="http://twitter.com/home/?status=' + str(r[0]) +'">'
          +     '</a><span onclick="tweetLink(&quot;'+str(r[0])+'&quot;)" style="color:white;background-color:#318ce7;padding:5px 5px;border-radius:5px;margin-bottom:20px;display:inline-block;">Tweet the link</span>')
  #     + '<div class="tweet">'
        # + "Tweet it" + '<br>' 
  #               + '</div>'
  #               + '</a>' + '<br>')

    return answer



##===========START TWITTER===========



# Use Twitter as example remote application
twitter = oauth.remote_app('twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/1.1/',
    # where flask should look for new request tokens
    request_token_url='https://api.twitter.com/oauth/request_token',
    # where flask should exchange the token with the remote application
    access_token_url='https://api.twitter.com/oauth/access_token',
    # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
    # they mostly work the same, but for sign on /authenticate is
    # expected because this will give the user a slightly different
    # user interface on the twitter side.
    authorize_url='https://api.twitter.com/oauth/authenticate',
    # the consumer keys from the twitter application registry.
    consumer_key='PxOmrR580HNL3j5YB1S74t2hp',
    consumer_secret='vNd8aqeajik3D44PI9dgcTBMPj1cLPFpJ6pyVBkl4uOVau2hBy'
)

class User():
    name = ''
    id = ''
    oauth_token = ''
    oauth_secret = ''

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.after_request
@crossdomain(origin='*')
def after_request(response):
    response.headers['Access-Control-Allow-Headers'] = "*"
    return response


@twitter.tokengetter
@crossdomain(origin='*')
def get_twitter_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls.  During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret

@app.route('/tweet', methods=['POST', 'GET', 'OPTIONS'])
@crossdomain(origin='*')
def tweet():
    """Calls the remote twitter API to create a new status update."""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    return 'got to after login'
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    return 'got to right before post'
    resp = twitter.post('statuses/update.json', data={
        'status':       status
    })
    if resp.status == 403:
        flash('Your tweet was too long.')
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def login():
    #return 'got to login'
    return twitter.authorize()

@app.route('/logout', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def logout():
    session.pop('user', None)
    return redirect(request.referrer or url_for('index'))


@app.route('/oauth-authorized', methods=['GET', 'OPTIONS'])
@twitter.authorized_handler
@crossdomain(origin='*')
def oauth_authorized(resp):

    """Called after authorization.  After this function finished handling,
    the OAuth information is removed from the session again.  When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.

    Because the remote application could have re-authorized the application
    it is necessary to update the values in the database.

    If the application redirected back after denying, the response passed
    to the function will be `None`.  Otherwise a dictionary with the values
    the application submitted.  Note that Twitter itself does not really
    redirect back unless the user clicks on the application name.
    """
    return 'got to oauth-authorized' 
    resp.headers['Access-Control-Allow-Headers'] = "*"
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    user = User() 
    user.name = resp['screen_name']
    user.oauth_token = resp['oauth_token']
    user.oauth_secret = resp['oauth_token_secret']
    user.id = resp['user_id']

    session['user'] = user

    return redirect(next_url)



##===========END TWITTER===========


    
@app.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def home():
  try:  # Reset saved files on each start
    rmtree(DATA_DIR, True)
    os.mkdir(DATA_DIR)
  except OSError:
    pass

  return """
<!doctype html>
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
    padding-right: 1em;

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

#image-header {
  display: none;
}

h3 {
  text-align: center;
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

</style>


<h3>Print Share</h3>
<p>Share the web version of a print article</p>
<p id="status"></p>

<h3 id="image-header">Your Picture</h3>

<form>
  <img src="" id='crop-image'/>

  <div id="crop-submit">Submit</div>

  <p class="waitToShow">Have we not found it yet? Sorry about that! Help us narrow it down:</p>
  <p id="q1" class="waitToShow">Publication<br><input type="text" name="q1" id="text1"></input></p>
  <p id="q2" class="waitToShow">Author<br><input type="text" name="q2" id="text2"></input></p>
  <p id="q3" class="waitToShow">Date<br><input type="text" name="q3" id="text3"></input></p>
  <p id="q4" class="waitToShow">Other Keywords<br><input type="text" name="q4" id="text4"></input>
  <br>
  
</form>

<noscript>Note: You must have javascript enabled in order to upload and
dynamically view new images.</noscript>
<form>
  <p>Upload an image</p>
  <div id="progressbar"></div>
  <input id="file" type="file" />
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
    $(".waitToShow").css('display', 'block');
    $("#image-header").css('display', 'initial');

    $('#crop-submit').unbind().click(function (){
          var target = $('#crop-image')
          var pub = $('#text1').val();
          var author = $('#text2').val();
          var date = $('#text3').val();
          var other = $('#text4').val();

          $.post('/crop', {target: targetURL, left: c.x, upper: c.y, right: c.x2, lower: c.y2,
                            q1: pub, q2: author, q3: date, q4: other},
                            function(reply){
            $('#status').html(reply)
            })
      })
  }

  $('#file').change(function(e){
      file_select_handler(e.target.files[0]);
      e.target.value = '';
  });

function tweetLink(link){
  console.log('tweetLink engaged')
  $.post('/tweet', {tweet: link},
                            function(reply){
                            console.log(reply)
            $('#status').html('HOLY SHIT YOU TWEETED IT')
            })
}
</script>
""" 

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', threaded=True)
