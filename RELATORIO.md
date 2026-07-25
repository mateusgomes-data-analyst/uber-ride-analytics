# Relatório da análise — Uber Ride

Gerado automaticamente por `uber_ride_analysis.py`.

## Pergunta central

De cada 100 pedidos, quantos viram corrida concluída — e por que os outros falham?

## Como os números foram obtidos

1. Carregamos `data/ncr_ride_bookings.csv` (~150 mil pedidos de 2024).
2. Contamos `Booking Status` para montar o funil.
3. Nas corridas **Completed**, calculamos médias de espera (VTAT), duração (CTAT), valor, distância e notas.
4. Agrupamos por hora (`Time`) para achar o pico de demanda.
5. Somamos `Booking Value` por `Payment Method` só nas concluídas.
6. Comparamos cancelamento de cliente vs motorista em % do total de pedidos.

## Resultados principais

| Indicador | Valor |
|-----------|-------|
| Pedidos | 150.000 |
| Concluídas | 62.0% |
| Cancel. motorista | 18.0% |
| Cancel. cliente | 7.0% |
| Sem motorista | 7.0% |
| Incompletas | 6.0% |
| Pico de demanda | 18h (12.397 pedidos) |
| Pagamento líder (receita) | UPI |
| Veículo mais pedido | Auto |
| Espera média (VTAT) | 8.51 min |
| Duração média (CTAT) | 30.03 min |
| Valor médio | ₹ 508.18 |
| Nota do cliente | 4.4 |

## Insight

O motorista cancela cerca de **2.6×** mais que o cliente (18.0% vs 7.0%). Somando cancelamento do motorista e falta de oferta, a maior perda está no lado da oferta.

## Top motivos de cancelamento (quando preenchidos)

### Cliente

- Wrong Address: 2362
- Change of plans: 2353
- Driver is not moving towards pickup location: 2335
- Driver asked to cancel: 2295
- AC is not working: 1155

### Motorista

- Customer related issue: 6837
- The customer was coughing/sick: 6751
- Personal & Car related issues: 6726
- More than permitted people in there: 6686

## Arquivos gerados

- `outputs/analise-uber.png` — painel visual do case
- `outputs/insights.json` — métricas em JSON
- `outputs/RELATORIO.md` — este arquivo
