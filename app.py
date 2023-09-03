import os
import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route("/", methods=("GET", "POST"))
def index():
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
                {"role": "user", "content": generate_prompt(date, day, resume)}
            ],
            "temperature": temperature
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_data = response.json()

        result = response_data["choices"][0]["message"]["content"].strip()
        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template("index.html", result=result)

def generate_prompt(date, day, resume):
    return f"""
    Sur la base des informations fournies : 
    - Date : {date} (format jj/mm/aaa)
    - Jour : {day}
    - Résumé de la journée : {resume}

    Veuillez générer un journal de bord structuré avec des balises HTML pour chaque section, tu utiliseras le format de date jj/mm/aaaa :

    <h2>Jour {day} - {date}</h2>
    <h3>Résumé de la journée</h3>
    <p>{resume}</p>
    <h3>Tâches réalisées</h3>
    <ul>
        <li>...</li>
    </ul>
    <h3>Problèmes rencontrés</h3>
    <p>...</p>
    <h3>Solutions envisagées</h3>
    <p>...</p>
    <h3>Prochaines étapes</h3>
    <p>...</p>
    
    """

if __name__ == "__main__":
    app.run(debug=True)
