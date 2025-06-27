import math
import pickle
import requests
import datetime
import os
import sys
from dataclasses import dataclass, asdict
import json

@dataclass
class WordleSolution:
    solution: str
    solved: bool
    attempt: list

class WordleSolver:
    def __init__(self, solution=None):
        if not os.path.exists('allowed_guesses.txt'):
            print("must provide allowed_guesses.txt")
            sys.exit(1)
        else:
            print("loading allowed guesses")
            with open('allowed_guesses.txt') as f:
                self.allowed_guesses = [line.strip().lower() for line in f if line.strip()]
        self.word_to_index = {word: idx for idx, word in enumerate(self.allowed_guesses)}
        if not os.path.exists('solutions.txt'):
            print("must provide solutions.txt")
            sys.exit(1)
        else:
            print("loading solutions")
            with open('solutions.txt') as f:
                self.solutions = [line.strip().lower() for line in f if line.strip()]
        if not os.path.exists('feedback_matrix.bin'):
            print("writing feedback matrix")
            with open('feedback_matrix.bin', 'wb') as f:
                pickle.dump(self.precompute_feedback_matrix(), f)
        print("loading feedback matrix")
        with open('feedback_matrix.bin', 'rb') as f:
            self.feedback_matrix = pickle.load(f)
        if not os.path.exists('first_guess.txt'):
            print("writing first guess")
            with open('first_guess.txt', 'w') as f:
                f.write(str(self.precompute_first_guess_index()))
        print("loading first guess")
        with open('first_guess.txt') as f:
            self.first_guess_index = int(f.read())
        self.reset(solution)
        
    def get_feedback_code(self, guess, solution=None):
        if not solution:
            solution = self.solution
        pattern = [0] * 5
        freq = [0] * 26
        for i in range(5):
            if guess[i] == solution[i]:
                pattern[i] = 2
            else:
                idx = ord(solution[i]) - ord('a')
                freq[idx] += 1
        for i in range(5):
            if pattern[i] == 2:
                continue
            letter = guess[i]
            idx = ord(letter) - ord('a')
            if freq[idx] > 0:
                pattern[i] = 1
                freq[idx] -= 1
            else:
                pattern[i] = 0
        code = 0
        for i in range(5):
            code = code * 3 + pattern[i]
        return code

    def precompute_feedback_matrix(self) -> list[list]:
        n_guesses = len(self.allowed_guesses)
        n_solutions = len(self.solutions)
        matrix = [[0] * n_solutions for _ in range(n_guesses)]
        for i, guess in enumerate(self.allowed_guesses):
            for j, solution in enumerate(self.solutions):
                code = self.get_feedback_code(guess, solution)
                matrix[i][j] = code
        return matrix
 
    def precompute_first_guess_index(self) -> int:
        n_solutions = len(self.solutions)
        best_entropy = -1
        best_guess_index = None
        for guess_index in range(len(self.allowed_guesses)):
            counts = [0] * 243
            for sol_index in range(n_solutions):
                code = self.feedback_matrix[guess_index][sol_index]
                counts[code] += 1
            entropy = 0.0
            for count_val in counts:
                if count_val == 0:
                    continue
                p = count_val / n_solutions
                entropy -= p * math.log2(p)
            if entropy > best_entropy:
                best_entropy = entropy
                best_guess_index = guess_index
        return best_guess_index
    
    def reset(self, solution):
        if not solution:
            print("getting daily solution")
            self.solution = requests.get(url=f"https://www.nytimes.com/svc/wordle/v2/{str(datetime.date.today())}.json").json()["solution"]
        else:
            self.solution = solution
        self.candidate_set = list(range(len(self.solutions)))
        self.first_step_done = False

    def suggest_guess(self):
        if not self.candidate_set:
            return None
        n = len(self.candidate_set)
        if n == 1:
            word = self.solutions[self.candidate_set[0]]
            return self.word_to_index[word]
        if not self.first_step_done:
            return self.first_guess_index
        best_entropy = -1
        best_guess_index = None
        for guess_idx in range(len(self.allowed_guesses)):
            counts = [0] * 243
            for sol_idx in self.candidate_set:
                code = self.feedback_matrix[guess_idx][sol_idx]
                counts[code] += 1
            entropy = 0.0
            for count_val in counts:
                if count_val == 0:
                    continue
                p = count_val / n
                entropy -= p * math.log2(p)
            if entropy > best_entropy:
                best_entropy = entropy
                best_guess_index = guess_idx
        return best_guess_index

    def update(self, guess_index, feedback_tuple):
        self.first_step_done = True
        code = 0
        for i in range(5):
            code = code * 3 + feedback_tuple[i]
        new_candidate_set = []
        for sol_idx in self.candidate_set:
            if self.feedback_matrix[guess_index][sol_idx] == code:
                new_candidate_set.append(sol_idx)
        self.candidate_set = new_candidate_set
        
    def compute_feedback(self, guess) -> tuple:
        feedback = [0,0,0,0,0]
        for idx, char in enumerate(guess):
            if self.solution[idx] == char:
                feedback[idx] = 2
                continue
            for s_idx, _ in enumerate(self.solution):
                if self.solution[s_idx] == char:
                    feedback[idx] = 1
                    continue
        return tuple(feedback)

    def is_solved(self, feedback: tuple) -> bool:
        print()
        return ''.join([str(x) for x in feedback]) == '22222'
        
    def play(self) -> WordleSolution:
        guesses = []
        max_guesses = 6
        guess_count = 1
        solved = False
        while guess_count <= max_guesses:
            guess_idx = self.suggest_guess()
            if guess_idx is None:
                print("No solution found.")
                break
            guess_word = self.allowed_guesses[guess_idx]
            guesses.append(guess_word)
            print(f"Guess: {guess_word}")
            feedback = self.compute_feedback(guess_word)
            print(f"Feedback: {feedback}")
            solved = self.is_solved(feedback)
            if solved:
                break
            self.update(guess_idx, feedback)
            guess_count += 1
        print(f"Solved! Guess count: {guess_count}") if solved else print(f"Could not solve in {max_guesses} guesses :(")
        return WordleSolution(self.solution, solved, guesses)

    def play_all(self) -> list[WordleSolution]:
        wordle_solutions = []
        for solution in self.solutions:
            self.reset(solution)
            wordle_solutions.append(self.play())
        return wordle_solutions
            


if __name__ == "__main__":
    solver = WordleSolver()
    with open("results.json", "w") as f:
        f.write(json.dumps([asdict(x) for x in solver.play_all()]))
