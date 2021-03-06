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

        cur.execute("SELECT LeaderEmail FROM Groups WHERE IDNumber=%i" % (int(groupID,)))
        leaderEmail = None
        for row in cur.fetchall():
            leaderEmail = row[0]

        isLeader = False
        if userInfo[1] == leaderEmail:
            isLeader = True

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

        members = []
        cur.execute("SELECT Name,Email FROM UserGroupList NATURAL JOIN User WHERE GroupID=%i" % (int(groupID),))
        inGroup = False
        for row in cur.fetchall():
            if row[1] == userInfo[1]:
                inGroup = True
                members = [row] + members
            else:
                members.append(row)

        description=""
        cur.execute("SELECT Description FROM Groups WHERE IDNumber=%i" % (int(groupID),))
        for row in cur.fetchall():
            description = row

        polls = []

        cur.execute("SELECT PollID,Name,Question FROM Polls JOIN User ON PosterEmail=Email WHERE GroupID=%i" % (int(groupID),))
        for row in cur.fetchall():
            initList = []
            initList.append(row[0])
            initList.append(row[1])
            initList.append(row[2])
            polls.append(copy.deepcopy(initList))

        for poll in polls:
            pollID = int(poll[0])
            cur.execute("SELECT Choice, ChoiceID FROM PollChoices WHERE PollChoices.PollID=%i ORDER BY ChoiceID" % (pollID,))
            choiceList = []
            choiceIDList = []
            votesList = []
            for row in cur.fetchall():
                choiceList.append(row[0])
                choiceIDList.append(row[1])
                #votesList.append(row[1])

            for choiceID in choiceIDList:
                cur.execute("SELECT COUNT(DISTINCT Email) FROM PollVotes WHERE ChoiceID=%i" % int(choiceID))
                for row in cur.fetchall():
                    votesList.append(int(row[0]))

            poll.append(copy.deepcopy(choiceList))
            poll.append(copy.deepcopy(votesList))
            poll.append(copy.deepcopy(choiceIDList))

        polls = polls[::-1]
        logging.info(str(polls))







        context = {'polls': polls, 'description': description, 'groupFinder': '/groupFinder/', 'classSearch': '/classSearch/', 'leader': isLeader, 'inGroup': inGroup, 'members': members, 'replyComments': replys, 'comments': comments, 'groupID': groupID, 'groupName': groupName, 'groups': groups, 'ClassID': str(courseID), 'professorName': professorName, 'className': className, 'profile': '/profile/' + sessionkey, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/ /', 'signout': '/signout/' + sessionkey, 'name': userInfo[2]}
        self.render("Group.html", **context)

