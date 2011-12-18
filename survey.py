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

class Users(db.Model):
	"""Models a user entry with just userID, loginDate."""
	userID = db.UserProperty()
	loginDate = db.DateTimeProperty()

class Questions(db.Model):
	"""Models a question entry with question, choices, multiple, answers, userID, surveyID, questionID."""
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
	userID = db.UserProperty()
	createDate = db.DateTimeProperty()
	LastVoteDate = db.DateTimeProperty()

class Votes(db.Model):
	"""Models a vote entry with userID, surveyID, result."""
	userID = db.UserProperty()
	surveyID = db.StringProperty()
	result = db.StringProperty(multiline=True)

class BrowseUser(webapp.RequestHandler):
    def get(self):
	form = cgi.FieldStorage()
	userName = form["userID"].value
	# get the login user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	# get the browsed user
	allUsers = Users.all()
	for userEntry in allUsers:
		if (userEntry.userID.nickname() == userName):
			userBrowsed = userEntry.userID
	# get survey that user created
	surveyCreated = Surveys.all().filter("userID", userBrowsed)
	# get survey that user voted
	surveyVoted = Votes.all().filter("userID", userBrowsed)
	path = os.path.join(os.path.dirname(__file__), 'browseUser.html')
	# if done those survey before
	votedSurveyME = Votes.all().filter("userID", user)
	surveyVotedME = "blah"
	for surveyII in votedSurveyME:
		surveyVotedME = surveyVotedME+"\n"+surveyII.surveyID
	# get all users

	template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'userName': userName,
			'surveyCreated': surveyCreated,
			'surveyVoted': surveyVoted,
			'surveyVotedME': surveyVotedME,
	}
	self.response.out.write(template.render(path, template_values))
	if (form.has_key("back")):
		self.redirect('/')

class EditSurvey(webapp.RequestHandler):
    def get(self):
	# Show survey questions and choices and let vote!
	form = cgi.FieldStorage()
	surveyID = form["surveyID"].value
	# get the user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	# get question need to show
	questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
	path = os.path.join(os.path.dirname(__file__), 'editSurvey.html')
	addNewQ = False
	template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'surveyID': surveyID,
			'addNewQ': addNewQ,
			'questionShows': questionShows,
	}
	self.response.out.write(template.render(path, template_values))
	thisQid = 1
	for question in questionShows:
		if (question.questionID):
			thisQid = question.questionID + 1

    def post(self):	# need to change something here...
	# Show survey questions and choices and let vote!
	form = cgi.FieldStorage()
	surveyID = form.getvalue("surveyID")
	if (type(surveyID) is str):
		surveyID = surveyID
	else:
	 	surveyID = surveyID[0]
	# get the user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	# get question need to show
	questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
	path = os.path.join(os.path.dirname(__file__), 'editSurvey.html')
	addNewQ = False
	template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'surveyID': surveyID,
			'addNewQ': addNewQ,
			'questionShows': questionShows,
	}
	self.response.out.write(template.render(path, template_values))
	thisQid = 1
	for question in questionShows:
		if (question.questionID):
			thisQid = question.questionID + 1
	if (form.has_key("back")):
		self.redirect('/')
	# add new questions...	
	if (form.has_key("add")):
		addNewQ = True
		self.response.clear()
		questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
		for question in questionShows:
			if (question.questionID):
				thisQid = question.questionID + 1
		template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'surveyID': surveyID,
			'addNewQ': addNewQ,
			'questionShows': questionShows,
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
			questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
			for question in questionShows:
				if (question.questionID):
					thisQid = question.questionID + 1
			template_values = {
				'greeting': greeting,
				'url': url,
				'url_linktext': url_linktext,
				'surveyID': surveyID,
				'addNewQ': addNewQ,
				'questionShows': questionShows,
				'thisQid': thisQid,
			}
			self.response.out.write(template.render(path, template_values))
			# update database
			for questionEntry in questionShows:
				if (form.has_key(str(questionEntry.questionID)+"question") and form.has_key(str(questionEntry.questionID)+"choices")):
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
			questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")

			for question in questionShows:
				if (question.questionID):
					thisQid = question.questionID + 1
			template_values = {
				'greeting': greeting,
				'url': url,
				'url_linktext': url_linktext,
				'surveyID': surveyID,
				'addNewQ': addNewQ,
				'questionShows': questionShows,
				'thisQid': thisQid,
			}
			self.response.out.write(template.render(path, template_values))
			addNewQ = False
	if (form.has_key("done")):
		# update Questions database
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
				Questions(question = form["question"].value,
					  choices = form["choices"].value,
					  multiple = multiple,
					  answers = answers,
					  surveyID = surveyID,
					  questionID = thisQid,
					  key_name=surveyID+str(thisQid)).put()
		# reset Surveys database
		surveyToUpdate = Surveys.all().filter("surveyID", surveyID)
		for surveyEntry in surveyToUpdate:
			surveyEntry.voteN = 0
			surveyEntry.CreateDate = datetime.datetime.now()
