from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import json
import requests
import datetime

with open("results.json", "r") as f:
    results = json.load(f)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/v1/results/today")
def get_todays_results():
    todays_solution = requests.get(url=f"https://www.nytimes.com/svc/wordle/v2/{str(datetime.date.today())}.json").json()["solution"]
    return next((x for x in results if x["solution"] == todays_solution), None)
