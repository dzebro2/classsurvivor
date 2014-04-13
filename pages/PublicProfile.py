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


class PublicProfile(base_handler.BaseHandler):
    def get(self, email):
        #args = self.request.get('args')
        logging.info("I GET HERE!")
        logging.info('loading page for: ' + email)
        #logging.info("Session Key: " + sessionkey)
        sessionkey = self.request.cookies.get('auth')
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

        cur.execute("SELECT * FROM User WHERE email='%s'" % (email,))

        profileUser = None
        for row in cur.fetchall():
            profileUser = row

        if userInfo is None or sessionkey == 'NULL':
            self.redirect('/home')
            return

        statement = "SELECT ClassID FROM UserClassList WHERE email='%s'" % (email,)
        cur.execute(statement)
        ids = []
        for row in cur.fetchall():
            ids.append(row)

        classes = []
        for idi in ids:
            cur.execute("SELECT ClassDepartment,CourseNumber,ClassName,ProfessorName,ClassID FROM Class WHERE ClassID=%i" % idi)
            for row in cur.fetchall():
                classes.append(row)
        statement = "SELECT ProfilePic FROM User WHERE email='%s'" % email
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
            " WHERE first.Email='%s'" % (email,)
        )

        for row in cur.fetchall():
            groups.append(row)
        tutorInfo = []
        cur.execute(
            "SELECT ClassName,Price,Rating,Availability,OtherNotes " +
            "FROM Class NATURAL JOIN TutorClassList NATURAL JOIN Tutor " +
            "WHERE Email='%s'" % email
        )

        for row in cur.fetchall():
            tutorInfo.append(row)


        info = [['Email', userInfo[1]], ['Name', userInfo[2]], ['Major', userInfo[4]], ['Class Status', userInfo[5]], ['Gender', userInfo[6]], ['Location', userInfo[7]]]
        info2 = [['Email', profileUser[1]], ['Name', profileUser[2]], ['Major', profileUser[4]], ['Class Status', profileUser[5]], ['Gender', profileUser[6]], ['Location', profileUser[7]]]
        context = {'groupFinder': '/groupFinder/', 'tutorInfo': tutorInfo, 'publicProfile': info2, 'classSearch': '/classSearch/', 'groups': groups, 'profilePic': profilePic, 'classes': classes, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'profile': '/profile/' + sessionkey, 'signout': '/signout/' + sessionkey, 'name': userInfo[2], 'infoList': info}
        self.render("PublicProfile.html", **context)
