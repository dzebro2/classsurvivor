import logging
import webapp2
import sys
import os
import re
import jinja2

from pages import base_handler

class Home(base_handler.BaseHandler):
	def get(self):
		self.render("home.html")

	#def post(self):
	#does nothing right now
	#would look like self.render("home.html", stuff we want to put on the page)