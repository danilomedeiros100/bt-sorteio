from flask import Flask, render_template, redirect, url_for, request
import json
import os
import random
from collections import defaultdict

app = Flask(__name__)
DATA_FILE = "data/jogadores.json"

def carregar_jogadores():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def criar_duplas(jogadores, categoria):
    if categoria == "mista":
        homens = [j for j in jogadores if "mista" in j["categorias"] and j["sexo"] == "M"]
        mulheres = [j for j in jogadores if "mista" in j["categorias"] and j["sexo"] == "F"]
        random.shuffle(homens)
        random.shuffle(mulheres)
        return list(zip(homens, mulheres))
    else:
        grupo = [j for j in jogadores if categoria in j["categorias"] and j["sexo"].lower().startswith(categoria[0])]
        random.shuffle(grupo)
        return [tuple(grupo[i:i + 2]) for i in range(0, len(grupo) - 1, 2)]

def gerar_chaves(duplas):
    chaves = defaultdict(list)
    random.shuffle(duplas)
    chave_atual = "A"
    for i in range(0, len(duplas), 3):
        grupo = duplas[i:i + 3]
        if len(grupo) == 3:
            confrontos = [
                (grupo[0], grupo[1]),
                (grupo[0], grupo[2]),
                (grupo[1], grupo[2])
            ]
            chaves[chave_atual] = confrontos
            chave_atual = chr(ord(chave_atual) + 1)
    return chaves

def get_status():
    return {
        "mista": {"realizado": os.path.exists("data/sorteio_mista.json")},
        "masculino": {"realizado": os.path.exists("data/sorteio_masculino.json")},
        "feminino": {"realizado": os.path.exists("data/sorteio_feminino.json")}
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/painel")
def painel():
    return render_template("painel.html", status=get_status())

@app.route("/sortear/<categoria>", methods=["POST"])
def sortear_categoria(categoria):
    jogadores = carregar_jogadores()
    duplas = criar_duplas(jogadores, categoria)
    chaves = gerar_chaves(duplas)

    data = {
        "chaves": chaves,
        "jogadores": jogadores
    }

    with open(f"data/sorteio_{categoria}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return redirect(url_for("painel"))

@app.route("/resetar/<categoria>")
def resetar_categoria(categoria):
    path = f"data/sorteio_{categoria}.json"
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for("painel"))

@app.route("/chaves/<categoria>")
def chaves_categoria(categoria):
    path = f"data/sorteio_{categoria}.json"
    jogadores = carregar_jogadores()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return render_template(f"chaves_{categoria}.html", jogadores=data["jogadores"], chaves=data["chaves"], categoria=categoria)
    return render_template(f"chaves_{categoria}.html", jogadores=jogadores, chaves={}, categoria=categoria)

if __name__ == "__main__":
    app.run(debug=True)
