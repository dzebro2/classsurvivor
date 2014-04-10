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


class AccountInfo(base_handler.BaseHandler):
    def get(self, sessionkey, results=None, updated=None):
        #args = self.request.get('args')
        logging.info("I GET HERE!")
        logging.info("Session Key: " + sessionkey)
        logging.info('Updated: ' + str(updated))
        logging.info('results: ' + str(results))

        if (os.getenv('SERVER_SOFTWARE') and
                os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
        else:
            myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")

        #myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
        #                                 user="akkowal2_drew", passwd="cs411sp14")
        cur = myDB.cursor()
        cur.execute("SELECT * FROM User WHERE SessionKey=%s", (sessionkey,))
        userInfo = None
        for row in cur.fetchall():
            userInfo = row

        if userInfo is None or sessionkey == 'NULL':
            logging.info('i dungoofed')
            self.redirect('/home')
            return

        if not updated:
            update = False
        else:
            update = True

        classes = []
        departments = []

        if not results:
            results = []
        else:
            #myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor",
            #                       user="akkowal2_drew", passwd="cs411sp14")
            if (os.getenv('SERVER_SOFTWARE') and
                    os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
                myDB = MySQLdb.connect(unix_socket='/cloudsql/class--survivor:survivor', db='akkowal2_survivor', user='root')
            else:
                myDB = MySQLdb.connect(host="engr-cpanel-mysql.engr.illinois.edu", port=3306, db="akkowal2_survivor", user="akkowal2_drew", passwd="cs411sp14")
            cur = myDB.cursor()

            deptCode = results[0:results.find('&')]
            courseNum = results[results.find('&')+1:]
            logging.info('deptCode: ' + deptCode)
            logging.info('courseNum: ' + courseNum)

            try:
                Statement = ''
                if deptCode and courseNum:
                    statement = "SELECT ClassID, ClassDepartment, CourseNumber, ProfessorName FROM Class WHERE ClassDepartment='%s' AND CourseNumber=%s" % (deptCode, courseNum)
                elif deptCode and not courseNum:
                    statement = "SELECT ClassID, ClassDepartment, CourseNumber, ProfessorName FROM Class WHERE ClassDepartment='%s'" % (deptCode,)
                elif not deptCode and courseNum:
                    statement = "SELECT ClassID, ClassDepartment, CourseNumber, ProfessorName FROM Class WHERE CourseNumber=%s" % (courseNum,)

                cur.execute(statement)

                for row in cur:
                    classes.append(row)
                classes.sort()
            except:
                classes = []

        statement = "SELECT ClassDepartment FROM Class"
        cur.execute(statement)

        for row in cur.fetchall():
            if row[0] not in departments:
                departments.append(row[0])
        departments.sort()
        logging.info(departments)


        info = [['Email', userInfo[1]], ['Name', userInfo[2]], ['Major', userInfo[4]], ['Class Status', userInfo[5]], ['Gender', userInfo[6]], ['Location', userInfo[7]]]
        context = {'classSearch': '/classSearch/', 'departments': departments, 'profile': '/profile/' + sessionkey, 'searchResults': classes, 'updated': update, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'signout': '/signout/' + sessionkey, 'name': userInfo[2], 'infoList': info}
        self.render("AccountInfo.html", **context)

