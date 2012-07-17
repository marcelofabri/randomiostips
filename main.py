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
import webapp2
from google.appengine.ext import db
import uuid
import os
from google.appengine.ext.webapp import template
from django.template import defaultfilters 
import random
import tweepy
from google.appengine.api import memcache



class Tip(db.Model):
	content = db.StringProperty()
	tweeted = db.BooleanProperty()
	hash = db.StringProperty()

class MainHandler(webapp2.RequestHandler):
	def get(self, hash = None):
		if hash is None:
			item_keys = memcache.get('keys')
			if item_keys is None:
				item_keys = Tip.all(keys_only=True).fetch(2000)
				memcache.add('keys', item_keys, 3600)
				
			random_key = random.choice(item_keys)
			item = db.get(random_key)
		else:
			item = memcache.get(hash)
			if item is None:
				item = Tip.all().filter("hash =", hash).get()
				if item is None:
					item = Tip()
					item.content = "Don't try to be smart and change the tip parameter!"
					item.hash = hash
				else:
					memcache.add(hash, item, 3600)
					
		template_values = { 'tip': item, 'url': 'http://www.randomiostips.com/%s' % item.hash, 'random': hash is None}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
		
class PostHandler(webapp2.RequestHandler):
	def get(self):
		tip_content = self.request.get("tip")
		if tip_content is None:
			return;
		
		tip = Tip()
		tip.content = tip_content
		tip.tweeted = False
		tip.hash = str(uuid.uuid4()).replace('-', '')
				        
		tip.put()	
		
class TweetHandler(webapp2.RequestHandler):
	def get(self):
		
		consumer_key="Insert consumer key here"
		consumer_secret="Insert consumer secret here"
		access_token="Insert access token here"
		access_token_secret="Insert access token secret here"

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)

		api = tweepy.API(auth)

		item_keys = Tip.all(keys_only=True).filter('tweeted =', False).fetch(2000)
		if len(item_keys) > 0:
			random_key = random.choice(item_keys)
			item = db.get(random_key)

			content = defaultfilters.removetags(item.content,"a code")
			api.update_status(content)
			item.tweeted = True
			item.put()
		
app = webapp2.WSGIApplication([ ('/', MainHandler), ('/tweet', TweetHandler),  ('/post', PostHandler), ('/(.*)', MainHandler)],
                              debug=False)
