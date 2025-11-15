#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Torneio de Beach Tennis - 5 Rodadas com Duplas Mistas
Desenvolvido para BT Mania
"""

from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import os
import hashlib
from datetime import datetime
from utils.sorteio_rodadas import (
    gerar_5_rodadas,
    validar_participantes,
    calcular_ranking_individual,
    separar_ranking_por_genero,
    analisar_viabilidade_categoria,
    analisar_viabilidade_misto,
    gerar_sorteio_mesmo_genero_v2
)

app = Flask(__name__)

# Arquivos de dados
DATA_FILE = os.path.join("data", "jogadores.json")
RODADAS_FILE = "data/rodadas.json"
RANKING_FILE = "data/ranking.json"
VISITAS_FILE = "data/visitas.json"
VISITAS_DETALHADAS_FILE = "data/visitas_detalhadas.json"

# Arquivos v3 - por categoria
RODADAS_MISTO_FILE = "data/rodadas_misto.json"
RODADAS_MASCULINO_FILE = "data/rodadas_masculino.json"
RODADAS_FEMININO_FILE = "data/rodadas_feminino.json"
RANKING_MISTO_FILE = "data/ranking_misto.json"
RANKING_MASCULINO_FILE = "data/ranking_masculino.json"
RANKING_FEMININO_FILE = "data/ranking_feminino.json"


# ============================================================================
# FUNÇÕES AUXILIARES - JOGADORES
# ============================================================================

def carregar_jogadores():
    """Carrega jogadores do arquivo JSON"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            jogadores = json.load(f)
            for j in jogadores:
                if "confirmado" not in j:
                    j["confirmado"] = False
                if "categorias" not in j:
                    j["categorias"] = ["mista"]
            return jogadores
    except FileNotFoundError:
        return []


