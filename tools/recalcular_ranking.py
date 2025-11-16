#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recalcular o ranking a partir das rodadas atualizadas
"""

import json
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sorteio_rodadas import calcular_ranking_individual, separar_ranking_por_genero

def carregar_jogadores():
    """Carrega jogadores do arquivo JSON"""
    with open("data/jogadores.json", "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_rodadas():
    """Carrega rodadas do arquivo JSON"""
    with open("data/rodadas_mista.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_ranking(dados):
    """Salva o ranking no arquivo JSON"""
    with open("data/ranking.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    print("Recalculando ranking...")
    
    # Carrega dados
    jogadores_data = carregar_jogadores()
    dados_rodadas = carregar_rodadas()
    
    # Calcula ranking individual
    ranking_individual = calcular_ranking_individual(dados_rodadas["rodadas"])
    
    # Separa por gênero
    ranking_por_genero = separar_ranking_por_genero(ranking_individual, jogadores_data)
    
    # Adiciona metadados
    ranking_final = {
        "categoria": "mista",
        "ultima_atualizacao": datetime.now().isoformat(),
        "masculino": ranking_por_genero["masculino"],
        "feminino": ranking_por_genero["feminino"]
    }
    
    # Salva
    salvar_ranking(ranking_final)
    
    print("✓ Ranking recalculado e salvo em data/ranking.json")
    print(f"  - Masculino: {len(ranking_final['masculino'])} jogadores")
    print(f"  - Feminino: {len(ranking_final['feminino'])} jogadoras")

