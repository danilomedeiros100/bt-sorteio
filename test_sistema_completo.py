#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste completo do sistema de 5 rodadas"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def limpar_dados():
    """Limpa dados antigos"""
    print("🧹 Limpando dados antigos...")
    import os
    arquivos = ["data/jogadores.json", "data/rodadas.json", "data/ranking.json"]
    for arq in arquivos:
        if os.path.exists(arq):
            os.remove(arq)
    print("✅ Dados limpos\n")

def cadastrar_jogadores():
    """Cadastra jogadores de teste"""
    print("👥 Cadastrando jogadores...")
    
    homens = [f"Homem{i}" for i in range(1, 13)]  # 12 homens
    mulheres = [f"Mulher{i}" for i in range(1, 13)]  # 12 mulheres
    
    jogadores = []
    for nome in homens:
        jogadores.append({"nome": nome, "sexo": "M", "confirmado": True})
    
    for nome in mulheres:
        jogadores.append({"nome": nome, "sexo": "F", "confirmado": True})
    
    # Salva direto no arquivo
    with open("data/jogadores.json", "w", encoding="utf-8") as f:
        json.dump(jogadores, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(jogadores)} jogadores cadastrados (12H + 12M)\n")
    return jogadores

def gerar_rodadas():
    """Gera as 5 rodadas"""
    print("🎲 Gerando 5 rodadas...")
    
    response = requests.post(f"{BASE_URL}/gerar-rodadas")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['total_rodadas']} rodadas geradas com sucesso!\n")
        return True
    else:
        print(f"❌ Erro: {response.json()}\n")
        return False

def simular_resultados():
    """Simula resultados aleatórios"""
    print("📝 Simulando resultados...")
    
    with open("data/rodadas.json", "r", encoding="utf-8") as f:
        dados_rodadas = json.load(f)
    
    import random
    total_jogos = 0
    
    for rodada_idx, rodada in enumerate(dados_rodadas['rodadas']):
        for confronto_idx, confronto in enumerate(rodada['confrontos']):
            # Gera placar aleatório (6-0, 6-1, 6-2, 6-3, 6-4, 7-5, 7-6)
            placares = [
                (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
                (7, 5), (7, 6),
                (0, 6), (1, 6), (2, 6), (3, 6), (4, 6),
                (5, 7), (6, 7)
            ]
            games_d1, games_d2 = random.choice(placares)
            
            # Salva via API
            response = requests.post(
                f"{BASE_URL}/salvar-resultado",
                data={
                    "rodada": rodada_idx + 1,
                    "confronto": confronto_idx,
                    "games_dupla1": games_d1,
                    "games_dupla2": games_d2
                }
            )
            
            if response.status_code == 200:
                total_jogos += 1
                dupla1 = f"{confronto['dupla1']['jogador1']}/{confronto['dupla1']['jogador2']}"
                dupla2 = f"{confronto['dupla2']['jogador1']}/{confronto['dupla2']['jogador2']}"
                print(f"  Rodada {rodada_idx+1} | Quadra {confronto['quadra']}: {dupla1} {games_d1}x{games_d2} {dupla2}")
            else:
                print(f"  ❌ Erro ao salvar resultado: {response.json()}")
    
    print(f"\n✅ {total_jogos} resultados salvos!\n")

def ver_ranking():
    """Exibe o ranking"""
    print("🏆 RANKING FINAL:")
    print("=" * 80)
    
    with open("data/ranking.json", "r", encoding="utf-8") as f:
        ranking = json.load(f)
    
    print("\n👨 MASCULINO (Top 5):")
    print("-" * 80)
    for i, jogador in enumerate(ranking['masculino'][:5], 1):
        print(f"  {i}º {jogador['nome']:<15} | {jogador['vitorias']}V {jogador['derrotas']}D | "
              f"Saldo: {jogador['saldo_games']:+3} | GF:{jogador['games_feitos']} GS:{jogador['games_sofridos']}")
    
    print("\n👩 FEMININO (Top 5):")
    print("-" * 80)
    for i, jogadora in enumerate(ranking['feminino'][:5], 1):
        print(f"  {i}º {jogadora['nome']:<15} | {jogadora['vitorias']}V {jogadora['derrotas']}D | "
              f"Saldo: {jogadora['saldo_games']:+3} | GF:{jogadora['games_feitos']} GS:{jogadora['games_sofridos']}")
    
    print("\n" + "=" * 80)

def main():
    print("\n" + "=" * 80)
    print("TESTE COMPLETO DO SISTEMA DE 5 RODADAS")
    print("=" * 80 + "\n")
    
    # 1. Limpar dados
    limpar_dados()
    
    # 2. Cadastrar jogadores
    cadastrar_jogadores()
    
    # 3. Gerar rodadas
    if not gerar_rodadas():
        print("❌ Falha ao gerar rodadas. Abortando teste.")
        return
    
    # 4. Simular resultados
    simular_resultados()
    
    # 5. Ver ranking
    ver_ranking()
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\n📱 Acesse no navegador:")
    print(f"   • Rodadas: {BASE_URL}/rodadas")
    print(f"   • Ranking: {BASE_URL}/ranking-individual")
    print(f"   • Resultados: {BASE_URL}/registro-resultados")
    print()

if __name__ == "__main__":
    main()





