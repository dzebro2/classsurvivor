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
import zlib
#from google.appengine.api import rdbms

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

                sessionKey = hashlib.sha256(str(email)+str(self.request.remote_addr)+str(self.request.get('RPassword'))+str(time.time())).hexdigest()
                self.response.set_cookie(key='auth', value=sessionKey, httponly=True, max_age=86400, overwrite=True) #remember to add secure=True when deploying
                cur.execute("""UPDATE User SET SessionKey=%s WHERE Email=%s""", (sessionKey, email))
                myDB.commit()
                self.redirect('/accountinfo/' + sessionKey + '/ /')
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
        statement = "SELECT Password FROM User WHERE Email='%s'" % (email,)
        logging.info(statement)
        cur.execute(statement)
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
                self.response.set_cookie(key='auth', value=sessionKey, httponly=True, max_age=86400, overwrite=True) #remember to add secure=True when deploying
                cur.execute("""UPDATE User SET SessionKey=%s WHERE Email=%s""", (sessionKey, email))
                myDB.commit()
                self.redirect('/accountinfo/' + sessionKey + '/ /')
            else:
                logging.info('Incorrect Email/Password')
                self.render("home.html")

    def editPost(self, SK):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        name = self.request.get('Name')
        major = self.request.get('Major')
        classStatus = self.request.get('Class Status')
        gender = self.request.get('Gender')
        location = self.request.get('Location')

        if name == "":
            name = None
        if classStatus == "":
            classStatus = None
        if major == "":
            major = None
        if gender == "":
            gender = None
        if location == "":
            location = None

        cur.execute("UPDATE User SET Name=%s, Major=%s, ClassStatus=%s, Gender=%s, Location=%s WHERE SessionKey=%s", (name, major, classStatus, gender, location, SK))
        myDB.commit()
        self.redirect('/accountinfo/' + SK + '/ /a')

    def deleteAccountPost(self):
        logging.info('account agreed to deletion')
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        cookie = self.request.cookies.get('auth')

        try:
            cur.execute("DELETE FROM User WHERE SessionKey='%s'" % (cookie,))
            myDB.commit()
            self.response.delete_cookie('auth')
            self.redirect('/home')
        except:
            myDB.rollback()
            self.redirect('/accountinfo/' + cookie + '/')

    def courseSearchPost(self):
        logging.info('I get here')
        deptCode = self.request.get('departmentCode')
        courseNum = self.request.get('courseNumber')
        logging.info(deptCode)
        logging.info(courseNum)
        cookie = self.request.cookies.get('auth')
        self.redirect('/accountinfo/' + cookie + '/' + deptCode + '&' + courseNum + '/')

    def addClassPost(self):
        logging.info('hereasdfasd')
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        classID = self.request.get('classID')
        cookie = self.request.cookies.get('auth')
        try:
            cur.execute("SELECT Email FROM User WHERE SessionKey=%s", (cookie,))
        except:
            logging.info('ruh roh')
        email = None
        for row in cur:
            email = row[0]

        logging.info('email' + email)

        try:
            statement = "INSERT INTO UserClassList VALUES ('%s', %s)" % (email, classID)
            logging.info(statement)
            cur.execute(statement)
            myDB.commit()
            logging.info('here????')
            self.redirect('/accountinfo/' + cookie + '/ /a')
        except:
            myDB.rollback()
            self.redirect('/accountinfo/' + cookie + '/ /')

    def uploadPicPost(self):
        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        picture = self.request.get('uploadButton')


        cookie = self.request.cookies.get('auth')
        try:
            cur.execute("UPDATE User SET ProfilePic=%s WHERE SessionKey=%s", (picture, cookie))
            myDB.commit()
        except:
            logging.info('uploading picture problem!')
            myDB.rollback()

        self.redirect('/profile/' + cookie)

    def deleteClassPost(self):
        logging.info('delete class: ' + self.request.get('delete'))
        delClass = self.request.get('delete')

        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        firstSpace = delClass.find(' ')
        secondSpace = delClass.find(' ', firstSpace+1)
        logging.info('firstSpace: ' + str(firstSpace))
        logging.info('secondSpace: ' + str(secondSpace))
        deptName = delClass[0:firstSpace]
        logging.info('deptName: ' + deptName)

        courseNum = delClass[firstSpace+1:secondSpace]
        logging.info('courseNum: ' + str(courseNum))

        profName = delClass[secondSpace+1:]
        logging.info('professorName: ' + profName)
        sessionKey = self.request.cookies.get('auth')

        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)

        email = ''

        for row in cur.fetchall():
            email = row[0]

        logging.info('got email: ' + email)

        cur.execute("SELECT ClassID FROM Class WHERE ClassDepartment='%s' AND CourseNumber=%i AND ProfessorName='%s'" % (deptName, int(courseNum), profName))

        courseID = -1
        for row in cur.fetchall():
            courseID = int(row[0])

        logging.info('got course id: ' + str(courseID))
        statement = "DELETE FROM UserClassList WHERE Email='%s' AND ClassID=%i" % (email, courseID)
        logging.info(statement)
        try:
            cur.execute(statement)
            myDB.commit()
        except:
            logging.info('could not delete class')
            myDB.rollback()

        self.redirect('/profile/' + sessionKey)

    def post(self, SK=None, results=None, update=None):
        if self.request.get('register'):
            self.registerPost()
        elif self.request.get('login'):
            self.loginPost()
        elif self.request.get('editInfo'):
            self.editPost(SK)
        elif self.request.get('deleteAccount'):
            self.deleteAccountPost()
        elif self.request.get('courseSearch'):
            self.courseSearchPost()
        elif self.request.get('addClass'):
            logging.info('please get here')
            self.addClassPost()
        elif self.request.get('picUpload'):
            self.uploadPicPost()
        elif self.request.get('deleteClass'):
            self.deleteClassPost()


