#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação Completa do Sistema de 5 Rodadas
Testa diferentes números de participantes e valida:
- Todos jogam 5 jogos
- Nenhuma dupla se repete
- Ranking funciona corretamente
- Identifica número mínimo/máximo de participantes
"""

import sys
import json
from collections import defaultdict
from utils.sorteio_rodadas import gerar_5_rodadas, calcular_ranking_individual, separar_ranking_por_genero

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def gerar_nomes_teste(num_homens, num_mulheres):
    """Gera nomes fictícios para teste"""
    homens = [f"Homem{i+1}" for i in range(num_homens)]
    mulheres = [f"Mulher{i+1}" for i in range(num_mulheres)]
    return homens, mulheres

def validar_rodadas(rodadas_data, num_homens, num_mulheres):
    """
    Valida se as rodadas geradas atendem todos os critérios
    Retorna: (sucesso, erros_encontrados)
    """
    erros = []
    warnings = []
    
    rodadas = rodadas_data.get("rodadas", [])
    total_participantes = num_homens + num_mulheres
    
    # 1. Verifica se gerou 5 rodadas
    if len(rodadas) != 5:
        erros.append(f"Deveria ter 5 rodadas, mas tem {len(rodadas)}")
    
    # 2. Conta jogos por pessoa
    jogos_por_pessoa = defaultdict(int)
    duplas_vistas = set()
    confrontos_vistos = set()
    
    for rodada in rodadas:
        for confronto in rodada["confrontos"]:
            # Jogadores da dupla 1
            j1_d1 = confronto["dupla1"]["jogador1"]
            j2_d1 = confronto["dupla1"]["jogador2"]
            jogos_por_pessoa[j1_d1] += 1
            jogos_por_pessoa[j2_d1] += 1
            
            # Jogadores da dupla 2
            j1_d2 = confronto["dupla2"]["jogador1"]
            j2_d2 = confronto["dupla2"]["jogador2"]
            jogos_por_pessoa[j1_d2] += 1
            jogos_por_pessoa[j2_d2] += 1
            
            # Verifica duplas repetidas
            dupla1 = tuple(sorted([j1_d1, j2_d1]))
            dupla2 = tuple(sorted([j1_d2, j2_d2]))
            
            if dupla1 in duplas_vistas:
                erros.append(f"Dupla repetida: {dupla1}")
            else:
                duplas_vistas.add(dupla1)
            
            if dupla2 in duplas_vistas:
                erros.append(f"Dupla repetida: {dupla2}")
            else:
                duplas_vistas.add(dupla2)
            
            # Verifica confrontos repetidos
            confronto_key = tuple(sorted([dupla1, dupla2]))
            if confronto_key in confrontos_vistos:
                erros.append(f"Confronto repetido: {dupla1} vs {dupla2}")
            else:
                confrontos_vistos.add(confronto_key)
    
    # 3. Verifica se todos jogam 5 vezes
    for pessoa, num_jogos in jogos_por_pessoa.items():
        if num_jogos != 5:
            erros.append(f"{pessoa} jogou {num_jogos} vezes (deveria ser 5)")
    
    # 4. Verifica se todos os participantes estão jogando
    todos_jogadores = set()
    for rodada in rodadas:
        for confronto in rodada["confrontos"]:
            todos_jogadores.add(confronto["dupla1"]["jogador1"])
            todos_jogadores.add(confronto["dupla1"]["jogador2"])
            todos_jogadores.add(confronto["dupla2"]["jogador1"])
            todos_jogadores.add(confronto["dupla2"]["jogador2"])
        
        # Adiciona os que estão descansando
        for jogador in rodada.get("descansando", []):
            todos_jogadores.add(jogador)
    
    if len(todos_jogadores) != total_participantes:
        erros.append(f"Nem todos participantes estão nas rodadas: {len(todos_jogadores)}/{total_participantes}")
    
    # 5. Verifica distribuição de descanso (se houver ímpar)
    if total_participantes % 2 != 0:
        descansos_por_pessoa = defaultdict(int)
        for rodada in rodadas:
            for jogador in rodada.get("descansando", []):
                descansos_por_pessoa[jogador] += 1
        
        # Todos devem descansar 1 vez se ímpar
        for pessoa in todos_jogadores:
            descansos = descansos_por_pessoa.get(pessoa, 0)
            if descansos != 1:
                warnings.append(f"{pessoa} descansou {descansos} vez(es) (esperado: 1)")
    
    return len(erros) == 0, erros, warnings

def simular_resultados(rodadas_data):
    """Simula resultados aleatórios para teste"""
    import random
    
    for rodada in rodadas_data["rodadas"]:
        for confronto in rodada["confrontos"]:
            # Simula placar 6-0 a 6-4
            games_d1 = random.choice([6, 6, 6, 7])
            if games_d1 == 6:
                games_d2 = random.randint(0, 4)
            else:  # 7-5 ou 7-6
                games_d2 = random.choice([5, 6])
            
            # 50% chance de inverter
            if random.random() > 0.5:
                games_d1, games_d2 = games_d2, games_d1
            
            confronto["resultado"]["games_dupla1"] = games_d1
            confronto["resultado"]["games_dupla2"] = games_d2
            confronto["resultado"]["finalizado"] = True

def testar_cenario(num_homens, num_mulheres):
    """
    Testa um cenário específico de número de participantes
    Retorna: (sucesso, mensagem, detalhes)
    """
    total = num_homens + num_mulheres
    print(f"\n{Colors.BOLD}Testando: {num_homens}H + {num_mulheres}F = {total} participantes{Colors.END}")
    print("-" * 80)
    
    try:
        # 1. Gera nomes
        homens, mulheres = gerar_nomes_teste(num_homens, num_mulheres)
        
        # 2. Tenta gerar rodadas
        print_info(f"Gerando 5 rodadas para {num_homens}H + {num_mulheres}F...")
        rodadas_data = gerar_5_rodadas(homens, mulheres)
        
        if not rodadas_data:
            print_error("FALHOU: Não conseguiu gerar rodadas")
            return False, "Impossível gerar rodadas", None
        
        # 3. Valida as rodadas
        print_info("Validando restrições...")
        sucesso, erros, warnings = validar_rodadas(rodadas_data, num_homens, num_mulheres)
        
        if not sucesso:
            print_error("FALHOU na validação:")
            for erro in erros:
                print(f"  - {erro}")
            return False, f"Falha na validação: {len(erros)} erro(s)", {"erros": erros}
        
        if warnings:
            for warning in warnings:
                print_warning(warning)
        
        # 4. Simula resultados
        print_info("Simulando resultados...")
        simular_resultados(rodadas_data)
        
        # 5. Calcula ranking
        print_info("Calculando ranking...")
        ranking = calcular_ranking_individual(rodadas_data["rodadas"])
        
        # Cria jogadores_data para separação por gênero
        jogadores_data = []
        for h in homens:
            jogadores_data.append({"nome": h, "sexo": "M", "confirmado": True})
        for m in mulheres:
            jogadores_data.append({"nome": m, "sexo": "F", "confirmado": True})
        
        ranking_separado = separar_ranking_por_genero(ranking, jogadores_data)
        
        # 6. Valida ranking
        total_no_ranking = len(ranking_separado["masculino"]) + len(ranking_separado["feminino"])
        if total_no_ranking != total:
            print_error(f"FALHOU: Ranking tem {total_no_ranking} jogadores, esperado {total}")
            return False, f"Ranking incompleto: {total_no_ranking}/{total}", None
        
        # Verifica se todos têm 5 jogos
        for jogador in ranking:
            if jogador["jogos_realizados"] != 5:
                print_error(f"FALHOU: {jogador['nome']} tem {jogador['jogos_realizados']} jogos (esperado 5)")
                return False, "Nem todos jogaram 5 vezes no ranking", None
        
        # SUCESSO!
        print_success(f"SUCESSO! Todas as validações passaram")
        print_info(f"  → {len(rodadas_data['rodadas'])} rodadas geradas")
        print_info(f"  → {total_no_ranking} jogadores no ranking (todos com 5 jogos)")
        print_info(f"  → Masculino: {len(ranking_separado['masculino'])} | Feminino: {len(ranking_separado['feminino'])}")
        
        return True, "Sucesso completo", {
            "rodadas": len(rodadas_data['rodadas']),
            "ranking_masc": len(ranking_separado['masculino']),
            "ranking_fem": len(ranking_separado['feminino'])
        }
        
    except Exception as e:
        print_error(f"ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Exceção: {str(e)}", None

def main():
    print_header("TESTE DE VALIDAÇÃO COMPLETA - SISTEMA DE 5 RODADAS")
    
    # Cenários para testar
    cenarios = []
    
    # Cenários balanceados (mesmo número H e M)
    print_header("CENÁRIOS BALANCEADOS (H = M)")
    for n in range(2, 16):  # De 2 a 15 de cada
        cenarios.append((n, n))
    
    # Cenários com diferença pequena (±1, ±2)
    print_header("CENÁRIOS COM PEQUENA DIFERENÇA (±1, ±2)")
    for base in range(4, 12):
        cenarios.append((base, base + 1))
        cenarios.append((base, base + 2))
        cenarios.append((base + 1, base))
        cenarios.append((base + 2, base))
    
    # Cenários extremos
    print_header("CENÁRIOS EXTREMOS")
    cenarios.extend([
        (1, 1),   # Mínimo absoluto
        (20, 20), # Muitos participantes
        (3, 7),   # Diferença grande
        (7, 3),   # Diferença grande invertida
        (5, 10),  # Mais mulheres
        (10, 5),  # Mais homens
    ])
    
    # Resultados
    sucessos = []
    falhas = []
    
    # Executa todos os testes
    for num_h, num_m in cenarios:
        sucesso, msg, detalhes = testar_cenario(num_h, num_m)
        
        if sucesso:
            sucessos.append((num_h, num_m, detalhes))
        else:
            falhas.append((num_h, num_m, msg))
    
    # Relatório Final
    print_header("RELATÓRIO FINAL")
    
    print(f"\n{Colors.BOLD}RESUMO:{Colors.END}")
    print(f"  {Colors.GREEN}✓ Sucessos: {len(sucessos)}{Colors.END}")
    print(f"  {Colors.RED}✗ Falhas: {len(falhas)}{Colors.END}")
    print(f"  📊 Total de cenários testados: {len(cenarios)}")
    
    # Sucessos
    if sucessos:
        print(f"\n{Colors.BOLD}{Colors.GREEN}CONFIGURAÇÕES QUE FUNCIONAM:{Colors.END}")
        for num_h, num_m, detalhes in sucessos[:10]:  # Mostra os primeiros 10
            total = num_h + num_m
            print(f"  ✓ {num_h}H + {num_m}M = {total} participantes")
        if len(sucessos) > 10:
            print(f"  ... e mais {len(sucessos) - 10} configurações")
    
    # Falhas
    if falhas:
        print(f"\n{Colors.BOLD}{Colors.RED}CONFIGURAÇÕES QUE FALHARAM:{Colors.END}")
        for num_h, num_m, msg in falhas:
            total = num_h + num_m
            print(f"  ✗ {num_h}H + {num_m}M = {total} participantes")
            print(f"    Motivo: {msg}")
    
    # Análise de Limites
    print(f"\n{Colors.BOLD}{Colors.CYAN}ANÁLISE DE LIMITES:{Colors.END}")
    
    # Mínimos
    sucessos_balanceados = [(h, m) for h, m, _ in sucessos if h == m]
    if sucessos_balanceados:
        min_balanceado = min(sucessos_balanceados, key=lambda x: x[0])
        print_success(f"Mínimo balanceado que funciona: {min_balanceado[0]}H + {min_balanceado[1]}M = {sum(min_balanceado)} total")
    
    # Máximos
    if sucessos:
        max_total = max(sucessos, key=lambda x: x[0] + x[1])
        print_success(f"Máximo testado que funciona: {max_total[0]}H + {max_total[1]}M = {max_total[0] + max_total[1]} total")
    
    # Recomendações
    print(f"\n{Colors.BOLD}{Colors.YELLOW}RECOMENDAÇÕES:{Colors.END}")
    
    sucessos_ordenados = sorted(sucessos, key=lambda x: x[0] + x[1])
    if sucessos_ordenados:
        min_config = sucessos_ordenados[0]
        print_info(f"Mínimo recomendado: {min_config[0]}H + {min_config[1]}M = {min_config[0] + min_config[1]} participantes")
        
        # Faixa ideal (8-16 participantes)
        ideais = [s for s in sucessos if 8 <= (s[0] + s[1]) <= 16]
        if ideais:
            print_info(f"Faixa ideal de participantes: 8-16 ({len(ideais)} configurações funcionam)")
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}\n")

if __name__ == "__main__":
    main()

