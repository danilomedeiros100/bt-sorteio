#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para validar rodadas feminino
Verifica:
1. Se cada jogador joga exatamente o número especificado de vezes
2. Se nenhuma dupla se repete
"""

import json
from collections import defaultdict, Counter

def validar_rodadas_feminino(arquivo="data/rodadas_feminino.json"):
    """Valida as rodadas geradas para categoria feminino"""
    
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    categoria = dados.get("categoria", "feminino")
    total_jogadores = dados.get("total_jogadores", 0)
    jogos_por_pessoa = dados.get("jogos_por_pessoa", 0)
    rodadas = dados.get("rodadas", [])
    
    print("=" * 60)
    print("📊 VALIDAÇÃO DE RODADAS - CATEGORIA FEMININO")
    print("=" * 60)
    print(f"\n📋 Configuração:")
    print(f"   - Total de jogadores: {total_jogadores}")
    print(f"   - Jogos por pessoa: {jogos_por_pessoa}")
    print(f"   - Total de rodadas: {len(rodadas)}")
    print()
    
    # Contador de jogos por jogador
    jogos_por_jogador = defaultdict(int)
    
    # Lista de todas as duplas (normalizadas)
    todas_duplas = []
    
    # Lista de todos os jogadores
    todos_jogadores = set()
    
    # Processa cada rodada
    for rodada in rodadas:
        rodada_num = rodada.get("numero", 0)
        confrontos = rodada.get("confrontos", [])
        
        print(f"🔍 Rodada {rodada_num}: {len(confrontos)} confronto(s)")
        
        for confronto in confrontos:
            dupla1 = confronto.get("dupla1")
            dupla2 = confronto.get("dupla2")
            
            if not dupla1:
                continue
            
            # Processa dupla1
            j1_d1 = dupla1.get("jogador1")
            j2_d1 = dupla1.get("jogador2")
            
            if j1_d1 and j2_d1:
                todos_jogadores.add(j1_d1)
                todos_jogadores.add(j2_d1)
                jogos_por_jogador[j1_d1] += 1
                jogos_por_jogador[j2_d1] += 1
                
                # Normaliza dupla (ordem alfabética)
                dupla_normalizada = tuple(sorted([j1_d1, j2_d1]))
                todas_duplas.append(dupla_normalizada)
            
            # Processa dupla2 (se existir)
            if dupla2:
                j1_d2 = dupla2.get("jogador1")
                j2_d2 = dupla2.get("jogador2")
                
                if j1_d2 and j2_d2:
                    todos_jogadores.add(j1_d2)
                    todos_jogadores.add(j2_d2)
                    jogos_por_jogador[j1_d2] += 1
                    jogos_por_jogador[j2_d2] += 1
                    
                    # Normaliza dupla (ordem alfabética)
                    dupla_normalizada = tuple(sorted([j1_d2, j2_d2]))
                    todas_duplas.append(dupla_normalizada)
    
    print()
    print("=" * 60)
    print("✅ VALIDAÇÃO 1: JOGOS POR JOGADOR")
    print("=" * 60)
    
    todos_corretos = True
    for jogador in sorted(todos_jogadores):
        jogos = jogos_por_jogador[jogador]
        status = "✅" if jogos == jogos_por_pessoa else "❌"
        if jogos != jogos_por_pessoa:
            todos_corretos = False
        print(f"   {status} {jogador}: {jogos} jogos (esperado: {jogos_por_pessoa})")
    
    if todos_corretos:
        print(f"\n✅ SUCESSO: Todos os jogadores jogam exatamente {jogos_por_pessoa} vezes!")
    else:
        print(f"\n❌ ERRO: Alguns jogadores não estão jogando {jogos_por_pessoa} vezes!")
    
    print()
    print("=" * 60)
    print("✅ VALIDAÇÃO 2: DUPLAS REPETIDAS")
    print("=" * 60)
    
    # Conta ocorrências de cada dupla
    contador_duplas = Counter(todas_duplas)
    duplas_repetidas = {dupla: count for dupla, count in contador_duplas.items() if count > 1}
    
    if duplas_repetidas:
        print(f"\n❌ ERRO: Encontradas {len(duplas_repetidas)} dupla(s) repetida(s):")
        for dupla, count in sorted(duplas_repetidas.items()):
            print(f"   ❌ {dupla[0]} & {dupla[1]}: aparece {count} vez(es)")
        todos_corretos = False
    else:
        print(f"\n✅ SUCESSO: Nenhuma dupla se repete!")
        print(f"   Total de duplas únicas: {len(contador_duplas)}")
    
    print()
    print("=" * 60)
    print("📊 ESTATÍSTICAS")
    print("=" * 60)
    print(f"   - Total de jogadores: {len(todos_jogadores)}")
    print(f"   - Total de duplas geradas: {len(todas_duplas)}")
    print(f"   - Duplas únicas: {len(contador_duplas)}")
    print(f"   - Duplas esperadas: {(len(todos_jogadores) * jogos_por_pessoa) // 2}")
    
    print()
    print("=" * 60)
    if todos_corretos and not duplas_repetidas:
        print("🎉 VALIDAÇÃO COMPLETA: TUDO CORRETO! ✅")
    else:
        print("⚠️  VALIDAÇÃO: ENCONTRADOS PROBLEMAS! ❌")
    print("=" * 60)
    
    return todos_corretos and not duplas_repetidas

if __name__ == "__main__":
    validar_rodadas_feminino()




