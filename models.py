"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    screen_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    ranking = ndb.IntegerProperty(default=0)

    def to_form(self):
        return UserForm(user_name=self.screen_name,
                        ranking=self.ranking)


class Transaction(ndb.Model):
    """Game Transactions"""
    date = ndb.DateTimeProperty(required=True)
    game = ndb.KeyProperty(required=True, kind='Game')
    guess = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)

    def to_form(self):
        return TransactionForm(date=str(self.date),
                               guess=self.guess,
                               result=self.result)


class Game(ndb.Model):
    """Game object"""
    game_word = ndb.StringProperty(required=True)
    correct_guesses = ndb.StringProperty(repeated=True)
    incorrect_guesses = ndb.StringProperty(repeated=True)
    attempts_remaining = ndb.IntegerProperty(required=True)
    hangman = ndb.StringProperty(repeated=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    game_cancelled = ndb.BooleanProperty(default=False)

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.key.parent().get().screen_name
        form.gameX_word = self.game_word
        form.correct_guesses = self.correct_guesses
        form.lame_guesses = self.incorrect_guesses
        form.attempts_remaining = self.attempts_remaining
        form.hangman = self.hangman
        form.game_over = self.game_over
        form.game_cancelled = self.game_cancelled
        form.message = message
        return form


class Score(ndb.Model):
    """Score object"""
    date = ndb.DateTimeProperty(required=True)
    won = ndb.BooleanProperty(default=False)
    points = ndb.IntegerProperty(default=0)

    def to_form(self):
        return ScoreForm(user_name=self.key.parent().parent()
                         .get().screen_name,
                         date=str(self.date),
                         won=self.won,
                         points=self.points)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    gameX_word = messages.StringField(3, required=True)
    correct_guesses = messages.StringField(4, repeated=True)
    lame_guesses = messages.StringField(5, repeated=True)
    attempts_remaining = messages.IntegerField(6, required=True)
    hangman = messages.StringField(7, repeated=True)
    game_over = messages.BooleanField(8, required=True)
    game_cancelled = messages.BooleanField(9, required=True)
    message = messages.StringField(10, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    games = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class MakeGuessForm(messages.Message):
    """Used to make a guess in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    points = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    scores = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """UserForm for outbound User information"""
    user_name = messages.StringField(1, required=True)
    ranking = messages.IntegerField(2, required=True)


class UserForms(messages.Message):
    """Return multiple UserForms"""
    users = messages.MessageField(UserForm, 1, repeated=True)


class TransactionForm(messages.Message):
    """TransactionForm for outbound transaction information"""
    date = messages.StringField(1, required=True)
    guess = messages.StringField(2, required=True)
    result = messages.StringField(3, required=True)


class TransactionForms(messages.Message):
    """Return multiple TransactionForms"""
    transactions = messages.MessageField(TransactionForm, 1, repeated=True)
