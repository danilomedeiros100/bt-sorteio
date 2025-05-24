def criar_grupos_duplas(duplas):
    # Distribui duplas em grupos de 3 ou 4 tentando balancear ao máximo
    total = len(duplas)
    grupos_tamanhos = []
    while total > 0:
        if total % 3 == 0 or total == 3:
            grupos_tamanhos.append(3)
            total -= 3
        elif total % 4 == 0:
            grupos_tamanhos.append(4)
            total -= 4
        elif total >= 7:
            grupos_tamanhos.append(3)
            total -= 3
        else:
            grupos_tamanhos.append(total)
            break
    grupos = []
    inicio = 0
    for tamanho in grupos_tamanhos:
        grupos.append(duplas[inicio:inicio + tamanho])
        inicio += tamanho
    return grupos
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
        return [tuple(grupo[i:i + 2]) for i in range(0, len(grupo) - 1, 2) if len(grupo[i:i + 2]) == 2]

def gerar_chaves(duplas, categoria=None):
    chaves = {}
    random.shuffle(duplas)
    grupos = criar_grupos_duplas(duplas)

    if categoria == "masculino":
        quadras_disponiveis = [1, 3, 5]
    elif categoria == "feminino":
        quadras_disponiveis = [2, 4, 6]
    else:
        quadras_disponiveis = list(range(1, 7))

    for idx, grupo in enumerate(grupos):
        chave = chr(ord("A") + idx)
        confrontos = []
        quadra = quadras_disponiveis[idx % len(quadras_disponiveis)]
        quadra2 = quadras_disponiveis[(idx + 1) % len(quadras_disponiveis)]
        if len(grupo) == 3:
            confrontos = [
                (grupo[0], grupo[1], quadra),
                (grupo[0], grupo[2], quadra),
                (grupo[1], grupo[2], quadra)
            ]
        elif len(grupo) == 4:
            confrontos = [
                (grupo[0], grupo[1], quadra),
                (grupo[2], grupo[3], quadra2),
                (grupo[0], grupo[2], quadra),
                (grupo[1], grupo[3], quadra2)
            ]
        chaves[chave] = confrontos
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
        "feminino": len([j for j in jogadores if j["confirmado"] and "feminino" in j["categorias"]])
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
    chaves = gerar_chaves(duplas, categoria)

    data = {
        "chaves": chaves,
        "jogadores": jogadores
    }

    # Sorteio especial para mista: Ranking dos 10 melhores, 6 vão direto, 4 repescagem, quartas, mas NÃO semifinais/final!
    if categoria == "mista":
        jogadores_stats = calcular_estatisticas_por_jogador(data)
        # associar grupo a cada dupla
        for chave, jogos in chaves.items():
            for jogo in jogos:
                dupla1_nome = " e ".join([j["nome"] if isinstance(j, dict) else j for j in jogo[0]])
                dupla2_nome = " e ".join([j["nome"] if isinstance(j, dict) else j for j in jogo[1]])
                for dupla_nome in [dupla1_nome, dupla2_nome]:
                    for j in jogadores_stats:
                        if j["nome"] == dupla_nome:
                            j["grupo"] = chave

        def selecionar_2_por_grupo(jogadores_stats):
            grupos = defaultdict(list)
            for j in jogadores_stats:
                if "grupo" in j:
                    grupos[j["grupo"]].append(j)
            classificados = []
            for grupo_duplas in grupos.values():
                classificados.extend(calcular_saldo_e_classificar(grupo_duplas)[:2])
            return classificados

        # NOVA LÓGICA: aplica corretamente critérios de desempate e confronto direto
        classificados_10 = selecionar_2_por_grupo(jogadores_stats)
        classificados_10 = aplicar_confronto_direto(classificados_10)
        ranking_completo = calcular_saldo_e_classificar(classificados_10)
        diretos = ranking_completo[:6]
        repescagem = ranking_completo[6:]

        confrontos = []
        # Repescagem (4 duplas, em 2 jogos)
        confrontos += [
            {"partida": "Repescagem 1", "dupla1": repescagem[0]["nome"], "dupla2": repescagem[3]["nome"], "quadra": 1},
            {"partida": "Repescagem 2", "dupla1": repescagem[1]["nome"], "dupla2": repescagem[2]["nome"], "quadra": 2},
        ]
        # Quartas de final (6 diretos + 2 vencedores repescagem)
        confrontos += [
            {"partida": "Quartas 1", "dupla1": diretos[0]["nome"], "dupla2": "Vencedor Repescagem 2", "quadra": 1},
            {"partida": "Quartas 2", "dupla1": diretos[1]["nome"], "dupla2": "Vencedor Repescagem 1", "quadra": 2},
            {"partida": "Quartas 3", "dupla1": diretos[2]["nome"], "dupla2": diretos[5]["nome"], "quadra": 3},
            {"partida": "Quartas 4", "dupla1": diretos[3]["nome"], "dupla2": diretos[4]["nome"], "quadra": 4},
        ]
        # Incluir também semifinais e final com nomes fictícios
        semifinal1 = {
            "partida": "Semifinal 1",
            "dupla1": "Vencedor Quartas 1",
            "dupla2": "Vencedor Quartas 4",
            "quadra": 1
        }
        semifinal2 = {
            "partida": "Semifinal 2",
            "dupla1": "Vencedor Quartas 2",
            "dupla2": "Vencedor Quartas 3",
            "quadra": 2
        }
        final = {
            "partida": "Final",
            "dupla1": "Vencedor Semifinal 1",
            "dupla2": "Vencedor Semifinal 2",
            "quadra": 3
        }
        confrontos.extend([semifinal1, semifinal2, final])
        data["confrontos"] = confrontos

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
        # Reestruturando confrontos para exibir no HTML, incluindo placar e vencedor se houver
        chaves_convertidas = {}
        for chave, jogos in data["chaves"].items():
            chaves_convertidas[chave] = []
            for jogo in jogos:
                confronto = {
                    "dupla1": jogo[0],
                    "dupla2": jogo[1],
                    "quadra": jogo[2]
                }
                if len(jogo) > 3:
                    confronto["resultado"] = jogo[3].get("resultado", [0, 0])
                    confronto["vencedor"] = jogo[3].get("vencedor")
                chaves_convertidas[chave].append(confronto)
        confrontos = []
        ranking = []
        if categoria == "mista" and "confrontos" in data:
            confrontos = data["confrontos"]
            jogadores_stats = calcular_estatisticas_por_jogador(data)

            # associar grupo a cada dupla
            for chave, jogos in data["chaves"].items():
                for jogo in jogos:
                    dupla1_nome = " e ".join([j["nome"] if isinstance(j, dict) else j for j in jogo[0]])
                    dupla2_nome = " e ".join([j["nome"] if isinstance(j, dict) else j for j in jogo[1]])
                    for dupla_nome in [dupla1_nome, dupla2_nome]:
                        for j in jogadores_stats:
                            if j["nome"] == dupla_nome:
                                j["grupo"] = chave

            def selecionar_2_por_grupo(jogadores_stats):
                grupos = defaultdict(list)
                for j in jogadores_stats:
                    if "grupo" in j:
                        grupos[j["grupo"]].append(j)
                classificados = []
                for grupo_duplas in grupos.values():
                    classificados.extend(calcular_saldo_e_classificar(grupo_duplas)[:2])
                return classificados

            # NOVA LÓGICA: aplica corretamente critérios de desempate e confronto direto
            classificados_10 = selecionar_2_por_grupo(jogadores_stats)
            classificados_10 = aplicar_confronto_direto(classificados_10)
            ranking_completo = calcular_saldo_e_classificar(classificados_10)

            ranking = [{
                "posicao": i + 1,
                "nome": dupla["nome"],
                "vitorias": dupla["vitorias"],
                "saldo_sets": dupla["saldo_sets"],
                "saldo_games": dupla["saldo_games"]
            } for i, dupla in enumerate(ranking_completo)]

        return render_template(
            f"chaves_{categoria}.html",
            jogadores=data["jogadores"],
            chaves=chaves_convertidas,
            categoria=categoria,
            confrontos=confrontos,
            ranking=ranking
        )
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


