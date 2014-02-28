import logging
import webapp2
import sys
import os
import re
import jinja2

import hashlib
import MySQLdb

from pages import base_handler


class Sign(base_handler.BaseHandler):
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

    def valid_email(self, email):
        return self.EMAIL_RE.match(email)

    def get(self):
        questions = ["Name", "Email", "Password", "ConfirmPassword"]
        context = {'qList': questions}
        self.render("register.html", **context)