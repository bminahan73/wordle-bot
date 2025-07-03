import math
import pickle
import requests
import datetime
import os
import sys
from dataclasses import dataclass, asdict
import json
import click

@dataclass
class WordleSolution:
    solution: str
    solved: bool
    attempt: list

class WordleSolver:
    def __init__(self, solution: str = None, use_all_allowed_guesses: bool = False):
        allowed_guesses_file = 'allowed_guesses.txt' if use_all_allowed_guesses else 'solutions.txt'
        if not os.path.exists(allowed_guesses_file):
            print(f"must provide {allowed_guesses_file}")
            sys.exit(1)
        else:
            print("loading allowed guesses")
            with open(allowed_guesses_file) as f:
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
        print(f"(solution: {self.solution})")
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

    def update(self, guess_index, feedback_code: int):
        self.first_step_done = True
        new_candidate_set = []
        for sol_idx in self.candidate_set:
            if self.feedback_matrix[guess_index][sol_idx] == feedback_code:
                new_candidate_set.append(sol_idx)
        self.candidate_set = new_candidate_set

    def is_solved(self, feedback_code: int) -> bool:
        return feedback_code == 242
        
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
            feedback_code = self.get_feedback_code(guess_word)
            print(f"Feedback: {feedback_code}")
            solved = self.is_solved(feedback_code)
            if solved:
                break
            self.update(guess_idx, feedback_code)
            guess_count += 1
        print(f"Solved! Guess count: {guess_count}") if solved else print(f"Could not solve in {max_guesses} guesses :(")
        return WordleSolution(self.solution, solved, guesses)

    def play_all(self) -> list[WordleSolution]:
        wordle_solutions = []
        for solution in self.solutions:
            self.reset(solution)
            wordle_solutions.append(self.play())
        return wordle_solutions

    def save_all(self):
        with open("results.json", "w") as f:
            f.write(json.dumps([asdict(x) for x in self.play_all()]))
    
    @staticmethod
    def analyze():
        with open("results.json", "r") as f:
            results = json.load(f)
        total_solutions = len(results)
        solved_solutions = 0
        guess_counts = [0] * 6 
        for result in results:
            if result["solved"]:
                solved_solutions += 1
                guess_counts[len(result["attempt"]) - 1] += 1
        solved_percent = (solved_solutions / total_solutions) * 100
        average_num_guesses = round(((guess_counts[0] * 1) + (guess_counts[1] * 2) + (guess_counts[2] * 3) + (guess_counts[3] * 4) + (guess_counts[4] * 5) + (guess_counts[5] * 6)) / total_solutions, 2)
        print(f"Total solutions: {total_solutions}")
        print(f"Solved solutions: {solved_solutions}")
        print(f"Solved percent: {solved_percent}%")
        print(f"Average number of guesses: {average_num_guesses}")
        print(f"First guess: {guess_counts[0]}")
        print(f"Second guess: {guess_counts[1]}")
        print(f"Third guess: {guess_counts[2]}")
        print(f"Forth guess: {guess_counts[3]}")
        print(f"Fifth guess: {guess_counts[4]}")
        print(f"Sixth guess: {guess_counts[5]}")
            

@click.group()
def cli():
    pass

@cli.command()
def once():
    solver = WordleSolver()
    solver.play()
    
@cli.command()
def all():
    solver = WordleSolver()
    solver.save_all()

@cli.command()
def analyze():
    WordleSolver.analyze()

if __name__ == "__main__":
    cli()
