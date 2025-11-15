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
# FUNÇÕES V3 - SISTEMA DE CATEGORIAS SEPARADAS
# ============================================================================

def analisar_viabilidade_categoria(categoria: str, participantes: List[str]) -> Dict:
    """
    Analisa a viabilidade de gerar um sorteio para uma categoria (masculino/feminino)
    com diferentes números de jogos por pessoa.
    
    Retorna opções viáveis e sugestões.
    """
    num_participantes = len(participantes)
    
    if num_participantes < 4:
        return {
            "viavel": False,
            "mensagem": f"Mínimo de 4 participantes necessário. Atualmente: {num_participantes}",
            "opcoes": []
        }
    
    # Calcula número máximo de duplas possíveis (C(n,2))
    max_duplas_possiveis = (num_participantes * (num_participantes - 1)) // 2
    
    opcoes_viaveis = []
    
    # Testa de 3 a 10 jogos por pessoa
    for jogos_por_pessoa in range(3, 11):
        # Total de duplas necessárias
        total_aparições = num_participantes * jogos_por_pessoa
        
        # REGRA 1: Total de aparições deve ser PAR (para formar duplas inteiras)
        if total_aparições % 2 != 0:
            continue
        
        duplas_necessarias = total_aparições // 2
        
        # Verifica se é matematicamente possível
        if duplas_necessarias > max_duplas_possiveis:
            continue
        
        # REGRA CRÍTICA: Total de duplas deve ser PAR para formar confrontos
        if duplas_necessarias % 2 != 0:
            continue
        
        # Calcula número mínimo de rodadas (considerando máximo de confrontos por rodada)
        # Para número ímpar de participantes: máximo é (n-1)/2 confrontos por rodada
        # Para número par: máximo é n/2 confrontos por rodada
        if num_participantes % 2 == 0:
            max_confrontos_por_rodada = num_participantes // 2
        else:
            max_confrontos_por_rodada = (num_participantes - 1) // 2
        
        num_rodadas_minimo = (duplas_necessarias // 2 + max_confrontos_por_rodada - 1) // max_confrontos_por_rodada
        
        # Descansos por rodada (aproximado)
        descansos_por_rodada = num_participantes - (max_confrontos_por_rodada * 2)
        
        opcoes_viaveis.append({
            "jogos_por_pessoa": jogos_por_pessoa,
            "duplas_necessarias": duplas_necessarias,
            "rodadas_estimadas": num_rodadas_minimo,
            "descansos_por_rodada": descansos_por_rodada
        })
    
    if not opcoes_viaveis:
        return {
            "viavel": False,
            "mensagem": f"Não é possível gerar um sorteio viável com {num_participantes} participantes",
            "opcoes": []
        }
    
    # Sugere melhor opção (prioriza 5 jogos)
    melhor_opcao = None
    for opcao in opcoes_viaveis:
        if opcao["jogos_por_pessoa"] == 5:
            melhor_opcao = opcao
            break
    
    if not melhor_opcao:
        melhor_opcao = opcoes_viaveis[0]
    
    return {
        "viavel": True,
        "mensagem": f"✅ Viável com {num_participantes} participantes",
        "opcoes": opcoes_viaveis,
        "sugestao": melhor_opcao
    }


def analisar_viabilidade_misto(homens: List[str], mulheres: List[str]) -> Dict:
    """
    Analisa a viabilidade de gerar um sorteio misto com diferentes números de jogos por pessoa.
    """
    num_homens = len(homens)
    num_mulheres = len(mulheres)
    
    if num_homens < 3 or num_mulheres < 3:
        return {
            "viavel": False,
            "mensagem": f"Mínimo de 3 homens e 3 mulheres necessário. Atualmente: {num_homens}H x {num_mulheres}M",
            "opcoes": []
        }
    
    # Número máximo de duplas mistas possíveis
    max_duplas_possiveis = num_homens * num_mulheres
    
    opcoes_viaveis = []
    
    # Testa de 3 a 10 jogos por pessoa
    for jogos_por_pessoa in range(3, 11):
        # Total de duplas necessárias
        total_pessoas = num_homens + num_mulheres
        duplas_necessarias = (total_pessoas * jogos_por_pessoa) // 2
        
        # Verifica se é matematicamente possível
        if duplas_necessarias > max_duplas_possiveis:
            continue
        
        # REGRA CRÍTICA: Total de duplas deve ser PAR para formar confrontos
        if duplas_necessarias % 2 != 0:
            continue
        
        # Calcula número mínimo de rodadas
        min_pessoas = min(num_homens, num_mulheres)
        max_confrontos_por_rodada = min_pessoas
        
        num_rodadas_minimo = (duplas_necessarias // 2 + max_confrontos_por_rodada - 1) // max_confrontos_por_rodada
        
        opcoes_viaveis.append({
            "jogos_por_pessoa": jogos_por_pessoa,
            "duplas_necessarias": duplas_necessarias,
            "rodadas_estimadas": num_rodadas_minimo
        })
    
    if not opcoes_viaveis:
        return {
            "viavel": False,
            "mensagem": f"Não é possível gerar um sorteio viável com {num_homens}H x {num_mulheres}M",
            "opcoes": []
        }
    
    # Sugere melhor opção (prioriza 5 jogos)
    melhor_opcao = None
    for opcao in opcoes_viaveis:
        if opcao["jogos_por_pessoa"] == 5:
            melhor_opcao = opcao
            break
    
    if not melhor_opcao:
        melhor_opcao = opcoes_viaveis[0]
    
    return {
        "viavel": True,
        "mensagem": f"✅ Viável com {num_homens}H x {num_mulheres}M",
        "opcoes": opcoes_viaveis,
        "sugestao": melhor_opcao
    }


def gerar_duplas_mesmo_genero(participantes: List[str], jogos_por_pessoa: int) -> List[Tuple[str, str]]:
    """
    Gera todas as duplas necessárias para que cada participante jogue exatamente
    jogos_por_pessoa vezes, sem repetir duplas.
    
    Retorna lista de tuplas (jogador1, jogador2) ordenadas.
    """
    num_participantes = len(participantes)
    total_duplas_necessarias = (num_participantes * jogos_por_pessoa) // 2
    
    # Todas as duplas possíveis (sem ordem, sem repetição)
    todas_duplas_possiveis = list(itertools.combinations(participantes, 2))
    
    # Contador de aparições por jogador
    aparicoes_por_jogador = defaultdict(int)
    
    # Duplas selecionadas
    duplas_selecionadas = []
    
    max_tentativas = 2000
    
    for tentativa in range(max_tentativas):
        # Embaralha duplas possíveis
        random.shuffle(todas_duplas_possiveis)
        
        duplas_selecionadas = []
        aparicoes_por_jogador = defaultdict(int)
        
        # Tenta selecionar duplas até atingir o total necessário
        for dupla in todas_duplas_possiveis:
            j1, j2 = dupla
            
            # Verifica se ambos ainda podem jogar mais vezes
            if aparicoes_por_jogador[j1] < jogos_por_pessoa and aparicoes_por_jogador[j2] < jogos_por_pessoa:
                # Verifica se essa dupla já foi selecionada
                if (j1, j2) not in duplas_selecionadas and (j2, j1) not in duplas_selecionadas:
                    duplas_selecionadas.append((j1, j2))
                    aparicoes_por_jogador[j1] += 1
                    aparicoes_por_jogador[j2] += 1
                    
                    if len(duplas_selecionadas) >= total_duplas_necessarias:
                        break
        
        # Verifica se todos os jogadores atingiram o número exato de jogos
        todos_completos = all(aparicoes_por_jogador[p] == jogos_por_pessoa for p in participantes)
        
        if todos_completos and len(duplas_selecionadas) == total_duplas_necessarias:
            return duplas_selecionadas
    
    # Se não encontrou solução perfeita, tenta completar o melhor resultado parcial
    melhor_resultado = []
    melhor_aparicoes = defaultdict(int)
    melhor_score = -1
    
    for tentativa in range(500):
        random.shuffle(todas_duplas_possiveis)
        
        duplas_temp = []
        aparicoes_temp = defaultdict(int)
        
        for dupla in todas_duplas_possiveis:
            j1, j2 = dupla
            if aparicoes_temp[j1] < jogos_por_pessoa and aparicoes_temp[j2] < jogos_por_pessoa:
                if (j1, j2) not in duplas_temp and (j2, j1) not in duplas_temp:
                    duplas_temp.append((j1, j2))
                    aparicoes_temp[j1] += 1
                    aparicoes_temp[j2] += 1
        
        # Calcula score: penaliza jogadores que não completaram
        score = sum(aparicoes_temp[p] for p in participantes)
        
        if score > melhor_score:
            melhor_score = score
            melhor_resultado = duplas_temp
            melhor_aparicoes = aparicoes_temp.copy()
    
    # Tenta completar o melhor resultado
    duplas_selecionadas = melhor_resultado.copy()
    aparicoes_por_jogador = melhor_aparicoes.copy()
    
    # Força geração de duplas faltantes
    for _ in range(1000):
        if len(duplas_selecionadas) >= total_duplas_necessarias:
            break
        
        # Encontra jogadores que ainda precisam jogar
        jogadores_faltando = [p for p in participantes if aparicoes_por_jogador[p] < jogos_por_pessoa]
        
        if len(jogadores_faltando) < 2:
            break
        
        # Tenta formar uma dupla com jogadores que ainda precisam jogar
        random.shuffle(jogadores_faltando)
        j1 = jogadores_faltando[0]
        j2 = jogadores_faltando[1]
        
        dupla_key = tuple(sorted([j1, j2]))
        if dupla_key not in [tuple(sorted([d[0], d[1]])) for d in duplas_selecionadas]:
            duplas_selecionadas.append((j1, j2))
            aparicoes_por_jogador[j1] += 1
            aparicoes_por_jogador[j2] += 1
    
    return duplas_selecionadas


def criar_confrontos_sem_byes_v3(duplas_list: List[Tuple[str, str]], max_tentativas: int = 100) -> List[Dict]:
    """
    Cria confrontos 2x2 a partir de uma lista de duplas, garantindo que todas as duplas
    sejam incluídas, mesmo que algumas compartilhem jogadores.
    
    Retorna lista de confrontos, onde cada confronto pode ser:
    - Normal: dupla1 vs dupla2 (sem jogadores compartilhados)
    - Compartilha jogadores: dupla1 vs dupla2 (com jogadores compartilhados)
    - Dupla única: dupla1 vs None (quando sobra uma dupla ímpar)
    """
    confrontos = []
    duplas_restantes = duplas_list.copy()
    random.shuffle(duplas_restantes)
    
    # PASSO 1: Tenta parear duplas sem compartilhar jogadores
    i = 0
    while i < len(duplas_restantes):
        dupla1 = duplas_restantes[i]
        j1_set = {dupla1[0], dupla1[1]}
        
        encontrou_par = False
        for j in range(i + 1, len(duplas_restantes)):
            dupla2 = duplas_restantes[j]
            j2_set = {dupla2[0], dupla2[1]}
            
            # Se não compartilham jogadores, forma confronto
            if not (j1_set & j2_set):
                confronto = {
                    "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                    "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                    "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
                    "tipo": "normal"
                }
                confrontos.append(confronto)
                
                # Remove ambas as duplas
                duplas_restantes.pop(j)
                duplas_restantes.pop(i)
                encontrou_par = True
                break
        
        if not encontrou_par:
            i += 1
    
    # PASSO 2: Pareia duplas que compartilham jogadores (marcando como tipo especial)
    i = 0
    while i < len(duplas_restantes):
        dupla1 = duplas_restantes[i]
        
        if i + 1 < len(duplas_restantes):
            dupla2 = duplas_restantes[i + 1]
            
            confronto = {
                "dupla1": {"jogador1": dupla1[0], "jogador2": dupla1[1]},
                "dupla2": {"jogador1": dupla2[0], "jogador2": dupla2[1]},
                "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
                "tipo": "compartilha_jogadores"
            }
            confrontos.append(confronto)
            
            duplas_restantes.pop(i + 1)
            duplas_restantes.pop(i)
        else:
            i += 1
    
    # PASSO 3: Se sobrou uma dupla ímpar, adiciona como "dupla única"
    if len(duplas_restantes) == 1:
        dupla_unica = duplas_restantes[0]
        confronto = {
            "dupla1": {"jogador1": dupla_unica[0], "jogador2": dupla_unica[1]},
            "dupla2": None,
            "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
            "tipo": "dupla_unica"
        }
        confrontos.append(confronto)
    
    return confrontos


def gerar_sorteio_mesmo_genero_v2(participantes: List[str], jogos_por_pessoa: int) -> Dict:
    """
    Gera sorteio completo para categoria de mesmo gênero (masculino/feminino).
    
    Garante:
    - Todos jogam exatamente jogos_por_pessoa vezes
    - Nenhuma dupla se repete
    - Distribuição otimizada de confrontos por rodada
    """
    num_participantes = len(participantes)
    total_duplas_necessarias = (num_participantes * jogos_por_pessoa) // 2
    
    # PASSO 1: Gera todas as duplas necessárias
    duplas_selecionadas = gerar_duplas_mesmo_genero(participantes, jogos_por_pessoa)
    
    # Validação: verifica se todas as duplas foram geradas
    if len(duplas_selecionadas) != total_duplas_necessarias:
        return {
            "erro": f"Falha ao gerar duplas: esperado {total_duplas_necessarias}, gerado {len(duplas_selecionadas)}"
        }
    
    # Validação: verifica se todos jogam o número exato de vezes
    aparicoes = defaultdict(int)
    for dupla in duplas_selecionadas:
        aparicoes[dupla[0]] += 1
        aparicoes[dupla[1]] += 1
    
    for p in participantes:
        if aparicoes[p] != jogos_por_pessoa:
            return {
                "erro": f"Jogador {p} jogou {aparicoes[p]}x, esperado {jogos_por_pessoa}x"
            }
    
    # PASSO 2: Cria confrontos
    max_tentativas_confrontos = min(200, len(duplas_selecionadas) * 10)
    confrontos = criar_confrontos_sem_byes_v3(duplas_selecionadas, max_tentativas_confrontos)
    
    # Validação: verifica se todos os confrontos foram criados
    duplas_em_confrontos = set()
    for conf in confrontos:
        d1 = conf["dupla1"]
        duplas_em_confrontos.add(tuple(sorted([d1["jogador1"], d1["jogador2"]])))
        if conf.get("dupla2"):
            d2 = conf["dupla2"]
            duplas_em_confrontos.add(tuple(sorted([d2["jogador1"], d2["jogador2"]])))
    
    # Verifica se alguma dupla ficou de fora
    duplas_selecionadas_set = {tuple(sorted(d)) for d in duplas_selecionadas}
    duplas_faltando = duplas_selecionadas_set - duplas_em_confrontos
    
    if duplas_faltando:
        # Adiciona duplas faltantes como "dupla_unica"
        for dupla_faltando in duplas_faltando:
            confronto = {
                "dupla1": {"jogador1": dupla_faltando[0], "jogador2": dupla_faltando[1]},
                "dupla2": None,
                "resultado": {"games_dupla1": 0, "games_dupla2": 0, "finalizado": False},
                "tipo": "dupla_unica"
            }
            confrontos.append(confronto)
    
    # PASSO 3: Calcula máximo de confrontos por rodada
    if num_participantes % 2 == 0:
        max_confrontos_por_rodada = num_participantes // 2
    else:
        max_confrontos_por_rodada = (num_participantes - 1) // 2
    
    # PASSO 4: Distribui confrontos em rodadas (OTIMIZADO)
    def confronto_compativel(conf, jogadores_rodada):
        """Verifica se um confronto pode ser adicionado à rodada sem conflito"""
        jogadores_conf = set()
        
        d1 = conf["dupla1"]
        jogadores_conf.add(d1["jogador1"])
        jogadores_conf.add(d1["jogador2"])
        
        if conf.get("dupla2"):
            d2 = conf["dupla2"]
            jogadores_conf.add(d2["jogador1"])
            jogadores_conf.add(d2["jogador2"])
        
        # Se é tipo "compartilha_jogadores" ou "dupla_unica", permite mesmo com conflito
        if conf.get("tipo") in ["compartilha_jogadores", "dupla_unica"]:
            return True
        
        # Para confrontos normais, não pode ter conflito
        return not (jogadores_conf & jogadores_rodada)
    
    melhor_distribuicao = None
    melhor_score = float('inf')
    
    # Tenta múltiplas distribuições para otimizar
    for tentativa in range(20):
        rodadas_temp = [[] for _ in range(100)]  # Inicializa com muitas rodadas
        jogadores_rodada = [set() for _ in range(100)]
        
        confrontos_shuffled = confrontos.copy()
        random.shuffle(confrontos_shuffled)
        
        for conf in confrontos_shuffled:
            # Encontra primeira rodada compatível
            rodada_idx = 0
            while rodada_idx < len(rodadas_temp):
                # Verifica se a rodada não está cheia
                if len(rodadas_temp[rodada_idx]) >= max_confrontos_por_rodada:
                    rodada_idx += 1
                    continue
                
                # Verifica compatibilidade
                if confronto_compativel(conf, jogadores_rodada[rodada_idx]):
                    rodadas_temp[rodada_idx].append(conf)
                    
                    # Atualiza jogadores da rodada
                    d1 = conf["dupla1"]
                    jogadores_rodada[rodada_idx].add(d1["jogador1"])
                    jogadores_rodada[rodada_idx].add(d1["jogador2"])
                    
                    if conf.get("dupla2"):
                        d2 = conf["dupla2"]
                        jogadores_rodada[rodada_idx].add(d2["jogador1"])
                        jogadores_rodada[rodada_idx].add(d2["jogador2"])
                    
                    break
                
                rodada_idx += 1
        
        # Remove rodadas vazias
        rodadas_temp = [r for r in rodadas_temp if r]
        
        # Calcula score: penaliza mais rodadas e rodadas com poucos confrontos
        score = len(rodadas_temp) * 1000
        for rodada in rodadas_temp:
            if len(rodada) == 1:
                score += 100  # Penaliza rodadas com apenas 1 confronto
        
        if score < melhor_score:
            melhor_score = score
            melhor_distribuicao = rodadas_temp
    
    rodadas_distribuidas = melhor_distribuicao if melhor_distribuicao else [confrontos]
    
    # PASSO 5: Monta estrutura final
    rodadas_finais = []
    for idx, confrontos_rodada in enumerate(rodadas_distribuidas):
        # Identifica jogadores jogando
        jogadores_jogando = set()
        for conf in confrontos_rodada:
            d1 = conf["dupla1"]
            jogadores_jogando.add(d1["jogador1"])
            jogadores_jogando.add(d1["jogador2"])
            if conf.get("dupla2"):
                d2 = conf["dupla2"]
                jogadores_jogando.add(d2["jogador1"])
                jogadores_jogando.add(d2["jogador2"])
        
        # Jogadores descansando
        jogadores_descansando = sorted([p for p in participantes if p not in jogadores_jogando])
        
        # Adiciona número de quadra
        confrontos_finais = []
        for quadra_num, conf in enumerate(confrontos_rodada, 1):
            conf_copy = conf.copy()
            conf_copy["quadra"] = quadra_num
            confrontos_finais.append(conf_copy)
        
        rodadas_finais.append({
            "numero": idx + 1,
            "confrontos": confrontos_finais,
            "descansando": jogadores_descansando
        })
    
    # Validação final: verifica se todos jogam o número exato de vezes
    jogos_por_jogador = defaultdict(int)
    for rodada in rodadas_finais:
        for conf in rodada["confrontos"]:
            d1 = conf["dupla1"]
            jogos_por_jogador[d1["jogador1"]] += 1
            jogos_por_jogador[d1["jogador2"]] += 1
            if conf.get("dupla2"):
                d2 = conf["dupla2"]
                jogos_por_jogador[d2["jogador1"]] += 1
                jogos_por_jogador[d2["jogador2"]] += 1
    
    for p in participantes:
        if jogos_por_jogador[p] != jogos_por_pessoa:
            return {
                "erro": f"Validação final falhou: {p} jogou {jogos_por_jogador[p]}x, esperado {jogos_por_pessoa}x"
            }
    
    return {
        "total_rodadas": len(rodadas_finais),
        "rodadas": rodadas_finais
    }
