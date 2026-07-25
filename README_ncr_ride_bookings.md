# Dados

Arquivo: `ncr_ride_bookings.csv` (~25 MB, ~150 mil linhas).

## Origem

- Conjunto: [Uber Ride Analytics Dashboard](https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard) (Kaggle)
- Autor no Kaggle: yashdevladdha (publicação comunitária; **não** é um release oficial da Uber Corp.)
- Período dos registros: 2024
- Região: NCR (Índia)

## Colunas principais

| Coluna | Uso na análise |
|--------|----------------|
| `Date`, `Time` | Volume por dia/hora; pico de demanda |
| `Booking Status` | Funil (concluída, cancelamentos, sem motorista, incompleta) |
| `Vehicle Type` | Tipo de veículo mais pedido |
| `Avg VTAT` | Tempo médio até o veículo (espera) |
| `Avg CTAT` | Duração média da corrida |
| `Booking Value` | Valor da corrida (INR ₹) |
| `Ride Distance` | Distância |
| `Driver Ratings`, `Customer Rating` | Qualidade percebida |
| `Payment Method` | Receita por forma de pagamento |
| Motivos de cancelamento | Detalhe dos gargalos |

## Como obter de novo (opcional)

Se preferir baixar em vez de usar o CSV versionado neste repositório:

```bash
pip install kagglehub
python -c "import kagglehub; print(kagglehub.dataset_download('yashdevladdha/uber-ride-analytics-dashboard'))"
```

Copie o `ncr_ride_bookings.csv` para esta pasta `data/`.
