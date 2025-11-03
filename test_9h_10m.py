#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Detalhado: 9 Homens + 10 Mulheres = 19 participantes
Mostra EXATAMENTE onde o algoritmo falha
"""

import json
from collections import defaultdict
from utils.sorteio_rodadas import gerar_5_rodadas, calcular_ranking_individual, separar_ranking_por_genero

# Cores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*90}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(90)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*90}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*90}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"  {text}")

print_header("TESTE DETALHADO: 9 HOMENS + 10 MULHERES = 19 PARTICIPANTES")

# Gera nomes
homens = [f"Homem{i+1}" for i in range(9)]
mulheres = [f"Mulher{i+1}" for i in range(10)]

print_section("1. PARTICIPANTES")
print_info(f"Homens ({len(homens)}): {', '.join(homens)}")
print_info(f"Mulheres ({len(mulheres)}): {', '.join(mulheres)}")
print_info(f"Total: {len(homens) + len(mulheres)} participantes")

# Tenta gerar rodadas
print_section("2. GERANDO 5 RODADAS")
try:
    rodadas_data = gerar_5_rodadas(homens, mulheres)
    
    if not rodadas_data or "erro" in rodadas_data:
        print_error(f"FALHOU: {rodadas_data.get('erro', 'Não conseguiu gerar rodadas')}")
        exit(1)
    
    print_success(f"Gerou {len(rodadas_data['rodadas'])} rodadas")
except Exception as e:
    print_error(f"ERRO CRÍTICO: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Analisa as rodadas
print_section("3. ANÁLISE DETALHADA DAS RODADAS")

rodadas = rodadas_data["rodadas"]
jogos_por_pessoa = defaultdict(int)
duplas_formadas = defaultdict(set)  # Para cada pessoa, com quem formou dupla
adversarios = defaultdict(set)  # Para cada pessoa, quem enfrentou
descansou = defaultdict(int)

for idx_rodada, rodada in enumerate(rodadas, 1):
    print(f"\n{Colors.BOLD}Rodada {idx_rodada}:{Colors.END}")
    
    # Confrontos
    for idx_confronto, confronto in enumerate(rodada["confrontos"], 1):
        j1_d1 = confronto["dupla1"]["jogador1"]
        j2_d1 = confronto["dupla1"]["jogador2"]
        j1_d2 = confronto["dupla2"]["jogador1"]
        j2_d2 = confronto["dupla2"]["jogador2"]
        
        # Conta jogos
        for jogador in [j1_d1, j2_d1, j1_d2, j2_d2]:
            jogos_por_pessoa[jogador] += 1
        
        # Registra duplas
        duplas_formadas[j1_d1].add(j2_d1)
        duplas_formadas[j2_d1].add(j1_d1)
        duplas_formadas[j1_d2].add(j2_d2)
        duplas_formadas[j2_d2].add(j1_d2)
        
        # Registra adversários
        for jogador_d1 in [j1_d1, j2_d1]:
            for jogador_d2 in [j1_d2, j2_d2]:
                adversarios[jogador_d1].add(jogador_d2)
                adversarios[jogador_d2].add(jogador_d1)
        
        print_info(f"  Quadra {confronto['quadra']}: {j1_d1} & {j2_d1}  VS  {j1_d2} & {j2_d2}")
    
    # Descansando
    if rodada.get("descansando"):
        for jogador in rodada["descansando"]:
            descansou[jogador] += 1
        print_info(f"  {Colors.YELLOW}Descansando: {', '.join(rodada['descansando'])}{Colors.END}")

# Análise de distribuição de jogos
print_section("4. DISTRIBUIÇÃO DE JOGOS POR PESSOA")

todos_participantes = set(homens + mulheres)
erros_jogos = []
problemas = defaultdict(list)

print(f"\n{'Jogador':<15} | {'Jogos':<6} | {'Descansou':<10} | {'Status':<30}")
print("-" * 90)

for pessoa in sorted(todos_participantes):
    jogos = jogos_por_pessoa.get(pessoa, 0)
    descansos = descansou.get(pessoa, 0)
    
    status = ""
    if jogos == 5:
        status = f"{Colors.GREEN}✓ OK{Colors.END}"
    elif jogos < 5:
        status = f"{Colors.RED}✗ JOGOU MENOS ({5 - jogos} jogos faltando){Colors.END}"
        erros_jogos.append(f"{pessoa}: jogou {jogos}/5")
        problemas[pessoa].append(f"Faltaram {5 - jogos} jogos")
    else:
        status = f"{Colors.YELLOW}⚠ JOGOU MAIS (+{jogos - 5} jogos extras){Colors.END}"
        erros_jogos.append(f"{pessoa}: jogou {jogos}/5 (excesso)")
        problemas[pessoa].append(f"Jogou {jogos - 5} jogos a mais")
    
    print(f"{pessoa:<15} | {jogos:<6} | {descansos:<10} | {status}")

# Análise de duplas
print_section("5. ANÁLISE DE DUPLAS FORMADAS")

print(f"\n{'Jogador':<15} | {'Parceiros':<10} | Quem foram")
print("-" * 90)

for pessoa in sorted(todos_participantes):
    parceiros = duplas_formadas.get(pessoa, set())
    num_parceiros = len(parceiros)
    
    if num_parceiros == 5:
        status = f"{Colors.GREEN}{num_parceiros}{Colors.END}"
    elif num_parceiros < 5:
        status = f"{Colors.RED}{num_parceiros}{Colors.END}"
        problemas[pessoa].append(f"Só formou {num_parceiros} duplas diferentes (esperado 5)")
    else:
        status = f"{Colors.YELLOW}{num_parceiros}{Colors.END}"
    
    parceiros_str = ', '.join(sorted(parceiros)) if parceiros else "Nenhum"
    print(f"{pessoa:<15} | {status:<10} | {parceiros_str}")

# Análise de adversários
print_section("6. ANÁLISE DE ADVERSÁRIOS ENFRENTADOS")

print(f"\n{'Jogador':<15} | {'Adversários':<12} | Status")
print("-" * 90)

for pessoa in sorted(todos_participantes):
    advs = adversarios.get(pessoa, set())
    num_advs = len(advs)
    
    jogos = jogos_por_pessoa.get(pessoa, 0)
    # Cada jogo enfrenta 2 adversários, então esperado = jogos * 2
    esperado = jogos * 2
    
    if num_advs == esperado:
        status = f"{Colors.GREEN}✓ {num_advs}/{esperado} OK{Colors.END}"
    else:
        status = f"{Colors.YELLOW}⚠ {num_advs}/{esperado}{Colors.END}"
    
    print(f"{pessoa:<15} | {num_advs:<12} | {status}")

# Verifica duplas repetidas
print_section("7. VERIFICAÇÃO DE DUPLAS REPETIDAS")

duplas_vistas = defaultdict(int)
duplas_repetidas = []

for rodada in rodadas:
    for confronto in rodada["confrontos"]:
        j1_d1 = confronto["dupla1"]["jogador1"]
        j2_d1 = confronto["dupla1"]["jogador2"]
        j1_d2 = confronto["dupla2"]["jogador1"]
        j2_d2 = confronto["dupla2"]["jogador2"]
        
        dupla1 = tuple(sorted([j1_d1, j2_d1]))
        dupla2 = tuple(sorted([j1_d2, j2_d2]))
        
        duplas_vistas[dupla1] += 1
        duplas_vistas[dupla2] += 1

for dupla, vezes in duplas_vistas.items():
    if vezes > 1:
        duplas_repetidas.append((dupla, vezes))
        print_error(f"Dupla {dupla[0]} & {dupla[1]} jogou {vezes} vezes (deveria ser 1)")

if not duplas_repetidas:
    print_success("Nenhuma dupla se repetiu ✓")

# Relatório de Erros
print_section("8. RESUMO DE ERROS ENCONTRADOS")

total_erros = 0

# Erros de distribuição de jogos
pessoas_com_erro = [p for p in todos_participantes if jogos_por_pessoa.get(p, 0) != 5]
if pessoas_com_erro:
    total_erros += len(pessoas_com_erro)
    print_error(f"PROBLEMA 1: {len(pessoas_com_erro)} pessoas NÃO jogaram 5 vezes")
    for pessoa in sorted(pessoas_com_erro):
        jogos = jogos_por_pessoa.get(pessoa, 0)
        print_info(f"  - {pessoa}: jogou {jogos} vezes (faltou {5 - jogos})")
else:
    print_success("Todas as pessoas jogaram exatamente 5 vezes")

# Duplas repetidas
if duplas_repetidas:
    total_erros += len(duplas_repetidas)
    print_error(f"PROBLEMA 2: {len(duplas_repetidas)} duplas se repetiram")
    for dupla, vezes in duplas_repetidas:
        print_info(f"  - {dupla[0]} & {dupla[1]}: {vezes} vezes")
else:
    print_success("Nenhuma dupla se repetiu")

# Teste de ranking
print_section("9. TESTE DO RANKING")

try:
    # Simula resultados
    import random
    for rodada in rodadas_data["rodadas"]:
        for confronto in rodada["confrontos"]:
            games_d1 = random.choice([6, 6, 6, 7])
            if games_d1 == 6:
                games_d2 = random.randint(0, 4)
            else:
                games_d2 = random.choice([5, 6])
            
            if random.random() > 0.5:
                games_d1, games_d2 = games_d2, games_d1
            
            confronto["resultado"]["games_dupla1"] = games_d1
            confronto["resultado"]["games_dupla2"] = games_d2
            confronto["resultado"]["finalizado"] = True
    
    # Calcula ranking
    ranking = calcular_ranking_individual(rodadas_data["rodadas"])
    
    # Cria jogadores_data
    jogadores_data = []
    for h in homens:
        jogadores_data.append({"nome": h, "sexo": "M", "confirmado": True})
    for m in mulheres:
        jogadores_data.append({"nome": m, "sexo": "F", "confirmado": True})
    
    ranking_separado = separar_ranking_por_genero(ranking, jogadores_data)
    
    # Verifica ranking
    total_no_ranking = len(ranking_separado["masculino"]) + len(ranking_separado["feminino"])
    
    print_info(f"Total no ranking: {total_no_ranking}/{len(todos_participantes)}")
    print_info(f"Masculino: {len(ranking_separado['masculino'])}/{len(homens)}")
    print_info(f"Feminino: {len(ranking_separado['feminino'])}/{len(mulheres)}")
    
    if total_no_ranking == len(todos_participantes):
        print_success("Ranking incluiu todos os participantes ✓")
    else:
        total_erros += 1
        print_error(f"Ranking incompleto: {total_no_ranking}/{len(todos_participantes)}")
    
    # Verifica se todos têm o número correto de jogos no ranking
    erros_ranking = []
    for jogador in ranking:
        jogos = jogador["jogos_realizados"]
        esperado = jogos_por_pessoa.get(jogador["nome"], 0)
        if jogos != esperado:
            erros_ranking.append(f"{jogador['nome']}: {jogos} no ranking, {esperado} nas rodadas")
    
    if erros_ranking:
        total_erros += len(erros_ranking)
        print_error(f"PROBLEMA 3: Inconsistência no ranking")
        for erro in erros_ranking:
            print_info(f"  - {erro}")
    else:
        print_success("Ranking consistente com as rodadas ✓")
        
except Exception as e:
    print_error(f"ERRO ao calcular ranking: {str(e)}")
    import traceback
    traceback.print_exc()
    total_erros += 1

# Conclusão Final
print_header("CONCLUSÃO FINAL")

print(f"\n{Colors.BOLD}Configuração testada: 9 Homens + 10 Mulheres = 19 participantes{Colors.END}\n")

if total_erros == 0:
    print(f"{Colors.GREEN}{Colors.BOLD}✓ SUCESSO! Sistema funciona perfeitamente!{Colors.END}\n")
else:
    print(f"{Colors.RED}{Colors.BOLD}✗ FALHOU! Encontrados {total_erros} problema(s) crítico(s){Colors.END}\n")
    
    print(f"{Colors.YELLOW}MOTIVOS DA FALHA:{Colors.END}")
    print_info("1. Algoritmo não consegue distribuir 5 jogos igualmente para 9H + 10M")
    print_info("2. Número ímpar de participantes causa desbalanceamento")
    print_info("3. Diferença entre H e M (9 vs 10) dificulta matching perfeito")
    print_info("4. Com 19 pessoas, sobra sempre 1 descansando por rodada")
    print_info("5. Algoritmo atual não otimiza bem para números ímpares desbalanceados")
    
    print(f"\n{Colors.CYAN}RECOMENDAÇÕES:{Colors.END}")
    print_info("✓ Use 8H + 8M = 16 participantes (deixar 3 como reserva)")
    print_info("✓ Use 10H + 10M = 20 participantes (adicionar 1 pessoa)")
    print_info("✓ Use 6H + 6M = 12 participantes (deixar 7 como reserva)")
    print_info("✗ NÃO use 9H + 10M = 19 (não funciona corretamente)")

print(f"\n{Colors.CYAN}{'='*90}{Colors.END}\n")

