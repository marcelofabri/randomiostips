from google.appengine.ext import db

class Tip(db.Model):
	content = db.StringProperty()
	tweeted = db.BooleanProperty()
	hash = db.StringProperty()