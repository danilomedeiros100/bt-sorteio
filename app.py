from flask import Flask, render_template, redirect
import json
import random
from collections import defaultdict
import os

app = Flask(__name__)
DATA_FILE = "data/jogadores.json"

def carregar_jogadores():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_sorteio(categoria, chaves):
    path = f"data/sorteio_{categoria}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chaves, f, ensure_ascii=False, indent=2)

def carregar_sorteio(categoria):
    path = f"data/sorteio_{categoria}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def resetar_sorteio(categoria):
    path = f"data/sorteio_{categoria}.json"
    if os.path.exists(path):
        os.remove(path)

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
        return [tuple(grupo[i:i+2]) for i in range(0, len(grupo), 2) if i + 1 < len(grupo)]

def gerar_chaves(duplas):
    chaves = defaultdict(list)
    random.shuffle(duplas)
    chave_atual = "A"
    for i in range(0, len(duplas), 3):
        grupo = duplas[i:i+3]
        if len(grupo) == 3:
            confrontos = [
                (grupo[0], grupo[1]),
                (grupo[0], grupo[2]),
                (grupo[1], grupo[2])
            ]
            chaves[chave_atual] = confrontos
            chave_atual = chr(ord(chave_atual) + 1)
    return chaves

@app.route("/")
def index():
    return '''
        <h1>Painel do Torneio</h1>
        <ul>
            <li><a href="/chaves/mista">Categoria Mista - 24/05</a></li>
            <li><a href="/chaves/genero">Masculino e Feminino - 25/05</a></li>
        </ul>
        <h3>Administração</h3>
        <ul>
            <li><a href="/painel/mista">Painel Mista</a></li>
            <li><a href="/painel/genero">Painel Masculino/Feminino</a></li>
        </ul>
    '''

# --- Rotas públicas ---

@app.route("/chaves/mista")
def chaves_mista():
    jogadores = carregar_jogadores()
    chaves = carregar_sorteio("mista")
    jogadores_mista = [j for j in jogadores if "mista" in j["categorias"]]
    return render_template("chaves_mista.html", chaves=chaves, jogadores=jogadores_mista)

@app.route("/chaves/genero")
def chaves_genero():
    jogadores = carregar_jogadores()
    masc = carregar_sorteio("masculino")
    fem = carregar_sorteio("feminino")
    jogadores_m = [j for j in jogadores if "masculino" in j["categorias"] and j["sexo"] == "M"]
    jogadores_f = [j for j in jogadores if "feminino" in j["categorias"] and j["sexo"] == "F"]
    return render_template("chaves_genero.html", masculino=masc, feminino=fem, jogadores_m=jogadores_m, jogadores_f=jogadores_f)

# --- Painéis administrativos ---

@app.route("/painel/mista")
def painel_mista():
    jogadores = carregar_jogadores()
    jogadores_mista = [j for j in jogadores if "mista" in j["categorias"]]
    return render_template("painel_mista.html", jogadores=jogadores_mista)

@app.route("/painel/genero")
def painel_genero():
    jogadores = carregar_jogadores()
    jogadores_m = [j for j in jogadores if "masculino" in j["categorias"] and j["sexo"] == "M"]
    jogadores_f = [j for j in jogadores if "feminino" in j["categorias"] and j["sexo"] == "F"]
    return render_template("painel_genero.html", jogadores_m=jogadores_m, jogadores_f=jogadores_f)

# --- Ações ---

@app.route("/sortear/<categoria>")
def sortear_categoria(categoria):
    jogadores = carregar_jogadores()
    duplas = criar_duplas(jogadores, categoria)
    chaves = gerar_chaves(duplas)
    salvar_sorteio(categoria, chaves)
    destino = "genero" if categoria in ["masculino", "feminino"] else "mista"
    return redirect(f"/chaves/{destino}")

@app.route("/resetar/<categoria>")
def resetar_categoria(categoria):
    resetar_sorteio(categoria)
    destino = "genero" if categoria in ["masculino", "feminino"] else "mista"
    return redirect(f"/chaves/{destino}")