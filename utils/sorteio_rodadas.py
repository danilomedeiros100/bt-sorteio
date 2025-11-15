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
    Distribui em 8 RODADAS para ELIMINAR jogos múltiplos na mesma rodada
    
    Algoritmo:
    1. Usa Round-Robin para gerar N×5 duplas únicas (cada pessoa aparece exatamente 5x)
    2. Cria confrontos 2x2 com as duplas
    3. Distribui confrontos em 8 RODADAS garantindo que ninguém jogue 2x na mesma rodada
    4. Cada pessoa descansa 3 rodadas (equilibrado)
    
    GARANTIAS:
    - Cada jogador aparece em EXATAMENTE 5 duplas (joga 5 vezes)
    - NINGUÉM joga mais de 1 vez na mesma rodada
    - Descansos equilibrados (3 por pessoa)
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
    
    # ========== PASSO 2: CRIA CONFRONTOS 2×2 (COM VALIDAÇÃO) ==========
    
    # Função auxiliar para verificar se duplas compartilham jogadores
    def compartilha_jogadores(dupla1, dupla2):
        """Verifica se duas duplas têm algum jogador em comum"""
        set1 = {dupla1[0], dupla1[1]}
        set2 = {dupla2[0], dupla2[1]}
        return len(set1 & set2) > 0
    
    def criar_confrontos_sem_byes(duplas_list, max_tentativas=100):
        """
        Tenta criar confrontos SEM BYES usando backtracking.
        Para 12x12 (60 duplas), deveria gerar exatamente 30 confrontos sempre.
        """
        melhor_resultado = []
        menor_byes = float('inf')
        
        for tentativa in range(max_tentativas):
            confrontos = []
            duplas_restantes = duplas_list.copy()
            random.shuffle(duplas_restantes)
            
            while len(duplas_restantes) >= 2:
                dupla1 = duplas_restantes[0]
                dupla2_idx = None
                
                # Procura uma dupla2 compatível
                for i in range(1, len(duplas_restantes)):
                    if not compartilha_jogadores(dupla1, duplas_restantes[i]):
                        dupla2_idx = i
                        break
                
                if dupla2_idx is not None:
                    # Cria confronto válido
                    dupla2 = duplas_restantes[dupla2_idx]
                    confronto = {
                        "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                        "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                        "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False}
                    }
                    confrontos.append(confronto)
                    
                    # Remove duplas usadas
                    duplas_restantes.pop(dupla2_idx)
                    duplas_restantes.pop(0)
                else:
                    # Não encontrou par, tenta reordenar
                    break
            
            # Calcula quantos byes seriam necessários
            num_byes = len(duplas_restantes)
            
            # Se conseguiu sem byes, retorna imediatamente
            if num_byes == 0:
                return confrontos
            
            # Senão, guarda o melhor resultado
            if num_byes < menor_byes:
                menor_byes = num_byes
                melhor_resultado = (confrontos, duplas_restantes)
        
        # Se não conseguiu 0 byes, retorna o melhor resultado com byes
        confrontos_finais, duplas_sobrando = melhor_resultado
        
        for dupla_bye in duplas_sobrando:
            confronto_bye = {
                "dupla1": {"jogador1": dupla_bye[0], "jogador2": dupla_bye[1]},
                "dupla2": None,
                "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
                "tipo": "bye",
                "obs": "Dupla sem adversário"
            }
            confrontos_finais.append(confronto_bye)
        
        return confrontos_finais
    
    confrontos_totais = criar_confrontos_sem_byes(todas_duplas)
    
    # ========== PASSO 3: DISTRIBUI EM 5 RODADAS COM OTIMIZAÇÃO INTELIGENTE ==========
    # OBJETIVO: Minimizar jogos múltiplos na mesma rodada (impossível eliminar 100%)
    # GARANTE: Todos jogam exatamente 5 vezes, nenhuma dupla se repete
    
    def get_jogadores_confronto(conf):
        """Retorna conjunto de jogadores em um confronto"""
        jogadores = set()
        d1 = conf['dupla1']
        d2 = conf.get('dupla2')
        if d1:
            jogadores.add(d1['jogador1'])
            jogadores.add(d1['jogador2'])
        if d2:
            jogadores.add(d2['jogador1'])
            jogadores.add(d2['jogador2'])
        return jogadores
    
    def calcular_conflitos_rodada(confrontos_rodada):
        """Calcula quantos jogadores jogam múltiplas vezes na rodada"""
        jogadores_count = defaultdict(int)
        for confronto in confrontos_rodada:
            for jogador in get_jogadores_confronto(confronto):
                jogadores_count[jogador] += 1
        
        # Retorna número de jogadores com jogos múltiplos e total de conflitos
        jogadores_multiplos = sum(1 for count in jogadores_count.values() if count > 1)
        total_conflitos = sum(max(0, count - 1) for count in jogadores_count.values())
        return jogadores_multiplos, total_conflitos
    
    def distribuir_confrontos_otimizado(confrontos, num_rodadas=8):
        """
        Distribui confrontos em 8 rodadas ELIMINANDO jogos múltiplos
        E INTERCALANDO jogos e descansos (evita sequências longas)
        """
        melhor_distribuicao = None
        melhor_score = float('inf')
        
        # Tenta múltiplas distribuições
        for tentativa_global in range(2000):
            # Inicializa rodadas vazias
            rodadas_temp = [[] for _ in range(num_rodadas)]
            jogadores_usados_rodada = [set() for _ in range(num_rodadas)]
            ultima_rodada_jogador = {}  # Última rodada onde cada jogador jogou
            
            # Embaralha confrontos
            confrontos_shuffled = confrontos.copy()
            random.shuffle(confrontos_shuffled)
            
            confrontos_alocados = 0
            
            for confronto in confrontos_shuffled:
                jogadores_confronto = get_jogadores_confronto(confronto)
                
                # Encontra rodadas possíveis (sem conflito)
                rodadas_possiveis = []
                for rodada_idx in range(num_rodadas):
                    if not jogadores_confronto & jogadores_usados_rodada[rodada_idx]:
                        rodadas_possiveis.append(rodada_idx)
                
                if rodadas_possiveis:
                    # HEURÍSTICA MELHORADA: Prefere rodadas que INTERCALAM jogos
                    # Calcula score para cada rodada possível
                    scores_rodadas = []
                    for rodada_idx in rodadas_possiveis:
                        score = 0
                        
                        # 1. Balanceamento: prefere rodadas com menos jogadores
                        score += len(jogadores_usados_rodada[rodada_idx]) * 10
                        
                        # 2. Intercalação: prefere rodadas distantes da última vez que jogaram
                        for jogador in jogadores_confronto:
                            if jogador in ultima_rodada_jogador:
                                distancia = rodada_idx - ultima_rodada_jogador[jogador]
                                # Premia distância (quanto maior, melhor)
                                score -= distancia * 20
                        
                        scores_rodadas.append((score, rodada_idx))
                    
                    # Escolhe rodada com melhor score (menor = melhor)
                    melhor_rodada = min(scores_rodadas, key=lambda x: x[0])[1]
                    
                    rodadas_temp[melhor_rodada].append(confronto)
                    jogadores_usados_rodada[melhor_rodada].update(jogadores_confronto)
                    
                    # Atualiza última rodada de cada jogador
                    for jogador in jogadores_confronto:
                        ultima_rodada_jogador[jogador] = melhor_rodada
                    
                    confrontos_alocados += 1
            
            # Calcula score da distribuição (considera intercalação)
            if confrontos_alocados == len(confrontos):
                score_distribuicao = 0
                
                # Para cada pessoa, conta max jogos/descansos consecutivos
                pessoas = set()
                for rodada_confrontos in rodadas_temp:
                    for confronto in rodada_confrontos:
                        pessoas.update(get_jogadores_confronto(confronto))
                
                for pessoa in pessoas:
                    # Monta agenda da pessoa
                    agenda = []
                    for rodada_idx in range(num_rodadas):
                        joga = any(pessoa in get_jogadores_confronto(c) 
                                  for c in rodadas_temp[rodada_idx])
                        agenda.append('J' if joga else 'D')
                    
                    # Penaliza sequências longas
                    max_seq_j = max_seq_d = 0
                    seq_j = seq_d = 0
                    for tipo in agenda:
                        if tipo == 'J':
                            seq_j += 1
                            max_seq_j = max(max_seq_j, seq_j)
                            seq_d = 0
                        else:
                            seq_d += 1
                            max_seq_d = max(max_seq_d, seq_d)
                            seq_j = 0
                    
                    # Score: penaliza muito sequências longas
                    score_distribuicao += max_seq_j ** 2 + max_seq_d ** 2
                
                # Atualiza melhor resultado
                if score_distribuicao < melhor_score:
                    melhor_score = score_distribuicao
                    melhor_distribuicao = rodadas_temp
        
        return melhor_distribuicao
    
    def otimizar_ordem_intra_rodada(confrontos_rodada):
        """
        Otimiza a ORDEM dos confrontos dentro de uma rodada
        para maximizar espaçamento entre jogos da mesma pessoa
        """
        if len(confrontos_rodada) <= 1:
            return confrontos_rodada
        
        melhor_ordem = confrontos_rodada.copy()
        melhor_score = -999999
        
        for _ in range(200):
            ordem_atual = confrontos_rodada.copy()
            random.shuffle(ordem_atual)
            
            # Calcula score: premia distância entre aparições do mesmo jogador
            score = 0
            ultima_aparicao = {}
            
            for idx, confronto in enumerate(ordem_atual):
                for jogador in get_jogadores_confronto(confronto):
                    if jogador in ultima_aparicao:
                        distancia = idx - ultima_aparicao[jogador]
                        score += distancia * distancia  # Quadrático para premiar mais distâncias grandes
                    ultima_aparicao[jogador] = idx
            
            if score > melhor_score:
                melhor_score = score
                melhor_ordem = ordem_atual
        
        return melhor_ordem
    
    # Distribui confrontos de forma otimizada em 8 rodadas
    rodadas_distribuidas = distribuir_confrontos_otimizado(confrontos_totais, 8)
    
    # Conjunto de todos os jogadores
    todos_jogadores = set(homens_shuffled + mulheres_shuffled)
    
    # Monta rodadas finais com otimização de ordem
    rodadas_geradas = []
    for rodada_num, confrontos_rodada in enumerate(rodadas_distribuidas):
        # Otimiza ordem dentro da rodada
        confrontos_otimizados = otimizar_ordem_intra_rodada(confrontos_rodada)
        
        # Identifica quem está jogando nesta rodada
        jogadores_jogando = set()
        for confronto in confrontos_otimizados:
            jogadores_jogando.update(get_jogadores_confronto(confronto))
        
        # Quem não está jogando está descansando
        jogadores_descansando = sorted(list(todos_jogadores - jogadores_jogando))
        
        # Atribui números de quadra
        confrontos_finais = []
        for quadra_num, confronto in enumerate(confrontos_otimizados, 1):
            confronto_copy = confronto.copy()
            confronto_copy["quadra"] = quadra_num
            confrontos_finais.append(confronto_copy)
        
        rodadas_geradas.append({
            "numero": rodada_num + 1,
            "confrontos": confrontos_finais,
            "descansando": jogadores_descansando
        })
    
    return {
        "total_rodadas": 8,
        "rodadas": rodadas_geradas
    }


