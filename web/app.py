import os

from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
from collections import Counter



app = Flask(__name__)


DB_PATH = "../data/jobs.db"

import subprocess
import sys

@app.route("/api/actualizar", methods=["POST"])
def actualizar():
    try:
        scraper_path = os.path.join(os.path.dirname(__file__), "../scraper/Scraper.py")
        subprocess.run([sys.executable, scraper_path], check=True)
        return jsonify({"status": "ok", "mensaje": "Datos actualizados correctamente"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

def get_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM ofertas", conn)
    conn.close()
    return df


def top_tecnologias(df):
    todas = []
    for techs in df["tecnologias"].dropna():
        if techs.strip():
            todas.extend([t.strip() for t in techs.split(",")])
    conteo = Counter(todas)
    top = conteo.most_common(10)
    return {"labels": [x[0] for x in top], "values": [x[1] for x in top]}


def top_empresas(df):
    top = df["empresa"].value_counts().head(10)
    return {"labels": top.index.tolist(), "values": top.values.tolist()}


@app.route("/")
def index():
    df = get_data()
    stats = {
        "total_ofertas": len(df),
        "empresas_unicas": df["empresa"].nunique(),
        "ultima_extraccion": df["fecha_scraping"].max()
    }
    return render_template("index.html", stats=stats)


@app.route("/api/tecnologias")
def api_tecnologias():
    df = get_data()
    return jsonify(top_tecnologias(df))


@app.route("/api/empresas")
def api_empresas():
    df = get_data()
    return jsonify(top_empresas(df))


if __name__ == "__main__":
    app.run(debug=True)