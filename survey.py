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
hadQ = False
thisQid = 1

class Questions(db.Model):
	"""Models anquestion entry with question, choices, multiple, answers, userID, surveyID, questionID."""
	question = db.StringProperty()
	choices = db.StringProperty(multiline=True)
	multiple = db.BooleanProperty()
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
		global surveyID
		global surveyIDempty
		global addNewQ
		global surveyIDvalid
		global addNewQ
		global hadQ
		global thisQid
		surveyID = ""
		surveyIDempty = True
		addNewQ = False
		surveyIDvalid = False
		addNewQ = False
		hadQ = False
		thisQid = 1
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
	global hadQ
	global thisQid

	template_values = {
	    'surveyID': surveyID,
	    'surveyIDempty': surveyIDempty,
	    'surveyIDvalid': surveyIDvalid,
	    'addNewQ': addNewQ,
	}
	self.response.out.write(template.render(path, template_values))
	form = cgi.FieldStorage()
	# update surveyID and surveyID valid boolean
	if (form.has_key("surveyID") and not surveyIDvalid and surveyIDempty):
		addNewQ = False
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
		addNewQ = False
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
		self.response.clear()
		question_query = Questions.all()
		question_query.filter("surveyID", surveyID)
		question_query.order("questionID")
		questionShows = question_query.fetch(100)
		for question in questionShows:
			if (question.questionID):
				hadQ = True
				thisQid = question.questionID + 1
		template_values = {
			'surveyID': surveyID,
			'surveyIDempty': surveyIDempty,
			'surveyIDvalid': surveyIDvalid,
			'addNewQ': addNewQ,
			'questionShows': questionShows,
			'hadQ': hadQ,
			'thisQid': thisQid,
		}
		self.response.out.write(template.render(path, template_values))
		# update database
		if (form.has_key("question") and form.has_key("choices")):
			if (form.has_key("multiple")):
				multiple = True
			else:
			 	multiple = False
			# should add a message here!!!
			Questions(question = form["question"].value,
				  choices = form["choices"].value,
				  multiple = multiple,
				  surveyID = surveyID,
				  questionID = thisQid,
				  key_name=surveyID+str(thisQid)).put()
			# set site consistant with database
			self.response.clear()
			question_query = Questions.all()
			question_query.filter("surveyID", surveyID)
			question_query.order("questionID")
			questionShows = question_query.fetch(100)
			for question in questionShows:
				if (question.questionID):
					hadQ = True
					thisQid = question.questionID + 1
			template_values = {
				'surveyID': surveyID,
				'surveyIDempty': surveyIDempty,
				'surveyIDvalid': surveyIDvalid,
				'addNewQ': addNewQ,
				'questionShows': questionShows,
				'hadQ': hadQ,
				'thisQid': thisQid,
			}
			self.response.out.write(template.render(path, template_values))
			# update database
			for questionEntry in questionShows:
#self.response.out.write(newQuestion + " <br />")				
				if (form.has_key(str(questionEntry.questionID)+"question") and form.has_key(str(questionEntry.questionID)+"choices")):
					self.response.out.write("question: "+form[str(questionEntry.questionID)+"question"].value +" <br />")
					self.response.out.write("choices: "+form[str(questionEntry.questionID)+"choices"].value +" <br />")
					if (form.has_key(str(questionEntry.questionID)+"multiple")):
						multiple = True
					else:
				 		multiple = False
				
					Questions(question = form[str(questionEntry.questionID)+"question"].value,
						  choices = form[str(questionEntry.questionID)+"choices"].value,
						  multiple = multiple,
						  surveyID = surveyID,
						  questionID = questionEntry.questionID,
						  key_name=surveyID+str(questionEntry.questionID)).put()
			# set site consistant with database
			self.response.clear()
			question_query = Questions.all()
			question_query.filter("surveyID", surveyID)
			question_query.order("questionID")
			questionShows = question_query.fetch(100)

			for question in questionShows:
				if (question.questionID):
					hadQ = True
					thisQid = question.questionID + 1
			template_values = {
				'surveyID': surveyID,
				'surveyIDempty': surveyIDempty,
				'surveyIDvalid': surveyIDvalid,
				'addNewQ': addNewQ,
				'questionShows': questionShows,
				'hadQ': hadQ,
				'thisQid': thisQid,
			}
			self.response.out.write(template.render(path, template_values))



			self.response.out.write(form["choices"].value + "!! <br />")

			addNewQ = False





	# just for testing...
	surveyQuery = Surveys.all()	# will be deleted
	surveyShows = surveyQuery.fetch(1000)	# will be deleted
	self.response.out.write('Already had questions: '+ str(hadQ) + "<br />")
	self.response.out.write('Last question ID: '+ str(thisQid) + "<br />")
	for surveyII in surveyShows:	# will be deleted
		voteN = str(surveyII.voteN)	# will be deleted
		self.response.out.write("Survey Name: "+surveyII.surveyID+" ; Vote Number: "+voteN+"<br />")	# will be deleted
	self.response.out.write('surveyID: '+ surveyID + "<br />")
	sIe = str(surveyIDempty)
	sIv = str(surveyIDvalid)
	self.response.out.write('surveyIDempty: '+ sIe + "<br />")
	self.response.out.write('surveyIDvalid: '+ sIv + "<br />")
	self.response.out.write('addNewQ: '+ str(addNewQ) + "<br />")





application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/create', CreateSurvey),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
