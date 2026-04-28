from flask import Flask, render_template, request, jsonify, Response
import json, os, csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

ARQUIVO = "dados.json"
CONFIG = "config.json"

def carregar():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add():
    dados = carregar()
    data = request.get_json()

    if data["fim"] <= data["inicio"]:
        return "Erro horário", 400

    data_br = datetime.strptime(data["data"], "%Y-%m-%d").strftime("%d/%m/%Y")

    novo = {
        "id": len(dados) + 1,
        "data": data_br,
        "nome": data["nome"],
        "tipo": data["tipo"],
        "inicio": data["inicio"],
        "fim": data["fim"]
    }

    dados.append(novo)
    salvar(dados)

    return jsonify({"ok": True})

@app.route("/listar")
def listar():
    return jsonify(carregar())

@app.route("/deletar/<int:id>")
def deletar(id):
    dados = carregar()
    dados = [d for d in dados if d["id"] != id]
    salvar(dados)
    return jsonify({"ok": True})

@app.route("/planilha")
def planilha():
    dados = carregar()

    si = StringIO()
    writer = csv.writer(si, delimiter=';')

    writer.writerow(["Data","Nome","Evento","Hora Inicial","Hora Final"])

    for d in dados:
        writer.writerow([
            d.get("data",""),
            d.get("nome",""),
            d.get("tipo",""),
            d.get("inicio",""),
            d.get("fim","")
        ])

    return Response(
        '\ufeff' + si.getvalue(),
        mimetype="text/csv; charset=utf-8"
    )

if __name__ == "__main__":
    app.run()
