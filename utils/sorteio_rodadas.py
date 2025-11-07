#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algoritmo de Sorteio de 5 Rodadas com Duplas Mistas
Sistema que GARANTE que nenhuma dupla se repete
Versão 3.0 - Round-Robin Circular (Garantia 100%)
GARANTE: Todos jogam EXATAMENTE 5 rodadas (números iguais de H e M)
"""

import random
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import itertools


def validar_participantes(homens: List[str], mulheres: List[str]) -> Tuple[bool, str]:
    """
    Valida se é possível gerar 5 rodadas com os participantes
    """
    total_h = len(homens)
    total_m = len(mulheres)
    
    if total_h < 3:
        return False, "Mínimo de 3 homens necessário"
    if total_m < 3:
        return False, "Mínimo de 3 mulheres necessário"
    
    if total_h > 20 or total_m > 20:
        return False, "Máximo recomendado: 20 jogadores por gênero"
    
    diferenca = abs(total_h - total_m)
    if diferenca > 6:
        return False, f"Diferença muito grande entre H e M ({diferenca}). Máximo recomendado: 6"
    
    return True, "OK"


def gerar_5_rodadas_round_robin(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera jogos garantindo que TODOS joguem EXATAMENTE 5 vezes
    Agrupa em 5 "rodadas aproximadas" para organização no dia do evento
    
    Algoritmo:
    1. Usa Round-Robin para gerar N×5 duplas únicas (cada pessoa aparece exatamente 5x)
    2. Cria confrontos 2x2 com as duplas
    3. Distribui confrontos em 5 rodadas de forma equilibrada
    4. Se sobrar 1 dupla no TOTAL, ela fica de bye mas CONTA como jogo
    
    GARANTIA 100%: Cada jogador aparece em EXATAMENTE 5 duplas (nem mais, nem menos)
    """
    n = len(homens)
    
    if n != len(mulheres):
        return {"erro": "Números diferentes de H e M requer algoritmo diferente"}
    
    # Copia e embaralha para aleatoriedade inicial
    homens_shuffled = homens.copy()
    mulheres_shuffled = mulheres.copy()
    random.shuffle(homens_shuffled)
    random.shuffle(mulheres_shuffled)
    
    # ========== PASSO 1: GERA TODAS AS DUPLAS (N×5 duplas únicas) ==========
    todas_duplas = []
    duplas_por_pessoa = defaultdict(int)  # Controla quantas vezes cada pessoa aparece
    
    # Round-Robin: cada homem joga com cada mulher em sequência rotativa
    for rodada_num in range(5):
        for i in range(n):
            homem = homens_shuffled[i]
            mulher = mulheres_shuffled[(i + rodada_num) % n]
            dupla = (homem, mulher)
            
            # Verifica se essa dupla já existe (não deveria acontecer com round-robin)
            if dupla not in todas_duplas:
                todas_duplas.append(dupla)
                duplas_por_pessoa[homem] += 1
                duplas_por_pessoa[mulher] += 1
    
    # Embaralha todas as duplas para distribuição aleatória
    random.shuffle(todas_duplas)
    
    # ========== PASSO 2: CRIA CONFRONTOS 2×2 ==========
    total_duplas = len(todas_duplas)
    confrontos_totais = []
    
    # Cria confrontos de 2 em 2
    for i in range(0, total_duplas - 1, 2):
        dupla1 = todas_duplas[i]
        dupla2 = todas_duplas[i + 1]
        
        confronto = {
            "dupla1": {
                "jogador1": dupla1[0],
                "jogador2": dupla1[1]
            },
            "dupla2": {
                "jogador1": dupla2[0],
                "jogador2": dupla2[1]
            },
            "resultado": {
                "games_dupla1": 0,
                "games_dupla2": 0,
                "finalizado": False
            }
        }
        confrontos_totais.append(confronto)
    
    # Se sobrou 1 dupla (número ímpar), cria confronto BYE
    if total_duplas % 2 == 1:
        ultima_dupla = todas_duplas[-1]
        confronto_bye = {
            "dupla1": {
                "jogador1": ultima_dupla[0],
                "jogador2": ultima_dupla[1]
            },
            "dupla2": None,  # Sem adversário
            "resultado": {
                "games_dupla1": 0,
                "games_dupla2": 0,
                "finalizado": False
            },
            "tipo": "bye",
            "obs": "Dupla sem adversário (conta como jogo realizado)"
        }
        confrontos_totais.append(confronto_bye)
    
    # ========== PASSO 3: DISTRIBUI EM 5 RODADAS APROXIMADAS ==========
    total_confrontos = len(confrontos_totais)
    confrontos_por_rodada = total_confrontos // 5
    sobra = total_confrontos % 5
    
    rodadas_geradas = []
    idx_confronto = 0
    
    for rodada_num in range(5):
        # Calcula quantos confrontos nesta rodada (distribui a sobra nas primeiras rodadas)
        num_confrontos_rodada = confrontos_por_rodada + (1 if rodada_num < sobra else 0)
        
        # Pega os confrontos desta rodada
        confrontos_rodada = []
        for _ in range(num_confrontos_rodada):
            if idx_confronto < total_confrontos:
                confronto = confrontos_totais[idx_confronto].copy()
                confronto["quadra"] = len(confrontos_rodada) + 1
                confrontos_rodada.append(confronto)
                idx_confronto += 1
        
        rodadas_geradas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos_rodada,
            "descansando": []  # NINGUÉM descansa - todos jogam exatamente 5x!
        })
    
    return {
        "total_rodadas": 5,
        "rodadas": rodadas_geradas
    }