def salvar_jogadores(jogadores):
    """Salva jogadores no arquivo JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, indent=2)


# ============================================================================
# FUNÇÕES AUXILIARES - RODADAS E RANKING
# ============================================================================

def carregar_rodadas():
    """Carrega as rodadas do arquivo JSON"""
    try:
        with open(RODADAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def salvar_rodadas(dados):
    """Salva as rodadas no arquivo JSON"""
    with open(RODADAS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_ranking():
    """Carrega o ranking do arquivo JSON"""
    try:
        with open(RANKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def salvar_ranking(dados):
    """Salva o ranking no arquivo JSON"""
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ============================================================================
# FUNÇÕES AUXILIARES V3 - POR CATEGORIA
# ============================================================================

def get_rodadas_file(categoria: str) -> str:
    """Retorna o caminho do arquivo de rodadas para a categoria"""
    files = {
        "misto": RODADAS_MISTO_FILE,
        "masculino": RODADAS_MASCULINO_FILE,
        "feminino": RODADAS_FEMININO_FILE
    }
    return files.get(categoria, RODADAS_FILE)


def get_ranking_file(categoria: str) -> str:
    """Retorna o caminho do arquivo de ranking para a categoria"""
    files = {
        "misto": RANKING_MISTO_FILE,
        "masculino": RANKING_MASCULINO_FILE,
        "feminino": RANKING_FEMININO_FILE
    }
    return files.get(categoria, RANKING_FILE)


def carregar_rodadas_categoria(categoria: str):
    """Carrega as rodadas de uma categoria específica"""
    try:
        file_path = get_rodadas_file(categoria)
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def salvar_rodadas_categoria(categoria: str, dados):
    """Salva as rodadas de uma categoria específica"""
    file_path = get_rodadas_file(categoria)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_ranking_categoria(categoria: str):
    """Carrega o ranking de uma categoria específica"""
    try:
        file_path = get_ranking_file(categoria)
        with open(file_path, "r", encoding="utf-8") as f:
            dados = json.load(f)
            # Normaliza estrutura antiga (lista) para nova (dict)
            if isinstance(dados, list):
                return {"ranking": dados, "tem_resultados": False}
            return dados
    except FileNotFoundError:
        return None


def salvar_ranking_categoria(categoria: str, dados):
    """Salva o ranking de uma categoria específica"""
    file_path = get_ranking_file(categoria)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def calcular_ranking_categoria(categoria: str):
    """Calcula o ranking para uma categoria específica"""
    rodadas_data = carregar_rodadas_categoria(categoria)
    
    if not rodadas_data or "rodadas" not in rodadas_data:
        # Se não há rodadas, retorna lista de participantes confirmados
        jogadores = carregar_jogadores()
        
        if categoria == "misto":
            participantes = [j["nome"] for j in jogadores if j.get("confirmado", False)]
        elif categoria == "masculino":
            participantes = [j["nome"] for j in jogadores if j.get("confirmado", False) and j.get("sexo") == "M"]
        else:  # feminino
            participantes = [j["nome"] for j in jogadores if j.get("confirmado", False) and j.get("sexo") == "F"]
        
        ranking = []
        for nome in sorted(participantes):
            ranking.append({
                "nome": nome,
                "vitorias": 0,
                "derrotas": 0,
                "games_feitos": 0,
                "games_sofridos": 0,
                "saldo_games": 0,
                "jogos_realizados": 0,
                "percentual_vitorias": 0.0
            })
        
        return {"ranking": ranking, "tem_resultados": False}
    
    rodadas = rodadas_data["rodadas"]
    ranking = calcular_ranking_individual(rodadas)
    
    # Verifica se há resultados
    tem_resultados = any(p["jogos_realizados"] > 0 for p in ranking)
    
    return {"ranking": ranking, "tem_resultados": tem_resultados}


# ============================================================================
# MIDDLEWARE - CONTADOR DE VISITAS
# ============================================================================

def obter_ip_real():
    """Obtém o IP real do cliente, mesmo atrás de proxies/load balancers"""
    # Tenta vários headers usados por proxies
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For pode ter múltiplos IPs separados por vírgula
        # O primeiro é o IP original do cliente
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
        ip = request.headers.get('CF-Connecting-IP')
    else:
        ip = request.remote_addr
    return ip


@app.before_request
def registrar_visita_global():
    """Registra visitas únicas por IP e salva dados detalhados"""
    try:
        # Obtém IP real (considerando proxies)
        ip = obter_ip_real()
        user_hash = hashlib.md5(ip.encode()).hexdigest()
        
        # Coleta todos os dados possíveis do visitante
        dados_visita = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_hash": user_hash,  # Hash para privacidade
            "ip_original": ip,  # IP real (pode ser removido se preferir mais privacidade)
            "user_agent": request.headers.get('User-Agent', ''),
            "navegador": request.user_agent.browser if hasattr(request, 'user_agent') else None,
            "plataforma": request.user_agent.platform if hasattr(request, 'user_agent') else None,
            "idioma": request.headers.get('Accept-Language', ''),
            "referrer": request.referrer,
            "url_acessada": request.url,
            "path": request.path,
            "metodo": request.method,
            "host": request.host,
            "scheme": request.scheme,  # http ou https
        }
        
        # 1. Atualiza contador de visitantes únicos (data/visitas.json)
        try:
            with open(VISITAS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                ips = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            ips = []

        if user_hash not in ips:
            ips.append(user_hash)
            with open(VISITAS_FILE, "w", encoding="utf-8") as f:
                json.dump(ips, f, indent=2)
        
        # 2. Salva log detalhado de todas as visitas (data/visitas_detalhadas.json)
        try:
            with open(VISITAS_DETALHADAS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                logs = json.loads(content) if content else []
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        
        logs.append(dados_visita)
        
        # Mantém apenas os últimos 1000 logs para não crescer infinitamente
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(VISITAS_DETALHADAS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        # Log de erro (opcional)
        print(f"Erro ao registrar visita: {e}")
        pass  # Não interrompe a aplicação por erros de analytics


# ============================================================================
# ROTAS - PÁGINA INICIAL
# ============================================================================

@app.route("/")
def index():
    """Página inicial do torneio"""
    total_visitas = 0
    try:
        with open(VISITAS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            visitas = json.loads(content) if content else []
            total_visitas = len(visitas)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return render_template("index.html", total_visitas=total_visitas)


# ============================================================================
# ROTAS - GESTÃO DE JOGADORES
# ============================================================================

@app.route("/presenca")
def presenca():
    """Página de confirmação de presença e cadastro"""
    jogadores = sorted(carregar_jogadores(), key=lambda j: j["nome"])
    categorias = {
        "mista_m": len([j for j in jogadores if j["confirmado"] and j["sexo"] == "M"]),
        "mista_f": len([j for j in jogadores if j["confirmado"] and j["sexo"] == "F"]),
        "masculino": len([j for j in jogadores if j["confirmado"] and j["sexo"] == "M"]),
        "feminino": len([j for j in jogadores if j["confirmado"] and j["sexo"] == "F"])
    }
    return render_template("presenca.html", jogadores=jogadores, categorias=categorias)


@app.route("/confirmar_presenca", methods=["POST"])
def confirmar_presenca():
    """API para confirmar presença de jogadores"""
    jogadores = carregar_jogadores()
    confirmados = request.json.get("confirmado", [])
    
    for j in jogadores:
        j["confirmado"] = j["nome"] in confirmados
    
    salvar_jogadores(jogadores)
    return {"status": "ok"}


@app.route("/adicionar_ou_editar_jogador", methods=["POST"])
def adicionar_ou_editar_jogador():
    """API para adicionar ou editar jogador"""
    data = request.get_json()
    nome = data.get("nome", "").strip()
    sexo = data.get("sexo")
    categorias = data.get("categorias", ["mista"])

    if not nome or not sexo:
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

    salvar_jogadores(jogadores)
    return {"status": "ok"}


@app.route("/excluir_jogador", methods=["POST"])
def excluir_jogador():
    """API para excluir jogador"""
    try:
        data = request.get_json(force=True)
        nome = data.get("nome")

        if not nome:
            return jsonify({'status': 'erro', 'mensagem': 'Nome não fornecido'}), 400

        jogadores = carregar_jogadores()
        jogadores_filtrados = [j for j in jogadores if j["nome"] != nome]

        salvar_jogadores(jogadores_filtrados)
        return jsonify({'status': 'ok'})

    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500


# ============================================================================
# ROTAS - SISTEMA DE 5 RODADAS
# ============================================================================

@app.route("/gerar-rodadas", methods=["POST"])
def rota_gerar_rodadas():
    """Gera as 5 rodadas com duplas mistas"""
    jogadores = carregar_jogadores()
    confirmados = [j for j in jogadores if j.get("confirmado")]
    
    # Separa por gênero
    homens = [j["nome"] for j in confirmados if j["sexo"] == "M"]
    mulheres = [j["nome"] for j in confirmados if j["sexo"] == "F"]
    
    # Valida
    valido, mensagem = validar_participantes(homens, mulheres)
    if not valido:
        return jsonify({"erro": mensagem}), 400
    
    # Gera rodadas
    resultado = gerar_5_rodadas(homens, mulheres)
    
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"]}), 400
    
    # Adiciona metadados
    dados_completos = {
        "data_sorteio": datetime.now().isoformat(),
        "total_homens": len(homens),
        "total_mulheres": len(mulheres),
        "total_rodadas": resultado["total_rodadas"],
        "rodadas": resultado["rodadas"]
    }
    
    # Salva
    salvar_rodadas(dados_completos)
    
    # Inicializa ranking com jogadores confirmados (todos com 0)
    masculino = sorted([{
        "nome": nome,
        "vitorias": 0,
        "derrotas": 0,
        "percentual_vitorias": 0,
        "saldo_games": 0,
        "games_feitos": 0,
        "games_sofridos": 0
    } for nome in homens], key=lambda x: x["nome"])
    
    feminino = sorted([{
        "nome": nome,
        "vitorias": 0,
        "derrotas": 0,
        "percentual_vitorias": 0,
        "saldo_games": 0,
        "games_feitos": 0,
        "games_sofridos": 0
    } for nome in mulheres], key=lambda x: x["nome"])
    
    ranking_inicial = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "masculino": masculino,
        "feminino": feminino
    }
    salvar_ranking(ranking_inicial)
    
    return jsonify({"status": "ok", "total_rodadas": resultado["total_rodadas"]})


@app.route("/resetar-rodadas")
def rota_resetar_rodadas():
    """Remove as rodadas e ranking gerados"""
    if os.path.exists(RODADAS_FILE):
        os.remove(RODADAS_FILE)
    if os.path.exists(RANKING_FILE):
        os.remove(RANKING_FILE)
    
    return redirect(url_for("presenca"))


# ============================================================================
# ROTAS - REGISTRO DE RESULTADOS
# ============================================================================

@app.route("/registro-resultados")
def rota_registro_resultados():
    """Página para registrar resultados dos jogos"""
    dados_rodadas = carregar_rodadas()
    
    if not dados_rodadas:
        return redirect(url_for("presenca"))
    
    return render_template("registro_resultados.html", dados=dados_rodadas)


@app.route("/salvar-resultado", methods=["POST"])
def rota_salvar_resultado():
    """Salva o resultado de um confronto"""
    dados_rodadas = carregar_rodadas()
    
    if not dados_rodadas:
        return jsonify({"erro": "Rodadas não encontradas"}), 404
    
    # Extrai dados do formulário
    rodada_num = int(request.form.get("rodada"))
    confronto_idx = int(request.form.get("confronto"))
    games_d1 = int(request.form.get("games_dupla1"))
    games_d2 = int(request.form.get("games_dupla2"))
    
    # Valida o placar
    if games_d1 < 0 or games_d2 < 0:
        return jsonify({"erro": "Placar inválido"}), 400
    
    # Beach Tennis: mínimo de 6 games para ganhar (ou 7 no tiebreak)
    if games_d1 < 6 and games_d2 < 6:
        return jsonify({"erro": "Placar inválido. Mínimo de 6 games para vencer"}), 400
    
    # Atualiza o confronto
    rodada = dados_rodadas["rodadas"][rodada_num - 1]
    confronto = rodada["confrontos"][confronto_idx]
    
    confronto["resultado"]["games_dupla1"] = games_d1
    confronto["resultado"]["games_dupla2"] = games_d2
    confronto["resultado"]["finalizado"] = True
    
    # Salva rodadas atualizadas
    salvar_rodadas(dados_rodadas)
    
    # Recalcula o ranking
    ranking = calcular_ranking_individual(dados_rodadas["rodadas"])
    ranking_separado = separar_ranking_por_genero(ranking, carregar_jogadores())
    
    dados_ranking = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "masculino": ranking_separado["masculino"],
        "feminino": ranking_separado["feminino"]
    }
    
    salvar_ranking(dados_ranking)
    
    return jsonify({"status": "ok"})


# ============================================================================
# ROTAS - RANKING
# ============================================================================

@app.route("/ranking")
def rota_ranking_individual():
    """Exibe o ranking - suporta todas as categorias v3"""
    # Carrega rankings de todas as categorias que têm sorteio
    rankings_por_categoria = {}
    categorias_com_sorteio = []
    
    for cat in ["misto", "masculino", "feminino"]:
        rodadas_data = carregar_rodadas_categoria(cat)
        if rodadas_data:
            categorias_com_sorteio.append(cat)
            ranking_data = carregar_ranking_categoria(cat)
            if not ranking_data:
                ranking_data = calcular_ranking_categoria(cat)
                salvar_ranking_categoria(cat, ranking_data)
            rankings_por_categoria[cat] = ranking_data
    
    # Se há categorias v3, usa o template v3
    if categorias_com_sorteio:
        jogadores = carregar_jogadores()
        
        # Para categoria mista, separa ranking por gênero
        if "misto" in rankings_por_categoria:
            ranking_misto = rankings_por_categoria["misto"]
            ranking_separado = separar_ranking_por_genero(ranking_misto["ranking"], jogadores)
            rankings_por_categoria["misto_separado"] = ranking_separado
        
        return render_template(
            "ranking_todas_categorias.html",
            rankings_por_categoria=rankings_por_categoria,
            categorias_com_sorteio=categorias_com_sorteio
        )
    
    # Sistema antigo (compatibilidade)
    ranking = carregar_ranking()
    
    # Verifica se o ranking existe e tem dados
    tem_dados_ranking = ranking and ranking.get("masculino") and len(ranking.get("masculino", [])) > 0
    
    if not tem_dados_ranking:
        # Se não tem ranking ou está vazio, tenta gerar baseado nas rodadas
        dados_rodadas = carregar_rodadas()
        if dados_rodadas:
            ranking_calc = calcular_ranking_individual(dados_rodadas["rodadas"])
            ranking_sep = separar_ranking_por_genero(ranking_calc, carregar_jogadores())
            
            # Se o cálculo retornou dados, usa ele e salva
            if ranking_sep["masculino"] or ranking_sep["feminino"]:
                ranking = {
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "masculino": ranking_sep["masculino"],
                    "feminino": ranking_sep["feminino"]
                }
                salvar_ranking(ranking)  # Salva o ranking recalculado
            else:
                # Se não tem resultados ainda, mostra jogadores confirmados em ordem alfabética
                jogadores = carregar_jogadores()
                confirmados = [j for j in jogadores if j.get("confirmado")]
                
                masculino = sorted([{
                    "nome": j["nome"],
                    "vitorias": 0,
                    "derrotas": 0,
                    "percentual_vitorias": 0,
                    "saldo_games": 0,
                    "games_feitos": 0,
                    "games_sofridos": 0
                } for j in confirmados if j["sexo"] == "M"], key=lambda x: x["nome"])
                
                feminino = sorted([{
                    "nome": j["nome"],
                    "vitorias": 0,
                    "derrotas": 0,
                    "percentual_vitorias": 0,
                    "saldo_games": 0,
                    "games_feitos": 0,
                    "games_sofridos": 0
                } for j in confirmados if j["sexo"] == "F"], key=lambda x: x["nome"])
                
                ranking = {
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "masculino": masculino,
                    "feminino": feminino
                }
        else:
            # Se não tem rodadas ainda, mostra jogadores confirmados em ordem alfabética
            jogadores = carregar_jogadores()
            confirmados = [j for j in jogadores if j.get("confirmado")]
            
            masculino = sorted([{
                "nome": j["nome"],
                "vitorias": 0,
                "derrotas": 0,
                "percentual_vitorias": 0,
                "saldo_games": 0,
                "games_feitos": 0,
                "games_sofridos": 0
            } for j in confirmados if j["sexo"] == "M"], key=lambda x: x["nome"])
            
            feminino = sorted([{
                "nome": j["nome"],
                "vitorias": 0,
                "derrotas": 0,
                "percentual_vitorias": 0,
                "saldo_games": 0,
                "games_feitos": 0,
                "games_sofridos": 0
            } for j in confirmados if j["sexo"] == "F"], key=lambda x: x["nome"])
            
            ranking = {
                "ultima_atualizacao": datetime.now().isoformat(),
                "masculino": masculino,
                "feminino": feminino
            }
    
    return render_template("ranking_individual.html", ranking=ranking)


# Rota de redirecionamento para compatibilidade
@app.route("/ranking-individual")
def rota_ranking_individual_old():
    """Redirecionamento da URL antiga para a nova"""
    return redirect(url_for("rota_ranking_individual"))


# ============================================================================
# ROTAS - ADMINISTRAÇÃO
# ============================================================================

@app.route("/admin")
def admin():
    """Painel administrativo"""
    return render_template("admin.html")


@app.route("/admin/visitas")
def admin_visitas():
    """Estatísticas de visitas"""
    try:
        # Carrega visitantes únicos
        with open(VISITAS_FILE, "r", encoding="utf-8") as f:
            visitas_unicas = json.load(f)
        
        # Carrega logs detalhados
        try:
            with open(VISITAS_DETALHADAS_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        
        # Análise de dados
        from collections import Counter
        
        # Navegadores
        navegadores = Counter(log.get('navegador', 'Desconhecido') for log in logs)
        
        # Plataformas
        plataformas = Counter(log.get('plataforma', 'Desconhecido') for log in logs)
        
        # Páginas mais acessadas
        paginas = Counter(log.get('path', '/') for log in logs)
        
        # Referrers (origem do tráfego)
        referrers = Counter(
            log.get('referrer', '(acesso direto)') if log.get('referrer') else '(acesso direto)' 
            for log in logs
        )
        
        # Horários de acesso (por hora)
        horarios = Counter()
        for log in logs:
            timestamp = log.get('timestamp', '')
            if timestamp and len(timestamp) >= 13:
                hora = timestamp[11:13]  # Extrai a hora
                horarios[hora] += 1
        
        return render_template(
            "admin_visitas.html",
            total_unicos=len(visitas_unicas),
            total_acessos=len(logs),
            navegadores=dict(navegadores.most_common(10)),
            plataformas=dict(plataformas.most_common(10)),
            paginas=dict(paginas.most_common(10)),
            referrers=dict(referrers.most_common(10)),
            horarios=dict(sorted(horarios.items())),
            ultimos_logs=logs[-50:][::-1] if logs else []  # Últimos 50 em ordem reversa
        )
    except Exception as e:
        return f"Erro ao carregar estatísticas: {e}", 500


# ============================================================================
# ROTAS V3 - SISTEMA DE CATEGORIAS SEPARADAS
# ============================================================================

@app.route("/gerar-sorteio")
def rota_gerar_sorteio():
    """Página para gerar sorteio v3"""
    jogadores = carregar_jogadores()
    return render_template("gerar_sorteio.html", jogadores=jogadores)


@app.route("/api/analisar_categoria", methods=["POST"])
def api_analisar_categoria():
    """API para analisar viabilidade de uma categoria"""
    data = request.json
    categoria = data.get("categoria")
    
    jogadores = carregar_jogadores()
    
    if categoria == "misto":
        homens = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "M"]
        mulheres = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "F"]
        resultado = analisar_viabilidade_misto(homens, mulheres)
    else:
        if categoria == "masculino":
            participantes = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "M"]
        else:  # feminino
            participantes = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "F"]
        resultado = analisar_viabilidade_categoria(categoria, participantes)
    
    return jsonify(resultado)


@app.route("/api/gerar-sorteio", methods=["POST"])
def api_gerar_sorteio():
    """API para gerar sorteio v3"""
    data = request.json
    categoria = data.get("categoria")
    jogos_por_pessoa = data.get("jogos_por_pessoa")
    
    if not categoria or not jogos_por_pessoa:
        return jsonify({"erro": "Categoria e jogos_por_pessoa são obrigatórios"}), 400
    
    jogadores = carregar_jogadores()
    
    try:
        if categoria == "misto":
            # Valida viabilidade antes de gerar
            homens = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "M"]
            mulheres = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "F"]
            
            viabilidade = analisar_viabilidade_misto(homens, mulheres)
            opcoes_validas = [op["jogos_por_pessoa"] for op in viabilidade.get("opcoes", [])]
            
            if jogos_por_pessoa not in opcoes_validas:
                return jsonify({"erro": f"Jogos por pessoa ({jogos_por_pessoa}) não é viável para esta configuração"}), 400
            
            resultado = gerar_5_rodadas(homens, mulheres)
        else:
            # Valida viabilidade antes de gerar
            if categoria == "masculino":
                participantes = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "M"]
            else:  # feminino
                participantes = [j["nome"] for j in jogadores if j.get("confirmado") and j.get("sexo") == "F"]
            
            viabilidade = analisar_viabilidade_categoria(categoria, participantes)
            opcoes_validas = [op["jogos_por_pessoa"] for op in viabilidade.get("opcoes", [])]
            
            if jogos_por_pessoa not in opcoes_validas:
                return jsonify({"erro": f"Jogos por pessoa ({jogos_por_pessoa}) não é viável para esta configuração"}), 400
            
            resultado = gerar_sorteio_mesmo_genero_v2(participantes, jogos_por_pessoa)
        
        if "erro" in resultado:
            return jsonify(resultado), 400
        
        # Salva rodadas
        salvar_rodadas_categoria(categoria, resultado)
        
        # Calcula e salva ranking inicial
        ranking_data = calcular_ranking_categoria(categoria)
        salvar_ranking_categoria(categoria, ranking_data)
        
        return jsonify({"sucesso": True, "rodadas": resultado})
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/ranking/<categoria>")
def rota_ranking_categoria(categoria):
    """Ranking de uma categoria específica"""
    if categoria not in ["misto", "masculino", "feminino"]:
        return redirect(url_for("rota_ranking"))
    
    # Verifica se existe sorteio para esta categoria
    rodadas_data = carregar_rodadas_categoria(categoria)
    if not rodadas_data:
        return redirect(url_for("rota_ranking"))
    
    # Carrega ou calcula ranking
    ranking_data = carregar_ranking_categoria(categoria)
    if not ranking_data:
        ranking_data = calcular_ranking_categoria(categoria)
        salvar_ranking_categoria(categoria, ranking_data)
    
    # Lista categorias com sorteio para o seletor
    categorias_com_sorteio = []
    for cat in ["misto", "masculino", "feminino"]:
        if carregar_rodadas_categoria(cat):
            categorias_com_sorteio.append(cat)
    
    jogadores = carregar_jogadores()
    
    if categoria == "misto":
        # Separa ranking por gênero
        ranking_separado = separar_ranking_por_genero(ranking_data["ranking"], jogadores)
        return render_template(
            "ranking_v3.html",
            categoria=categoria,
            ranking=ranking_data,
            ranking_separado=ranking_separado,
            categorias_com_sorteio=categorias_com_sorteio
        )
    else:
        return render_template(
            "ranking_v3.html",
            categoria=categoria,
            ranking=ranking_data,
            categorias_com_sorteio=categorias_com_sorteio
        )


@app.route("/rodadas")
def rota_ver_rodadas():
    """Visualiza rodadas - suporta categoria via query param"""
    categoria = request.args.get("categoria", "misto")
    
    if categoria not in ["misto", "masculino", "feminino"]:
        categoria = "misto"
    
    rodadas_data = carregar_rodadas_categoria(categoria)
    
    if not rodadas_data:
        # Se não há rodadas para esta categoria, mostra todas as categorias disponíveis
        categorias_disponiveis = {}
        for cat in ["misto", "masculino", "feminino"]:
            rodadas_cat = carregar_rodadas_categoria(cat)
            if rodadas_cat:
                categorias_disponiveis[cat] = rodadas_cat
        
        return render_template(
            "rodadas.html",
            categorias_disponiveis=categorias_disponiveis,
            categoria_selecionada=None
        )
    
    return render_template(
        "rodadas.html",
        rodadas_data=rodadas_data,
        categoria=categoria,
        categoria_selecionada=categoria
    )


@app.route("/api/salvar-resultado", methods=["POST"])
def api_salvar_resultado():
    """API para salvar resultado de um confronto - suporta categoria"""
    data = request.json
    categoria = data.get("categoria", "misto")
    rodada_num = data.get("rodada_num")
    confronto_idx = data.get("confronto_idx")
    games_dupla1 = data.get("games_dupla1")
    games_dupla2 = data.get("games_dupla2")
    
    rodadas_data = carregar_rodadas_categoria(categoria)
    
    if not rodadas_data:
        return jsonify({"erro": "Rodadas não encontradas"}), 404
    
    try:
        rodada = rodadas_data["rodadas"][rodada_num - 1]
        confronto = rodada["confrontos"][confronto_idx]
        
        # Inicializa resultado se não existir
        if "resultado" not in confronto:
            confronto["resultado"] = {}
        
        confronto["resultado"]["games_dupla1"] = games_dupla1
        confronto["resultado"]["games_dupla2"] = games_dupla2
        confronto["resultado"]["finalizado"] = True
        
        salvar_rodadas_categoria(categoria, rodadas_data)
        
        # Recalcula ranking
        ranking_data = calcular_ranking_categoria(categoria)
        salvar_ranking_categoria(categoria, ranking_data)
        
        return jsonify({"sucesso": True})
    
    except (IndexError, KeyError) as e:
        return jsonify({"erro": f"Erro ao salvar resultado: {str(e)}"}), 400


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == "__main__":
    app.run(debug=True)
