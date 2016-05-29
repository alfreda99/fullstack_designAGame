#Full Stack Nanodegree Project 4

##Game Description:
Hangman is a simple guessing game where a random word is picked and the user
guesses one letter at at time until they have guessed all the letters that spell
the word. If they guess a letter that is not in the word, they will build the body
of a stick "hangman".  The stick man has 6 body parts and thus the user has 6 times to
to guess a wrong letter before the hangman is completely constructed.  If the
hangman is built, the user will have lost the game and the game will end. If all
the letters of the word are guessed, the user wins.
'Guesses' are sent to the `make_guess` endpoint which will reply
with either: 'You guessed right. The game word does contain the letter',
'Sorry, the game word does not contain the letter', 'you win'(if the work is correctly
guessed), or 'game over' (if the hangman is completely built).
IT is a single player game.  Many different games can be played by many different
Users at any given time. Each game can be retrieved or played by using the path
parameter `urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Also initializes the
    the games Score object.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_guess**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Contains the bulk of the game logic. It Accepts a 'guess' and
    determines if the guess is contained within the game word.  If the guess is not
    contained in the gameword, a body part of the hangman is added, the number of
    available tries is reduced by one and a message returned.  If the guess is
    in the game word, the correct guesses is updated, the score is incremented by
    1.  If the word is completely guessed correctly the score is incremented by 30.
    If the hangman is completely constructed, the game ends. In all cases, it
    returns the updated state of the game.
    Each time a guess is made, a transaction record is created that contains the
    guess, the time and the result.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **get_user_games**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms.
    - Description: Returns all of an individual User's active games (unordered).
    Will raise a NotFoundException if the User does not exist.

- **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: Message confirming game cancellation.
    - Description: Cancels a game.

- **get_high_scores**
    - Path: 'scores/highscore'
    - Method: GET
    - Parameters: number_of_results
    - Returns: ScoreForms.
    - Description: Returns the highest scores in descending order.  If the
    number_of_results in passed in the request, the number of results returned
    will be limited the the value passed in.

- **get_user_rankings**
    - Path: 'user/rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserForms.
    - Description: Returns user rankings in descending order.  The ranking is
    calculated by the ratio of correct guess to total guesses plus the score.
    for all games played. Once calculated, the ranking is added to the User entity.

- **get_game_history**
    - Path: 'game/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: TransactionForms.
    - Description: Returns the a listing of all guesses made in the given game
    ordered by transaction date/time.


##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address, and ranking.

 - **Game**
    - Stores unique game states. A child of the User model.

 - **Score**
    - Stores the scores of each game. A child of the Game model.

- **Transaction**
    - Stores the transaction of each guess. Associated with Game
    model via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, user_name, gameX_word,
    correct_guesses, lame_guesses, attempts_remaining, hangman, game_ove,
    flag, game_cancelled flag, message).
 - **GameForms**
    - Multiple GameForm container.
 - **NewGameForm**
    - Used to create a new game (user_name)
 - **MakeGuessForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a game's Score (user_name, date, won flag,
    points).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **UserForm**
    - Representation of a User (user_name, ranking).
 - **UserForms**
    - Multiple UserForm container.
 - **TransactionForm**
    - Representation of each transaction(guess) made in the game (date,
    guess, result).
 - **TransactionForms**
    - Multiple TransactionForm container.
