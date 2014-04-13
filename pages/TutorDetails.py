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
import copy

from pages import base_handler


class TutorDetails(base_handler.BaseHandler):
    def get(self):
        #logging.info('courseInfo: ' + courseID)
        sessionkey = self.request.cookies.get('auth')

        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        cur.execute("SELECT * FROM User WHERE SessionKey=%s", (sessionkey,))
        userInfo = None
        for row in cur.fetchall():
            userInfo = row

        if userInfo is None or sessionkey == 'NULL':
            logging.info('i dungoofed')
            self.redirect('/home')
            return



        context = {'groupFinder': '/groupFinder/', 'classSearch': '/classSearch/', 'profile': '/profile/' + sessionkey, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'signout': '/signout/' + sessionkey, 'name': userInfo[2]}
        self.render("TutorDetails.html", **context)

