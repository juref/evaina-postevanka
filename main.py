#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import jinja2
import webapp2
import random
import logging
from models import Equations
from HTMLParser import HTMLParser
from google.appengine.api import users

reload(sys)
sys.setdefaultencoding('utf8')


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            equation = str(x) + " x " + str(y)
            quotient = x * y
            params = {"user": user, "quotient": quotient, "equation": equation}
        else:
            login_url = users.create_login_url('/')
            params = {"login_url": login_url}

        self.html = "index.html"
        return self.render_template("%s" % self.html, params=params)

    def post(self):
        user = users.get_current_user()
        math_user = user.email()
        equation = self.request.get("equation")
        answer = self.request.get("answer")
        quotient = self.request.get("quotient")
        correct = 0
        wrong = 0

        if str(answer) == str(quotient):
            correct = 1
            note = "Bravo! <br/>" + quotient + " je pravilen odgovor!"
            style = "correct"
        else:
            wrong = 1
            note = "Ojoj... tole pa ni pravilno! <br/>Pravilen odgovor je " + quotient
            style = "wrong"

        try:
            equation_id = (Equations.query(Equations.theEquation == equation, Equations.mathUser == str(user.email())).get()).key.id()
            equation_data = Equations.get_by_id(int(equation_id))
            equation_data.equationCount = equation_data.equationCount + 1
            equation_data.correctAnswer = equation_data.correctAnswer + int(correct)
            equation_data.wrongAnswer = equation_data.wrongAnswer + int(wrong)
            equation_data.put()

            logging.info(correct)
            logging.info(wrong)
        except:
            equation_count = 1
            correctAnswer = int(correct)
            wrongAnswer = int(wrong)
            equation_data = Equations(mathUser=math_user, theEquation=equation, equationCount=equation_count,
                                      correctAnswer=correctAnswer, wrongAnswer=wrongAnswer)
            equation_data.put()

        if user:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            equation = str(x) + " x " + str(y)
            quotient = x * y

            params = {"user": user, "equation": equation, "quotient" :quotient, "note": note, "style": style}

        else:
            login_url = users.create_login_url('/')
            params = {"login_url": login_url}

        self.html = "index.html"
        return self.render_template("%s" % self.html, params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
], debug=True)