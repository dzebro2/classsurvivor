__author__ = 'Drew'

import logging
import webapp2
import sys
import os
import re
import jinja2

import hashlib
import MySQLdb
import time
from datetime import date
import zlib
import base64

from pages import base_handler


class Profile(base_handler.BaseHandler):
    def get(self, sessionkey):
        #args = self.request.get('args')
        logging.info("I GET HERE!")
        logging.info("Session Key: " + sessionkey)

        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        
        sanity = "SELECT * FROM User WHERE SessionKey='%s'" % (sessionkey,)
        
        cur.execute(sanity)
        userInfo = None
        for row in cur.fetchall():
            userInfo = row
        
        if userInfo is None or sessionkey == 'NULL':
            self.redirect('/home')
            return
        
        statement = "SELECT ClassID FROM UserClassList WHERE email='%s'" % (userInfo[1],)
        cur.execute(statement)
        ids = []
        for row in cur.fetchall():
            ids.append(row)

        classes = []
        for idi in ids:
            cur.execute("SELECT ClassDepartment,CourseNumber,ClassName,ProfessorName,ClassID FROM Class WHERE ClassID=%i" % idi)
            for row in cur.fetchall():
                classes.append(row)
        statement = "SELECT ProfilePic FROM User WHERE email='%s'" % userInfo[1]
        logging.info(statement)
        cur.execute(statement)
        profilePic = 'default'
        for row in cur.fetchall():
            #logging.info(row)
            #logging.info(row[0])
            profilePic = row[0]
            try:
                test = len(profilePic)
                profilePic = base64.b64encode(profilePic)
            except:
                profilePic = 'default'

            logging.info(profilePic)



        if not profilePic:
            #profilePic = '../../static/images/default_profile_pic.jpg'
            pass
        else:
            fileName = 'user.jpg'
            #profilePic = zlib.decompress(profilePic)
            #open(fileName, 'wb').write(profilePic)
            #profilePic = fileName

        groups = []
        cur.execute(
                    "SELECT first.Name,Class.ClassName,first.IDNumber" +
                    " FROM ((SELECT * FROM Groups INNER JOIN UserGroupList ON Groups.IDNumber=UserGroupList.GroupID) AS first)" +
                    " INNER JOIN Class ON first.ClassID=Class.ClassID" +
                    " WHERE first.Email='%s'" % (userInfo[1],)
        )

        for row in cur.fetchall():
            groups.append(row)

        cur.execute("SELECT Email FROM Tutor WHERE Email=%s", (userInfo[1],))

        tutor = False
        for row in cur.fetchall():
            logging.info('Tutor Row: ' + str(row))
            if row:
                tutor = True

        tutorInfo = []
        cur.execute(
            "SELECT Price,Rating,Availability,OtherNotes " +
            "FROM Tutor " +
            "WHERE Email='%s'" % userInfo[1]
        )

        for row in cur.fetchall():
            tutorInfo.append(row)

        cur.execute("SELECT ClassName,ClassID FROM Class NATURAL JOIN TutorClassList WHERE Email='%s'" % userInfo[1])

        tutorClasses = []
        for row in cur.fetchall():
            tutorClasses.append(row)

        logging.info('Tutor Info: ' + str(tutorInfo))
        logging.info('Tutor Classes: ' + str(tutorClasses))

         
        
        info = [['Email', userInfo[1]], ['Name', userInfo[2]], ['Major', userInfo[4]], ['Class Status', userInfo[5]], ['Gender', userInfo[6]], ['Location', userInfo[7]]]
        context = {'tutorClasses': tutorClasses, 'tutorInfo': tutorInfo, 'groupFinder': '/groupFinder/', 'tutor': tutor, 'classSearch': '/classSearch/', 'groups': groups, 'profilePic': profilePic, 'classes': classes, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'profile': '/profile/' + sessionkey, 'signout': '/signout/' + sessionkey, 'name': userInfo[2], 'infoList': info}
        self.render("Profile.html", **context)
