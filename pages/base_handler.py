import logging
import webapp2
import sys
import os
import re
import jinja2
import MySQLdb
import hashlib
import uuid

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
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    def isPassword(self, password, digest):
        passwrd, salt = digest.split(':')
        return passwrd == hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    def registerPost(self):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="8558438")
        cur = myDB.cursor()
        email = self.request.get('REmail')
        cur.execute("SELECT Email FROM User WHERE Email=%s", (email,))
        if not cur.fetchall():
            #CREATE ACCOUNT
            if self.valid_email(email) and (
                    self.request.get('RPassword') == self.request.get('RConfirmPassword')):
                #passwords match and email is valid
                name = self.request.get('RName')
                email = self.request.get('REmail')
                hashedPass = self.getDigest(self.request.get('RPassword'))
                try:
                    cur.execute("""INSERT INTO User (Email, Name, Password) VALUES (%s, %s, %s)""",
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
                               user="akkowal2_drew", passwd="4564845348")
        cur = myDB.cursor()
        email = self.request.get('Lemail')

        logging.info("email: " + email)

        cur.execute("SELECT Password FROM User WHERE Email=%s", email)
        if not cur.fetchall():
            logging.info('Incorrect Email/Password')
        else:
            digest = None
            for row in cur:
                digest = row[0]
            correctPass = self.isPassword(self.request.get('Lpassword'), digest)
            if correctPass:
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