# Rota para exibir confrontos da fase de grupos com campos para input de games
@app.route("/painel_resultados/<categoria>")
def painel_resultados(categoria):
    path = f"data/sorteio_{categoria}.json"
    if not os.path.exists(path):
        return f"Sorteio da categoria {categoria} não encontrado", 404

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chaves_convertidas = {}
    for chave, jogos in data.get("chaves", {}).items():
        chaves_convertidas[chave] = []
        for jogo in jogos:
            dupla1 = [j["nome"] if isinstance(j, dict) else j for j in jogo[0]]
            dupla2 = [j["nome"] if isinstance(j, dict) else j for j in jogo[1]]
            confronto = {
                "dupla1": dupla1,
                "dupla2": dupla2,
                "quadra": jogo[2],
            }
            if len(jogo) > 3:
                confronto["resultado"] = jogo[3].get("resultado", [0, 0])
                confronto["vencedor"] = jogo[3].get("vencedor")
            chaves_convertidas[chave].append(confronto)

    eliminatoria_convertida = defaultdict(list)

    for confronto in data.get("confrontos", []):
        if not all(key in confronto for key in ("partida", "dupla1", "dupla2", "quadra")):
            continue

        fase = confronto["partida"]
        if fase.startswith("Repescagem"):
            chave = "Repescagem"
        elif fase.startswith("Quartas"):
            chave = "Quartas de Final"
        elif fase.startswith("Semifinal"):
            chave = "Semifinais"
        elif fase == "Final":
            chave = "Final"
        else:
            continue

        item = {
            "dupla1": confronto["dupla1"],
            "dupla2": confronto["dupla2"],
            "quadra": confronto["quadra"],
            "partida": confronto["partida"],
            "resultado": confronto.get("resultado", [0, 0]),
            "vencedor": confronto.get("vencedor")
        }
        eliminatoria_convertida[chave].append(item)

    return render_template(
        "painel_resultados.html",
        categoria=categoria,
        chaves=chaves_convertidas,
        eliminatoria=eliminatoria_convertida
    )



