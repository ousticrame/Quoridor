from flask import Flask, jsonify, request
from flask_cors import CORS
from wordle_solver import solver_lib
import pandas as pd
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue.js frontend

total_words = pd.read_fwf("wordle_solver/words_alpha.txt", names=["words"])
words = total_words[total_words["words"].str.len() == 5]
words_data = [tuple([ord(c) - ord('a') for c in word]) for word in words["words"]]

current_game = {
    "target_word": None,
    "guesses": [],
    "feedback": []
}

@app.route('/new-game', methods=['POST'])
def new_game():
    current_game["target_word"] = solver_lib.choose_target(words["words"].tolist())
    current_game["guesses"] = []
    current_game["feedback"] = []
    return jsonify(current_game)

@app.route('/solver-guess', methods=['GET'])
def get_solver_guess():
    response = solver_lib.solve_wordle(
        valid_words=words_data,
        target_word=current_game["target_word"],
        max_attempts=10,
        print_output=False
    )
    return jsonify({
        "guesses": response["guesses"],
        "feedback": response["feedback"],
        "nb_possible_words": response["nb_possible_words"],
    })

if __name__ == '__main__':
    app.run(port=5000)