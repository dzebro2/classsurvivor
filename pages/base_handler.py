import logging
import webapp2
import sys
import os
import re
import jinja2
import MySQLdb
import hashlib

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    loggedIn = None
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def getDigest(self, password):
        return hashlib.sha256(password).hexdigest()

    def isPassword(self, password, digest):
        return self.getDigest(password) == digest

    def registerPost(self):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="asdfasdasf")
        cur = myDB.cursor()
        cur.execute("SELECT Email FROM User WHERE Email='" + self.request.get('REmail') + "'")
        if not cur.fetchall():
            #CREATE ACCOUNT
            if self.valid_email(self.request.get('REmail')) and (
                    self.request.get('RPassword') == self.request.get('RConfirmPassword')):
                #passwords match and email is valid
                name = self.request.get('RName')
                email = self.request.get('REmail')
                hashedPass = self.getDigest(self.request.get('RPassword'))
                try:
                    cur.execute("""INSERT INTO User (Email, Name, HashedPassword) VALUES (%s, %s, %s)""",
                                (email, name, hashedPass))
                    myDB.commit()
                except:
                    myDB.rollback()

                #cur.query()
                #logging.info("Status: " + cur.statusmessage)
                self.redirect('/register')
            else:
                self.redirect('/home')
        else:
            self.redirect('/home')
            logging.info("LIST NOT EMPTY")

        cur.close()

    def loginPost(self):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="asdfasdafsd")
        cur = myDB.cursor()

        hash = self.getDigest(self.request.get('Lpassword'))
        email = self.request.get('Lemail')

        logging.info("email: " + email)
        logging.info("hash: " + hash)

        cur.execute("SELECT * FROM User WHERE Email='" + email + "' AND HashedPassword='" + hash + "'")

        if cur.fetchall():
            loggedIn = email
            logging.info(loggedIn + " is logged in!")
        else:
            logging.info('Incorrect Email/Password')

        self.render("home.html")

    def post(self):
        if self.request.get('register'):
            self.registerPost()
        elif self.request.get('login'):
            self.loginPost()
