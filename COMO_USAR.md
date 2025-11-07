# 📱 Como Usar o Sistema de 5 Rodadas

## 🚀 Início Rápido

### 1️⃣ Iniciar o Servidor

```bash
cd /Users/daniloamedeiros/PycharmProjects/bt-sorteio
source venv/bin/activate
python app.py
```

O servidor estará disponível em: **http://127.0.0.1:5000**

---

## 📋 Fluxo Completo do Torneio

### **PASSO 1: Confirmar Presenças** 
📍 **http://127.0.0.1:5000/presenca**

1. Marque os checkboxes dos jogadores confirmados
2. Se precisar, cadastre novos jogadores (apenas Nome e Sexo)
3. Confira os totais: Homens e Mulheres
4. **Clique em "⚡ GERAR 5 RODADAS"**

**Requisitos:**
- Mínimo de 3 homens e 3 mulheres
- Máximo recomendado: 20 de cada gênero
- Diferença entre H e M: máximo 6

---

### **PASSO 2: Ver as Rodadas Geradas**
📍 **http://127.0.0.1:5000/rodadas**

Aqui você verá:
- As 5 rodadas completas
- Todos os confrontos com quadras
- Quem está descansando em cada rodada
- Status dos resultados (✅ finalizado ou ⏳ aguardando)

---

### **PASSO 3: Registrar Resultados**
📍 **http://127.0.0.1:5000/registro-resultados**

Para cada confronto:
1. Digite os **games** de cada dupla
2. Exemplos válidos:
   - `6 x 4` ✅
   - `7 x 5` ✅
   - `7 x 6` ✅ (tiebreak)
   - `6 x 0` ✅
3. Clique em "✅ Salvar Resultado"
4. O ranking é atualizado **automaticamente**!

**Regras de Placar:**
- Mínimo de 6 games para vencer
- Máximo de 7 games (tiebreak)
- Se chegou 6x6, vai para 7x6

---

### **PASSO 4: Ver o Ranking**
📍 **http://127.0.0.1:5000/ranking-individual**

O ranking mostra:
- **Masculino** e **Feminino** separados
- Critérios de ordenação:
  1. **Vitórias** (mais importante)
  2. **Saldo de Games** (games feitos - games sofridos)
  3. **Games Feitos** (desempate final)
- 🥇🥈🥉 Destaque para o TOP 3
- Atualização automática a cada 30 segundos

**Legenda:**
- **V** = Vitórias
- **D** = Derrotas
- **%** = Percentual de Vitórias
- **Saldo** = Games Feitos - Games Sofridos
- **GF** = Games Feitos
- **GS** = Games Sofridos

---

## 📱 URLs Principais

| Página | URL | Descrição |
|--------|-----|-----------|
| **Presenças** | `/presenca` | Cadastro e geração de rodadas |
| **Rodadas** | `/rodadas` | Ver todas as 5 rodadas |
| **Resultados** | `/registro-resultados` | Registrar placares |
| **Ranking** | `/ranking-individual` | Ranking ao vivo |

---

## 🔄 Resetar Tudo

Se precisar refazer o sorteio:
1. Acesse `/rodadas`
2. Clique em "🔄 Resetar Tudo"
3. Confirme (⚠️ **todos os dados serão perdidos!**)
4. Volte para `/presenca` e gere novamente

---

## 🧪 Testar o Sistema

Execute o script de teste:

```bash
source venv/bin/activate
python test_sistema_completo.py
```

Isso irá:
- Cadastrar 24 jogadores (12H + 12M)
- Gerar 5 rodadas
- Simular todos os resultados
- Mostrar o ranking final

---

## 📊 Estrutura de Dados

### `data/jogadores.json`
```json
[
  {
    "nome": "João Silva",
    "sexo": "M",
    "confirmado": true,
    "categorias": ["mista"]
  }
]
```

### `data/rodadas.json`
```json
{
  "data_sorteio": "2025-11-02T10:00:00",
  "total_homens": 12,
  "total_mulheres": 12,
  "total_rodadas": 5,
  "rodadas": [
    {
      "numero": 1,
      "confrontos": [...],
      "descansando": []
    }
  ]
}
```

### `data/ranking.json`
```json
{
  "ultima_atualizacao": "2025-11-02T11:00:00",
  "masculino": [
    {
      "nome": "João Silva",
      "vitorias": 4,
      "derrotas": 1,
      "games_feitos": 28,
      "games_sofridos": 20,
      "saldo_games": 8,
      "percentual_vitorias": 80.0
    }
  ],
  "feminino": [...]
}
```

---

## ⚠️ Troubleshooting

### Erro: "Mínimo de 3 homens/mulheres necessário"
- Confirme pelo menos 3 jogadores de cada gênero
- Verifique se os checkboxes estão marcados

### Erro: "Diferença muito grande entre H e M"
- A diferença não pode ser maior que 6
- Exemplo: 5H e 12M = diferença de 7 ❌
- Ajuste os participantes

### Erro: "Placar inválido"
- Lembre-se: mínimo de 6 games para vencer
- Apenas um pode ter 7 (tiebreak)

### Ranking não atualiza
- Clique no botão "🔄 Atualizar Ranking"
- Ou recarregue a página

---

## 🎯 Dicas para o Evento

1. **Antes do Evento:**
   - Cadastre todos os jogadores antecipadamente
   - Faça um sorteio teste
   - Imprima as rodadas como backup

2. **Durante o Evento:**
   - Tenha 1 pessoa responsável por registrar resultados
   - Use celular ou tablet para acessar o sistema
   - Mostre o ranking em um telão (se disponível)

3. **Backup:**
   - Os arquivos JSON em `data/` são seu backup
   - Faça cópia antes de resetar
   - Guarde para histórico futuro

---

## 🚀 Deploy em Produção

Para colocar online (Heroku, Railway, etc):

```bash
# Já está configurado!
# Basta fazer deploy com:
git push heroku main
```

O `Procfile` já está pronto:
```
web: gunicorn app:app --timeout 120
```

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs: `cat /tmp/flask_novo.log`
2. Reinicie o servidor
3. Execute o teste: `python test_sistema_completo.py`

---

**Desenvolvido com ❤️ para o evento de Beach Tennis BT Mania** 🎾