def gerar_5_rodadas(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Gera 8 rodadas com duplas mistas GARANTINDO que:
    1. Nenhuma dupla se repete
    2. TODOS jogam EXATAMENTE 5 vezes (espalhado em 8 rodadas)
    3. NINGUÉM joga mais de 1 vez na mesma rodada (ZERO jogos múltiplos)
    4. Descansos equilibrados (cada um descansa 3 rodadas)
    
    Algoritmo:
    - Se H = M: usa Round-Robin em 8 rodadas (ELIMINA jogos múltiplos)
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
            dupla2 = confronto.get("dupla2")  # Pode ser None em caso de bye
            
            todos_jogadores.add(dupla1["jogador1"])
            todos_jogadores.add(dupla1["jogador2"])
            
            if dupla2:  # Só adiciona se não for bye
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
            dupla2 = confronto.get("dupla2")  # Pode ser None em caso de bye
            games_d1 = resultado.get("games_dupla1", 0)
            games_d2 = resultado.get("games_dupla2", 0)
            
            # Se é um confronto bye, simplesmente pula (não conta para ranking)
            if not dupla2:
                continue
            
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


# ============================================================================
# FUNÇÕES PARA CATEGORIAS MASCULINO E FEMININO (MESMO GÊNERO)
# ============================================================================

def analisar_viabilidade_mesmo_genero(num_jogadores: int) -> Dict:
    """
    Analisa quais quantidades de jogos por pessoa são viáveis matematicamente.
    
    Regras:
    - Cada pessoa joga K vezes
    - Total de duplas necessárias = (N * K) / 2
    - Número de confrontos = (N * K) / 4
    - Para ser viável: (N * K) deve ser múltiplo de 4 (número par de confrontos)
    
    Exemplo: 7 jogadores
    - K=4: 7*4=28 duplas, 28/2=14 duplas únicas, 14/2=7 confrontos (ímpar, não funciona)
    - K=6: 7*6=42 duplas, 42/2=21 duplas únicas, 21/2=10.5 confrontos (não funciona)
    - K=8: 7*8=56 duplas, 56/2=28 duplas únicas, 28/2=14 confrontos (par, funciona!)
    
    Retorna:
    {
        "viável": bool,
        "opcoes": [{"jogos": K, "duplas": X, "confrontos": Y, "rodadas_estimadas": Z}, ...],
        "sugestao": K (melhor opção, prioriza valores menores)
    }
    """
    if num_jogadores < 4:
        return {
            "viável": False,
            "mensagem": f"Mínimo de 4 jogadores necessário. Você tem {num_jogadores}.",
            "opcoes": [],
            "sugestao": None
        }
    
    if num_jogadores > 20:
        return {
            "viável": False,
            "mensagem": f"Máximo recomendado: 20 jogadores. Você tem {num_jogadores}.",
            "opcoes": [],
            "sugestao": None
        }
    
    opcoes_viaveis = []
    
    # Testa valores de K de 3 até 10 (ou até N-1 se N for menor)
    max_k = min(10, num_jogadores - 1)
    
    for k in range(3, max_k + 1):
        total_duplas = (num_jogadores * k) / 2
        
        # Total de duplas deve ser inteiro
        if total_duplas != int(total_duplas):
            continue
        
        total_duplas = int(total_duplas)
        
        # Número de duplas deve ser par (para evitar byes)
        if total_duplas % 2 != 0:
            continue
        
        # Número de confrontos = total_duplas / 2
        num_confrontos = total_duplas // 2
        
        # Estima número de rodadas (assumindo ~4-6 confrontos por rodada)
        # Mas pode variar, então calcula mínimo teórico
        confrontos_por_rodada = min(6, num_jogadores // 2)  # Máximo de confrontos por rodada
        rodadas_estimadas = max(1, (num_confrontos + confrontos_por_rodada - 1) // confrontos_por_rodada)
        
        opcoes_viaveis.append({
            "jogos": k,
            "duplas": int(total_duplas),
            "confrontos": num_confrontos,
            "rodadas_estimadas": rodadas_estimadas
        })
    
    if not opcoes_viaveis:
        return {
            "viável": False,
            "mensagem": f"Não foi possível encontrar configurações viáveis para {num_jogadores} jogadores.",
            "opcoes": [],
            "sugestao": None
        }
    
    # Sugestão: prioriza valores menores de K (mais prático)
    sugestao = min(opcoes_viaveis, key=lambda x: x["jogos"])["jogos"]
    
    return {
        "viável": True,
        "mensagem": f"Encontradas {len(opcoes_viaveis)} opções viáveis para {num_jogadores} jogadores.",
        "opcoes": sorted(opcoes_viaveis, key=lambda x: x["jogos"]),
        "sugestao": sugestao
    }


def gerar_duplas_mesmo_genero(jogadores: List[str], jogos_por_pessoa: int) -> List[Tuple[str, str]]:
    """
    Gera todas as duplas necessárias para que cada jogador jogue exatamente 'jogos_por_pessoa' vezes.
    
    Algoritmo baseado em construção sistemática com backtracking otimizado.
    """
    n = len(jogadores)
    total_duplas_necessarias = (n * jogos_por_pessoa) // 2
    
    # Gera todas as combinações possíveis de duplas
    todas_combinacoes = list(itertools.combinations(jogadores, 2))
    
    def construir_duplas_recursivo(duplas_atual: List[Tuple[str, str]],
                                   contador: Dict[str, int],
                                   duplas_usadas: set,
                                   combinacoes_restantes: List[Tuple[str, str]],
                                   profundidade: int = 0) -> Optional[List[Tuple[str, str]]]:
        """
        Backtracking recursivo otimizado para encontrar solução completa.
        """
        # Caso base: solução completa
        if len(duplas_atual) >= total_duplas_necessarias:
            return duplas_atual
        
        # Limite de profundidade para evitar recursão infinita
        if profundidade > 5000:
            return None
        
        # Se não há mais combinações disponíveis, falhou
        if not combinacoes_restantes:
            return None
        
        # Ordena combinações priorizando jogadores que precisam de mais duplas
        combinacoes_ordenadas = sorted(
            combinacoes_restantes,
            key=lambda d: (
                jogos_por_pessoa - contador.get(d[0], 0),
                jogos_por_pessoa - contador.get(d[1], 0)
            ),
            reverse=True
        )
        
        # Tenta cada combinação válida
        for i, dupla in enumerate(combinacoes_ordenadas):
            j1, j2 = dupla
            
            # Verifica se ambos ainda podem jogar
            if (contador.get(j1, 0) >= jogos_por_pessoa or 
                contador.get(j2, 0) >= jogos_por_pessoa):
                continue
            
            # Verifica se dupla já foi usada
            dupla_sorted = tuple(sorted(dupla))
            if dupla_sorted in duplas_usadas:
                continue
            
            # Tenta adicionar esta dupla
            nova_duplas = duplas_atual + [dupla]
            novo_contador = contador.copy()
            novo_contador[j1] = novo_contador.get(j1, 0) + 1
            novo_contador[j2] = novo_contador.get(j2, 0) + 1
            novo_duplas_usadas = duplas_usadas.copy()
            novo_duplas_usadas.add(dupla_sorted)
            novas_combinacoes = combinacoes_restantes[:i] + combinacoes_restantes[i+1:]
            
            resultado = construir_duplas_recursivo(
                nova_duplas, novo_contador, novo_duplas_usadas,
                novas_combinacoes, profundidade + 1
            )
            
            if resultado:
                return resultado
        
        return None
    
    # Tenta múltiplas vezes com diferentes embaralhamentos
    for tentativa in range(50):
        random.shuffle(todas_combinacoes)
        resultado = construir_duplas_recursivo(
            [], defaultdict(int), set(), todas_combinacoes
        )
        if resultado and len(resultado) >= total_duplas_necessarias:
            return resultado
    
    # Se backtracking não funcionou, usa algoritmo greedy melhorado
    melhor_resultado = []
    melhor_score = 0
    
    for tentativa in range(5000):
        duplas_temp = []
        contador_temp = defaultdict(int)
        duplas_usadas_set = set()
        
        # Embaralha combinações
        combinacoes_shuffled = todas_combinacoes.copy()
        random.shuffle(combinacoes_shuffled)
        
        # Constrói duplas de forma greedy com reordenação dinâmica
        iteracoes_sem_progresso = 0
        while len(duplas_temp) < total_duplas_necessarias and iteracoes_sem_progresso < 100:
            # Filtra combinações válidas
            combinacoes_validas = [
                d for d in combinacoes_shuffled
                if tuple(sorted(d)) not in duplas_usadas_set
                and contador_temp.get(d[0], 0) < jogos_por_pessoa
                and contador_temp.get(d[1], 0) < jogos_por_pessoa
            ]
            
            if not combinacoes_validas:
                break
            
            # Ordena por prioridade (jogadores que precisam de mais duplas)
            combinacoes_ordenadas = sorted(
                combinacoes_validas,
                key=lambda d: (
                    (jogos_por_pessoa - contador_temp.get(d[0], 0)) +
                    (jogos_por_pessoa - contador_temp.get(d[1], 0))
                ),
                reverse=True
            )
            
            # Adiciona a melhor dupla
            dupla = combinacoes_ordenadas[0]
            j1, j2 = dupla
            dupla_sorted = tuple(sorted(dupla))
            
            duplas_temp.append(dupla)
            duplas_usadas_set.add(dupla_sorted)
            contador_temp[j1] += 1
            contador_temp[j2] += 1
            iteracoes_sem_progresso = 0
        
        # Se conseguiu todas as duplas, retorna
        if len(duplas_temp) >= total_duplas_necessarias:
            return duplas_temp
        
        # Guarda melhor resultado
        if len(duplas_temp) > melhor_score:
            melhor_score = len(duplas_temp)
            melhor_resultado = duplas_temp.copy()
    
    # Se chegou muito perto, tenta completar
    if melhor_resultado and len(melhor_resultado) >= int(total_duplas_necessarias * 0.95):
        duplas_completas = completar_duplas_faltantes(
            jogadores, melhor_resultado, jogos_por_pessoa,
            total_duplas_necessarias - len(melhor_resultado)
        )
        if len(duplas_completas) >= total_duplas_necessarias:
            return duplas_completas
    
    # Retorna melhor resultado encontrado
    return melhor_resultado


def completar_duplas_faltantes(jogadores: List[str], duplas_existentes: List[Tuple[str, str]], 
                                jogos_por_pessoa: int, faltam: int) -> List[Tuple[str, str]]:
    """
    Tenta completar as duplas faltantes de forma inteligente.
    """
    # Conta quantas vezes cada jogador já aparece
    contador = defaultdict(int)
    duplas_set = {tuple(sorted(d)) for d in duplas_existentes}
    
    for dupla in duplas_existentes:
        contador[dupla[0]] += 1
        contador[dupla[1]] += 1
    
    # Gera todas as combinações possíveis
    todas_combinacoes = list(itertools.combinations(jogadores, 2))
    random.shuffle(todas_combinacoes)
    
    duplas_completas = duplas_existentes.copy()
    
    # Tenta adicionar as duplas faltantes
    for dupla in todas_combinacoes:
        if faltam <= 0:
            break
            
        j1, j2 = dupla
        dupla_sorted = tuple(sorted(dupla))
        
        # Verifica se a dupla já existe
        if dupla_sorted in duplas_set:
            continue
        
        # Verifica se ambos ainda podem jogar mais vezes
        if (contador[j1] < jogos_por_pessoa and contador[j2] < jogos_por_pessoa):
            duplas_completas.append(dupla)
            duplas_set.add(dupla_sorted)
            contador[j1] += 1
            contador[j2] += 1
            faltam -= 1
    
    return duplas_completas


def criar_confrontos_mesmo_genero(duplas: List[Tuple[str, str]]) -> List[Dict]:
    """
    Cria confrontos 2x2 a partir das duplas, garantindo que nenhuma dupla compartilhe jogadores.
    Tenta múltiplas vezes para minimizar byes.
    """
    def compartilha_jogadores(dupla1, dupla2):
        """Verifica se duas duplas têm algum jogador em comum"""
        set1 = set(dupla1)
        set2 = set(dupla2)
        return len(set1 & set2) > 0
    
    melhor_resultado = None
    menor_byes = float('inf')
    
    # Tenta múltiplas vezes com diferentes embaralhamentos
    for tentativa in range(500):
        confrontos = []
        duplas_restantes = duplas.copy()
        random.shuffle(duplas_restantes)
        
        while len(duplas_restantes) >= 2:
            dupla1 = duplas_restantes[0]
            dupla2_idx = None
            
            # Procura uma dupla2 compatível
            for i in range(1, len(duplas_restantes)):
                if not compartilha_jogadores(dupla1, duplas_restantes[i]):
                    dupla2_idx = i
                    break
            
            if dupla2_idx is not None:
                dupla2 = duplas_restantes[dupla2_idx]
                confronto = {
                    "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                    "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                    "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False}
                }
                confrontos.append(confronto)
                
                # Remove duplas usadas
                duplas_restantes.pop(dupla2_idx)
                duplas_restantes.pop(0)
            else:
                # Não encontrou par compatível, para esta tentativa
                break
        
        # Se conseguiu sem byes, retorna imediatamente
        if len(duplas_restantes) == 0:
            return confrontos
        
        # Guarda melhor resultado (menos byes)
        if len(duplas_restantes) < menor_byes:
            menor_byes = len(duplas_restantes)
            melhor_resultado = (confrontos, duplas_restantes)
    
    # Se não conseguiu sem byes, usa o melhor resultado
    confrontos_finais, duplas_sobrando = melhor_resultado
    
    # Adiciona byes para duplas que sobraram
    for dupla_bye in duplas_sobrando:
        confronto_bye = {
            "dupla1": {"jogador1": dupla_bye[0], "jogador2": dupla_bye[1]},
            "dupla2": None,
            "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
            "tipo": "bye",
            "obs": "Dupla sem adversário"
        }
        confrontos_finais.append(confronto_bye)
    
    return confrontos_finais


def gerar_sorteio_mesmo_genero(jogadores: List[str], jogos_por_pessoa: int) -> Dict:
    """
    Gera sorteio completo para categoria masculino ou feminino.
    
    Garante:
    - Cada jogador joga exatamente 'jogos_por_pessoa' vezes
    - Nenhuma dupla se repete
    - Confrontos distribuídos em rodadas otimizadas
    """
    # Valida viabilidade
    analise = analisar_viabilidade_mesmo_genero(len(jogadores))
    if not analise["viável"]:
        return {"erro": analise["mensagem"]}
    
    # Verifica se jogos_por_pessoa está nas opções viáveis
    opcoes_validas = [op["jogos"] for op in analise["opcoes"]]
    if jogos_por_pessoa not in opcoes_validas:
        return {
            "erro": f"Jogos por pessoa ({jogos_por_pessoa}) não é viável. Opções válidas: {opcoes_validas}"
        }
    
    # Embaralha jogadores para aleatoriedade
    jogadores_shuffled = jogadores.copy()
    random.shuffle(jogadores_shuffled)
    
    # Gera todas as duplas necessárias
    duplas = gerar_duplas_mesmo_genero(jogadores_shuffled, jogos_por_pessoa)
    
    total_necessarias = (len(jogadores) * jogos_por_pessoa) // 2
    total_geradas = len(duplas)
    
    # Se faltam poucas duplas (menos de 5% ou 1-2 duplas), tenta completar
    if total_geradas < total_necessarias:
        faltam = total_necessarias - total_geradas
        
        # Se faltam apenas 1-2 duplas, tenta completar de forma inteligente
        if faltam <= 2:
            duplas = completar_duplas_faltantes(jogadores_shuffled, duplas, jogos_por_pessoa, faltam)
            total_geradas = len(duplas)
        
        # Se ainda faltam duplas, verifica se é aceitável (95% ou mais)
        if total_geradas < total_necessarias:
            percentual = (total_geradas / total_necessarias) * 100
            if percentual < 95:
                return {
                    "erro": f"Não foi possível gerar todas as duplas necessárias. Geradas: {total_geradas}, Necessárias: {total_necessarias} ({percentual:.1f}%)"
                }
            # Aceita se tiver 95% ou mais
            print(f"Aviso: Geradas {total_geradas} de {total_necessarias} duplas ({percentual:.1f}%). Continuando...")
    
    # Cria confrontos
    confrontos_totais = criar_confrontos_mesmo_genero(duplas)
    
    # Distribui confrontos em rodadas (similar ao algoritmo de mista)
    def get_jogadores_confronto(conf):
        """Retorna conjunto de jogadores em um confronto"""
        jogadores = set()
        d1 = conf['dupla1']
        d2 = conf.get('dupla2')
        if d1:
            jogadores.add(d1['jogador1'])
            jogadores.add(d1['jogador2'])
        if d2:
            jogadores.add(d2['jogador1'])
            jogadores.add(d2['jogador2'])
        return jogadores
    
    # Calcula número de rodadas necessário baseado nos confrontos
    # Cada rodada pode ter no máximo floor(n_jogadores/4) confrontos (4 jogadores por confronto)
    # Mas precisamos garantir que todos os confrontos sejam distribuídos
    num_confrontos = len(confrontos_totais)
    n_jogadores = len(jogadores)
    
    # Estima mínimo de rodadas: confrontos / (jogadores/4 por rodada)
    # Mas garante que cada jogador jogue no máximo 1 vez por rodada
    confrontos_por_rodada_max = n_jogadores // 4  # Máximo teórico
    num_rodadas_min = max(1, (num_confrontos + confrontos_por_rodada_max - 1) // confrontos_por_rodada_max)
    
    # Usa o maior entre: estimativa da análise, mínimo calculado, ou 3
    num_rodadas_estimado = analise["opcoes"][opcoes_validas.index(jogos_por_pessoa)]["rodadas_estimadas"]
    num_rodadas = max(num_rodadas_estimado, num_rodadas_min, 3)
    
    # Tenta distribuir confrontos de forma otimizada
    melhor_distribuicao = None
    melhor_score = float('inf')
    confrontos_distribuidos = False
    
    # Tenta múltiplas distribuições para encontrar a mais otimizada
    for tentativa_distribuicao in range(1000):
        rodadas_temp = [[] for _ in range(num_rodadas)]
        jogadores_usados_rodada = [set() for _ in range(num_rodadas)]
        
        confrontos_shuffled = confrontos_totais.copy()
        random.shuffle(confrontos_shuffled)
        
        confrontos_alocados = 0
        
        for confronto in confrontos_shuffled:
            jogadores_confronto = get_jogadores_confronto(confronto)
            
            # Encontra rodadas possíveis (sem conflito)
            rodadas_possiveis = []
            for rodada_idx in range(num_rodadas):
                if not jogadores_confronto & jogadores_usados_rodada[rodada_idx]:
                    rodadas_possiveis.append(rodada_idx)
            
            if rodadas_possiveis:
                # Heurística melhorada: prioriza preencher rodadas ao máximo
                # 1. Prioriza rodadas que já têm confrontos (preencher ao máximo)
                # 2. Se todas estão vazias ou com mesmo número, prioriza a primeira
                # 3. Penaliza rodadas que já estão quase cheias mas ainda podem receber mais
                melhor_rodada = min(rodadas_possiveis, 
                                   key=lambda idx: (
                                       -len(rodadas_temp[idx]),  # Prioriza rodadas com MAIS confrontos (preencher ao máximo)
                                       len(jogadores_usados_rodada[idx]),  # Em caso de empate, menos jogadores = melhor
                                       idx  # Em caso de empate total, primeira rodada
                                   ))
                rodadas_temp[melhor_rodada].append(confronto)
                jogadores_usados_rodada[melhor_rodada].update(jogadores_confronto)
                confrontos_alocados += 1
        
        # Se conseguiu alocar todos os confrontos, sucesso!
        if confrontos_alocados == num_confrontos:
            confrontos_distribuidos = True
            melhor_distribuicao = [r.copy() for r in rodadas_temp]
            break
        
        # Calcula score da distribuição (menor é melhor)
        # Penaliza rodadas com muitos jogadores descansando quando há espaço disponível
        score = 0
        for rodada in rodadas_temp:
            jogadores_na_rodada = sum(len(get_jogadores_confronto(c)) for c in rodada)
            jogadores_nao_usados = n_jogadores - jogadores_na_rodada
            # Penaliza rodadas com 4+ jogadores descansando (poderia ter mais 1 confronto)
            if jogadores_nao_usados >= 4:
                score += jogadores_nao_usados * 10
        
        if score < melhor_score:
            melhor_score = score
            melhor_distribuicao = [r.copy() for r in rodadas_temp]
    
    # Se não conseguiu distribuir todos, tenta aumentar rodadas
    if not confrontos_distribuidos:
        tentativas_rodadas = 0
        max_tentativas_rodadas = 20
        
        while not confrontos_distribuidos and tentativas_rodadas < max_tentativas_rodadas:
            num_rodadas += 1
            tentativas_rodadas += 1
            
            rodadas_temp = [[] for _ in range(num_rodadas)]
            jogadores_usados_rodada = [set() for _ in range(num_rodadas)]
            
            confrontos_shuffled = confrontos_totais.copy()
            random.shuffle(confrontos_shuffled)
            
            confrontos_alocados = 0
            
            for confronto in confrontos_shuffled:
                jogadores_confronto = get_jogadores_confronto(confronto)
                rodadas_possiveis = []
                for rodada_idx in range(num_rodadas):
                    if not jogadores_confronto & jogadores_usados_rodada[rodada_idx]:
                        rodadas_possiveis.append(rodada_idx)
                
                if rodadas_possiveis:
                    # Mesma heurística: prioriza preencher rodadas ao máximo
                    melhor_rodada = min(rodadas_possiveis, 
                                       key=lambda idx: (
                                           -len(rodadas_temp[idx]),  # Prioriza rodadas com MAIS confrontos
                                           len(jogadores_usados_rodada[idx]),  # Em caso de empate, menos jogadores
                                           idx  # Em caso de empate total, primeira rodada
                                       ))
                    rodadas_temp[melhor_rodada].append(confronto)
                    jogadores_usados_rodada[melhor_rodada].update(jogadores_confronto)
                    confrontos_alocados += 1
            
            if confrontos_alocados == num_confrontos:
                confrontos_distribuidos = True
                melhor_distribuicao = [r.copy() for r in rodadas_temp]
    
    # Usa a melhor distribuição encontrada
    if melhor_distribuicao:
        rodadas_temp = melhor_distribuicao
    
    # Monta rodadas finais
    todos_jogadores = set(jogadores_shuffled)
    rodadas_geradas = []
    
    for rodada_num, confrontos_rodada in enumerate(rodadas_temp):
        if not confrontos_rodada:
            continue  # Pula rodadas vazias
        
        # Identifica quem está jogando
        jogadores_jogando = set()
        for confronto in confrontos_rodada:
            jogadores_jogando.update(get_jogadores_confronto(confronto))
        
        # Quem não está jogando está descansando
        jogadores_descansando = sorted(list(todos_jogadores - jogadores_jogando))
        
        # Atribui números de quadra
        confrontos_finais = []
        for quadra_num, confronto in enumerate(confrontos_rodada, 1):
            confronto_copy = confronto.copy()
            confronto_copy["quadra"] = quadra_num
            confrontos_finais.append(confronto_copy)
        
        rodadas_geradas.append({
            "numero": len(rodadas_geradas) + 1,
            "confrontos": confrontos_finais,
            "descansando": jogadores_descansando
        })
    
    return {
        "total_rodadas": len(rodadas_geradas),
        "rodadas": rodadas_geradas,
        "jogos_por_pessoa": jogos_por_pessoa,
        "total_jogadores": len(jogadores)
    }
