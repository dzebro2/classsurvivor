import logging
import webapp2
import sys
import os
import re
import jinja2
import MySQLdb
import hashlib
import uuid
import time
import datetime
from webapp2_extras import sessions

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
                               user="akkowal2_drew", passwd="cs411sp14")
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

                self.redirect('/register')
            else:
                self.redirect('/home')
        else:
            self.redirect('/home')
            logging.info("LIST NOT EMPTY")

        cur.close()

    def loginPost(self):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        email = self.request.get('Lemail')

        logging.info("email: " + email)

        cur.execute("SELECT Password FROM User WHERE Email=%s", email)
        if not cur.fetchall():
            logging.info('Incorrect Email/Password')
            self.render("home.html")
        else:
            digest = None
            for row in cur:
                digest = row[0]
            passW = self.request.get('Lpassword')
            correctPass = self.isPassword(passW, digest)
            if correctPass:
                loggedIn = email
                logging.info(loggedIn + " is logged in!")
                sessionKey = hashlib.sha256(str(email)+str(self.request.remote_addr)+str(passW)+str(time.time())).hexdigest()
                self.response.set_cookie(key='auth', value=sessionKey, httponly=True, max_age=60, overwrite=True) #remember to add secure=True when deploying
                cur.execute("""UPDATE User SET SessionKey=%s WHERE Email=%s""", (sessionKey, email))
                myDB.commit()
                self.redirect('/accountinfo/' + sessionKey + '/')
            else:
                logging.info('Incorrect Email/Password')
                self.render("home.html")

    def editPost(self, SK):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        name = self.request.get('Name')
        classStatus = self.request.get('Class Status')
        gender = self.request.get('Gender')
        location = self.request.get('Location')

        if name == "":
            name = None
        if classStatus == "":
            classStatus = None
        if gender == "":
            gender = None
        if location == "":
            location = None

        cur.execute("UPDATE User SET Name=%s, ClassStatus=%s, Gender=%s, Location=%s WHERE SessionKey=%s", (name, classStatus, gender, location, SK))
        myDB.commit()
        self.redirect('/accountinfo/' + SK + '/4bvgh')

    def post(self, SK=None, update=None):
        if self.request.get('register'):
            self.registerPost()
        elif self.request.get('login'):
            self.loginPost()
        elif self.request.get('editInfo'):
            self.editPost(SK)
