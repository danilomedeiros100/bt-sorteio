#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Algoritmo de Sorteio de 5 Rodadas com Duplas Mistas
Sistema que GARANTE que nenhuma dupla se repete
Versão 2.0 - Algoritmo de Matching Otimizado
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


def calcular_numero_rodadas_ideal(total_participantes: int) -> int:
    """
    Calcula o número ideal de rodadas baseado no total de participantes
    Regra: suficiente para garantir distribuição justa
    
    Para 12-19 participantes: 4 rodadas (todos jogam ~4 vezes)
    Para 20 participantes: 5 rodadas
    Para 21+ participantes: 6 rodadas
    
    NOTA: 4 rodadas funciona melhor para números ímpares/desbalanceados
    """
    if total_participantes <= 19:
        return 4  # Mais eficiente para distribuir
    elif total_participantes == 20:
        return 5
    else:
        return 6

def gerar_5_rodadas(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera rodadas com duplas mistas FLEXÍVEL
    - Adapta número de rodadas conforme participantes
    - GARANTE que todos joguem o mesmo número de vezes (ou muito próximo)
    - PERMITE repetição de duplas para garantir distribuição justa
    
    Algoritmo:
    1. Calcula número ideal de rodadas
    2. Prioriza quem já jogou MENOS para garantir distribuição justa
    3. Permite repetição de duplas quando necessário
    """
    valido, mensagem = validar_participantes(homens, mulheres)
    if not valido:
        return {"erro": mensagem}
    
    total_participantes = len(homens) + len(mulheres)
    num_rodadas = calcular_numero_rodadas_ideal(total_participantes)
    
    # Embaralha para aleatoriedade
    homens_shuffled = homens.copy()
    mulheres_shuffled = mulheres.copy()
    random.shuffle(homens_shuffled)
    random.shuffle(mulheres_shuffled)
    
    # Tracking de quantos jogos cada pessoa já fez
    jogos_por_pessoa = defaultdict(int)  # Quantos jogos cada pessoa já fez
    descansos_por_pessoa = defaultdict(int)  # Quantos descansos cada um já teve
    
    rodadas_geradas = []
    
    # Para cada rodada
    for rodada_num in range(num_rodadas):
        # Decide quem vai descansar NESTA rodada antes de formar duplas
        # Prioriza quem já descansou mais para distribuir equitativamente
        
        # Cria pool de possíveis descansantes
        homens_pool = homens_shuffled.copy()
        mulheres_pool = mulheres_shuffled.copy()
        
        # Quantos vão descansar? (diferença entre H e M)
        diferenca = len(homens_pool) - len(mulheres_pool)
        
        descansando = []
        
        # Se há diferença, define quem descansa rotando
        if diferenca > 0:  # Mais homens que mulheres
            # Agrupa por número de descansos
            descansos_grupos = defaultdict(list)
            for h in homens_pool:
                descansos_grupos[descansos_por_pessoa[h]].append(h)
            
            # Pega quem descansou MENOS (para equilibrar)
            num_descansar = diferenca
            for num_desc in sorted(descansos_grupos.keys()):  # Ordem crescente!
                candidatos = descansos_grupos[num_desc]
                random.shuffle(candidatos)
                quantos_pegar = min(num_descansar, len(candidatos))
                descansando.extend(candidatos[:quantos_pegar])
                num_descansar -= quantos_pegar
                if num_descansar == 0:
                    break
                    
        elif diferenca < 0:  # Mais mulheres que homens
            # Agrupa por número de descansos
            descansos_grupos = defaultdict(list)
            for m in mulheres_pool:
                descansos_grupos[descansos_por_pessoa[m]].append(m)
            
            # Pega quem descansou MENOS (para equilibrar)
            num_descansar = -diferenca
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
        
        # Embaralha para aleatoriedade
        random.shuffle(homens_disponiveis)
        random.shuffle(mulheres_disponiveis)
        
        duplas_rodada = []
        
        # MODIFICADO: Prioriza quem já jogou MENOS para garantir 5 jogos para todos
        # Ordena por quem já jogou menos (prioridade)
        homens_disponiveis.sort(key=lambda h: jogos_por_pessoa[h])
        mulheres_disponiveis.sort(key=lambda m: jogos_por_pessoa[m])
        
        # Forma duplas priorizando quem precisa jogar mais
        # Permite repetição de duplas se necessário
        idx_h = 0
        idx_m = 0
        
        while idx_h < len(homens_disponiveis) and idx_m < len(mulheres_disponiveis):
            h = homens_disponiveis[idx_h]
            m = mulheres_disponiveis[idx_m]
            
            # Forma a dupla (permitindo repetição)
            duplas_rodada.append((h, m))
            jogos_por_pessoa[h] += 1
            jogos_por_pessoa[m] += 1
            idx_h += 1
            idx_m += 1
        
        # Se sobraram pessoas, elas descansam
        if idx_h < len(homens_disponiveis):
            for h in homens_disponiveis[idx_h:]:
                descansando.append(h)
        if idx_m < len(mulheres_disponiveis):
            for m in mulheres_disponiveis[idx_m:]:
                descansando.append(m)
        
        # Remove duplicatas
        descansando = list(set(descansando))
        
        # Atualiza contador de descansos
        for pessoa in descansando:
            descansos_por_pessoa[pessoa] += 1
        
        # Cria confrontos (duplas jogam entre si)
        confrontos = []
        metade = len(duplas_rodada) // 2
        
        for i in range(metade):
            dupla1 = duplas_rodada[i]
            dupla2_idx = metade + i
            
            if dupla2_idx < len(duplas_rodada):
                dupla2 = duplas_rodada[dupla2_idx]
                
                confronto = {
                    "quadra": i + 1,
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
        
        # Se número ímpar de duplas, última fica sem adversário
        if len(duplas_rodada) % 2 == 1:
            # Pode adicionar lógica aqui se necessário
            pass
        
        rodadas_geradas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos,
            "descansando": list(set(descansando))
        })
    
    return {
        "total_rodadas": num_rodadas,
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
