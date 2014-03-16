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

        #cur.execute("SELECT * FROM User")
        #logging.info("User Information: " + str(userInfo))
        
        info = [['Email', userInfo[0]], ['Name', userInfo[1]], ['Class Status', userInfo[3]], ['Gender', userInfo[4]], ['Location', userInfo[5]]]
        context = {'time': str(date.today()), 'accountInfo': '/accountInfo/' + sessionkey + '/','profile': '/profile/' + sessionkey, 'signout': '/signout/' + sessionkey, 'name': userInfo[1], 'infoList': info}
        self.render("Profile.html", **context)
