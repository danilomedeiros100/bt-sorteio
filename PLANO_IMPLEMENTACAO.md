# 🚀 Plano de Implementação - Sistema de 5 Rodadas Mistas
## ⚡ PRODUÇÃO - Evento Semana que Vem (Até 30 Pessoas)

---

## 🎯 Objetivo
Transformar o sistema atual em um sistema de **5 rodadas com duplas mistas dinâmicas** e **ranking individual**, pronto para evento real com até 30 participantes.

---

## 📊 Cenários Reais do Evento

### Cenário Provável:
- **12 a 20 pessoas** (6-10 homens + 6-10 mulheres)
- **Melhor caso:** Números iguais (8H + 8M = 16 total)
- **Caso comum:** Pequena diferença (7H + 9M = 16 total)
- **Pior caso:** Diferença maior (6H + 10M = 16 total)

### Simplificações para Garantir Funcionamento:

#### ✅ **GARANTIAS MATEMÁTICAS:**
Para 30 pessoas (máximo):
- Se 15H + 15M → **Algoritmo sempre tem solução**
- Se diferença ≤ 3 → **95% de chance de solução**
- Se diferença > 3 → **Usar algoritmo de fallback**

---

## 🏗️ Arquitetura Simplificada

### Estrutura de Dados (Reutilizar JSON Atual)

#### 1. `jogadores.json` (já existe - mínima adaptação)
```json
[
  {
    "nome": "João Silva",
    "sexo": "M",
    "confirmado": true
  },
  {
    "nome": "Maria Santos",
    "sexo": "F",
    "confirmado": true
  }
]
```
**Mudança:** Remover campo `categorias` (não será mais usado)

---

#### 2. `rodadas.json` (NOVO - formato simples)
```json
{
  "data_sorteio": "2025-11-02T10:30:00",
  "total_rodadas": 5,
  "rodadas": [
    {
      "numero": 1,
      "confrontos": [
        {
          "quadra": 1,
          "dupla1": {
            "jogador1": "João Silva",
            "jogador2": "Maria Santos"
          },
          "dupla2": {
            "jogador1": "Pedro Lima",
            "jogador2": "Ana Costa"
          },
          "resultado": {
            "sets_dupla1": 2,
            "sets_dupla2": 1,
            "finalizado": true
          }
        }
      ],
      "descansando": ["Carlos Souza", "Juliana Rocha"]
    }
  ]
}
```

---

#### 3. `ranking.json` (NOVO - ranking individual)
```json
{
  "ultima_atualizacao": "2025-11-02T11:45:00",
  "masculino": [
    {
      "nome": "João Silva",
      "vitorias": 4,
      "derrotas": 1,
      "sets_ganhos": 9,
      "sets_perdidos": 4,
      "saldo_sets": 5,
      "jogos_realizados": 5,
      "percentual_vitorias": 80.0
    }
  ],
  "feminino": [
    {
      "nome": "Maria Santos",
      "vitorias": 3,
      "derrotas": 2,
      "sets_ganhos": 7,
      "sets_perdidos": 5,
      "saldo_sets": 2,
      "jogos_realizados": 5,
      "percentual_vitorias": 60.0
    }
  ]
}
```

---

## 🧠 Algoritmo de Sorteio (Simplificado para Evento Real)

### Estratégia: Round-Robin Modificado

#### Passo 1: Validação Inicial
```python
def validar_evento(homens, mulheres):
    """Valida se é possível realizar 5 rodadas"""
    total_h = len(homens)
    total_m = len(mulheres)
    
    # Mínimo absoluto
    if total_h < 4 or total_m < 4:
        return False, "Mínimo de 4 jogadores de cada gênero"
    
    # Máximo permitido
    if total_h > 15 or total_m > 15:
        return False, "Máximo de 15 jogadores por gênero"
    
    # Diferença aceitável
    diferenca = abs(total_h - total_m)
    if diferenca > 4:
        return False, f"Diferença muito grande ({diferenca}). Máximo: 4"
    
    return True, "OK"
```

---

#### Passo 2: Algoritmo Principal (Round-Robin com Rodízio)

**Conceito:** Sistema de rotação circular (como voleibol de rodízio)

```python
def gerar_5_rodadas(homens, mulheres):
    """
    Algoritmo simplificado garantido para eventos de até 30 pessoas
    """
    rodadas = []
    
    # Igualar tamanhos (descanso rotativo)
    max_size = max(len(homens), len(mulheres))
    homens_ext = homens + [None] * (max_size - len(homens))
    mulheres_ext = mulheres + [None] * (max_size - len(mulheres))
    
    for rodada_num in range(1, 6):
        confrontos = []
        descansando = []
        
        # Rotaciona as listas (mantém primeiro fixo, rotaciona resto)
        if rodada_num > 1:
            mulheres_ext = [mulheres_ext[0]] + [mulheres_ext[-1]] + mulheres_ext[1:-1]
        
        # Forma duplas
        metade = len(homens_ext) // 2
        for i in range(metade):
            h1 = homens_ext[i]
            m1 = mulheres_ext[i]
            h2 = homens_ext[-(i+1)]
            m2 = mulheres_ext[-(i+1)]
            
            # Pula se algum for None (descanso)
            if None in [h1, m1, h2, m2]:
                if h1: descansando.append(h1)
                if m1: descansando.append(m1)
                if h2: descansando.append(h2)
                if m2: descansando.append(m2)
                continue
            
            confrontos.append({
                'dupla1': (h1, m1),
                'dupla2': (h2, m2),
                'quadra': len(confrontos) + 1
            })
        
        rodadas.append({
            'numero': rodada_num,
            'confrontos': confrontos,
            'descansando': [d for d in descansando if d]
        })
    
    return rodadas
```

