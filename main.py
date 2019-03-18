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

### račun ###
def newEquation(addition,difference,multiplying,dividing):
    x = random.randint(1, 10)
    y = random.randint(1, 10)
    result = x * y
    options = []

    if addition:
        options.append("+")
    if difference:
        options.append("-")
    if multiplying:
        options.append("x")
    if dividing:
        options.append(":")

    operator = random.choice(options)

    if operator == "+":
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        result = x + y
        while x + y >= 100:
            x = random.randint(1, 100)
            y = random.randint(1, 100)
            result = x + y

    if operator == "-":
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        result = x - y
        while x <= y:
            x = random.randint(1, 100)
            y = random.randint(1, 100)
            result = x - y

    if operator == ":":
        x = x * y
        result = x / y

    params = {"x": x, "y": y, "operator": operator, "result": result}
    return params


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
        addition = self.request.get("addition")
        difference = self.request.get("difference")
        multiplying = self.request.get("multiplying")
        dividing = self.request.get("dividing")
        number = self.request.get("number")
        missing_number = self.request.get("missing_number")
        logging.info(missing_number)

        params = {
            "user": user,
            "addition": addition,
            "difference": difference,
            "multiplying": multiplying,
            "dividing": dividing,
            "number": number,
            "missing-number": missing_number
        }

        self.html = "calculation.html"
        return self.render_template("%s" % self.html, params=params)


class CalculationHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        addition = self.request.get("addition")
        difference = self.request.get("difference")
        multiplying = self.request.get("multiplying")
        dividing = self.request.get("dividing")
        number = self.request.get("number")
        missing_number = self.request.get("missing_number")
        logging.info(missing_number)
        today = 0
        step = 100 / int(number)
        counter = 1
        todayCorrect = 0
        todayWrong = 0

        options = []

        if addition:
            options.append("+")
        if difference:
            options.append("-")
        if multiplying:
            options.append("x")
        if dividing:
            options.append(":")

        if user:
            params = {
                "user": user,
                "today": today,
                "todayCorrect": todayCorrect,
                "todayWrong": todayWrong,
                "step": step,
                "addition": addition,
                "difference": difference,
                "multiplying": multiplying,
                "dividing": dividing,
                "counter": counter,
                "number": number,
                "missing_number": missing_number
            }
            params.update(newEquation(addition,difference,multiplying,dividing))

        else:
            login_url = users.create_login_url('/')
            params = {"login_url": login_url}

        self.html = "calculation.html"
        return self.render_template("%s" % self.html, params=params)

    def post(self):
        user = users.get_current_user()
        math_user = user.email()
        name = (MathUser.query(MathUser.mathUser == str(user.email())).get()).mathUserName

        addition = self.request.get("addition")
        difference = self.request.get("difference")
        multiplying = self.request.get("multiplying")
        dividing = self.request.get("dividing")

        x = self.request.get("x")
        y = self.request.get("y")
        resault = self.request.get("resault")
        correct_answer = self.request.get("correct_answer")
        operator = self.request.get("operator")

        answer = self.request.get("answer")

        todayCorrect = self.request.get("todayCorrect")
        todayWrong = self.request.get("todayWrong")
        today = self.request.get("today")
        number = self.request.get("number")
        missing_number = self.request.get("missing_number")
        step = self.request.get("step")

        equation = str(x) + " " + operator + " " + str(y)
        correct = 0
        wrong = 0
        today = int(today) + int(step)
        counter = int(today) / int(step) + 1

        ### Barva progress bara ###
        if today < 50:
            progressColour = "red"
        elif today < 75:
            progressColour = "orange"
        elif today < 89:
            progressColour = "yellow"
        else:
            progressColour = "green"

        ### Preverjanje rezultata ###
        if answer == correct_answer:
            correct = 1
            note = "Bravo! pravilen odgovor!"
            style = "correct"
        else:
            wrong = 1
            note = "Napačno! Pravilen odgovor je " + correct_answer
            style = "wrong"

        todayCorrect = int(todayCorrect) + correct
        todayWrong = int(todayWrong) + wrong

        ### preverjanje ali je račun že vpisani in vpis ali je bil rešen pravilno ###
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

        ### zaključek računanja ko je progress 100% ###
        if today >= 100:
            logout_url = users.create_logout_url('/')
            params = {
                "user": user,
                "name": name,
                "note": note,
                "style": style,
                "todayCorrect": todayCorrect,
                "todayWrong": todayWrong,
                "step": step,
                "counter": counter,
                "number": number,
                "logout_url": logout_url,
                "progressColour": progressColour,
            }
            self.html = "statistics.html"
            return self.render_template("%s" % self.html, params=params)

        ### kreiranje novega računa in passanje v hrml ###

        else:
            if user:
               params = {
                    "user": user,
                    "operator": operator,
                    "today": today,
                    "todayCorrect": todayCorrect,
                    "todayWrong": todayWrong,
                    "step": step,
                    "addition": addition,
                    "difference": difference,
                    "multiplying": multiplying,
                    "dividing": dividing,
                    "counter": counter,
                    "number": number,
                    "note": note,
                    "style": style,
                    "progressColour": progressColour,
                    "missing_number": missing_number,
               }

               options = []

               if addition:
                   options.append("+")
               if difference:
                   options.append("-")
               if multiplying:
                   options.append("x")
               if dividing:
                   options.append(":")
               params.update(newEquation(addition,difference,multiplying,dividing))


            ### redirect za nelogiranga userja ###
            else:
                login_url = users.create_login_url('/')
                params = {"login_url": login_url}
            logging.info(missing_number)
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