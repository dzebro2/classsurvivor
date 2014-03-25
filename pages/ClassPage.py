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


class ClassPage(base_handler.BaseHandler):
    def get(self, courseID):
        logging.info('courseInfo: ' + courseID)
        sessionkey = self.request.cookies.get('auth')

        myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
                               user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        cur.execute("SELECT * FROM User WHERE SessionKey=%s", (sessionkey,))
        userInfo = None
        for row in cur.fetchall():
            userInfo = row

        if userInfo is None or sessionkey == 'NULL':
            logging.info('i dungoofed')
            self.redirect('/home')
            return

        cur.execute("SELECT ClassName,ProfessorName FROM Class WHERE ClassID=%i" % (int(courseID)))
        className = ''
        professorName = ''
        for row in cur.fetchall():
            className = row[0]
            professorName = row[1]

        context = {'ClassID': str(courseID), 'professorName': professorName, 'className': className, 'profile': '/profile/' + sessionkey, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'signout': '/signout/' + sessionkey, 'name': userInfo[2]}
        self.render("Class.html", **context)

