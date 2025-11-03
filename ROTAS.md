# 🌐 Documentação Completa das Rotas - BT-Sorteio

## 📋 Índice
- [Páginas Públicas](#-páginas-públicas)
- [Administração](#️-administração)
- [Gestão de Jogadores](#-gestão-de-jogadores)
- [Sistema de Sorteio](#-sistema-de-sorteio)
- [Visualização de Chaves](#-visualização-de-chaves)
- [Gestão de Resultados](#-gestão-de-resultados)

---

## 🏠 Páginas Públicas

### `GET /`
**Descrição**: Página inicial do torneio  
**Acesso**: Público  
**Retorna**: Página home com botões para as 3 categorias  
**Exemplo**: 
```
http://127.0.0.1:5000/
```
**Funcionalidades**:
- Exibe logo do torneio
- Links para as categorias (Mista, Masculino, Feminino)
- Contador de visitantes únicos

---

## ⚙️ Administração

### `GET /admin`
**Descrição**: Painel administrativo central  
**Acesso**: Sem autenticação (⚠️ exposto)  
**Retorna**: Dashboard com links para todas as funções administrativas  
**Exemplo**: 
```
http://127.0.0.1:5000/admin
```
**Funcionalidades**:
- Link para gerenciar categorias (`/painel`)
- Link para confirmar presenças (`/presenca`)
- Links para painéis de resultados por categoria
- Link para página inicial

---

### `GET /painel`
**Descrição**: Painel de gerenciamento de sorteios  
**Acesso**: Administrativo  
**Retorna**: Status dos sorteios de cada categoria  
**Exemplo**: 
```
http://127.0.0.1:5000/painel
```
**Funcionalidades**:
- Visualizar status de cada categoria (sorteado ou não)
- Botões para sortear cada categoria
- Botões para refazer sorteio
- Botões para resetar sorteio
- Contador de visitantes

---

## 👥 Gestão de Jogadores

### `GET /presenca`
**Descrição**: Página de confirmação de presença e cadastro  
**Acesso**: Administrativo  
**Retorna**: Lista de jogadores com checkboxes e formulário de cadastro  
**Exemplo**: 
```
http://127.0.0.1:5000/presenca
```
**Funcionalidades**:
- Lista todos os jogadores cadastrados
- Checkboxes para confirmar presença
- Contador em tempo real por categoria
- Formulário para adicionar/editar jogadores
- Botão de exclusão de jogadores
- Atualização automática via AJAX

---

### `POST /confirmar_presenca`
**Descrição**: API para confirmar presença de jogadores  
**Acesso**: Administrativo  
**Content-Type**: `application/json`  
**Body**:
```json
{
  "confirmado": ["Nome Jogador 1", "Nome Jogador 2", ...]
}
```
**Retorna**: 
```json
{
  "status": "ok"
}
```
**Exemplo via curl**:
```bash
curl -X POST http://127.0.0.1:5000/confirmar_presenca \
  -H "Content-Type: application/json" \
  -d '{"confirmado": ["Danilo Medeiros", "Arthur"]}'
```

---

### `POST /adicionar_ou_editar_jogador`
**Descrição**: API para adicionar ou editar jogador  
**Acesso**: Administrativo  
**Content-Type**: `application/json`  
**Body**:
```json
{
  "nome": "Nome do Jogador",
  "sexo": "M",  // ou "F"
  "categorias": ["mista", "masculino"]  // array com categorias
}
```
**Retorna**: 
```json
{
  "status": "ok"
}
```
**Exemplo via curl**:
```bash
curl -X POST http://127.0.0.1:5000/adicionar_ou_editar_jogador \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "sexo": "M",
    "categorias": ["mista", "masculino"]
  }'
```

---

### `POST /excluir_jogador`
**Descrição**: API para excluir jogador  
**Acesso**: Administrativo  
**Content-Type**: `application/json`  
**Body**:
```json
{
  "nome": "Nome do Jogador"
}
```
**Retorna**: 
```json
{
  "status": "ok"
}
```
**Exemplo via curl**:
```bash
curl -X POST http://127.0.0.1:5000/excluir_jogador \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva"}'
```

---

## 🎲 Sistema de Sorteio

### `POST /sortear/<categoria>`
**Descrição**: Realiza o sorteio de uma categoria  
**Acesso**: Administrativo  
**Parâmetros**: 
- `categoria`: `mista` | `masculino` | `feminino`

**Exemplo**: 
```bash
# Sortear categoria masculina
curl -X POST http://127.0.0.1:5000/sortear/masculino

# Sortear categoria feminina
curl -X POST http://127.0.0.1:5000/sortear/feminino

# Sortear categoria mista
curl -X POST http://127.0.0.1:5000/sortear/mista
```

**Funcionalidades**:
- Cria duplas aleatórias com jogadores confirmados
- Distribui duplas em grupos balanceados
- Define quadras para cada confronto
- Gera estrutura de fases eliminatórias
- Salva resultado em `data/sorteio_<categoria>.json`

**Estrutura de Grupos**:
- **Masculino/Feminino**: 2 grupos (A e B)
- **Mista**: Múltiplos grupos + sistema de repescagem

**Quadras**:
- **Masculino**: 1, 3, 5
- **Feminino**: 2, 4, 6
- **Mista**: 1 a 6

---

### `GET /resetar/<categoria>`
**Descrição**: Remove o sorteio de uma categoria  
**Acesso**: Administrativo  
**Parâmetros**: 
- `categoria`: `mista` | `masculino` | `feminino`

**Exemplo**: 
```
http://127.0.0.1:5000/resetar/masculino
```

**Funcionalidades**:
- Deleta o arquivo `data/sorteio_<categoria>.json`
- Redireciona para `/painel`

---

## 📈 Visualização de Chaves

### `GET /chaves/<categoria>`
**Descrição**: Visualiza as chaves e resultados de uma categoria  
**Acesso**: Público  
**Parâmetros**: 
- `categoria`: `mista` | `masculino` | `feminino`

**Exemplo**: 
```
http://127.0.0.1:5000/chaves/masculino
http://127.0.0.1:5000/chaves/feminino
http://127.0.0.1:5000/chaves/mista
```

**Funcionalidades**:
- Lista todos os participantes da categoria
- Exibe grupos e confrontos da fase de grupos
- Mostra placares de cada jogo
- Destaca vencedores (verde) e perdedores (vermelho)
- Exibe ranking completo com estatísticas:
  - Vitórias
  - Saldo de sets
  - Saldo de games
- Mostra fases eliminatórias (Semifinais e Final)

---

### `GET /fase2/misto`
**Descrição**: Visualiza a fase 2 da categoria mista (mata-mata)  
**Acesso**: Público  
**Requer**: Sorteio da fase de grupos já realizado  

**Exemplo**: 
```
http://127.0.0.1:5000/fase2/misto
```

**Funcionalidades**:
- Seleciona os 8 melhores classificados
- Gera confrontos de quartas de final (1º×8º, 2º×7º, etc.)
- Exibe ranking dos classificados

---

## 📊 Gestão de Resultados

### `GET /painel_resultados/<categoria>`
**Descrição**: Painel para inserção de resultados  
**Acesso**: Administrativo  
**Parâmetros**: 
- `categoria`: `mista` | `masculino` | `feminino`

**Exemplo**: 
```
http://127.0.0.1:5000/painel_resultados/masculino
```

**Funcionalidades**:
- Formulários para inserir placar de cada jogo
- Campos para games de cada dupla
- Separação por grupos (A, B, C, ...)
- Seção para fases eliminatórias:
  - Repescagem (apenas mista)
  - Quartas de final (apenas mista)
  - Semifinais
  - Final

---

### `POST /salvar_resultados/<categoria>`
**Descrição**: API para salvar resultado de um jogo  
**Acesso**: Administrativo  
**Parâmetros**: 
- `categoria`: `mista` | `masculino` | `feminino`

**Content-Type**: `application/x-www-form-urlencoded`

**Body (Fase de Grupos)**:
```
grupo=A
index=0
games_1=6
games_2=4
```

**Body (Fase Eliminatória)**:
```
fase=Semifinal 1
dupla1=Arthur e Edgard
dupla2=Lucas e Neudson
games_1=6
games_2=3
```

**Retorna**: 
```json
{
  "status": "ok"
}
```

**Exemplo via curl (Fase de Grupos)**:
```bash
curl -X POST http://127.0.0.1:5000/salvar_resultados/masculino \
  -d "grupo=A&index=0&games_1=6&games_2=4"
```

**Exemplo via curl (Semifinal)**:
```bash
curl -X POST http://127.0.0.1:5000/salvar_resultados/masculino \
  -d "fase=Semifinal 1&dupla1=Francisco e Ricardo&dupla2=Bruno Rolim e Raul&games_1=6&games_2=4"
```

**Funcionalidades**:
- Salva placar do jogo
- Define vencedor automaticamente
- Atualiza estatísticas (vitórias, sets, games)
- Gera automaticamente próximas fases:
  - Quartas → Semifinais (categoria mista)
  - Semifinais → Final (todas as categorias)
- Atualiza ranking em tempo real

---

## 📊 Estrutura de Dados

### Arquivo de Jogadores (`data/jogadores.json`)
```json
[
  {
    "nome": "Danilo Medeiros",
    "sexo": "M",
    "categorias": ["mista", "masculino"],
    "confirmado": true
  }
]
```

### Arquivo de Sorteio (`data/sorteio_<categoria>.json`)
```json
{
  "chaves": {
    "A": [
      [
        [
          {"nome": "Jogador 1", "sexo": "M", ...},
          {"nome": "Jogador 2", "sexo": "M", ...}
        ],
        [
          {"nome": "Jogador 3", "sexo": "M", ...},
          {"nome": "Jogador 4", "sexo": "M", ...}
        ],
        1,  // número da quadra
        {
          "resultado": [6, 4],  // games de cada dupla
          "vencedor": "dupla1"
        }
      ]
    ]
  },
  "jogadores": [...],  // todos os jogadores confirmados
  "confrontos": [  // fases eliminatórias
    {
      "partida": "Semifinal 1",
      "dupla1": "Nome1 e Nome2",
      "dupla2": "Nome3 e Nome4",
      "quadra": 1,
      "resultado": [6, 3],
      "vencedor": "dupla1"
    }
  ]
}
```

---

## 🔐 Considerações de Segurança

⚠️ **ATENÇÃO**: As seguintes rotas estão **sem autenticação**:
- `/admin`
- `/painel`
- `/presenca`
- `/sortear/<categoria>`
- `/resetar/<categoria>`
- `/painel_resultados/<categoria>`
- `/salvar_resultados/<categoria>`
- `/adicionar_ou_editar_jogador`
- `/excluir_jogador`
- `/confirmar_presenca`

**Recomendação**: Implementar sistema de autenticação antes de colocar em produção!

---

## 🧪 Testando as Rotas

### 1. Adicionar um jogador
```bash
curl -X POST http://127.0.0.1:5000/adicionar_ou_editar_jogador \
  -H "Content-Type: application/json" \
  -d '{"nome": "Teste User", "sexo": "M", "categorias": ["masculino"]}'
```

### 2. Confirmar presença
```bash
curl -X POST http://127.0.0.1:5000/confirmar_presenca \
  -H "Content-Type: application/json" \
  -d '{"confirmado": ["Teste User"]}'
```

### 3. Realizar sorteio
```bash
curl -X POST http://127.0.0.1:5000/sortear/masculino
```

### 4. Ver resultado
```bash
curl http://127.0.0.1:5000/chaves/masculino
```

### 5. Salvar resultado de um jogo
```bash
curl -X POST http://127.0.0.1:5000/salvar_resultados/masculino \
  -d "grupo=A&index=0&games_1=6&games_2=4"
```

---

## 📱 URLs Úteis (Rodando Localmente)

| Descrição | URL |
|-----------|-----|
| **Página Inicial** | http://127.0.0.1:5000/ |
| **Painel Admin** | http://127.0.0.1:5000/admin |
| **Gerenciar Sorteios** | http://127.0.0.1:5000/painel |
| **Confirmar Presenças** | http://127.0.0.1:5000/presenca |
| **Chaves Masculino** | http://127.0.0.1:5000/chaves/masculino |
| **Chaves Feminino** | http://127.0.0.1:5000/chaves/feminino |
| **Chaves Mista** | http://127.0.0.1:5000/chaves/mista |
| **Resultados Masculino** | http://127.0.0.1:5000/painel_resultados/masculino |
| **Resultados Feminino** | http://127.0.0.1:5000/painel_resultados/feminino |
| **Fase 2 Mista** | http://127.0.0.1:5000/fase2/misto |

---

## 🚀 Servidor em Execução

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Rodar servidor
python app.py

# Servidor estará disponível em:
# http://127.0.0.1:5000
```

---

**Documentação gerada automaticamente** 🤖  
**Projeto**: BT-Sorteio - Sistema de Gerenciamento de Torneios de Beach Tennis  
**Versão**: 1.0