#			surveyEntry.userID = user
			surveyEntry.put()
		# update Votes database
		votes4surveyID = Votes.all().filter("surveyID", surveyID)
		for vote4surveyID in votes4surveyID:
			vote4surveyID.delete()
		# show edit result page
		questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
		self.response.clear()
		template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'surveyID': surveyID,
			'questionShows': questionShows,
		}
		path = os.path.join(os.path.dirname(__file__), 'createDone.html')
		self.response.out.write(template.render(path, template_values))	
	if (form.has_key("back")):
		self.redirect('/')

class ShowResults(webapp.RequestHandler):
    def get(self):
	# Show survey questions and choices and let vote!
	form = cgi.FieldStorage()
	surveyID = form["surveyID"].value
	# get the user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	# get questions to show
	questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
	template_values = {
		'greeting': greeting,
		'url': url,
		'url_linktext': url_linktext,
		'surveyID': surveyID,
		'questionShows': questionShows,
	}
	path = os.path.join(os.path.dirname(__file__), 'results.html')
	self.response.out.write(template.render(path, template_values))
	if (form.has_key("back")):
		self.redirect('/')

class VoteSurvey(webapp.RequestHandler):
    def get(self):
	# Show survey questions and choices and let vote!
	form = cgi.FieldStorage()
	surveyID = form["surveyID"].value
	# get the user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	# get questions to show
	questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
	votedQuery = Votes.all().filter("userID", user).filter("surveyID", surveyID)
	voteD = False
	votedResult = ""
	for votedQ in votedQuery:
		votedResult = votedQ.result
		voteD = True

	template_values = {
		'greeting': greeting,
		'url': url,
		'url_linktext': url_linktext,
		'surveyID': surveyID,
		'questionShows': questionShows,
		'voteD': voteD,
		'votedResult': votedResult,
	}
	path = os.path.join(os.path.dirname(__file__), 'vote.html')
	self.response.out.write(template.render(path, template_values))
	# Record vote results in Questions db
	if (form.has_key("vote")):
		voted = False	# if voted this time
		votes = ""	# the vote result of this time
		if (voteD):	# if voted before
			votedResult2D = []	# a 2D array with 0/1 to indicate choices
			for votedR in votedResult.splitlines():
				votedEachQ = votedR.split()
				votedResult2D.append(votedEachQ)
			
		for questionEntry in questionShows:
			questionID = questionEntry.questionID
			i = 0
			answer = []
			choices = questionEntry.choices.splitlines()
			answers = questionEntry.answers.splitlines()
			for choice in choices:
				if (voteD):	# subtract answers by 1
					if (votedResult2D[questionID-1][i] == "1"):
						answers[i] = str(int(answers[i])-1)
				selectV = "selection,"+str(questionID)
				if ( form.has_key(selectV) and i == int(form[selectV].value) ):
					answers[i] = str(int(answers[i])+1)
					voted = True
					votes = votes+"1 "
				elif (form.has_key("selection,"+str(questionID)+","+str(i))):
					answers[i] = str(int(answers[i])+1)
					voted = True
					votes = votes+"1 "
				else:
					votes = votes+"0 "
				i = i+1
			answersUpdate = "\n".join(answers)
			questionEntry.answers = answersUpdate
			questionEntry.put()
			votes = votes+"\n"
		if (not voted):
			template_values = { 'message': "Sorry!  You need to vote at least one question.  If you don't want to vote, please press 'Cancel' to go back to the main page." }
			path = os.path.join(os.path.dirname(__file__), 'alertDialogBox.html')
			self.response.out.write(template.render(path, template_values))
		else:
			# update Surveys database
			surveyToUpdate = Surveys.all().filter("surveyID", surveyID)
			for surveyEntry in surveyToUpdate:
				if (not voteD):
					surveyEntry.voteN += 1
				surveyEntry.LastVoteDate = datetime.datetime.now()
				surveyEntry.put()
			# update Votes database
			Votes(  userID = user,
				surveyID = surveyID, key_name=surveyID+str(user), #should be changed to surveyID + userID
				result = votes ).put()
			self.redirect("/results?surveyID="+surveyID)
	if (form.has_key("back")):
		self.redirect('/')

