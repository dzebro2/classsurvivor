import logging
import webapp2
import sys
import os
import re
import jinja2

from pages import base_handler

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Home(base_handler.BaseHandler):
	def get(self):
		self.render("home.html")

	#def post(self):
	#does nothing right now