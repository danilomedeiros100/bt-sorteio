#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair rodadas de HTML e converter para JSON no formato rodadas_mista.json
"""

import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

def extrair_rodadas_do_html(html_content):
    """Extrai rodadas do HTML e retorna no formato JSON"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extrair informações gerais
    data_sorteio = None
    info_geral = soup.find('p', string=re.compile('Torneio gerado em:'))
    if info_geral:
        data_text = info_geral.get_text()
        match = re.search(r'(\d{4}-\d{2}-\d{2})', data_text)
        if match:
            data_sorteio = match.group(1) + "T00:00:00"
    
    # Contar homens e mulheres
    total_homens = 12
    total_mulheres = 12
    
    # Encontrar todas as rodadas
    rodadas = []
    rodada_cards = soup.find_all('div', class_='rodada-card')
    
    for rodada_card in rodada_cards:
        # Extrair número da rodada
        h2 = rodada_card.find('h2')
        if not h2:
            continue
            
        numero_match = re.search(r'RODADA (\d+)', h2.get_text())
        if not numero_match:
            continue
            
        numero_rodada = int(numero_match.group(1))
        
        # Extrair confrontos
        confrontos = []
        matchup_containers = rodada_card.find_all('div', class_='matchup-container')
        
        for matchup in matchup_containers:
            # Extrair quadra
            quadra_badge = matchup.find('span', class_='badge')
            quadra = 1
            if quadra_badge:
                quadra_text = quadra_badge.get_text()
                quadra_match = re.search(r'Quadra (\d+)', quadra_text)
                if quadra_match:
                    quadra = int(quadra_match.group(1))
            
            # Extrair jogadores do data-jogadores
            data_jogadores = matchup.get('data-jogadores', '')
            if data_jogadores:
                jogadores = [j.strip() for j in data_jogadores.split(',')]
                if len(jogadores) == 4:
                    dupla1 = {
                        "jogador1": jogadores[0],
                        "jogador2": jogadores[1]
                    }
                    dupla2 = {
                        "jogador1": jogadores[2],
                        "jogador2": jogadores[3]
                    }
                    
                    confronto = {
                        "dupla1": dupla1,
                        "dupla2": dupla2,
                        "resultado": {
                            "games_dupla1": 0,
                            "games_dupla2": 0,
                            "finalizado": False
                        },
                        "quadra": quadra
                    }
                    confrontos.append(confronto)
        
        # Extrair jogadores descansando
        descansando = []
        descansando_div = rodada_card.find('div', class_='descansando-item')
        if descansando_div:
            data_descansando = descansando_div.get('data-descansando', '')
            if data_descansando:
                descansando = [j.strip() for j in data_descansando.split(',')]
        
        rodada = {
            "numero": numero_rodada,
            "confrontos": confrontos,
            "descansando": descansando
        }
        rodadas.append(rodada)
    
    # Ordenar rodadas por número
    rodadas.sort(key=lambda x: x['numero'])
    
    # Criar estrutura final
    resultado = {
        "categoria": "mista",
        "data_sorteio": data_sorteio or datetime.now().isoformat(),
        "total_homens": total_homens,
        "total_mulheres": total_mulheres,
        "total_rodadas": len(rodadas),
        "rodadas": rodadas
    }
    
    return resultado

if __name__ == '__main__':
    # Ler HTML do stdin ou arquivo
    import sys
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        html_content = sys.stdin.read()
    
    resultado = extrair_rodadas_do_html(html_content)
    
    # Salvar JSON
    output_file = 'data/rodadas_mista_novo.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"Rodadas extraídas e salvas em {output_file}")
    print(f"Total de rodadas: {len(resultado['rodadas'])}")

