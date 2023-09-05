import os
import requests
from flask import Flask, redirect, render_template, request, url_for, session
from pymongo import MongoClient
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

client = MongoClient('localhost', 27017)
db = client['journal_db']
collection = db['entries']

@app.route("/", methods=("GET", "POST"))
def index():
    elapsed_time = 0
    if request.method == "POST":
        date = request.form["date"]
        day = request.form["day"]
        resume = request.form["resume"]
        temperature = float(request.form.get("temperature", 0.7))
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo-0613",
            "messages": [
                {"role": "system", "content": "Vous êtes un assistant qui aide à remplir un journal de bord, vous n'hésiterez pas à utiliser vos talents d'écritures pour embéllir le tout"},
                {"role": "user", "content": f"""
    Sur la base des informations fournies : 
    - Date : {date} (format jj/mm/aaa)
    - Jour : {day}
    - Résumé de la journée : {resume}

    Veuillez générer un journal de bord au format JSON avec la structure suivante :

    {{
        "date": "{date}",
        "day": "{day}",
        "summary": "...",
        "tasks_completed": ["...", "..."],
        "issues_encountered": "...",
        "solutions_considered": "...",
        "next_steps": "..."
    }}
    """}
            ],
            "temperature": temperature
        }

        start_time = time.time()
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        elapsed_time = time.time() - start_time

        response_data = response.json()
        result = response_data["choices"][0]["message"]["content"].strip()

        entry = {
            "date": date,
            "day": day,
            "resume": resume,
            "temperature": temperature,
            "generated_content": result,
            "execution_time": elapsed_time
        }

        collection.insert_one(entry)
        session['form_submitted'] = True
        return redirect(url_for("index"))

    if 'form_submitted' in session:
        last_entry = collection.find_one(sort=[('_id', -1)])
        result = last_entry["generated_content"]
        elapsed_time = last_entry["execution_time"]
        session.pop('form_submitted', None)
    else:
        result = None
        elapsed_time = None

    return render_template("index.html", result=result, elapsed_time=elapsed_time)

@app.route("/all_entries")
def all_entries():
    entries = collection.find()
    return render_template("all_entries.html", entries=entries)

if __name__ == "__main__":
    app.run(debug=True)
