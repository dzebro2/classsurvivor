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


class AccountInfo(base_handler.BaseHandler):
    def get(self, sessionkey, updated=None):
        #args = self.request.get('args')
        logging.info("I GET HERE!")
        logging.info("Session Key: " + sessionkey)

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

        #logging.info("User Information: " + str(userInfo))
        if not updated:
            update = False
        else:
            update = True

        info = [['Email', userInfo[0]], ['Name', userInfo[1]], ['Major', userInfo[3]], ['Class Status', userInfo[4]], ['Gender', userInfo[5]], ['Location', userInfo[6]]]
        context = {'updated': update, 'time': str(date.today()), 'accountInfo': '/accountinfo/' + sessionkey + '/', 'signout': '/signout/' + sessionkey, 'name': userInfo[1], 'infoList': info}
        self.render("AccountInfo.html", **context)
