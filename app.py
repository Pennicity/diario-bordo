from flask import Flask, render_template, request, jsonify, Response
import json, os, csv
from io import StringIO
from datetime import datetime, timedelta

app = Flask(__name__)

ARQUIVO = "dados.json"
CONFIG = "config.json"

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
def calcular_duracao(inicio, fim):
    t1 = datetime.strptime(inicio, "%H:%M")
    t2 = datetime.strptime(fim, "%H:%M")
    return (t2 - t1).seconds // 60

def minutos_para_horas(minutos):
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"

# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
@app.route("/add", methods=["POST"])
def add():
    dados = carregar()
    data = request.get_json()

    if data["fim"] <= data["inicio"]:
        return "Erro horário", 400

    data_br = datetime.strptime(data["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
    duracao = minutos_para_horas(calcular_duracao(data["inicio"], data["fim"]))

    novo = {
        "id": len(dados) + 1,
        "data": data_br,
        "data_raw": data["data"],
        "nome": data["nome"],
        "cavalo": data["cavalo"],
        "reboque": data["reboque"],
        "tipo": data["tipo"],
        "inicio": data["inicio"],
        "fim": data["fim"],
        "duracao": duracao
    }

    dados.append(novo)
    salvar(dados)

    return jsonify({"ok": True})

# =========================
@app.route("/listar")
def listar():
    dados = carregar()

    total = 0
    for d in dados:
        h, m = map(int, d["duracao"].split(":"))
        total += h*60 + m

    return jsonify({
        "dados": dados,
        "total": minutos_para_horas(total)
    })

# =========================
@app.route("/deletar/<int:id>")
def deletar(id):
    dados = carregar()
    dados = [d for d in dados if d["id"] != id]
    salvar(dados)
    return jsonify({"ok": True})

# =========================
@app.route("/exportar")
def exportar():
    dados = carregar()

    si = StringIO()
    writer = csv.writer(si, delimiter=';')

    writer.writerow(["Data", "Nome", "Evento", "Hora Inicial", "Hora Final"])

    for d in dados:
        writer.writerow([
            d["data"],
            d["nome"],
            d["tipo"],
            d["inicio"],
            d["fim"]
        ])

    salvar([])

    return Response(
        '\ufeff' + si.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=relatorio.csv"}
    )

# =========================
# 🔥 NOVA ROTA PARA EXCEL ONLINE
@app.route("/planilha")
def planilha():
    dados = carregar()

    si = StringIO()
    writer = csv.writer(si, delimiter=';')

    writer.writerow(["Data", "Nome", "Evento", "Hora Inicial", "Hora Final"])

    for d in dados:
        writer.writerow([
            d["data"],
            d["nome"],
            d["tipo"],
            d["inicio"],
            d["fim"]
        ])

    return Response(
        '\ufeff' + si.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "inline; filename=planilha.csv"}
    )

# =========================
@app.route("/config")
def config():
    if not os.path.exists(CONFIG):
        return jsonify({})
    with open(CONFIG, "r") as f:
        return jsonify(json.load(f))

@app.route("/salvar_config", methods=["POST"])
def salvar_conf():
    with open(CONFIG, "w") as f:
        json.dump(request.get_json(), f)
    return jsonify({"ok": True})

# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
