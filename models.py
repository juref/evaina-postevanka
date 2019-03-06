from google.appengine.ext import ndb


class Equations(ndb.Model):
    mathUser = ndb.StringProperty()
    theEquation = ndb.StringProperty()
    equationCount = ndb.IntegerProperty(default=0)
    correctAnswer = ndb.IntegerProperty(default=1)
    wrongAnswer = ndb.IntegerProperty(default=1)

class MathUser(ndb.Model):
    mathUser = ndb.StringProperty()
    mathUserName = ndb.StringProperty()