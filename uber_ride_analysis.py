"""
Análise Uber Ride (Kaggle, 2024) — portfólio Mateus Gomes.

Lê data/ncr_ride_bookings.csv e gera:
  - outputs/analise-uber.png     → painel visual
  - outputs/insights.json        → métricas usadas no site
  - outputs/RELATORIO.md         → como chegamos aos números

"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "ncr_ride_bookings.csv"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# Prévia do site (só se a pasta existir)
PORTFOLIO_PREVIEW = ROOT.parents[1] / "public" / "previews" / "analise-uber.png"

BG = "#f7f8fa"
CARD = "#ffffff"
INK = "#0f172a"
MUTED = "#64748b"
ACCENT = "#1d4ed8"
ACCENT_DEEP = "#1e3a8a"
ALERT = "#c2410c"
OK = "#0f766e"
SOFT = "#e2e8f0"


def style_ax(ax: plt.Axes) -> None:
    ax.set_facecolor(CARD)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(SOFT)
    ax.spines["bottom"].set_color(SOFT)
    ax.grid(axis="x", color=SOFT, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)


def pct(n: int, total: int) -> float:
    return round(n / total * 100, 2) if total else 0.0


def load_and_prepare() -> tuple[pd.DataFrame, dict]:
    if not DATA.exists():
        raise FileNotFoundError(
            f"CSV não encontrado em {DATA}.\n"
            "Veja data/README.md para baixar a base do Kaggle."
        )

    df = pd.read_csv(DATA, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S", errors="coerce").dt.hour

    total = len(df)
    status = df["Booking Status"].fillna("Unknown").value_counts()
    completed = int(status.get("Completed", 0))
    cancel_cust = int(status.get("Cancelled by Customer", 0))
    cancel_drv = int(status.get("Cancelled by Driver", 0))
    no_driver = int(status.get("No Driver Found", 0))
    incomplete = int(status.get("Incomplete", 0))

    completed_mask = df["Booking Status"] == "Completed"
    avg_vtat = float(pd.to_numeric(df.loc[completed_mask, "Avg VTAT"], errors="coerce").mean())
    avg_ctat = float(pd.to_numeric(df.loc[completed_mask, "Avg CTAT"], errors="coerce").mean())
    avg_dist = float(pd.to_numeric(df.loc[completed_mask, "Ride Distance"], errors="coerce").mean())
    avg_value = float(pd.to_numeric(df.loc[completed_mask, "Booking Value"], errors="coerce").mean())
    avg_drv_rating = float(pd.to_numeric(df.loc[completed_mask, "Driver Ratings"], errors="coerce").mean())
    avg_cust_rating = float(pd.to_numeric(df.loc[completed_mask, "Customer Rating"], errors="coerce").mean())

    hourly = df.groupby("hour").size().reindex(range(24), fill_value=0)
    peak_hour = int(hourly.idxmax())

    pay = (
        df.loc[completed_mask]
        .groupby("Payment Method", dropna=False)["Booking Value"]
        .apply(lambda s: pd.to_numeric(s, errors="coerce").sum())
        .sort_values(ascending=False)
    )

    vehicle = df["Vehicle Type"].fillna("Unknown").value_counts()
    top_vehicle = str(vehicle.index[0]) if len(vehicle) else "—"

    # Motivos (quando preenchidos)
    reason_cust = (
        df.loc[df["Booking Status"] == "Cancelled by Customer", "Reason for cancelling by Customer"]
        .dropna()
        .astype(str)
        .value_counts()
        .head(5)
    )
    reason_drv = (
        df.loc[df["Booking Status"] == "Cancelled by Driver", "Driver Cancellation Reason"]
        .dropna()
        .astype(str)
        .value_counts()
        .head(5)
    )

    insights = {
        "total_bookings": total,
        "completed": completed,
        "success_rate_pct": pct(completed, total),
        "cancel_customer": cancel_cust,
        "cancel_driver": cancel_drv,
        "cancel_rate_pct": pct(cancel_cust + cancel_drv, total),
        "cancel_customer_pct": pct(cancel_cust, total),
        "cancel_driver_pct": pct(cancel_drv, total),
        "no_driver": no_driver,
        "no_driver_pct": pct(no_driver, total),
        "incomplete": incomplete,
        "incomplete_pct": pct(incomplete, total),
        "avg_vtat_min": round(avg_vtat, 2),
        "avg_ctat_min": round(avg_ctat, 2),
        "avg_distance_km": round(avg_dist, 2),
        "avg_booking_value_inr": round(avg_value, 2),
        "avg_driver_rating": round(avg_drv_rating, 2),
        "avg_customer_rating": round(avg_cust_rating, 2),
        "peak_hour": peak_hour,
        "peak_hour_bookings": int(hourly[peak_hour]),
        "top_payment": str(pay.index[0]) if len(pay) else None,
        "top_vehicle": top_vehicle,
        "revenue_by_payment_inr": {str(k): float(v) for k, v in pay.items()},
        "top_cancel_reasons_customer": {str(k): int(v) for k, v in reason_cust.items()},
        "top_cancel_reasons_driver": {str(k): int(v) for k, v in reason_drv.items()},
    }

    ctx = {
        "df": df,
        "total": total,
        "status": status,
        "completed": completed,
        "cancel_cust": cancel_cust,
        "cancel_drv": cancel_drv,
        "no_driver": no_driver,
        "incomplete": incomplete,
        "completed_mask": completed_mask,
        "hourly": hourly,
        "peak_hour": peak_hour,
        "pay": pay,
        "insights": insights,
        "top_vehicle": top_vehicle,
        "avg_vtat": avg_vtat,
        "avg_ctat": avg_ctat,
        "avg_value": avg_value,
        "avg_cust_rating": avg_cust_rating,
    }
    return df, ctx


def build_chart(ctx: dict) -> Path:
    total = ctx["total"]
    status = ctx["status"]
    cancel_cust = ctx["cancel_cust"]
    cancel_drv = ctx["cancel_drv"]
    hourly = ctx["hourly"]
    peak_hour = ctx["peak_hour"]
    pay = ctx["pay"]
    top_vehicle = ctx["top_vehicle"]
    avg_vtat = ctx["avg_vtat"]
    avg_ctat = ctx["avg_ctat"]
    avg_value = ctx["avg_value"]
    avg_cust_rating = ctx["avg_cust_rating"]

    status_order = [
        ("Completed", "Concluída", OK),
        ("Cancelled by Driver", "Cancel. motorista", ALERT),
        ("No Driver Found", "Sem motorista", "#475569"),
        ("Cancelled by Customer", "Cancel. cliente", "#94a3b8"),
        ("Incomplete", "Incompleta", ACCENT_DEEP),
    ]
    status_labels = [lab for _, lab, _ in status_order]
    status_vals = [int(status.get(key, 0)) for key, _, _ in status_order]
    status_colors = [color for _, _, color in status_order]
    status_pcts = [v / total * 100 for v in status_vals]

    fig = plt.figure(figsize=(13.5, 8.2), facecolor=BG)
    fig.suptitle(
        "Análise de dados — Uber Ride",
        fontsize=18,
        fontweight="bold",
        color=INK,
        x=0.03,
        ha="left",
        y=0.97,
    )
    fig.text(
        0.03,
        0.925,
        "Base 2024 · Kaggle · 150 mil pedidos  ·  Insight: a maior perda está no lado do motorista (18%) e na falta de oferta (7%)",
        fontsize=10,
        color=MUTED,
        ha="left",
    )

    gs = fig.add_gridspec(
        2,
        3,
        height_ratios=[1.15, 1],
        width_ratios=[1.15, 1.15, 0.95],
        left=0.07,
        right=0.97,
        top=0.88,
        bottom=0.08,
        hspace=0.32,
        wspace=0.28,
    )

    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1)
    y = np.arange(len(status_labels))
    bars = ax1.barh(y, status_vals[::-1], color=status_colors[::-1], height=0.62, zorder=3)
    ax1.set_yticks(y)
    ax1.set_yticklabels(status_labels[::-1], fontsize=9.5, color=INK)
    ax1.set_xlabel("Pedidos", color=MUTED, fontsize=9)
    ax1.set_title("O que aconteceu com cada pedido", loc="left", fontsize=11.5, fontweight="600", color=INK, pad=10)
    ax1.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x / 1000)} mil" if x >= 1000 else f"{int(x)}")
    )
    for bar, val, p in zip(bars, status_vals[::-1], status_pcts[::-1]):
        ax1.text(
            bar.get_width() + total * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{p:.0f}%",
            va="center",
            ha="left",
            fontsize=9,
            fontweight="600",
            color=INK,
        )
    ax1.set_xlim(0, max(status_vals) * 1.18)

    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2)
    ax2.grid(axis="y", color=SOFT, linewidth=0.8, alpha=0.9)
    ax2.grid(axis="x", visible=False)
    ax2.fill_between(hourly.index, hourly.values, color=ACCENT, alpha=0.15)
    ax2.plot(hourly.index, hourly.values, color=ACCENT, linewidth=2.4, zorder=3)
    ax2.scatter([peak_hour], [hourly[peak_hour]], color=ALERT, s=55, zorder=4)
    ax2.axvline(peak_hour, color=ALERT, linestyle="--", linewidth=1.1, alpha=0.85)
    ax2.annotate(
        f"Pico às {peak_hour}h\n{int(hourly[peak_hour]):,} pedidos".replace(",", "."),
        xy=(peak_hour, hourly[peak_hour]),
        xytext=(peak_hour - 7.5, hourly[peak_hour] * 0.78),
        fontsize=8.5,
        color=ALERT,
        fontweight="600",
        arrowprops=dict(arrowstyle="->", color=ALERT, lw=1),
    )
    ax2.set_xlim(-0.5, 23.5)
    ax2.set_xticks([0, 6, 12, 18, 23])
    ax2.set_title("Pedidos ao longo do dia", loc="left", fontsize=11.5, fontweight="600", color=INK, pad=10)
    ax2.set_xlabel("Hora", color=MUTED, fontsize=9)
    ax2.set_ylabel("Pedidos", color=MUTED, fontsize=9)
    ax2.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x / 1000)}k" if x >= 1000 else f"{int(x)}")
    )

    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3)
    ax3.grid(axis="y", color=SOFT, linewidth=0.8, alpha=0.9)
    ax3.grid(axis="x", visible=False)
    pay_top = pay.head(5)
    pay_labels = pay_top.index.astype(str).tolist()
    pay_vals_mi = (pay_top.values / 1_000_000).tolist()
    bars3 = ax3.bar(pay_labels, pay_vals_mi, color=ACCENT, width=0.62, zorder=3)
    ax3.set_title(
        "Receita por pagamento (corridas concluídas)",
        loc="left",
        fontsize=11.5,
        fontweight="600",
        color=INK,
        pad=10,
    )
    ax3.set_ylabel("₹ milhões", color=MUTED, fontsize=9)
    ax3.tick_params(axis="x", rotation=0, labelsize=9)
    for bar, val in zip(bars3, pay_vals_mi):
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.25,
            f"{val:.1f} Mi",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="600",
            color=INK,
        )
    ax3.set_ylim(0, max(pay_vals_mi) * 1.2)

    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4)
    ax4.grid(axis="y", color=SOFT, linewidth=0.8, alpha=0.9)
    ax4.grid(axis="x", visible=False)
    cancel_labels = ["Cliente", "Motorista"]
    cancel_vals = [cancel_cust / total * 100, cancel_drv / total * 100]
    bars4 = ax4.bar(cancel_labels, cancel_vals, color=["#94a3b8", ALERT], width=0.55, zorder=3)
    ax4.set_title("Quem cancela mais? (% dos pedidos)", loc="left", fontsize=11.5, fontweight="600", color=INK, pad=10)
    ax4.set_ylabel("% dos pedidos", color=MUTED, fontsize=9)
    for bar, val in zip(bars4, cancel_vals):
        ax4.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"{val:.0f}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="700",
            color=INK,
        )
    ax4.set_ylim(0, max(cancel_vals) * 1.35)
    ax4.text(
        0.5,
        -0.22,
        "Motorista cancela ~2,5× mais que o cliente",
        transform=ax4.transAxes,
        ha="center",
        fontsize=8.5,
        color=ALERT,
        fontweight="600",
    )

    ax5 = fig.add_subplot(gs[:, 2])
    ax5.set_facecolor(BG)
    ax5.axis("off")
    ax5.set_title("Indicadores-chave", loc="left", fontsize=11.5, fontweight="600", color=INK, pad=10)

    kpis = [
        ("150 mil", "Pedidos analisados", ACCENT),
        ("62%", "Corridas concluídas", OK),
        ("25%", "Cancelamentos", ALERT),
        ("18%", "Cancel. pelo motorista", ALERT),
        ("7%", "Sem motorista", "#475569"),
        (f"{avg_vtat:.1f}".replace(".", ",") + " min", "Espera média do veículo", ACCENT_DEEP),
        (f"{avg_ctat:.0f} min", "Duração média da corrida", ACCENT_DEEP),
        (f"₹ {avg_value:.0f}", "Valor médio (INR)", ACCENT),
        (f"{avg_cust_rating:.2f}".replace(".", ","), "Nota do cliente", OK),
        (top_vehicle, "Veículo mais pedido (riquixá)" if top_vehicle == "Auto" else "Veículo mais pedido", MUTED),
    ]

    card_h = 0.078
    gap = 0.012
    top = 0.90
    for i, (value, label, color) in enumerate(kpis):
        y_pos = top - i * (card_h + gap)
        box = FancyBboxPatch(
            (0.02, y_pos - card_h),
            0.96,
            card_h,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=1,
            edgecolor=SOFT,
            facecolor=CARD,
            transform=ax5.transAxes,
            clip_on=False,
        )
        ax5.add_patch(box)
        ax5.text(
            0.08,
            y_pos - card_h / 2,
            value,
            transform=ax5.transAxes,
            va="center",
            ha="left",
            fontsize=11,
            fontweight="800",
            color=color,
        )
        ax5.text(
            0.42,
            y_pos - card_h / 2,
            label,
            transform=ax5.transAxes,
            va="center",
            ha="left",
            fontsize=8.3,
            color=MUTED,
        )

    out_path = OUT / "analise-uber.png"
    fig.savefig(out_path, dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)

    if PORTFOLIO_PREVIEW.parent.exists():
        PORTFOLIO_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        PORTFOLIO_PREVIEW.write_bytes(out_path.read_bytes())
        print("saved", PORTFOLIO_PREVIEW)

    return out_path


def write_report(insights: dict) -> Path:
    ratio = (
        round(insights["cancel_driver_pct"] / insights["cancel_customer_pct"], 1)
        if insights["cancel_customer_pct"]
        else 0
    )
    lines = [
        "# Relatório da análise — Uber Ride",
        "",
        "Gerado automaticamente por `uber_ride_analysis.py`.",
        "",
        "## Pergunta central",
        "",
        "De cada 100 pedidos, quantos viram corrida concluída — e por que os outros falham?",
        "",
        "## Como os números foram obtidos",
        "",
        "1. Carregamos `data/ncr_ride_bookings.csv` (~150 mil pedidos de 2024).",
        "2. Contamos `Booking Status` para montar o funil.",
        "3. Nas corridas **Completed**, calculamos médias de espera (VTAT), duração (CTAT), valor, distância e notas.",
        "4. Agrupamos por hora (`Time`) para achar o pico de demanda.",
        "5. Somamos `Booking Value` por `Payment Method` só nas concluídas.",
        "6. Comparamos cancelamento de cliente vs motorista em % do total de pedidos.",
        "",
        "## Resultados principais",
        "",
        f"| Indicador | Valor |",
        f"|-----------|-------|",
        f"| Pedidos | {insights['total_bookings']:,} |".replace(",", "."),
        f"| Concluídas | {insights['success_rate_pct']}% |",
        f"| Cancel. motorista | {insights['cancel_driver_pct']}% |",
        f"| Cancel. cliente | {insights['cancel_customer_pct']}% |",
        f"| Sem motorista | {insights['no_driver_pct']}% |",
        f"| Incompletas | {insights['incomplete_pct']}% |",
        f"| Pico de demanda | {insights['peak_hour']}h ({insights['peak_hour_bookings']:,} pedidos) |".replace(",", "."),
        f"| Pagamento líder (receita) | {insights['top_payment']} |",
        f"| Veículo mais pedido | {insights['top_vehicle']} |",
        f"| Espera média (VTAT) | {insights['avg_vtat_min']} min |",
        f"| Duração média (CTAT) | {insights['avg_ctat_min']} min |",
        f"| Valor médio | ₹ {insights['avg_booking_value_inr']} |",
        f"| Nota do cliente | {insights['avg_customer_rating']} |",
        "",
        "## Insight",
        "",
        f"O motorista cancela cerca de **{ratio}×** mais que o cliente "
        f"({insights['cancel_driver_pct']}% vs {insights['cancel_customer_pct']}%). "
        "Somando cancelamento do motorista e falta de oferta, a maior perda está no lado da oferta.",
        "",
        "## Top motivos de cancelamento (quando preenchidos)",
        "",
        "### Cliente",
        "",
    ]
    for reason, n in insights["top_cancel_reasons_customer"].items():
        lines.append(f"- {reason}: {n}")
    lines += ["", "### Motorista", ""]
    for reason, n in insights["top_cancel_reasons_driver"].items():
        lines.append(f"- {reason}: {n}")
    lines += [
        "",
        "## Arquivos gerados",
        "",
        "- `outputs/analise-uber.png` — painel visual do case",
        "- `outputs/insights.json` — métricas em JSON",
        "- `outputs/RELATORIO.md` — este arquivo",
        "",
    ]
    path = OUT / "RELATORIO.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    _, ctx = load_and_prepare()
    insights = ctx["insights"]

    chart = build_chart(ctx)
    print("saved", chart)

    json_path = OUT / "insights.json"
    json_path.write_text(json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", json_path)

    report = write_report(insights)
    print("saved", report)

    print(
        f"\nResumo: {insights['total_bookings']} pedidos | "
        f"{insights['success_rate_pct']}% concluídas | "
        f"pico {insights['peak_hour']}h | "
        f"cancel. motorista {insights['cancel_driver_pct']}%"
    )


if __name__ == "__main__":
    main()
