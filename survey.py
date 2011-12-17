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

suveyID = ""
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
	answers = db.StringProperty(multiline=True)
	userID = db.UserProperty()
	surveyID = db.StringProperty()
	questionID = db.IntegerProperty()

class Surveys(db.Model):
	"""Models a survey entry with surveyID, voteN, createDate, LastVoteDate."""
	surveyID = db.StringProperty()
	voteN = db.IntegerProperty()
	createDate = db.DateTimeProperty()
	LastVoteDate = db.DateTimeProperty()

class Votes(db.Model):
	"""Models a vote entry with userID, surveyID, result."""
	userID = db.UserProperty()
	surveyID = db.StringProperty()
	result = db.StringProperty(multiline=True)

class VoteSurvey(webapp.RequestHandler):
    def get(self):
	# Show survey questions and choices and let vote!
	form = cgi.FieldStorage()
	surveyID = form["surveyID"].value

	question_query = Questions.all()
	question_query.filter("surveyID", surveyID)
	question_query.order("questionID")
	questionShows = question_query.fetch(100)

	template_values = {
		'surveyID': surveyID,
		'questionShows': questionShows,
	}
	path = os.path.join(os.path.dirname(__file__), 'vote.html')
	self.response.out.write(template.render(path, template_values))
	# Record vote results
	if (form.has_key("vote")):
		voted = False
		votes = ""
		for questionEntry in questionShows:
			questionID = questionEntry.questionID
			self.response.out.write(questionEntry.question+"<br />")
			i = 0
			answer = []
			choices = questionEntry.choices.splitlines()
			answers = questionEntry.answers.splitlines()
			for choice in choices:
				selectV = "selection,"+str(questionID)
				if ( form.has_key(selectV) and i == int(form[selectV].value) ):
					answers[i] = str(int(answers[i])+1)
					self.response.out.write(choice+"---Yes---:"+answers[i]+" <br />")
					voted = True
					votes = votes+"1 "
				elif (form.has_key("selection,"+str(questionID)+","+str(i))):
					answers[i] = str(int(answers[i])+1)
					self.response.out.write(choice+"---Yes---:"+answers[i]+" <br />")
					voted = True
					votes = votes+"1 "
				else:
					self.response.out.write(choice+"---No---:"+answers[i]+" <br />")
					votes = votes+"0 "
				i = i+1		
			answersUpdate = "\n".join(answers)
			questionEntry.answers = answersUpdate
			questionEntry.put()
			self.response.out.write(questionEntry.answers+" <br />")
			votes = votes+"\n"
		if (not voted):
			template_values = { 'message': "Sorry!  You need to vote at least one question.  If you don't want to vote, please press 'Cancel' to go back to the main page." }
			path = os.path.join(os.path.dirname(__file__), 'alertDialogBox.html')
			self.response.out.write(template.render(path, template_values))
		else:
			# update Surveys database
			surveyToUpdate = Surveys.all().filter("surveyID", surveyID).fetch(1)
			for surveyEntry in surveyToUpdate:
				surveyEntry.voteN += 1
				surveyEntry.LastVoteDate = datetime.datetime.now()
				surveyEntry.put()
				# self.response.out.write(str(surveyEntry.voteN)+":"+str(surveyEntry.LastVoteDate)+" <br />")
			# update Votes database
			Votes(  #userID = "athena",
				surveyID = surveyID, key_name=surveyID, #should be changed to surveyID + userID
				result = votes ).put()
			userVotes = Votes.all().filter("surveyID", surveyID).fetch(1)
			self.response.out.write(votes+" <br />")			
			for userVote in userVotes:
#				userVote.delete()
				self.response.out.write(userVote.surveyID + ": " + userVote.result + "<br />")

			# self.redirect("/results?surveyID="+surveyID)

	if (form.has_key("back")):
		self.redirect('/')


class MainPage(webapp.RequestHandler):
    def get(self):
	# get all surveyIDs we already have
	survey_queryAll = Surveys.all()
	# survey_queryAll.order("")	Can be changed according to the display order...........
	surveyEntrysAll = survey_queryAll.fetch(1000)

	# get all surveyIDs the login user have access to...
	survey_queryUser = Surveys.all()	#will be changed according to the user ID
	# survey_queryUser .order("")	Can be changed according to the display order...........
	surveyEntrysUser = survey_queryUser.fetch(1000)

	# url = "/vote?surveyID=helloAthena"
        template_values = {
            'surveyEntrysAll': surveyEntrysAll,
            'surveyEntrysUser': surveyEntrysUser,
        }
        path = os.path.join(os.path.dirname(__file__), 'mainPage.html')
        self.response.out.write(template.render(path, template_values))
	form = cgi.FieldStorage()

	if (form.has_key("create")):
		self.redirect('/create')
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

class CreateSurvey(webapp.RequestHandler):
    def get(self):
	global surveyID
	global surveyIDempty
	global addNewQ
	global surveyIDvalid
	global addNewQ
	global hadQ
	global thisQid

	survey_query = Surveys.all()
	surveyEntrys = survey_query.fetch(1000)

	path = os.path.join(os.path.dirname(__file__), 'createSurvey.html')
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
		if (form.has_key("surveyID") and not surveyIDvalid):
			addNewQ = False
			surveyID =  form["surveyID"].value
			# check if surveyID is valid
			if (surveyID != ""):
				surveyIDvalid = True
				surveyIDempty = False
			for surveyIDhad in surveyEntrys:
				if (surveyID == surveyIDhad.surveyID):
					surveyIDvalid = False
	# if surveyID is valid
	if (surveyIDvalid and form.has_key("test")):
		addNewQ = False
		Surveys(surveyID=surveyID, key_name=surveyID, voteN = 0, createDate = datetime.datetime.now()).put()
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
			addNewQ = False
	if (form.has_key("done")):
		for questionID in range(1,thisQid):
			if (form.has_key(str(questionID)+"question") and form.has_key(str(questionID)+"choices")):
				question = form[str(questionID)+"question"].value	# question
				choices = form[str(questionID)+"choices"].value		# choices
				if (form.has_key(str(questionID)+"multiple")):		# multiple
					multiple = True
				else:
			 		multiple = False

				answers = ""						# answers
				for choice in choices.splitlines():
					answers = answers+"0\n"
				# final update of the creation	
				Questions(question = question,
					  choices = choices,
					  multiple = multiple,
					  answers = answers,
					  surveyID = surveyID,
					  questionID = questionID,
					  key_name=surveyID+str(questionID)).put()
		if (form.has_key("question") and form.has_key("choices")):
				choices = form["choices"].value
				if (form.has_key("multiple")):
					multiple = True
				else:
			 		multiple = False
				answers = ""						# answers
				for choice in choices.splitlines():
					answers = answers+"0\n"
				# final update of the creation
				Questions(question = form["question"].value,
					  choices = form["choices"].value,
					  multiple = multiple,
					  answers = answers,
					  surveyID = surveyID,
					  questionID = thisQid,
					  key_name=surveyID+str(thisQid)).put()
		
		question_query = Questions.all()
		question_query.filter("surveyID", surveyID)
		question_query.order("questionID")
		questionShows = question_query.fetch(100)

		self.response.clear()
		template_values = {
				'surveyID': surveyID,
				'questionShows': questionShows,
		}
		path = os.path.join(os.path.dirname(__file__), 'createDone.html')
		self.response.out.write(template.render(path, template_values))
	
	if (form.has_key("back")):
		self.redirect('/')

	# just for testing...
	self.response.out.write("<br />*******just for testing******<br />")
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
  ('/vote', VoteSurvey),
#  ('/results', ShowResults),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
