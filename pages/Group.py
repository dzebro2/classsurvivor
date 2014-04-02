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


class Group(base_handler.BaseHandler):
    def get(self, groupID):
        logging.info('courseInfo: ' + groupID)
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

        cur.execute("SELECT ClassID,Name FROM Groups WHERE IDNumber=%i" % (int(groupID),))
        courseID = None
        groupName = ''
        for row in cur.fetchall():
            courseID = row[0]
            groupName = row[1]

        cur.execute("SELECT ClassName,ProfessorName FROM Class WHERE ClassID=%i" % (int(courseID)))
        className = ''
        professorName = ''
        for row in cur.fetchall():
            className = row[0]
            professorName = row[1]

        cur.execute("SELECT Name,Size,privacy,IDNumber FROM Groups WHERE ClassID=%i" % (int(courseID),))
        groups = []
        for row in cur.fetchall():
            if row[2] == 0:
                groups.append(row)

        comments = []

        cur.execute("SELECT Name,Content,CommentID FROM (User INNER JOIN Comments ON User.Email=Comments.PosterEmail) WHERE ParentID=0 AND GroupID=%i" % (int(groupID),))

        for row in cur.fetchall():
            comments.append(row)
        statement = "SELECT ParentID,Name,Content FROM (User INNER JOIN Comments ON User.Email=Comments.PosterEmail) WHERE GroupID=%i" % (int(groupID),)
        logging.info(statement)
        cur.execute(statement)

        replys = []

        for row in cur.fetchall():
            replys.append(row)

        context = {'replyComments': replys, 'comments': comments, 'groupID': groupID, 'groupName': groupName, 'groups': groups, 'ClassID': str(courseID), 'professorName': professorName, 'className': className, 'profile': '/profile/' + sessionkey, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'signout': '/signout/' + sessionkey, 'name': userInfo[2]}
        self.render("Group.html", **context)

