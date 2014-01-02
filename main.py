
import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Task(ndb.Model):
	content = ndb.TextProperty()
	date = ndb.DateProperty(auto_now_add=True)
	done = ndb.BooleanProperty()

class Tasks(ndb.Model):
	user = ndb.UserProperty()
	date = ndb.DateProperty(auto_now_add = True)
	tasklist = ndb.StructuredProperty(Task, repeated = True)

class MainHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		tasks = None

		tasklist = Tasks.query().filter(Tasks.user == user, Tasks.date == datetime.now().date()).fetch()

		if len(tasklist) > 0:
			tasks = tasklist
		
		template_values = {
			'user': user,
			'login': users.create_login_url(self.request.uri),
			'logout': users.create_logout_url(self.request.uri),
			'date': datetime.now().date(),
			'tasks': tasks,
		}
		
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class ProcessTasks(webapp2.RequestHandler):
	def post(self):
		current_user = users.get_current_user()

		if current_user:
			tasks = Tasks(user = current_user)
			task1_content = self.request.get('task1')
			task2_content = self.request.get('task2')
			task3_content = self.request.get('task3')

			task1 = Task(content =  task1_content, done = False)
			task1.put()
			task2 = Task(content =  task2_content, done = False)
			task2.put()
			task3 = Task(content =  task3_content, done = False)
			task3.put()

			tasks.tasklist.append(task1)
			tasks.tasklist.append(task2)
			tasks.tasklist.append(task3)
			tasks.put()

			self.redirect('/')

class ToggleDone(webapp2.RequestHandler):
	def post(self):
		key = ndb.Key(self.request.get('id'))
		tasks = Task.query().fetch()
		for task in tasks:
			if task.key == key:
				task.done = not task.done
				task.put()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/process-tasks', ProcessTasks),
    ('/toggle-done', ToggleDone),
], debug=True)
