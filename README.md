# wordle-bot

[Wordle Bot](https://wordle-bot.benminahan.com) plays wordle every day, using greatest-entrpoy algorithm. Can you do better?

This repo consists of:

1. an algorithm to play New York Times [wordle](https://fastapi.tiangolo.com/#example) in [wordle_bot.py](./wordle_bot.py)
2. a small site built using [fastapi](https://fastapi.tiangolo.com/#example) that displays the bot's results for the current day's word, which lives in [main.py](./main.py)

## How-Do

1. Set up your python environment however you do, and install requirements

```shell
python -m venv .venv
source .venv.bin.activate
pip install -r requirements.txt
```

2. Run the wordle bot:

```shell
python worlde_bot.py
```

> The algorithm goes through all the [allowed_guesses](./allowed_guesses.txt) and all [solutions](./solutions.txt) to determine best entropy for guesses as preprocessing, so first run can take 30 minutes or so. It will save the preprocessing results as local files `feedback_matrix.bin` and `first_guess.txt` so subsequent runs will be speedy.

3. When complete, wordle bot will produce a `results.json` which contains information on all its best attempt at all the possible solutions for Wordle.

4. Run the frontend site with `fastapi dev main.py`. You should then see the site at [http://127.0.0.1:8000](http://127.0.0.1:8000) with todays results!

> the results are pulled from wordle's website, and then looked up in the pre-computed `results.json` file.

## Server

1. Have an SSL Certificate. Put `cert.pem` and `key.pem` in the root of this repo (gitignored). You can generate a self-signed one:

```shell
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

2. Run `python main.py`. Will run `uvicorn` with SSL

## LICENSE

see [LICENSE.txt](./LICENSE.txt)

## Contribute

Right now the algorithms is unable to solve a handful of words. Any thoughts / PRs that would solve this would be greatly appreciated!