@app.route("/salvar_resultados/<categoria>", methods=["POST"])
def salvar_resultados(categoria):
    def salvar_resultados_interno(data, grupo, fase, index, g1, g2):
        if grupo:
            confronto = data["chaves"][grupo][index]
            if len(confronto) == 3:
                confronto.append({})
            confronto[3]["resultado"] = [g1, g2]
            confronto[3]["vencedor"] = "dupla1" if g1 > g2 else "dupla2"
        elif fase:
            dupla1_req = request.form.get("dupla1")
            dupla2_req = request.form.get("dupla2")
            fase_confrontos = [
                c for c in data.get("confrontos", [])
                if c.get("partida") == fase and (
                    (c.get("dupla1") == dupla1_req and c.get("dupla2") == dupla2_req) or
                    (c.get("dupla1") == dupla2_req and c.get("dupla2") == dupla1_req)
                )
            ]
            if not fase_confrontos:
                return "Confronto não encontrado", 404
            confronto = fase_confrontos[0]
            for i, c in enumerate(data["confrontos"]):
                if c.get("partida") == fase and (
                    (c.get("dupla1") == confronto["dupla1"] and c.get("dupla2") == confronto["dupla2"]) or
                    (c.get("dupla1") == confronto["dupla2"] and c.get("dupla2") == confronto["dupla1"])
                ):
                    data["confrontos"][i]["resultado"] = [g1, g2]
                    data["confrontos"][i]["vencedor"] = "dupla1" if g1 > g2 else "dupla2"
                    nome_vencedor = confronto["dupla1"] if g1 > g2 else confronto["dupla2"]
                    partida_id = confronto["partida"]
                    for proximo in data["confrontos"]:
                        if proximo.get("dupla1") == f"Vencedor {partida_id}":
                            proximo["dupla1"] = nome_vencedor
                        if proximo.get("dupla2") == f"Vencedor {partida_id}":
                            proximo["dupla2"] = nome_vencedor
                    break
            else:
                return "Confronto não encontrado", 404

            # Geração automática de semifinais após quartas
            if "Quartas" in confronto["partida"]:
                quartas = [c for c in data.get("confrontos", []) if "Quartas" in c.get("partida", "")]
                if all("vencedor" in c for c in quartas):
                    semifinal_ja_gerada = any("Semifinal" in c.get("partida", "") for c in data["confrontos"])
                    if not semifinal_ja_gerada:
                        semi1 = {
                            "partida": "Semifinal 1",
                            "dupla1": quartas[0]["dupla1"] if quartas[0]["vencedor"] == "dupla1" else quartas[0]["dupla2"],
                            "dupla2": quartas[3]["dupla1"] if quartas[3]["vencedor"] == "dupla1" else quartas[3]["dupla2"],
                            "quadra": 1
                        }
                        semi2 = {
                            "partida": "Semifinal 2",
                            "dupla1": quartas[1]["dupla1"] if quartas[1]["vencedor"] == "dupla1" else quartas[1]["dupla2"],
                            "dupla2": quartas[2]["dupla1"] if quartas[2]["vencedor"] == "dupla1" else quartas[2]["dupla2"],
                            "quadra": 2
                        }
                        data["confrontos"].extend([semi1, semi2])

            # Geração automática da final após semifinais
            if "Semifinal" in confronto["partida"]:
                semifinais = [c for c in data.get("confrontos", []) if "Semifinal" in c.get("partida", "")]
                if all("vencedor" in c for c in semifinais):
                    final_ja_gerado = any(c.get("partida") == "Final" for c in data["confrontos"])
                    if not final_ja_gerado:
                        final = {
                            "partida": "Final",
                            "dupla1": semifinais[0]["dupla1"] if semifinais[0]["vencedor"] == "dupla1" else semifinais[0]["dupla2"],
                            "dupla2": semifinais[1]["dupla1"] if semifinais[1]["vencedor"] == "dupla1" else semifinais[1]["dupla2"],
                            "quadra": 3
                        }
                        data["confrontos"].append(final)
        else:
            return "Identificação de confronto ausente", 400
        return data

    path = f"data/sorteio_{categoria}.json"
    if not os.path.exists(path):
        return "Arquivo de sorteio não encontrado", 404

    grupo = request.form.get("grupo")
    fase = request.form.get("fase") or request.form.get("partida")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if grupo:
        try:
            index = int(request.form.get("index"))
            g1 = int(request.form.get("games_1"))
            g2 = int(request.form.get("games_2"))
        except (TypeError, ValueError):
            return "Dados inválidos", 400
        # lógica de fase de grupos permanece como está
        try:
            result = salvar_resultados_interno(data, grupo, None, index, g1, g2)
            if isinstance(result, tuple):  # caso retorne erro
                return result
        except (KeyError, IndexError):
            return "Confronto não encontrado", 404
    elif fase:
        dupla1 = request.form.get("dupla1")
        dupla2 = request.form.get("dupla2")
        try:
            g1 = int(request.form.get("games_1"))
            g2 = int(request.form.get("games_2"))
        except (TypeError, ValueError):
            return "Dados inválidos", 400
        # lógica da fase eliminatória permanece como está
        try:
            result = salvar_resultados_interno(data, None, fase, None, g1, g2)
            if isinstance(result, tuple):  # caso retorne erro
                return result
        except (KeyError, IndexError):
            return "Confronto não encontrado", 404
    else:
        return "Identificação de confronto ausente", 400

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "ok"})

    return redirect(url_for("painel_resultados", categoria=categoria))


