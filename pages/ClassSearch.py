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


class ClassSearch(base_handler.BaseHandler):
    def get(self, searchRes=''):
        logging.info('searchRes: ' + searchRes)
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

        searchResults = []
        if searchRes != '':
            logging.info('FOUND ~ AT: ' + str(searchRes.find('~')))
            logging.info('FOUND = AT: ' + str(searchRes.find('=')))
            if searchRes.find('~') != -1:
                deptCode = searchRes[0:searchRes.find('~')]
                cur.execute("SELECT ClassDepartment,CourseNumber,ClassName,ProfessorName,ClassID FROM Class WHERE ClassDepartment='%s'" % (deptCode,))
                for row in cur.fetchall():
                    change = []
                    for item in row:
                        change.append(item)
                    change[3] = change[3].replace('&#039;', "'")
                    searchResults.append(change)
            elif searchRes.find('=') != -1:
                courseNum = searchRes[0:searchRes.find('=')]
                cur.execute("SELECT ClassDepartment,CourseNumber,ClassName,ProfessorName,ClassID FROM Class WHERE CourseNumber=%i" % (int(courseNum),))
                for row in cur.fetchall():
                    change = []
                    for item in row:
                        change.append(item)
                    change[3] = change[3].replace('&#039;', "'")
                    searchResults.append(change)
            else:
                deptCode = searchRes[0:searchRes.find('_')]
                courseNum = searchRes[searchRes.find('_')+1:searchRes.find('_')+4]
                cur.execute("SELECT ClassDepartment,CourseNumber,ClassName,ProfessorName,ClassID FROM Class WHERE ClassDepartment='%s' AND CourseNumber=%i" % (deptCode, int(courseNum)))
                for row in cur.fetchall():
                    change = []
                    for item in row:
                        change.append(item)
                    change[3] = change[3].replace('&#039;', "'")
                    searchResults.append(change)



        context = {'groupFinder': '/groupFinder/', 'searchResults': searchResults, 'classSearch': '/classSearch/', 'profile': '/profile/' + sessionkey, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'signout': '/signout/' + sessionkey, 'name': userInfo[2]}
        self.render("ClassSearch.html", **context)

