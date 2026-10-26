from pathlib import Path
from decimal import Decimal, localcontext
import json, sys, html
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
W, H = A4
M = 42
WIDTH = W - 2 * M
NAVY = colors.HexColor("#142f49")
TEAL = colors.HexColor("#087f96")
GRAY = colors.HexColor("#607286")
LIGHT = colors.HexColor("#edf3f7")
RED = colors.HexColor("#ae4848")
SEGMENTS = ["development", "validation", "test"]
NAMES = {"development": "Desenvolvimento", "validation": "Validação", "test": "Teste final"}
VARIANTS = ["base", "double_costs", "delay_1candle", "double_costs_delay"]
VNAMES = {
    "base": "Base",
    "double_costs": "Custos dobrados",
    "delay_1candle": "Atraso de 1 candle",
    "double_costs_delay": "Custos + atraso",
}
PROFILES = ["sma", "cash", "buy_hold_100pct", "buy_hold_10pct"]
PNAMES = {
    "sma": "SMA20/50 (entrada 10%)",
    "cash": "Caixa",
    "buy_hold_100pct": "Buy-and-hold 100%",
    "buy_hold_10pct": "Buy-and-hold 10%",
}
D = lambda x: Decimal(str(x))


def money(x, places=2):
    return f"{D(x):,.{places}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def percent(x):
    return money(D(x) * 100) + "%"


def date(ms):
    from datetime import datetime, timezone

    return datetime.fromtimestamp(int(ms) / 1000, timezone.utc).strftime("%d/%m/%Y")


