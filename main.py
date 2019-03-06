#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import jinja2
import webapp2
import random
import logging
from models import Equations, MathUser
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
            try:
                name = ((MathUser.query(MathUser.mathUser == str(user.email())).get()).mathUserName).capitalize()
                params = {
                    "user": user,
                    "name": name
                }
            except:
                return self.redirect("new_user")

        else:
            login_url = users.create_login_url('/')
            params = {"login_url": login_url}

        self.html = "index.html"
        return self.render_template("%s" % self.html, params=params)

    def post(self):
        user = users.get_current_user()
        multiplying = self.request.get("multiplying")
        dividing = self.request.get("dividing")
        number = self.request.get("number")

        logging.info(multiplying)
        logging.info(dividing)
        logging.info(number)

        params = {
            "user": user,
            "multiplying": multiplying,
            "dividing": dividing,
            "number": number
        }

        self.html = "calculation.html"
        return self.render_template("%s" % self.html, params=params)


class CalculationHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        multiplying = self.request.get("multiplying")
        dividing = self.request.get("dividing")
        number = self.request.get("number")
        today = 0
        step = 100 / int(number)
        counter = 1
        logging.info(step)

        if user:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            equation = str(x) + " x " + str(y)
            quotient = x * y
            todayCorrect = 0
            todayWrong = 0
            params = {
                "user": user,
                "quotient": quotient,
                "equation": equation,
                "today": today,
                "todayCorrect": todayCorrect,
                "todayWrong": todayWrong,
                "step": step,
                "multiplying": multiplying,
                "dividing": dividing,
                "counter": counter,
                "number": number,
            }
        else:
            login_url = users.create_login_url('/')
            params = {"login_url": login_url}

        self.html = "calculation.html"
        return self.render_template("%s" % self.html, params=params)

    def post(self):
        user = users.get_current_user()
        math_user = user.email()
        name = name = (MathUser.query(MathUser.mathUser == str(user.email())).get()).mathUserName
        multiplying = self.request.get("multiplying")
        dividing = self.request.get("dividing")
        equation = self.request.get("equation")
        answer = self.request.get("answer")
        quotient = self.request.get("quotient")
        todayCorrect = self.request.get("todayCorrect")
        todayWrong = self.request.get("todayWrong")
        today = self.request.get("today")
        number = self.request.get("number")
        step = self.request.get("step")
        correct = 0
        wrong = 0
        today = int(today) + int(step)
        counter = int(today) / int(step) + 1


        if today < 50:
            progressColour = "red"
        elif today < 80:
            progressColour = "orange"
        elif today < 95:
            progressColour = "yellow"
        else:
            progressColour = "green"


        if str(answer) == str(quotient):
            correct = 1
            note = "Bravo! pravilen odgovor!"
            style = "correct"
        else:
            wrong = 1
            note = "Napačno! Pravilen odgovor je " + quotient
            style = "wrong"

        todayCorrect = int(todayCorrect) + correct
        todayWrong = int(todayWrong) + wrong

        try:
            equation_id = (Equations.query(Equations.theEquation == equation, Equations.mathUser == str(user.email())).get()).key.id()
            equation_data = Equations.get_by_id(int(equation_id))
            equation_data.equationCount = equation_data.equationCount + 1
            equation_data.correctAnswer = equation_data.correctAnswer + int(correct)
            equation_data.wrongAnswer = equation_data.wrongAnswer + int(wrong)
            equation_data.put()

        except:
            equation_count = 1
            correctAnswer = int(correct)
            wrongAnswer = int(wrong)
            equation_data = Equations(mathUser=math_user, theEquation=equation, equationCount=equation_count,
                                      correctAnswer=correctAnswer, wrongAnswer=wrongAnswer)
            equation_data.put()

        if today >= 100:
            params = {
                "user": user,
                "name": name,
                "equation": equation,
                "quotient": quotient,
                "note": note,
                "style": style,
                "todayCorrect": todayCorrect,
                "todayWrong": todayWrong,
                "step": step,
                "counter": counter,
                "number": number,
            }
            self.html = "statistics.html"
            return self.render_template("%s" % self.html, params=params)

        else:
            if user:
                x = random.randint(1, 10)
                y = random.randint(1, 10)
                equation = str(x) + " x " + str(y)
                quotient = x * y

                params = {
                    "user": user,
                    "equation": equation,
                    "quotient" :quotient,
                    "note": note,
                    "style": style,
                    "today": today,
                    "progressColour": progressColour,
                    "todayCorrect": todayCorrect,
                    "todayWrong": todayWrong,
                    "step": step,
                    "counter": counter,
                    "number": number,
                }

            else:
                login_url = users.create_login_url('/')
                params = {"login_url": login_url}

        self.html = "calculation.html"
        return self.render_template("%s" % self.html, params=params)


class NewUserHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            params = {"user":user}
            self.html = "new_user.html"
            return self.render_template("%s" % self.html, params=params)
        else:
            login_url = users.create_login_url('/')
            params = {"login_url": login_url}

            self.html = "index.html"
            return self.render_template("%s" % self.html, params=params)

    def post(self):
        user = users.get_current_user()
        name = self.request.get("name")

        newUser = MathUser(mathUser=user.email(), mathUserName=name)
        newUser.put()

        params = {"user": user, "name": name}

        return self.render_template("index.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/calculation', CalculationHandler),
    webapp2.Route('/new_user', NewUserHandler, name="new_user"),
], debug=True)