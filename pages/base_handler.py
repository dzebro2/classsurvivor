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
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")

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
                self.response.set_cookie(key='auth', value=sessionKey, httponly=True, max_age=86400, overwrite=True, secure=True) #remember to add secure=True when deploying
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
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")


        #myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
        #                       user="akkowal2_drew", passwd="cs411sp14")
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
                self.response.set_cookie(key='auth', value=sessionKey, httponly=True, max_age=86400, overwrite=True, secure=True) #remember to add secure=True when deploying
                cur.execute("""UPDATE User SET SessionKey=%s WHERE Email=%s""", (sessionKey, email))
                myDB.commit()
                self.redirect('/accountinfo/' + sessionKey + '/ /')
            else:
                logging.info('Incorrect Email/Password')
                self.render("home.html")

    def editPost(self, SK):
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
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
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
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
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
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
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
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

        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
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

    def createGroupPost(self):
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        classID = self.request.get('createGroup')
        sessionKey = self.request.cookies.get('auth')
        groupName = self.request.get('groupName')
        groupSize = self.request.get('groupSize')
        privacy = self.request.get('privacy')
        priv = 0
        if privacy == 'privacy':
            priv = 1
        else:
            priv = 0

        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)

        email = ''

        for row in cur.fetchall():
            email = row[0]




        try:
            cur.execute("INSERT INTO Groups (ClassID, LeaderEmail, Name, Size, MaxSize, privacy) VALUES "
                        "(%i, '%s', '%s', %i, %i, %i)" % (int(classID), email, groupName, 1, int(groupSize), priv))
            logging.info('i get here 1')
            cur.execute("SELECT LAST_INSERT_ID() FROM Groups")
            logging.info('i get here 2')
            idNum = ''
            for row in cur.fetchall():
                logging.info(row)
                logging.info('i get here 3')
                idNum = row[0]
            cur.execute("INSERT INTO UserGroupList VALUES ('%s', %i)" % (email, int(idNum)))
            logging.info('i get here 4')
            myDB.commit()
        except:
            logging.info('ooooooooops')
            myDB.rollback()

        self.redirect('/class/' + classID)

    def commentPostParent(self):
        logging.info('do i get hereeeeeeeee')
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        content = self.request.get('comment')
        sessionKey = self.request.cookies.get('auth')
        groupID = self.request.get('postCommentParent')
        parentID = 0
        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)

        email = ''

        for row in cur.fetchall():
            email = row[0]

        try:
            statement = "INSERT INTO Comments (GroupID, ParentID, Content, PosterEmail) VALUES (%i, %i, '%s', '%s')" % (int(groupID), int(parentID), content, email)
            logging.info(statement)
            cur.execute(statement)
            myDB.commit()
        except:
            myDB.rollback()

        self.redirect('/group/' + groupID)

    def commentPostReply(self):
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        content = self.request.get('comment')
        sessionKey = self.request.cookies.get('auth')
        parentID = self.request.get('postCommentReply')

        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)
        email = ''

        for row in cur.fetchall():
            email = row[0]

        cur.execute("SELECT GroupID FROM Comments WHERE CommentID=%i" % (int(parentID),))
        groupID = None
        for row in cur.fetchall():
            groupID = row[0]

        try:
            cur.execute("INSERT INTO Comments (GroupID, ParentID, Content, PosterEmail) VALUES (%i, %i, '%s', '%s')" % (int(groupID), int(parentID), content, email))
            myDB.commit()
        except:
            myDB.rollback()

        self.redirect('/group/' + str(groupID))


    def joinGroupPost(self):
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        sessionKey = self.request.cookies.get('auth')
        groupID = self.request.get('joinGroup')

        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)
        email = ''

        for row in cur.fetchall():
            email = row[0]

        cur.execute("SELECT privacy,Size,MaxSize FROM Groups WHERE IDNumber=%i" % (int(groupID),))
        joinable = False
        for row in cur.fetchall():
            if int(row[0]) == 0 and (row[1] < row[2] or row[2] == 0):
                joinable = True

        if joinable:
            try:
                cur.execute("INSERT INTO UserGroupList VALUES ('%s', %i)" % (email, int(groupID)))
                myDB.commit()
            except:
                myDB.rollback()

        self.redirect('/group/' + groupID)

    def deleteMemberPost(self):
        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        member = self.request.get('member')
        groupID = self.request.get('deleteMember')

        try:
            cur.execute("DELETE FROM UserGroupList WHERE Email='%s' AND GroupID=%i" % (member, int(groupID)))
            myDB.commit()
        except:
            myDB.rollback()


        self.redirect('/group/' + groupID)

    def courseSearchPagePost(self):
        deptCode = self.request.get('searchDeptCode')
        courseNum = self.request.get('searchCourseNumber')

        self.redirect('/classSearch/' + str(deptCode) + '_' + str(courseNum))

    def addTutorPost(self):
        logging.info("inaddtutorpost")
        availability = self.request.get('availability')
        price = self.request.get('tutorPrice')
        otherNotes = self.request.get('otherNotes')


        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        sessionKey = self.request.cookies.get('auth')
        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)
        email = ''

        for row in cur.fetchall():
            email = row[0]

        try:
            logging.info("in tutor insert")
            cur.execute("INSERT INTO Tutor VALUES ('%s', %f, 0.00, '%s', '%s')" % (email, float(price), str(availability), str(otherNotes)))
            myDB.commit()
        except:
            myDB.rollback()


        self.redirect('/profile/' + self.request.cookies.get('auth'))

    def addTutorToClassPost(self):
        classID = self.request.get('addTutorClass')

        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()

        sessionKey = self.request.cookies.get('auth')
        cur.execute("SELECT Email FROM User WHERE SessionKey='%s'" % sessionKey)
        email = ''

        for row in cur.fetchall():
            email = row[0]

        try:
            cur.execute("INSERT INTO TutorClassList VALUES ('%s', %i)" % (email, int(classID)))
            myDB.commit()
        except:
            myDB.rollback()

        self.redirect('/class/' + str(classID))



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
        elif self.request.get('createGroup'):
            self.createGroupPost()
        elif self.request.get('postCommentParent'):
            self.commentPostParent()
        elif self.request.get('postCommentReply'):
            self.commentPostReply()
        elif self.request.get('joinGroup'):
            self.joinGroupPost()
        elif self.request.get('deleteMember'):
            self.deleteMemberPost()
        elif self.request.get('courseSearchPage'):
            self.courseSearchPagePost()
        elif self.request.get('addTutor'):
            self.addTutorPost()
        elif self.request.get('addTutorClass'):
            self.addTutorToClassPost()