# Funções para critérios de desempate e classificação
def calcular_saldo_e_classificar(jogadores):
    classificados = []
    for j in jogadores:
        vitorias = j.get("vitorias", 0)
        sets_v = j.get("sets_vencidos", 0)
        sets_p = j.get("sets_perdidos", 0)
        games_v = j.get("games_vencidos", 0)
        games_p = j.get("games_perdidos", 0)
        saldo_sets = sets_v - sets_p
        saldo_games = games_v - games_p
        j.update({
            "saldo_sets": saldo_sets,
            "saldo_games": saldo_games,
            "sets_vencidos": sets_v,
            "sets_perdidos": sets_p,
            "games_vencidos": games_v,
            "games_perdidos": games_p
        })
        classificados.append(j)

    classificados = sorted(classificados, key=lambda x: (
        -x["vitorias"],
        -x["saldo_sets"],
        -x["saldo_games"]
    ))
    return classificados

def aplicar_confronto_direto(duplas):
    i = 0
    while i < len(duplas) - 1:
        d1 = duplas[i]
        d2 = duplas[i + 1]
        if (d1["vitorias"] == d2["vitorias"] and
            d1["saldo_sets"] == d2["saldo_sets"] and
            d1["saldo_games"] == d2["saldo_games"]):
            confronto = d1.get("confrontos", {}).get(d2["nome"])
            if confronto == "derrota":
                duplas[i], duplas[i + 1] = duplas[i + 1], duplas[i]
        i += 1
    return duplas

