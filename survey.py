import os
from google.appengine.ext.webapp import template

import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    def get(self):
        surveysAlready = ("Video Game Survey", "Comic Survey", "Money Survey", "Video Game Survey 2")
        surveysMine = ("Video Game Survey", "Video Game Survey 2")
        template_values = {
            'surveysAlready': surveysAlready,
            'surveysMine': surveysMine,
        }

        path = os.path.join(os.path.dirname(__file__), 'mainPage.html')
        self.response.out.write(template.render(path, template_values))
#	form = cgi.FieldStorage()
#	if (form.has_key("create")):
#		self.response.out.write("Got it!")


application = webapp.WSGIApplication([
  ('/', MainPage),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
