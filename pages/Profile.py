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

from pages import base_handler


class Profile(base_handler.BaseHandler):
    def get(self, sessionkey):
        #args = self.request.get('args')
        logging.info("I GET HERE!")
        logging.info("Session Key: " + sessionkey)

        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        
        sanity = "SELECT * FROM User WHERE SessionKey='%s'" % (sessionkey,)
        
        cur.execute(sanity)
        userInfo = None
        for row in cur.fetchall():
            userInfo = row
        
        if userInfo is None or sessionkey == 'NULL':
            self.redirect('/home')
            return
        
        statement = "SELECT ClassID FROM UserClassList WHERE email='%s'" % (userInfo[0],)
        cur.execute(statement)
        ids = []
        for row in cur.fetchall():
            ids.append(row)

        classes = []
        for idi in ids:
            cur.execute("SELECT ClassDepartment,CourseNumber,ClassName FROM Class WHERE ClassID=%i" % idi)
            for row in cur.fetchall():
                classes.append(row)
        
        info = [['Email', userInfo[0]], ['Name', userInfo[1]], ['Major', userInfo[3]], ['Class Status', userInfo[4]], ['Gender', userInfo[5]], ['Location', userInfo[6]]]
        context = {'classes': classes, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'profile': '/profile/' + sessionkey, 'signout': '/signout/' + sessionkey, 'name': userInfo[1], 'infoList': info}
        self.render("Profile.html", **context)
