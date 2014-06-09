PrintShare
==========

## Overview
PrintShare is a proof-of-concept mobile web app that allows you to take a picture of a print article and share its online version through Twitter. The current version of the project can be found at http://printshare.herokuapp.com  

The project is built on Flask, with some javascript to help on the front end. Since this was all our first time using Flask, we often opted for the quickest solution over the 'correct' one, and so we forgoed the templating options provided with the framework. Most of the code lives in app_test.py - that's where you will find the front end, the implementation of the JCrop image uploader, and the cropping tool. We used Google's open source version of Python Tesseract, which was implemented in pytesseract.py. Finally, the calls to the Google Custom Search API are done in google.py.

There is a lot of room for some cool improvement with this app, especially with further cleaning the OCR results, improving the user experience, and integration with the Twitter API (a failed attempt can be found in app_test-tweetapi.py)


##Installation and Usage
- Install the latest version of [Flask](http://flask.pocoo.org/),  Google's version of [Python Tesseract](https://code.google.com/p/python-tesseract/), and the [Python Imaging Library](http://www.pythonware.com/products/pil/) 
- Clone this repository. 
- Replace your API keys for the Google Custom Search function, in google.py 


##Development
- run `foreman start` to build and view a local version of the app.
- You can turn debugging for Flask on and off at the bottom of app_test.py
- The folder 'test images' has a variety of photos and screenshots that we used for testing different components of the app. 
