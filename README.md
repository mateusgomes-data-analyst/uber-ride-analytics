# Análise de dados — Uber Ride

Estudo de caso com base pública de **~150 mil pedidos** de corrida (2024, região NCR / Índia), usada no portfólio de [Mateus Gomes](https://github.com/mateusgomes-data-analyst).

Este pacote contém **tudo para reproduzir** o funil, os KPIs e o painel visual do case:

| Conteúdo | Caminho |
|----------|---------|
| Base CSV | [`data/ncr_ride_bookings.csv`](data/ncr_ride_bookings.csv) |
| Script da análise | [`uber_ride_analysis.py`](uber_ride_analysis.py) |
| Dependências | [`requirements.txt`](requirements.txt) |
| Saídas (gráfico + métricas) | pasta [`outputs/`](outputs/) |

> **Aviso:** a base vem do Kaggle ([Uber Ride Analytics Dashboard](https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard)), publicação comunitária — **não** é um dataset oficial da Uber Corp.

---

## O que a análise responde

**Pergunta central:** de cada 100 pedidos, quantos viram corrida concluída — e por que os outros falham?

Principais achados (após rodar o script):

- **62%** dos pedidos são concluídos
- **18%** cancelados pelo motorista · **7%** pelo cliente · **7%** sem motorista · **6%** incompletos
- Pico de demanda às **18h**
- Pagamento com maior receita: **UPI** (valores em ₹ INR)
- Veículo mais pedido: **Auto** (riquixá)
- Quando a corrida acontece, a nota do cliente fica em torno de **4,4**

Conclusão em uma frase: a maior perda está no **lado da oferta** (motorista cancela ou não há motorista), não no passageiro.

---

## Como rodar (passo a passo)

### 1. Pré-requisitos

- Python 3.10+ recomendado
- pip

### 2. Ambiente e dependências

No diretório deste pacote (`analysis/uber-ride/` se estiver no repositório do portfólio):

```bash
cd analysis/uber-ride
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Dados

O CSV já está em `data/ncr_ride_bookings.csv`.  
Detalhes das colunas e como baixar de novo do Kaggle: [`data/README.md`](data/README.md).

### 4. Executar a análise

```bash
python uber_ride_analysis.py
```

### 5. O que é gerado

| Arquivo | Descrição |
|---------|-----------|
| `outputs/analise-uber.png` | Painel com funil, demanda por hora, receita, cancelamentos e KPIs |
| `outputs/insights.json` | Métricas em JSON (mesmos números do case no site) |
| `outputs/RELATORIO.md` | Relatório em texto: metodologia + resultados |

Se o script estiver dentro do repositório do portfólio, ele também atualiza:

`public/previews/analise-uber.png`

---

## Metodologia (como chegamos aos números)

1. **Carga e limpeza leve** — lemos o CSV; normalizamos nomes de colunas; convertemos `Date` e extraímos a hora de `Time`.
2. **Funil** — `value_counts` em `Booking Status` (Completed, Cancelled by Driver/Customer, No Driver Found, Incomplete) e % sobre o total de pedidos.
3. **Qualidade da viagem** — só em status `Completed`: média de `Avg VTAT` (espera), `Avg CTAT` (duração), `Booking Value`, `Ride Distance`, ratings.
4. **Demanda por hora** — `groupby` da hora; o índice com maior volume é o pico.
5. **Receita por pagamento** — soma de `Booking Value` por `Payment Method` nas concluídas.
6. **Comparativo de cancelamento** — % de cancelamento cliente vs motorista sobre o total (não só sobre cancelados).
7. **Motivos** — top motivos preenchidos nas colunas de reason (quando não nulos).

O case narrado no site espelha esses passos em português: funil → gargalo → recomendações.

---

## Estrutura do pacote

```
uber-ride/
├── README.md                 ← este arquivo
├── requirements.txt
├── uber_ride_analysis.py     ← script principal
├── data/
│   ├── README.md             ← origem e colunas
│   └── ncr_ride_bookings.csv
└── outputs/                  ← gerado ao rodar o script
    ├── analise-uber.png
    ├── insights.json
    └── RELATORIO.md
```

---

## Publicar este pacote no GitHub

Você pode:

1. **Manter no portfólio** em `analysis/uber-ride/` e linkar o case para este caminho; ou
2. **Criar o repositório** `uber-ride-analytics` e enviar só esta pasta como raiz do repo:

```bash
# Exemplo (a partir desta pasta)
git init
git add .
git commit -m "Análise Uber Ride: CSV, script e README reproduzível"
git branch -M main
git remote add origin https://github.com/mateusgomes-data-analyst/uber-ride-analytics.git
git push -u origin main
```

Não versionar a pasta `.venv/`.

---

## Licença dos dados

Os dados pertencem aos termos do dataset no Kaggle. Este repositório versiona uma cópia para fins de portfólio/reprodução educacional. Consulte a página do dataset para a licença oficial.