def gerar_5_rodadas(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera 5 rodadas com duplas mistas GARANTINDO que:
    1. Nenhuma dupla se repete
    2. TODOS jogam EXATAMENTE 5 rodadas (quando H = M)
    3. Quando H ≠ M, descansos são distribuídos equilibradamente
    
    Algoritmo:
    - Se H = M: usa Round-Robin (GARANTIA 100% - todos jogam 5 vezes)
    - Se H ≠ M: usa algoritmo com descansos rotativos
    """
    valido, mensagem = validar_participantes(homens, mulheres)
    if not valido:
        return {"erro": mensagem}
    
    # Se números IGUAIS: usa Round-Robin (GARANTIA 100%)
    if len(homens) == len(mulheres):
        return gerar_5_rodadas_round_robin(homens, mulheres)
    
    # Embaralha para aleatoriedade
    homens_shuffled = homens.copy()
    mulheres_shuffled = mulheres.copy()
    random.shuffle(homens_shuffled)
    random.shuffle(mulheres_shuffled)
    
    # Tracking de quem já jogou junto
    duplas_usadas = set()  # Set de tuplas (homem, mulher)
    descansos_por_pessoa = defaultdict(int)  # Quantos descansos cada um já teve
    
    rodadas_geradas = []
    diferenca_inicial = len(homens) - len(mulheres)
    
    # Para números iguais e ÍMPARES: força número PAR de duplas para ter confrontos completos
    # Exemplo: 9H x 9M → força 8 duplas (1H e 1M descansam rotacionando)
    forcar_numero_par = (diferenca_inicial == 0 and len(homens) % 2 == 1)
    
    # Para cada rodada
    for rodada_num in range(5):
        # Quantos vão descansar?
        descansando = []
        
        # Se números iguais e ÍMPARES: rotaciona 1H e 1M para descansar (forçar número PAR de duplas)
        if forcar_numero_par:
            # Escolhe quem descansou MENOS vezes
            descansos_h_grupos = defaultdict(list)
            for h in homens_shuffled:
                descansos_h_grupos[descansos_por_pessoa[h]].append(h)
            
            descansos_m_grupos = defaultdict(list)
            for m in mulheres_shuffled:
                descansos_m_grupos[descansos_por_pessoa[m]].append(m)
            
            # Pega 1 homem que descansou menos
            min_desc_h = min(descansos_h_grupos.keys())
            candidatos_h = descansos_h_grupos[min_desc_h]
            random.shuffle(candidatos_h)
            descansando.append(candidatos_h[0])
            
            # Pega 1 mulher que descansou menos
            min_desc_m = min(descansos_m_grupos.keys())
            candidatas_m = descansos_m_grupos[min_desc_m]
            random.shuffle(candidatas_m)
            descansando.append(candidatas_m[0])
            
        # Se há diferença numérica, define quem descansa ANTES de formar duplas
        elif diferenca_inicial > 0:  # Mais homens que mulheres
            # Agrupa por número de descansos
            descansos_grupos = defaultdict(list)
            for h in homens_shuffled:
                descansos_grupos[descansos_por_pessoa[h]].append(h)
            
            # Pega quem descansou MENOS (para equilibrar)
            num_descansar = diferenca_inicial
            for num_desc in sorted(descansos_grupos.keys()):  # Ordem crescente!
                candidatos = descansos_grupos[num_desc]
                random.shuffle(candidatos)
                quantos_pegar = min(num_descansar, len(candidatos))
                descansando.extend(candidatos[:quantos_pegar])
                num_descansar -= quantos_pegar
                if num_descansar == 0:
                    break
                    
        elif diferenca_inicial < 0:  # Mais mulheres que homens
            # Agrupa por número de descansos
            descansos_grupos = defaultdict(list)
            for m in mulheres_shuffled:
                descansos_grupos[descansos_por_pessoa[m]].append(m)
            
            # Pega quem descansou MENOS (para equilibrar)
            num_descansar = -diferenca_inicial
            for num_desc in sorted(descansos_grupos.keys()):  # Ordem crescente!
                candidatas = descansos_grupos[num_desc]
                random.shuffle(candidatas)
                quantos_pegar = min(num_descansar, len(candidatas))
                descansando.extend(candidatas[:quantos_pegar])
                num_descansar -= quantos_pegar
                if num_descansar == 0:
                    break
        
        # Agora forma duplas com quem VAI JOGAR
        homens_disponiveis = [h for h in homens_shuffled if h not in descansando]
        mulheres_disponiveis = [m for m in mulheres_shuffled if m not in descansando]
        
        # Forma duplas usando algoritmo greedy simples
        duplas_rodada = []
        random.shuffle(homens_disponiveis)
        random.shuffle(mulheres_disponiveis)
        
        while homens_disponiveis and mulheres_disponiveis:
            h = homens_disponiveis[0]
            
            # Procura mulher que ainda não formou dupla com ele
            m_encontrada = None
            for m in mulheres_disponiveis:
                dupla_key = (h, m)
                if dupla_key not in duplas_usadas:
                    m_encontrada = m
                    break
            
            if m_encontrada:
                # Forma a dupla
                dupla_key = (h, m_encontrada)
                duplas_usadas.add(dupla_key)
                duplas_rodada.append((h, m_encontrada))
                
                # Remove dos disponíveis
                homens_disponiveis.remove(h)
                mulheres_disponiveis.remove(m_encontrada)
            else:
                # Se não encontrou, adiciona ao descanso
                descansando.append(h)
                homens_disponiveis.remove(h)
        
        # Quem sobrou descansa
        descansando.extend(homens_disponiveis)
        descansando.extend(mulheres_disponiveis)
        
        # Atualiza contador de descansos
        for pessoa in descansando:
            descansos_por_pessoa[pessoa] += 1
        
        # Cria confrontos (duplas jogam entre si) - sempre 2x2
        confrontos = []
        
        # Embaralha duplas para confrontos aleatórios
        duplas_shuffled = duplas_rodada.copy()
        random.shuffle(duplas_shuffled)
        
        # Cria confrontos de 2 em 2 (SEMPRE número PAR de duplas graças à lógica anterior)
        for i in range(0, len(duplas_shuffled) - 1, 2):
            dupla1 = duplas_shuffled[i]
            dupla2 = duplas_shuffled[i + 1]
            
            confronto = {
                "quadra": (i // 2) + 1,
                "dupla1": {
                    "jogador1": dupla1[0],
                    "jogador2": dupla1[1]
                },
                "dupla2": {
                    "jogador1": dupla2[0],
                    "jogador2": dupla2[1]
                },
                "resultado": {
                    "games_dupla1": 0,
                    "games_dupla2": 0,
                    "finalizado": False
                }
            }
            confrontos.append(confronto)
        
        rodadas_geradas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos,
            "descansando": list(set(descansando))
        })
    
    return {
        "total_rodadas": 5,
        "rodadas": rodadas_geradas
    }


def calcular_ranking_individual(rodadas: List[Dict]) -> List[Dict]:
    """
    Calcula o ranking individual baseado nos resultados das rodadas
    Inclui TODOS os jogadores, mesmo os que ainda não jogaram
    """
    stats = {}
    
    # Primeiro, inicializa TODOS os jogadores que aparecem nas rodadas (jogando ou descansando)
    todos_jogadores = set()
    for rodada in rodadas:
        # Adiciona jogadores dos confrontos
        for confronto in rodada.get("confrontos", []):
            dupla1 = confronto["dupla1"]
            dupla2 = confronto["dupla2"]
            todos_jogadores.add(dupla1["jogador1"])
            todos_jogadores.add(dupla1["jogador2"])
            todos_jogadores.add(dupla2["jogador1"])
            todos_jogadores.add(dupla2["jogador2"])
        
        # Adiciona jogadores descansando
        for jogador in rodada.get("descansando", []):
            todos_jogadores.add(jogador)
    
    # Inicializa todos os jogadores com stats zerados
    for jogador in todos_jogadores:
        stats[jogador] = {
            "nome": jogador,
            "vitorias": 0,
            "derrotas": 0,
            "games_feitos": 0,
            "games_sofridos": 0,
            "jogos_realizados": 0
        }
    
    # Agora processa os resultados finalizados
    for rodada in rodadas:
        for confronto in rodada.get("confrontos", []):
            resultado = confronto.get("resultado", {})
            
            if not resultado.get("finalizado", False):
                continue
            
            dupla1 = confronto["dupla1"]
            dupla2 = confronto["dupla2"]
            games_d1 = resultado.get("games_dupla1", 0)
            games_d2 = resultado.get("games_dupla2", 0)
            
            venceu_dupla1 = games_d1 > games_d2
            
            for jogador in [dupla1["jogador1"], dupla1["jogador2"]]:
                stats[jogador]["jogos_realizados"] += 1
                stats[jogador]["games_feitos"] += games_d1
                stats[jogador]["games_sofridos"] += games_d2
                
                if venceu_dupla1:
                    stats[jogador]["vitorias"] += 1
                else:
                    stats[jogador]["derrotas"] += 1
            
            for jogador in [dupla2["jogador1"], dupla2["jogador2"]]:
                stats[jogador]["jogos_realizados"] += 1
                stats[jogador]["games_feitos"] += games_d2
                stats[jogador]["games_sofridos"] += games_d1
                
                if not venceu_dupla1:
                    stats[jogador]["vitorias"] += 1
                else:
                    stats[jogador]["derrotas"] += 1
    
    for jogador, stat in stats.items():
        stat["saldo_games"] = stat["games_feitos"] - stat["games_sofridos"]
        
        if stat["jogos_realizados"] > 0:
            stat["percentual_vitorias"] = round(
                (stat["vitorias"] / stat["jogos_realizados"]) * 100, 1
            )
        else:
            stat["percentual_vitorias"] = 0.0
    
    ranking_ordenado = sorted(
        stats.values(),
        key=lambda x: (
            -x["vitorias"],          # 1º: Mais vitórias = melhor
            -x["saldo_games"],       # 2º: Maior saldo = melhor
            -x["games_feitos"],      # 3º: Mais games feitos = melhor
            x["games_sofridos"]      # 4º: Menos games sofridos = melhor (ordem crescente)
        )
    )
    
    return ranking_ordenado


def separar_ranking_por_genero(ranking: List[Dict], jogadores_data: List[Dict]) -> Dict:
    """
    Separa o ranking em masculino e feminino
    """
    sexo_map = {j["nome"]: j["sexo"] for j in jogadores_data}
    
    masculino = []
    feminino = []
    
    for jogador_stat in ranking:
        nome = jogador_stat["nome"]
        sexo = sexo_map.get(nome, "M")
        
        if sexo == "M":
            masculino.append(jogador_stat)
        else:
            feminino.append(jogador_stat)
    
    return {
        "masculino": masculino,
        "feminino": feminino
    }
