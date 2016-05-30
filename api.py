# -*- coding: utf-8 -*-`

import random
from datetime import datetime

import endpoints

from protorpc import messages
from protorpc import message_types
from protorpc import remote

from models import User, Game, Score, Transaction
from models import StringMessage, NewGameForm, GameForm, MakeGuessForm,\
    GameForms, ScoreForms, UserForms, TransactionForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_GUESS_REQUEST = endpoints.ResourceContainer(
    MakeGuessForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
GET_HIGH_SCORE_REQUEST = endpoints.ResourceContainer(
        number_of_results=messages.IntegerField(1),)

WORD_LIST = ['carpet', 'bottle', 'pencil', 'jacket', 'rocket', 'planet',
             'phone', 'broom', 'light', 'bubble', 'brain', 'roof', 'water',
             'pink']
STICK_MAN_PARTS = ['left_leg', 'right_leg', 'left_arm', 'right_arm', 'body',
                   'head']


@endpoints.api(name='hang_man', version='v1')
class HangManApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.screen_name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(screen_name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.screen_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        random_word = random.choice(WORD_LIST)
        game = Game(game_word=random_word,
                    correct_guesses=['_' for i in random_word],
                    incorrect_guesses=[],
                    attempts_remaining=len(STICK_MAN_PARTS),
                    hangman=[],
                    game_over=False,
                    parent=user.key)
        game.put()

        score = Score(date=datetime.today(), parent=game.key)
        score.put()

        return game.to_form('Good luck playing Hang Man!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a guess!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_GUESS_REQUEST,
                      response_message=GameForm,
                      path='game/guess/{urlsafe_game_key}',
                      name='make_guess',
                      http_method='PUT')
    def make_guess(self, request):
        """Guess a letter. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            raise endpoints.BadRequestException(
                    'Game already over!')

        if game.game_cancelled:
            raise endpoints.BadRequestException(
                    'Game has been cancelled!')

        if len(request.guess) > 1:
            raise endpoints.BadRequestException(
                    'You can only guess one letter!')

        if not request.guess.isalpha():
            raise endpoints.BadRequestException(
                    'The guess must be a letter!')

        # Determine if guess is correct.  If so, update score
        score = Score.query(ancestor=game.key).get()
        if request.guess in game.game_word:
            msg = 'You guessed right. The game word does contain the letter '\
              + request.guess + '.'
            # find all correctly guess letters in the game word and
            # set those letters in the guess string
            for index, char in enumerate(game.game_word):
                if char == request.guess:
                    game.correct_guesses[index] = char
                    score.points += 1
        else:
            msg = 'Sorry, the game word does not contain the letter '\
              + request.guess + '.'
            game.hangman.append(STICK_MAN_PARTS[game.attempts_remaining-1])
            game.attempts_remaining -= 1
            game.incorrect_guesses.append(request.guess)

        if ''.join(game.correct_guesses) == game.game_word:
            game.game_over = True
            score.points += 30
            score.won = True
            msg = 'You win!'
        elif game.attempts_remaining < 1:
            game.game_over = True
            msg = msg + 'Sorry, Game over!'

        game.put()
        score.put()

        # Record the transaction
        trans = Transaction(date=datetime.today(),
                            game=game.key,
                            guess=request.guess,
                            result=msg)
        trans.put()

        return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(scores=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.screen_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        scores = Score.query(ancestor=user.key)
        return ScoreForms(scores=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of an individual User's active games"""
        user = User.query(User.screen_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(ancestor=user.key)
        games = games.filter(Game.game_over == False)
        games = games.filter(Game.game_cancelled != True)

        return GameForms(games=[game.to_form('') for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancels a game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            raise endpoints.BadRequestException('Game already over!')

        game.game_cancelled = True
        game.put()
        return StringMessage(message='Game has been cancelled')

    @endpoints.method(request_message=GET_HIGH_SCORE_REQUEST,
                      response_message=ScoreForms,
                      path='scores/highscore',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Returns the highest scores"""
        scores = Score.query()
        scores = scores.order(-Score.points)
        scores = scores.fetch(limit=request.number_of_results)
        return ScoreForms(scores=[score.to_form() for score in scores])

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=UserForms,
                      path='user/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns user rankings"""
        users = User.query()
        for user in users:
            total_rankings = 0
            ranking = 0
            games = Game.query(ancestor=user.key)
            for count, game in enumerate(games):
                # calculate ranking
                correct_guesses = (len(game.correct_guesses) -
                                   game.correct_guesses.count('_'))
                total_guesses = correct_guesses + len(game.incorrect_guesses)
                score = Score.query(ancestor=game.key).get()
                if score.points > 0 and total_guesses > 0:
                    ranking = score.points/total_guesses + score.points
                    total_rankings += ranking

            if total_rankings > 0:
                user.ranking = total_rankings/count
                user.put()

        users = User.query().order(-User.ranking)
        return UserForms(users=[user.to_form() for user in users])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=TransactionForms,
                      path='game/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns the a listing of all guesses made in the given game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        tx = Transaction.query(Transaction.game == game.key)
        tx = tx.order(Transaction.date)
        return TransactionForms(transactions=[trans.to_form()
                                for trans in tx])


api = endpoints.api_server([HangManApi])
