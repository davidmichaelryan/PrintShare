PrintShare
==========

## Overview
PrintShare is a proof-of-concept mobile web app that allows you to take a picture of a print article and share its online version through Twitter. The current version of the project can be found at http://printshare.herokuapp.com . 

The project is built on Flask, with some javascript to help on the front end. Since this was all our first time using Flask, the setup is deinitely a little hacky. Most of the code lives in app_test.py - that's where you will find the front end, the image uploader, and the cropping tool. We used Google's open source version of Python Tesseract, which was implemented in pytesseract.py. Finally, the calls to the Google Custom Search API was done in google.py.

There is a lot of room for some cool improvement with this app, specifically in better cleaning the OCR results, the user experience, and integration with the Twitter API (a failed attempt can be found in app_test-tweetapi.py)


##Installation and Usage
- Install the latest version of [Flask](http://flask.pocoo.org/),  Google's version of [Python Tesseract](https://code.google.com/p/python-tesseract/), and the [Python Imaging Library](http://www.pythonware.com/products/pil/) 
- Clone this repository. 
- Replace your API keys for the Google Custom Search function, in google.py 


##Development
- run `foreman start` to view a local version of the app.