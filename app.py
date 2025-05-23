from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import os
import random
from collections import defaultdict
import hashlib

app = Flask(__name__)
DATA_FILE = os.path.join("data", "jogadores.json")

def carregar_jogadores():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            jogadores = json.load(f)
            for j in jogadores:
                if "confirmado" not in j:
                    j["confirmado"] = False
            return jogadores
    except FileNotFoundError:
        return []



VISITAS_FILE = "data/visitas.json"


def criar_duplas(jogadores, categoria):
    jogadores = [j for j in jogadores if j.get("confirmado")]
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


@app.route("/painel")
def painel():
    total_visitas = 0
    try:
        with open("data/visitas.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            visitas = json.loads(content) if content else []
            total_visitas = len(visitas)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return render_template("painel.html", status=get_status(), total_visitas=total_visitas)

@app.route("/presenca")
def presenca():
    jogadores = sorted(carregar_jogadores(), key=lambda j: j["nome"])
    categorias = {
        "mista_m": len([j for j in jogadores if j["confirmado"] and "mista" in j["categorias"] and j["sexo"] == "M"]),
        "mista_f": len([j for j in jogadores if j["confirmado"] and "mista" in j["categorias"] and j["sexo"] == "F"]),
        "masculino": len([j for j in jogadores if j["confirmado"] and "masculino" in j["categorias"]]),
        "feminino": len([j for j in jogadores if j["confirmado"] and "feminino" in j["categorias"]]),
    }
    return render_template("presenca.html", jogadores=jogadores, categorias=categorias)

@app.route("/confirmar_presenca", methods=["POST"])
def confirmar_presenca():
    jogadores = carregar_jogadores()
    confirmados = request.json.get("confirmado", [])
    for j in jogadores:
        j["confirmado"] = j["nome"] in confirmados
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

@app.route("/sortear/<categoria>", methods=["POST"])
def sortear_categoria(categoria):
    jogadores = [j for j in carregar_jogadores() if j.get("confirmado")]
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

@app.route("/excluir_jogador", methods=["POST"])
def excluir_jogador():
    try:
        data = request.get_json(force=True)
        nome = data.get("nome")

        if not nome:
            return jsonify({'status': 'erro', 'mensagem': 'Nome não fornecido'}), 400

        jogadores = carregar_jogadores()
        jogadores_filtrados = [j for j in jogadores if j["nome"] != nome]

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(jogadores_filtrados, f, indent=2, ensure_ascii=False)

        return jsonify({'status': 'ok'})

    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500

@app.route("/adicionar_ou_editar_jogador", methods=["POST"])
def adicionar_ou_editar_jogador():
    data = request.get_json()
    nome = data.get("nome", "").strip()
    sexo = data.get("sexo")
    categorias = data.get("categorias", [])

    if not nome or not sexo or not categorias:
        return {"status": "erro", "mensagem": "Dados incompletos"}, 400

    jogadores = carregar_jogadores()
    jogador_existente = next((j for j in jogadores if j["nome"].lower() == nome.lower()), None)

    if jogador_existente:
        jogador_existente["sexo"] = sexo
        jogador_existente["categorias"] = categorias
    else:
        jogadores.append({
            "nome": nome,
            "sexo": sexo,
            "categorias": categorias,
            "confirmado": False
        })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, indent=2)

    return {"status": "ok"}

@app.route("/chaves/<categoria>")
def chaves_categoria(categoria):
    path = f"data/sorteio_{categoria}.json"
    jogadores = [j for j in carregar_jogadores() if j.get("confirmado")]
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return render_template(f"chaves_{categoria}.html", jogadores=data["jogadores"], chaves=data["chaves"], categoria=categoria)
    return render_template(f"chaves_{categoria}.html", jogadores=jogadores, chaves={}, categoria=categoria)

@app.route("/")
def index():
    total_visitas = 0
    try:
        with open("data/visitas.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            visitas = json.loads(content) if content else []
            total_visitas = len(visitas)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return render_template("index.html", total_visitas=total_visitas)

@app.before_request
def registrar_visita_global():
    try:
        ip = request.remote_addr
        user_hash = hashlib.md5(ip.encode()).hexdigest()
        with open(VISITAS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            ips = json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError):
        ips = []

    if user_hash not in ips:
        ips.append(user_hash)
        with open(VISITAS_FILE, "w", encoding="utf-8") as f:
            json.dump(ips, f)

if __name__ == "__main__":
    app.run(debug=True)