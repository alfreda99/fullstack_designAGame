#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import webapp2
from google.appengine.api import mail, app_identity

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            games = Game.query(ancestor=user.key)
            games = games.filter(Game.game_over == False)
            games = games.filter(Game.game_cancelled != True)
            if games.count() > 0:
                subject = 'This is a reminder!'
                body = 'Hello {}, This is a reminder for you to finish the \
                        Hangman game that you started playing.  You could be\
                        the winner!'.format(user.screen_name)
                body = body + '.  You have {} open games'.format(games.count())
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)

        self.response.set_status(204)


app = webapp2.WSGIApplication(
        [('/crons/send_reminder', SendReminderEmail),], debug=True)