class Summary:
    def __init__(self, report, target):
        self.r = report
        self.protocol = report["protocol"]
        self.dataset = self.protocol["dataset"]
        self.target = Path(target)
        self.c = canvas.Canvas(str(target), pagesize=A4, pageCompression=1)
        self.c.setTitle("Sprint 05 - Avaliação histórica PAPER")
        self.c.setAuthor("Cripto - relatório de simulação")
        self.real = self.dataset["source"] == "binance_public"
        self.curves = {(r["segment"], r["variant"], r["profile"]): r for r in report["curves"]}
        self.page = 0

    def text(self, x, y, s, size=9, color=NAVY, bold=False):
        self.c.setFillColor(color)
        self.c.setFont("DVB" if bold else "DV", size)
        self.c.drawString(x, y, s)

    def p(self, text, y, size=9, color=NAVY, width=WIDTH):
        style = ParagraphStyle(
            "p", fontName="DV", fontSize=size, leading=size * 1.45, textColor=color
        )
        p = Paragraph(text, style)
        _, h = p.wrap(width, 800)
        p.drawOn(self.c, M, y - h)
        return y - h - 10

    def title(self, title, subtitle):
        self.page += 1
        self.c.setFillColor(NAVY)
        self.c.rect(0, H - 121, W, 121, fill=1, stroke=0)
        self.text(M, H - 37, "CRIPTO  /  PAPER  /  LOCAL  /  BTCUSDT  /  15m", 8, colors.white)
        self.text(M, H - 71, title, 22, colors.white, True)
        self.text(M, H - 97, subtitle, 9, colors.HexColor("#cde0ec"))

    def footer(self):
        self.c.setStrokeColor(colors.HexColor("#d5e0e8"))
        self.c.line(M, 40, W - M, 40)
        self.text(
            M, 26, "Sprint 05 | 25/10/2026 | Sem ordens reais | Sem autorização LIVE", 7, GRAY
        )
        self.text(W - M - 18, 26, str(self.page), 8, GRAY)
        self.c.showPage()

    def table(self, rows, widths, y, size=8):
        style = ParagraphStyle(
            "cell", fontName="DV", fontSize=size, leading=size * 1.4, textColor=NAVY
        )
        header = ParagraphStyle("head", parent=style, fontName="DVB", textColor=colors.white)
        wrapped = [
            [Paragraph(html.escape(str(v)), header if i == 0 else style) for v in row]
            for i, row in enumerate(rows)
        ]
        t = Table(wrapped, colWidths=widths, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#d5e0e8")),
                ]
            )
        )
        _, h = t.wrap(WIDTH, H)
        t.drawOn(self.c, M, y - h)
        return y - h - 14

    def m(self, segment, variant="base", profile="sma"):
        return self.curves[(segment, variant, profile)]["metrics"]

    def build(self):
        self.overview()
        self.charts()
        self.sensitivity()
        self.audit()
        self.c.save()

    def overview(self):
        self.title(
            "Avaliação histórica",
            "Dados públicos - janela de 24 meses"
            if self.real
            else "Ensaio técnico - dados inteiramente sintéticos",
        )
        y = H - 148
        cards = [
            ("CANDLES DE SCORE", money(self.dataset["score_count"], 0)),
            ("CURVAS INDEPENDENTES", str(len(self.curves))),
            ("CAPITAL POR CURVA", "10.000,00 USDT"),
        ]
        cardw = (WIDTH - 20) / 3
        for i, (label, value) in enumerate(cards):
            x = M + i * (cardw + 10)
            self.c.setFillColor(LIGHT)
            self.c.roundRect(x, y - 58, cardw, 64, 6, fill=1, stroke=0)
            self.text(x + 10, y - 11, label, 7, GRAY, True)
            self.text(x + 10, y - 36, value, 13, TEAL, True)
        y -= 86
        y = self.p("O que foi processado", y, 13)
        description = (
            "Exportações públicas da Binance, obtidas por GETs permitidos em uma coleta separada."
            if self.real
            else "Fixture determinística de 1010 candles: 50 de aquecimento e dez dias de 96 candles. Os preços não representam mercado real."
        )
        y = self.p(
            description
            + " Avaliação SMA20/50, caixa e duas referências buy-and-hold, em quatro variantes previamente definidas. Cada carteira começa em caixa; patrimônios e retornos não são somados.",
            y,
        )
        rows = [["Segmento", "Início UTC", "Fim exclusivo UTC", "Candles"]]
        for segment in SEGMENTS:
            a, b = self.protocol["segments"][segment]
            rows.append([NAMES[segment], date(a), date(b), money((int(b) - int(a)) // 900000, 0)])
        y = self.table(rows, [144, 121, 136, WIDTH - 401], y)
        y = self.p("SMA - cenário-base, líquido de custos", y, 13)
        rows = [["Segmento", "E final (USDT)", "Retorno", "MDD", "Trades / fills"]]
        for segment in SEGMENTS:
            m = self.m(segment)
            rows.append(
                [
                    NAMES[segment],
                    money(m["final_equity"]),
                    percent(m["net_return"]),
                    percent(m["maximum_drawdown"]),
                    str(m["closed_trades"]) + " / " + str(m["fills"]),
                ]
            )
        y = self.table(rows, [132, 112, 82, 82, WIDTH - 408], y)
        m = self.m("test")
        y = self.p("Leitura do teste final", y, 13)
        y = self.p(
            "Resultado líquido da SMA no cenário-base: <b>"
            + percent(m["net_return"])
            + "</b>. Taxas de "
            + money(m["fees"])
            + " USDT; PnL realizado de "
            + money(m["realized"])
            + " USDT e não realizado de "
            + money(m["unrealized"])
            + " USDT. Posição residual: "
            + money(m["residual_btc"], 8)
            + " BTC.",
            y,
        )
        y = self.p(
            "Decisões: "
            + str(m["decisions"])
            + "; recusas: "
            + str(m["rejected"])
            + "; expirações: "
            + str(m["expired"])
            + ". Trava diária: "
            + ("sim" if m["daily_blocked"] else "não")
            + "; drawdown: "
            + ("sim" if m["drawdown_blocked"] else "não")
            + ".",
            y,
            8,
            GRAY,
        )
        y = self.p(
            "Capital fictício. O resultado não comprova execução real, liquidez ou rentabilidade futura. Filtros são proxy sintético; a política terminal marca a posição sem inventar venda.",
            y,
            8,
            GRAY,
        )
        assert y > 52, y
        self.footer()

    def charts(self):
        self.title(
            "Curvas comparáveis",
            "Cenário-base | capital inicial normalizado a 100 | séries independentes",
        )
        palette = {
            "sma": TEAL,
            "cash": GRAY,
            "buy_hold_100pct": colors.HexColor("#b47b22"),
            "buy_hold_10pct": colors.HexColor("#7054a1"),
        }
        y = H - 146
        for i, p in enumerate(PROFILES):
            self.c.setStrokeColor(palette[p])
            x = M + (i % 2) * 265
            yy = y - (i // 2) * 17
            self.c.line(x, yy, x + 20, yy)
            self.text(x + 26, yy - 3, PNAMES[p], 8)
        y -= 58
        for segment in SEGMENTS:
            self.text(M, y, NAMES[segment], 12, NAVY, True)
            x0 = M + 44
            x1 = W - M - 7
            top = y - 20
            bottom = y - 150
            data = {p: self.curves[(segment, "base", p)] for p in PROFILES}
            values = [
                float(D(point["equity"]) / 100)
                for curve in data.values()
                for point in curve["chart"]
            ]
            low = min(values)
            high = max(values)
            span = high - low or 1
            low -= span * 0.08
            high += span * 0.08
            span = high - low
            for f in [0, 0.5, 1]:
                yy = bottom + f * (top - bottom)
                self.c.setStrokeColor(colors.HexColor("#e2e9ef"))
                self.c.line(x0, yy, x1, yy)
                self.text(M, yy - 3, money(low + f * span), 7, GRAY)
            a, b = self.protocol["segments"][segment]
            for p, curve in data.items():
                path = self.c.beginPath()
                for j, point in enumerate(curve["chart"]):
                    x = x0 + (x1 - x0) * (int(point["at"]) - int(a)) / (int(b) - int(a))
                    v = float(D(point["equity"]) / 100)
                    yy = bottom + (v - low) / span * (top - bottom)
                    if j == 0:
                        path.moveTo(x, yy)
                    else:
                        path.lineTo(x, yy)
                self.c.setStrokeColor(palette[p])
                self.c.setLineWidth(1.3 if p == "sma" else 0.9)
                self.c.drawPath(path)
            self.text(x0, bottom - 14, date(a), 7, GRAY)
            self.text(x1 - 51, bottom - 14, date(b), 7, GRAY)
            y -= 180
        y = self.p(
            "A referência 100% assume exposição inicial diferente da SMA e do BH10. Gráficos usam redução determinística da apresentação; métricas oficiais usam todos os eventos, inclusive taxas, marcas e fills. Não há anualização.",
            y,
            8,
            GRAY,
        )
        assert y > 49, y
        self.footer()

    def sensitivity(self):
        self.title(
            "Sensibilidade e risco", "SMA20/50 | quatro variantes definidas antes dos resultados"
        )
        y = H - 145
        rows = [["Segmento / variante", "Retorno", "MDD", "Expos. média", "Taxas USDT", "Trades"]]
        for segment in SEGMENTS:
            for variant in VARIANTS:
                m = self.m(segment, variant)
                rows.append(
                    [
                        NAMES[segment] + " / " + VNAMES[variant],
                        percent(m["net_return"]),
                        percent(m["maximum_drawdown"]),
                        percent(m["average_exposure"]),
                        money(m["fees"]),
                        m["closed_trades"],
                    ]
                )
        y = self.table(rows, [188, 65, 65, 70, 71, WIDTH - 459], y, 7)
        y = self.p("Custos e tempo congelados", y, 12)
        y = self.table(
            [
                ["Variante", "Taxa / spread / slippage", "Atraso adicional"],
                ["Base", "10 / 10 / 5 bps", "0 candles"],
                ["Custos dobrados", "20 / 20 / 10 bps", "0 candles"],
                ["Atraso de 1 candle", "10 / 10 / 5 bps", "1 candle"],
                ["Custos + atraso", "20 / 20 / 10 bps", "1 candle"],
            ],
            [188, 195, WIDTH - 383],
            y,
            8,
        )
        y = self.p("Risco e interpretação", y, 12)
        y = self.p(
            "SMA: orçamento de entrada/peso até 10%, perda diária de 1% e drawdown de 5%. A exposição é revalidada na admissão e pode variar com o preço durante a posição. Travas bloqueiam novas entradas e não liquidam automaticamente a posição. O orçamento e a quantidade são revalidados quando a referência chega. SELL de redução passa pelos mesmos filtros e inventário.",
            y,
            8,
        )
        y = self.p(
            "Não selecionar retrospectivamente a melhor variante como resultado principal. Fills são eventos de execução; trades são ciclos encerrados. Custos já integram o PnL e não devem ser subtraídos novamente.",
            y,
            8,
            GRAY,
        )
        assert y > 49, y
        self.footer()

    def audit(self):
        self.title("Protocolo e auditoria", "Reprodução, limites e localização dos dados completos")
        y = H - 148
        y = self.p("Origem e congelamento", y, 13)
        y = self.p(
            "Fonte: "
            + html.escape(self.dataset["source"])
            + ". Janela de score: "
            + date(self.dataset["score_start"])
            + " a "
            + date(self.dataset["score_end"])
            + " UTC, fim exclusivo. Aquecimento de "
            + str(self.dataset["warmup"])
            + " fechamentos. "
            + str(len(self.dataset["sources"]))
            + " manifesto(s) de origem, com hashes dos quatro arquivos de cada exportação.",
            y,
        )
        for label, value in [
            ("Protocolo SHA256", self.protocol["protocol_hash"]),
            ("Dataset SHA256", self.dataset["data_sha256"]),
            ("Código SHA256", self.protocol["code_sha256"]),
            ("Resultado SHA256", self.r["result_sha256"]),
        ]:
            y = self.p("<b>" + label + "</b><br/>" + value[:32] + "<br/>" + value[32:], y, 7.5)
        y = self.p("Relógio e consumo do teste", y, 12)
        y = self.p(
            "Close disponível na fronteira -> decisão e slot SCHEDULED -> open observado em +1 ms -> admissão/reserva A -> fill B em +2 ms. A variante com atraso espera mais um candle. Freshness continua limitada a cinco segundos. No fim da janela há marcação, sem nova decisão ou liquidação implícita.",
            y,
            8,
        )
        y = self.p(
            "Desenvolvimento e validação completos precedem o teste. O primeiro uso final é registrado localmente; repetição exata é reprodução sem efeitos novos. Trocar ID ou diretório não torna uma janela real sobreposta intocada. Software e hashes não provam ausência de conhecimento humano prévio.",
            y,
            8,
        )
        y = self.p("Controle financeiro independente", y, 12)
        y = self.p(
            "Compra de referência 110 e venda 100, orçamento 1000 USDT, custos 10/10/5 bps: quantidade 9,072754 BTC, preços 110,11 / 99,90, taxas 0,99900095 / 0,90636813 e saldo final 9905,46181258 USDT. Esperado e obtido coincidiram no teste de aritmética; este controle não é o PnL das curvas acima.",
            y,
            8,
        )
        y = self.p("Dados completos e limitações", y, 12)
        y = self.p(
            "O export original contém report.html, report.json, equity.csv, trades.csv, decisions.csv e manifest.json com SHA256. O JSON inclui resultados mensais UTC e motivos de recusa. O guia docs/testes/sprint-05-validacao.md identifica comandos, arquivos, revisões, versões, cobertura e gates.",
            y,
            8,
        )
        y = self.p(
            "Fill integral com open OHLC é hipótese de simulação; não representa cotação tick a tick ou liquidez garantida. Filtros não são exchangeInfo histórico. USDT tem risco próprio; sem juros no caixa. Não transportar posição/PnL entre segmentos nem somar retornos das carteiras. Sem capital/taxas reais ou custo AWS.",
            y,
            8,
            GRAY,
        )
        assert y > 49, y
        self.footer()


if __name__ == "__main__":
    with localcontext() as ctx:
        ctx.prec = 80
        source = Path(sys.argv[1])
        target = Path(sys.argv[2])
        target.parent.mkdir(parents=True, exist_ok=True)
        Summary(json.loads(source.read_text()), target).build()
    print(target)
