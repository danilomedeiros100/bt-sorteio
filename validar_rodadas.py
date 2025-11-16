#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para validar rodadas geradas
"""

import json
from collections import defaultdict

def validar_rodadas(arquivo):
    """Valida se as rodadas estão corretas"""
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    categoria = dados.get('categoria')
    total_jogadores = dados.get('total_jogadores')
    jogos_por_pessoa = dados.get('jogos_por_pessoa')
    rodadas = dados.get('rodadas', [])
    
    print(f"=== VALIDAÇÃO: {categoria.upper()} ===")
    print(f"Total de jogadores: {total_jogadores}")
    print(f"Jogos por pessoa esperado: {jogos_por_pessoa}")
    print(f"Total de rodadas: {len(rodadas)}\n")
    
    # Contadores
    jogos_por_jogador = defaultdict(int)
    duplas_usadas = set()
    jogadores_encontrados = set()
    erros = []
    
    # Analisa cada rodada
    for rodada in rodadas:
        rodada_num = rodada.get('numero')
        confrontos = rodada.get('confrontos', [])
        descansando = rodada.get('descansando', [])
        
        print(f"--- Rodada {rodada_num} ---")
        print(f"  Confrontos: {len(confrontos)}")
        print(f"  Descansando: {len(descansando)}")
        
        # Analisa cada confronto
        for confronto in confrontos:
            dupla1 = confronto.get('dupla1', {})
            dupla2 = confronto.get('dupla2')
            
            if not dupla1:
                erros.append(f"Rodada {rodada_num}: Dupla1 vazia")
                continue
            
            j1_d1 = dupla1.get('jogador1')
            j2_d1 = dupla1.get('jogador2')
            
            if not j1_d1 or not j2_d1:
                erros.append(f"Rodada {rodada_num}: Dupla1 incompleta")
                continue
            
            jogadores_encontrados.add(j1_d1)
            jogadores_encontrados.add(j2_d1)
            jogos_por_jogador[j1_d1] += 1
            jogos_por_jogador[j2_d1] += 1
            
            # Cria tupla da dupla (ordenada para evitar duplicatas)
            dupla1_tuple = tuple(sorted([j1_d1, j2_d1]))
            
            if dupla1_tuple in duplas_usadas:
                erros.append(f"Rodada {rodada_num}: Dupla repetida: {dupla1_tuple}")
            else:
                duplas_usadas.add(dupla1_tuple)
            
            if dupla2:
                j1_d2 = dupla2.get('jogador1')
                j2_d2 = dupla2.get('jogador2')
                
                if not j1_d2 or not j2_d2:
                    erros.append(f"Rodada {rodada_num}: Dupla2 incompleta")
                    continue
                
                jogadores_encontrados.add(j1_d2)
                jogadores_encontrados.add(j2_d2)
                jogos_por_jogador[j1_d2] += 1
                jogos_por_jogador[j2_d2] += 1
                
                # Verifica se há jogadores repetidos entre as duplas
                if {j1_d1, j2_d1} & {j1_d2, j2_d2}:
                    erros.append(f"Rodada {rodada_num}: Jogador repetido no mesmo confronto")
                
                dupla2_tuple = tuple(sorted([j1_d2, j2_d2]))
                if dupla2_tuple in duplas_usadas:
                    erros.append(f"Rodada {rodada_num}: Dupla repetida: {dupla2_tuple}")
                else:
                    duplas_usadas.add(dupla2_tuple)
    
    print("\n=== RESULTADO DA VALIDAÇÃO ===\n")
    
    # Verifica se todos os jogadores jogaram a quantidade correta
    print("Jogos por jogador:")
    problemas_jogos = []
    for jogador in sorted(jogadores_encontrados):
        jogos = jogos_por_jogador[jogador]
        status = "✅" if jogos == jogos_por_pessoa else "❌"
        print(f"  {status} {jogador}: {jogos} jogos (esperado: {jogos_por_pessoa})")
        if jogos != jogos_por_pessoa:
            problemas_jogos.append(f"{jogador}: {jogos} jogos (esperado: {jogos_por_pessoa})")
    
    # Verifica se todos os jogadores foram encontrados
    if len(jogadores_encontrados) != total_jogadores:
        erros.append(f"Total de jogadores encontrados ({len(jogadores_encontrados)}) diferente do esperado ({total_jogadores})")
    
    # Estatísticas
    print(f"\nTotal de duplas únicas: {len(duplas_usadas)}")
    total_duplas_esperadas = (total_jogadores * jogos_por_pessoa) // 2
    print(f"Total de duplas esperadas: {total_duplas_esperadas}")
    
    if len(duplas_usadas) != total_duplas_esperadas:
        erros.append(f"Total de duplas ({len(duplas_usadas)}) diferente do esperado ({total_duplas_esperadas})")
    
    # Resumo
    print("\n=== RESUMO ===")
    if erros:
        print(f"❌ ERROS ENCONTRADOS: {len(erros)}")
        for erro in erros:
            print(f"  - {erro}")
    else:
        print("✅ Nenhum erro de estrutura encontrado")
    
    if problemas_jogos:
        print(f"\n❌ PROBLEMAS COM QUANTIDADE DE JOGOS: {len(problemas_jogos)}")
        for problema in problemas_jogos:
            print(f"  - {problema}")
    else:
        print("\n✅ Todos os jogadores jogaram a quantidade correta de vezes")
    
    if not erros and not problemas_jogos:
        print("\n🎉 VALIDAÇÃO COMPLETA: Tudo está correto!")
        return True
    else:
        print("\n⚠️ VALIDAÇÃO FALHOU: Há problemas que precisam ser corrigidos")
        return False

if __name__ == "__main__":
    validar_rodadas("data/rodadas_masculino.json")




