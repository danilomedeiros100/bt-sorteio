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
    separar_ranking_por_genero
)

app = Flask(__name__)

# Arquivos de dados
DATA_FILE = os.path.join("data", "jogadores.json")
RODADAS_FILE = "data/rodadas.json"
RANKING_FILE = "data/ranking.json"
VISITAS_FILE = "data/visitas.json"
VISITAS_DETALHADAS_FILE = "data/visitas_detalhadas.json"


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


@app.route("/rodadas")
def rota_ver_rodadas():
    """Visualiza todas as rodadas geradas"""
    dados_rodadas = carregar_rodadas()
    
    if not dados_rodadas:
        return render_template("rodadas.html", rodadas=None)
    
    return render_template("rodadas.html", rodadas=dados_rodadas)


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
    """Exibe o ranking"""
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
# INICIALIZAÇÃO
# ============================================================================

if __name__ == "__main__":
    app.run(debug=True)
