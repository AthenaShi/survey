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

surveyID = ""
surveyIDempty = True
addNewQ = False
surveyIDvalid = False
addNewQ = False

class Questions(db.Model):
	"""Models anquestion entry with question, choices, exclusive, answers, userID, surveyID, questionID."""
	question = db.StringProperty()
	choices = db.StringProperty(multiline=True)
	exclusive = db.BooleanProperty()
	answers = db.StringProperty()
	userID = db.UserProperty()
	surveyID = db.StringProperty()
	questionID = db.IntegerProperty()

class Surveys(db.Model):
	"""Models a survey entry with surveyID, voteN, createDate, LastVoteDate."""
	surveyID = db.StringProperty()
	voteN = db.IntegerProperty()
	createDate = db.DateTimeProperty()
	LastVoteDate = db.DateTimeProperty()

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
	form = cgi.FieldStorage()
	if (form.has_key("create")):
		self.response.out.write("Got it!")
		self.redirect('/create')

class CreateSurvey(webapp.RequestHandler):
    def get(self):
	survey_query = Surveys.all()
	surveyEntrys = survey_query.fetch(1000)
	path = os.path.join(os.path.dirname(__file__), 'createSurvey.html')
	global surveyID
	global surveyIDempty
	global addNewQ
	global surveyIDvalid
	global addNewQ
	template_values = {
	    'surveyID': surveyID,
	    'surveyIDempty': surveyIDempty,
	    'surveyIDvalid': surveyIDvalid,
	    'addNewQ': addNewQ,
	}
	self.response.out.write(template.render(path, template_values))
	form = cgi.FieldStorage()
	# update surveyID and surveyID valid boolean
	if (form.has_key("surveyID") and not surveyIDvalid):
		surveyID =  form["surveyID"].value
		# check if surveyID is valid
		if (surveyID != ""):
			surveyIDvalid = True
			surveyIDempty = False
		for surveyIDhad in surveyEntrys:
			if (surveyID == surveyIDhad.surveyID):
				surveyIDvalid = False
	# if suveryID is duplicated...
	if (not surveyIDvalid and form.has_key("test")):
		self.response.clear()
		template_values = {
			'surveyID': surveyID,
			'surveyIDempty': surveyIDempty,
			'surveyIDvalid': surveyIDvalid,
			'addNewQ': addNewQ,
		}
		self.response.out.write(template.render(path, template_values))
	# if surveyID is valid
	if (surveyIDvalid and form.has_key("test")):
		Surveys(surveyID=surveyID, key_name=surveyID, voteN = 0).put()
		self.response.clear()
		template_values = {
			'surveyID': surveyID,
			'surveyIDempty': surveyIDempty,
			'surveyIDvalid': surveyIDvalid,
			'addNewQ': addNewQ,
		}
		self.response.out.write(template.render(path, template_values))
	# add new questions...
	
	if (form.has_key("add")):
		addNewQ = True
#			question_query = Questions.all()
#			question_query.filter("surveyID", surveyID)
#			question_query.order("questionID")
#			questionShows = question_query.fetch(100)
#			template_values = {
#				'surveyID': surveyID,
#				'surveyIDempty': surveyIDempty,
#				'surveyIDvalid': surveyIDvalid,
#				'addNewQ': addNewQ,
#				'questionShows': questionShows
#			}
#			self.response.out.write(template.render(path, template_values))
#			self.response.out.write('addNewQ: '+ str(addNewQ) + "<br />")
		self.response.out.write("Add new question: "+ str(addNewQ)+" <br />")




	# just for testing...
	surveyQuery = Surveys.all()	# will be deleted
	surveyShows = surveyQuery.fetch(1000)	# will be deleted
	for surveyII in surveyShows:	# will be deleted
		voteN = str(surveyII.voteN)	# will be deleted
		self.response.out.write("Survey Name: "+surveyII.surveyID+" ; Vote Number: "+voteN+"<br />")	# will be deleted
	self.response.out.write('surveyID: '+ surveyID + "<br />")
	sIe = str(surveyIDempty)
	sIv = str(surveyIDvalid)
	self.response.out.write('surveyIDempty: '+ sIe + "<br />")
	self.response.out.write('surveyIDvalid: '+ sIv + "<br />")





application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/create', CreateSurvey),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