def selecionar_8_melhores(jogadores):
    classificados = calcular_saldo_e_classificar(jogadores)
    classificados = aplicar_confronto_direto(classificados)
    return classificados[:8]

def calcular_estatisticas_por_jogador(data):
    estatisticas = defaultdict(lambda: {
        "nome": "",
        "vitorias": 0,
        "sets_vencidos": 0,
        "sets_perdidos": 0,
        "games_vencidos": 0,
        "games_perdidos": 0,
        "confrontos": {}
    })

    for chave, jogos in data.get("chaves", {}).items():
        for jogo in jogos:
            dupla1 = jogo[0]
            dupla2 = jogo[1]
            resultado = jogo[3]["resultado"] if len(jogo) > 3 and "resultado" in jogo[3] else [0, 0]

            nome1 = " e ".join([j["nome"] if isinstance(j, dict) else j for j in dupla1])
            nome2 = " e ".join([j["nome"] if isinstance(j, dict) else j for j in dupla2])

            estatisticas[nome1]["nome"] = nome1
            estatisticas[nome2]["nome"] = nome2

            estatisticas[nome1]["games_vencidos"] += resultado[0]
            estatisticas[nome1]["games_perdidos"] += resultado[1]
            estatisticas[nome2]["games_vencidos"] += resultado[1]
            estatisticas[nome2]["games_perdidos"] += resultado[0]

            if resultado[0] > resultado[1]:
                estatisticas[nome1]["vitorias"] += 1
                estatisticas[nome1]["sets_vencidos"] += 1
                estatisticas[nome2]["sets_perdidos"] += 1
                estatisticas[nome1]["confrontos"][nome2] = "vitoria"
                estatisticas[nome2]["confrontos"][nome1] = "derrota"
            elif resultado[1] > resultado[0]:
                estatisticas[nome2]["vitorias"] += 1
                estatisticas[nome2]["sets_vencidos"] += 1
                estatisticas[nome1]["sets_perdidos"] += 1
                estatisticas[nome2]["confrontos"][nome1] = "vitoria"
                estatisticas[nome1]["confrontos"][nome2] = "derrota"

    return list(estatisticas.values())

@app.route("/fase2/misto")
def fase2_misto():
    path = "data/sorteio_mista.json"
    if not os.path.exists(path):
        return "Sorteio da fase de grupos do misto não encontrado", 404

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    jogadores = calcular_estatisticas_por_jogador(data)
    classificados = selecionar_8_melhores(jogadores)

    confrontos = []
    pares = [(0, 7), (1, 6), (2, 5), (3, 4)]
    for i, (a, b) in enumerate(pares):
        dupla1 = classificados[a]["nome"]
        dupla2 = classificados[b]["nome"]
        confrontos.append({
            "partida": f"Jogo {i+1}",
            "dupla1": dupla1,
            "dupla2": dupla2,
            "quadra": i + 1
        })

    ranking = [{"posicao": i+1, "nome": dupla["nome"], "vitorias": dupla["vitorias"],
                "saldo_sets": dupla["saldo_sets"], "saldo_games": dupla["saldo_games"]}
               for i, dupla in enumerate(classificados)]

    return render_template("fase2_misto.html", confrontos=confrontos, ranking=ranking)


# Rota administrativa
@app.route("/admin")
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)