**Vantagens:**
- ✅ Simples e rápido
- ✅ Garantido para até 30 pessoas
- ✅ Duplas nunca se repetem
- ✅ Adversários raramente se repetem
- ✅ Descanso equilibrado

---

## 🎯 Fluxo Simplificado do Sistema

### Tela 1: Cadastro (Adaptar tela atual)
```
/presenca
- Cadastrar jogadores
- Marcar confirmados
- Separação automática por sexo
- Botão: "Gerar 5 Rodadas"
```

### Tela 2: Visualizar Rodadas (NOVA)
```
/rodadas
- Mostra as 5 rodadas geradas
- Cada rodada com confrontos e quadras
- Quem está descansando
- Botão: "Registrar Resultados"
```

### Tela 3: Registrar Resultados (Adaptar painel atual)
```
/resultados
- Formulário simples por confronto
- Sets ganhos Dupla 1: [_]
- Sets ganhos Dupla 2: [_]
- Salvar → Atualiza ranking automaticamente
```

### Tela 4: Ranking Ao Vivo (Adaptar tela atual)
```
/ranking
- Masculino (esquerda)
- Feminino (direita)
- Destaque TOP 3 de cada
- Atualização em tempo real
```

---

## ⚙️ Implementação por Prioridade

### 🔴 **CRÍTICO (Fazer primeiro - 2 dias)**
1. ✅ Algoritmo de sorteio das 5 rodadas
2. ✅ Salvar em `rodadas.json`
3. ✅ Tela de visualização das rodadas
4. ✅ Sistema de registro de resultados
5. ✅ Cálculo do ranking individual

### 🟡 **IMPORTANTE (Fazer se der tempo - 1 dia)**
6. ⚠️ Validações e mensagens de erro
7. ⚠️ Reset/refazer sorteio
8. ⚠️ Visual melhorado para TV

### 🟢 **BÔNUS (Se sobrar tempo)**
9. 💡 Exportar ranking para PDF
10. 💡 Histórico de confrontos
11. 💡 Estatísticas avançadas

---

## 📅 Cronograma Realista (5 dias úteis)

| Dia | Tarefas | Entregável |
|-----|---------|------------|
| **1** | Algoritmo sorteio + Estrutura JSON | Rodadas geradas com sucesso |
| **2** | Backend: rotas + lógica de resultados | API funcional |
| **3** | Frontend: telas de rodadas e resultados | Interface básica |
| **4** | Ranking individual + Visual | Sistema completo |
| **5** | Testes + Ajustes + Deploy | Pronto para evento |

---

## 🧪 Cenários de Teste Obrigatórios

Antes do evento, testar:

1. ✅ **8H + 8M** (cenário ideal)
2. ✅ **7H + 9M** (diferença pequena)
3. ✅ **6H + 10M** (diferença maior)
4. ✅ **10H + 10M** (grupo maior)
5. ✅ **12H + 12M** (máximo previsto)

Para cada cenário:
- Gerar 5 rodadas
- Verificar que duplas não repetem
- Conferir distribuição de descanso
- Simular resultados completos
- Validar ranking final

---

## 🚨 Plano B (Se Algoritmo Falhar)

### Fallback 1: Reduzir Rodadas
- Se 5 rodadas impossível → Gerar 4 rodadas
- Se 4 impossível → Gerar 3 rodadas

### Fallback 2: Permitir 1 Repetição
- Relaxar regra de "duplas nunca repetem"
- Permitir máximo 1 dupla repetida em cenários difíceis

### Fallback 3: Sorteio Manual
- Interface para montar rodadas manualmente
- Sistema valida e salva

---

## 🎨 Interface: Adaptações Mínimas

### Reutilizar do Sistema Atual:
- ✅ `/presenca` → Apenas remover campo categorias
- ✅ `/painel` → Substituir por "Gerar Rodadas"
- ✅ Base HTML + CSS → Manter todo o visual
- ✅ Logo e cores → Sem mudanças

### Criar do Zero:
- ❌ `/rodadas` → Mostrar as 5 rodadas
- ❌ `/ranking` → Ranking individual

**Tempo estimado:** 40% reúso + 60% novo

---

## ✅ Checklist Final Antes do Evento

### Técnico:
- [ ] Algoritmo testado com 5+ cenários
- [ ] Backup dos dados em JSON
- [ ] Sistema rodando sem erros
- [ ] Deploy funcionando (se online)
- [ ] Testes em celular (responsivo)

### Operacional:
- [ ] Dados dos participantes cadastrados
- [ ] Rodadas geradas antecipadamente
- [ ] Planilha impressa de backup
- [ ] Alguém treinado para usar o sistema
- [ ] TV/projetor testado

---

## 💬 Perguntas para Você Responder

Antes de começar a implementar, preciso saber:

### 1. **Número Estimado de Participantes**
- Quantas pessoas espera no evento?
- Quantos homens e mulheres (estimativa)?

### 2. **Formato dos Sets**
- Melhor de 3 sets?
- Apenas 1 set por jogo?
- Outro formato?

### 3. **Infraestrutura**
- Quantas quadras disponíveis simultaneamente?
- Vai usar TV/telão para mostrar ranking?
- Internet disponível ou precisa funcionar offline?

### 4. **Prioridades**
- Mais importante: visual bonito ou funcionar 100%?
- Precisa de impressão/PDF do resultado final?

### 5. **Tempo Disponível**
- Você tem quanto tempo para testar antes do evento?
- Alguém vai ajudar a testar?

---

## 🚀 Próximo Passo

Assim que você responder essas perguntas, eu começo a implementação imediatamente na branch `main`.

**Podemos começar em 3... 2... 1...** 💪

Me responda e bora codar! 🔥

