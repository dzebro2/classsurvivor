#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from webapp2 import *
import logging
import sys
import os
import re
import jinja2
import json

from pages import *


class MainHandler(RequestHandler):
    def get(self):
        auth_cookie = self.request.cookies.get('auth')
        if not auth_cookie:
            logging.info('No Previous Auth Cookie!')
            self.redirect('/home')
        else:
            logging.info('Auth Cookie: ' + str(auth_cookie))
            self.redirect('/accountinfo/' + str(auth_cookie) + '/ /')



app = WSGIApplication([
                                  (r'/', MainHandler),
                                  (r'/home', home.Home),
                                  (r'/register', signup.Sign),
                                  (r'/accountinfo/(.*)/(.*)/(.*)', AccountInfo.AccountInfo),
                                  (r'/profile/(.*)', Profile.Profile),
                                  (r'/signout/(.*)', signout.signout)
                              ], debug=True)
