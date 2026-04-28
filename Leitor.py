from flask import Flask, render_template, request, redirect, jsonify, Response
import json, os, csv
from io import StringIO

app = Flask(__name__)

ARQUIVO = "dados.json"
CONFIG = "config.json"

# =========================
# DADOS
# =========================
def carregar():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r") as f:
        return json.load(f)

def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

# =========================
# CONFIG
# =========================
def carregar_config():
    if not os.path.exists(CONFIG):
        return {}
    with open(CONFIG, "r") as f:
        return json.load(f)

def salvar_config(dados):
    with open(CONFIG, "w") as f:
        json.dump(dados, f)

# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add():
    dados = carregar()

    inicio = request.form["inicio"]
    fim = request.form["fim"]

    if fim <= inicio:
        return "Erro: fim menor que início"

    novo = {
        "id": len(dados) + 1,  # ID único melhorado
        "data": request.form["data"],
        "nome": request.form["nome"],
        "cavalo": request.form["cavalo"],
        "reboque": request.form["reboque"],
        "tipo": request.form["tipo"],
        "inicio": inicio,
        "fim": fim
    }

    dados.append(novo)
    salvar(dados)

    return redirect("/")

@app.route("/listar")
def listar():
    return jsonify(carregar())

@app.route("/deletar/<int:id>")
def deletar(id):
    dados = carregar()
    novos = [d for d in dados if d["id"] != id]
    salvar(novos)
    return jsonify({"status": "ok"})

@app.route("/exportar")
def exportar():
    dados = carregar()

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(["Data","Nome","Cavalo","Reboque","Tipo","Inicio","Fim"])

    for d in dados:
        writer.writerow([
            d["data"],
            d["nome"],
            d["cavalo"],
            d["reboque"],
            d["tipo"],
            d["inicio"],
            d["fim"]
        ])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=relatorio.csv"}
    )

@app.route("/config")
def config():
    return jsonify(carregar_config())

@app.route("/salvar_config", methods=["POST"])
def salvar_conf():
    salvar_config(request.json)
    return jsonify({"status":"ok"})

# =========================
app.run(host="0.0.0.0", port=5000, debug=True)
