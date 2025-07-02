from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
import json
import requests
import datetime
import uvicorn
import pytz

with open("results.json", "r") as f:
    results = json.load(f)

api_app = FastAPI(title="api app")

@api_app.get("/results/today")
def get_todays_results(
    timezone: str = Query(default='UTC', description="IANA timezone name (e.g., 'America/New_York', 'Europe/London')")
):
    try:
        tz = pytz.timezone(timezone)
        now_in_tz = datetime.datetime.now(datetime.timezone.utc).astimezone(tz)
        date_str = now_in_tz.strftime("%Y-%m-%d")
        todays_solution = requests.get(
            url=f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
        ).json()["solution"]
        return next((x for x in results if x["solution"] == todays_solution), None)
    except pytz.exceptions.UnknownTimeZoneError:
        return {"error": "Invalid timezone provided"}
    except Exception as e:
        return {"error": str(e)}

app = FastAPI()

app.mount("/api/v1", api_app)
app.mount("/", StaticFiles(directory="static",html = True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