class MainPage(webapp.RequestHandler):
    def get(self):
	# get the user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	Users(userID=user, loginDate=datetime.datetime.now(),key_name=str(user)).put()
	# DELETE ALL THE DATA!!!
	'''surveyEntrysAll = Surveys.all()
	for delete in surveyEntrysAll:
		delete.delete()
	questionEntry = Questions.all()
	for delete in questionEntry:
		delete.delete()
	voteEntry = Votes.all()
	for delete in voteEntry:
		delete.delete()
	userEntry = Users.all()
	for delete in userEntry:
		delete.delete()'''

	# get all surveyIDs we already have
	surveyEntrysAll = Surveys.all()
	# surveyEntrysAll.order("")	Can be changed according to the display order...........

	# get all surveyIDs the login user have access to...
	surveyEntrysUser = Surveys.all().filter("userID", user)	#will be changed according to the user ID
	# surveyEntrysUser .order("")	Can be changed according to the display order...........
	# if done this survey before
	votedSurvey = Votes.all().filter("userID", user)
	surveyVoted = "blah"
	for surveyII in votedSurvey:
		surveyVoted = surveyVoted+"\n"+surveyII.surveyID
	# get all users
	allusers = Users.all()
	allusersArray = []
	for userEntry in allusers:
		allusersArray.append(userEntry.userID.nickname())
        template_values = {
	    'greeting': greeting,
	    'url': url,
            'url_linktext': url_linktext,
            'allusersArray': allusersArray,
            'surveyEntrysAll': surveyEntrysAll,
            'surveyEntrysUser': surveyEntrysUser,
            'surveyVoted': surveyVoted,
        }
        path = os.path.join(os.path.dirname(__file__), 'mainPage.html')
        self.response.out.write(template.render(path, template_values))
	form = cgi.FieldStorage()

	surveyToBeDeleted = Surveys.all().filter("userID", user)
	for surveyDelete in surveyToBeDeleted:
		surveyName = surveyDelete.surveyID
		if (form.has_key("delete"+surveyName)):	# "delete{{ surveysU.surveyID }}"
			# delete surveyID from Surveys DB
			surveyDelete.delete()
			# delete surveyID from Votes DB
			for surveyInVote in Votes.all().filter("surveyID", surveyName):
				surveyInVote.delete()
			# delete surveyID from Questions DB
			for surveyInQuestion in Questions.all().filter("surveyID", surveyName):
				surveyInQuestion.delete()
			self.redirect('/')

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
    def post(self):
	global surveyID
	global surveyIDempty
	global addNewQ
	global surveyIDvalid
	global addNewQ
	global hadQ
	surveyID = ""
	surveyIDempty = True
	addNewQ = False
	surveyIDvalid = False
	addNewQ = False
	hadQ = False
	thisQid = 1

	surveyEntrys = Surveys.all()
	# get the user 
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		greeting = "Hello, "+user.nickname()+"~ "
	else:
		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		greeting = "Hello, please: "
	path = os.path.join(os.path.dirname(__file__), 'createSurvey.html')
	template_values = {
		'greeting': greeting,
		'url': url,
		'url_linktext': url_linktext,
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
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
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
		Surveys(surveyID=surveyID, key_name=surveyID, userID = user, voteN = 0, createDate = datetime.datetime.now()).put()
		self.response.clear()
		template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'surveyID': surveyID,
			'surveyIDempty': surveyIDempty,
			'surveyIDvalid': surveyIDvalid,
			'addNewQ': addNewQ,
		}
		self.response.out.write(template.render(path, template_values))
	# add new questions...	
	if (form.has_key("add")):
		addNewQ = True
		thisQid = 1
		self.response.clear()
		questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
		for question in questionShows:
			if (question.questionID):
				hadQ = True
				thisQid = question.questionID + 1
		template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
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
				  userID = user,
				  key_name=surveyID+str(thisQid)).put()
			# set site consistant with database
			self.response.clear()
			questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
			for question in questionShows:
				if (question.questionID):
					hadQ = True
					thisQid = question.questionID + 1
			template_values = {
				'greeting': greeting,
				'url': url,
				'url_linktext': url_linktext,
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
			questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
			for question in questionShows:
				if (question.questionID):
					hadQ = True
					thisQid = question.questionID + 1
			template_values = {
				'greeting': greeting,
				'url': url,
				'url_linktext': url_linktext,
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
		thisQid = int(form["thisQid"].value)
#		self.response.out.write(thisQid)
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
				self.response.out.write(thisQid)
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
		questionShows = Questions.all().filter("surveyID", surveyID).order("questionID")
		self.response.clear()
		template_values = {
				'greeting': greeting,
				'url': url,
				'url_linktext': url_linktext,
				'surveyID': surveyID,
				'questionShows': questionShows,
		}
		path = os.path.join(os.path.dirname(__file__), 'createDone.html')
		self.response.out.write(template.render(path, template_values))
	
	if (form.has_key("cancel")):
		if (form["cancel"].value == "Abort"):
			surveyToDelete = Surveys.all().filter("surveyID", surveyID)
			for surveyToD in surveyToDelete:
				surveyToD.delete()
		self.redirect('/')

	if (form.has_key("back")):
		self.redirect('/')

	# just for testing...
	self.response.out.write("<br />*******just for testing******<br />")
	surveyShows = Surveys.all()	# will be deleted
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
  ('/browse', BrowseUser),
  ('/vote', VoteSurvey),
  ('/edit', EditSurvey),
  ('/results', ShowResults),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
