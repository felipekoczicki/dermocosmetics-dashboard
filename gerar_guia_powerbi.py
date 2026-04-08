from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

OUT = Path(r"C:\Users\Lenovo\Desktop\Claude_Cloude_Project\Guia_PowerBI_Comparacao_Periodos.pdf")

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
)

W = A4[0] - 4*cm  # largura útil

# ------------------------------------------------------------------
# Estilos
# ------------------------------------------------------------------
styles = getSampleStyleSheet()

titulo_doc = ParagraphStyle("titulo_doc",
    fontSize=22, leading=28, alignment=TA_CENTER,
    textColor=colors.HexColor("#1a1a2e"), spaceAfter=6,
    fontName="Helvetica-Bold",
)
subtitulo_doc = ParagraphStyle("subtitulo_doc",
    fontSize=12, leading=16, alignment=TA_CENTER,
    textColor=colors.HexColor("#555555"), spaceAfter=4,
    fontName="Helvetica",
)
titulo_secao = ParagraphStyle("titulo_secao",
    fontSize=14, leading=18,
    textColor=colors.white, spaceAfter=0, spaceBefore=16,
    fontName="Helvetica-Bold", leftIndent=0,
)
titulo_passo = ParagraphStyle("titulo_passo",
    fontSize=12, leading=16,
    textColor=colors.HexColor("#1a1a2e"), spaceAfter=4, spaceBefore=12,
    fontName="Helvetica-Bold",
)
corpo = ParagraphStyle("corpo",
    fontSize=10, leading=15,
    textColor=colors.HexColor("#333333"), spaceAfter=4,
    fontName="Helvetica",
)
codigo = ParagraphStyle("codigo",
    fontSize=9, leading=14,
    textColor=colors.HexColor("#1a1a2e"),
    fontName="Courier",
    backColor=colors.HexColor("#f4f4f4"),
    leftIndent=12, rightIndent=12,
    spaceBefore=4, spaceAfter=4,
    borderPadding=(6, 8, 6, 8),
)
nota = ParagraphStyle("nota",
    fontSize=9, leading=13,
    textColor=colors.HexColor("#555555"),
    fontName="Helvetica-Oblique",
    leftIndent=12, spaceAfter=4,
)
item = ParagraphStyle("item",
    fontSize=10, leading=15,
    textColor=colors.HexColor("#333333"),
    fontName="Helvetica",
    leftIndent=16, spaceAfter=3,
    bulletIndent=6,
)


def secao(titulo, cor="#16213e"):
    """Cabeçalho colorido de seção."""
    data = [[Paragraph(titulo, titulo_secao)]]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(cor)),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return t


def passo(numero, titulo_texto):
    """Número do passo + título."""
    data = [[
        Paragraph(f"<b>{numero}</b>", ParagraphStyle("num",
            fontSize=13, textColor=colors.white, fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        )),
        Paragraph(titulo_texto, ParagraphStyle("ptit",
            fontSize=11, textColor=colors.HexColor("#1a1a2e"),
            fontName="Helvetica-Bold", leading=15,
        )),
    ]]
    t = Table(data, colWidths=[1*cm, W - 1*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#0f3460")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#e8f0fe")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (0, 0), 4),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return t


def caixa_dax(codigo_texto):
    """Caixa de código DAX."""
    linhas = codigo_texto.strip().split("\n")
    data = [[Paragraph(l.replace("<", "&lt;").replace(">", "&gt;") or " ", codigo)] for l in linhas]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f4f4")),
        ("LINEAFTER", (0, 0), (-1, -1), 0.5, colors.HexColor("#0f3460")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#0f3460")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def li(texto):
    return Paragraph(f"• {texto}", item)


def sp(h=0.3):
    return Spacer(1, h*cm)


# ------------------------------------------------------------------
# Conteúdo
# ------------------------------------------------------------------
story = []

# Capa
story.append(sp(2))
story.append(Paragraph("Power BI", subtitulo_doc))
story.append(Paragraph("Comparação entre Dois Períodos", titulo_doc))
story.append(sp(0.3))
story.append(HRFlowable(width=W, thickness=2, color=colors.HexColor("#0f3460")))
story.append(sp(0.3))
story.append(Paragraph("Guia passo a passo para criar dois ranges de datas independentes", subtitulo_doc))
story.append(Paragraph("e medir variação de faturamento e pedidos entre períodos distintos.", subtitulo_doc))
story.append(sp(3))

# Visão geral
story.append(secao("  Visão Geral"))
story.append(sp(0.3))
story.append(Paragraph(
    "Este guia ensina a criar dois slicers de data independentes no Power BI — "
    "<b>Data Atual</b> e <b>Data Comparativa</b> — para comparar faturamento, "
    "pedidos pagos e ticket médio entre dois períodos distintos sem que um slicer "
    "interfira no outro.",
    corpo,
))
story.append(sp(0.2))
story.append(Paragraph("<b>O que você vai criar:</b>", corpo))
story.append(li("Dois slicers de data independentes (range de início e fim)"))
story.append(li("Duas tabelas de calendário separadas no modelo de dados"))
story.append(li("Medidas DAX para faturamento, pedidos e variação % por período"))
story.append(li("Cartões e gráficos de linha com os dois períodos sobrepostos"))
story.append(sp(0.5))

# ------------------------------------------------------------------ PARTE 1
story.append(PageBreak())
story.append(secao("  Parte 1 — Preparar o Modelo de Dados", cor="#0f3460"))
story.append(sp(0.4))

story.append(passo("1", "Importar os arquivos Parquet"))
story.append(sp(0.2))
story.append(Paragraph("No Power BI Desktop, siga:", corpo))
story.append(li("Clique em <b>Página Inicial → Obter Dados → Parquet</b>"))
story.append(li("Importe os três arquivos abaixo (um por vez):"))
story.append(sp(0.2))

caminhos = [
    ["Arquivo", "Caminho"],
    ["pedidos.parquet",  r"...\bling_integration\exports\pedidos.parquet"],
    ["itens.parquet",    r"...\bling_integration\exports\itens.parquet"],
    ["parcelas.parquet", r"...\bling_integration\exports\parcelas.parquet"],
    ["canais_template.csv", r"...\bling_integration\exports\canais_template.csv"],
]
t = Table(caminhos, colWidths=[4*cm, W - 4*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t)
story.append(sp(0.4))

story.append(passo("2", "Criar duas tabelas de Calendário separadas"))
story.append(sp(0.2))
story.append(Paragraph(
    "A chave para dois slicers independentes é ter <b>duas tabelas de datas distintas</b>. "
    "Uma se conecta à tabela de pedidos (filtra de verdade) e a outra fica isolada "
    "(alimenta apenas as medidas DAX).",
    corpo,
))
story.append(sp(0.2))
story.append(Paragraph("Vá em <b>Modelagem → Nova Tabela</b> e crie as duas tabelas abaixo:", corpo))
story.append(sp(0.2))
story.append(Paragraph("<b>Tabela 1 — Data Atual (conectada aos pedidos):</b>", corpo))
story.append(caixa_dax("""dim_calendario_atual =
CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31))"""))
story.append(sp(0.2))
story.append(Paragraph("<b>Tabela 2 — Data Comparativa (isolada, sem conexão):</b>", corpo))
story.append(caixa_dax("""dim_calendario_comp =
CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31))"""))
story.append(sp(0.2))
story.append(Paragraph(
    "⚠ Ajuste as datas DATE(2020,1,1) e DATE(2026,12,31) conforme o range dos seus dados.",
    nota,
))
story.append(sp(0.4))

story.append(passo("3", "Criar os relacionamentos"))
story.append(sp(0.2))
story.append(Paragraph("Vá em <b>Exibição de Modelo</b> e crie os relacionamentos:", corpo))
story.append(sp(0.2))

rels = [
    ["De", "Campo", "Para", "Campo", "Tipo"],
    ["dim_calendario_atual", "Date",    "pedidos",    "data",      "1 : Muitos"],
    ["pedidos",              "id",       "itens",      "pedido_id", "1 : Muitos"],
    ["pedidos",              "id",       "parcelas",   "pedido_id", "1 : Muitos"],
    ["pedidos",              "loja_id",  "dim_canais", "loja_id",   "Muitos : 1"],
]
t2 = Table(rels, colWidths=[4*cm, 3*cm, 3.5*cm, 3*cm, 3*cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t2)
story.append(sp(0.2))
story.append(Paragraph(
    "⚠ dim_calendario_comp NÃO deve ter relacionamento com nenhuma tabela — ela fica isolada.",
    nota,
))

# ------------------------------------------------------------------ PARTE 2
story.append(PageBreak())
story.append(secao("  Parte 2 — Medidas DAX", cor="#0f3460"))
story.append(sp(0.4))
story.append(Paragraph(
    "Crie uma tabela vazia para organizar as medidas: <b>Modelagem → Nova Tabela</b>:",
    corpo,
))
story.append(caixa_dax("_Medidas = ROW(\"x\", 1)"))
story.append(sp(0.3))
story.append(Paragraph("Em seguida, clique em <b>Nova Medida</b> dentro de <b>_Medidas</b> e crie cada uma abaixo:", corpo))
story.append(sp(0.3))

story.append(passo("4", "Medidas de Faturamento"))
story.append(sp(0.2))
story.append(Paragraph("<b>Faturamento — Data Atual:</b>", corpo))
story.append(caixa_dax("""Fat Data Atual =
CALCULATE(
    SUM(pedidos[total]),
    pedidos[situacao_valor] <> 2,
    TREATAS(VALUES(dim_calendario_atual[Date]), pedidos[data])
)"""))
story.append(sp(0.2))
story.append(Paragraph("<b>Faturamento — Data Comparativa:</b>", corpo))
story.append(caixa_dax("""Fat Data Comparativa =
CALCULATE(
    SUM(pedidos[total]),
    pedidos[situacao_valor] <> 2,
    TREATAS(VALUES(dim_calendario_comp[Date]), pedidos[data])
)"""))
story.append(sp(0.2))
story.append(Paragraph("<b>Variação de Faturamento (%):</b>", corpo))
story.append(caixa_dax("""Variação Fat % =
DIVIDE(
    [Fat Data Atual] - [Fat Data Comparativa],
    [Fat Data Comparativa],
    0
)"""))
story.append(sp(0.3))

story.append(passo("5", "Medidas de Pedidos Pagos"))
story.append(sp(0.2))
story.append(Paragraph("<b>Pedidos Pagos — Data Atual:</b>", corpo))
story.append(caixa_dax("""Pedidos Pagos Atual =
CALCULATE(
    COUNTROWS(pedidos),
    pedidos[situacao_valor] = 1,
    TREATAS(VALUES(dim_calendario_atual[Date]), pedidos[data])
)"""))
story.append(sp(0.2))
story.append(Paragraph("<b>Pedidos Pagos — Data Comparativa:</b>", corpo))
story.append(caixa_dax("""Pedidos Pagos Comp =
CALCULATE(
    COUNTROWS(pedidos),
    pedidos[situacao_valor] = 1,
    TREATAS(VALUES(dim_calendario_comp[Date]), pedidos[data])
)"""))
story.append(sp(0.2))
story.append(Paragraph("<b>Variação de Pedidos (%):</b>", corpo))
story.append(caixa_dax("""Variação Pedidos % =
DIVIDE(
    [Pedidos Pagos Atual] - [Pedidos Pagos Comp],
    [Pedidos Pagos Comp],
    0
)"""))
story.append(sp(0.3))

story.append(passo("6", "Medidas de Ticket Médio"))
story.append(sp(0.2))
story.append(caixa_dax("""Ticket Médio Atual =
DIVIDE([Fat Data Atual], [Pedidos Pagos Atual], 0)"""))
story.append(sp(0.2))
story.append(caixa_dax("""Ticket Médio Comp =
DIVIDE([Fat Data Comparativa], [Pedidos Pagos Comp], 0)"""))
story.append(sp(0.2))
story.append(caixa_dax("""Variação Ticket % =
DIVIDE(
    [Ticket Médio Atual] - [Ticket Médio Comp],
    [Ticket Médio Comp],
    0
)"""))

# ------------------------------------------------------------------ PARTE 3
story.append(PageBreak())
story.append(secao("  Parte 3 — Criar os Slicers e Visuais", cor="#0f3460"))
story.append(sp(0.4))

story.append(passo("7", "Inserir os dois slicers de data"))
story.append(sp(0.2))
story.append(Paragraph("<b>Slicer 1 — Data Atual:</b>", corpo))
story.append(li("Insira um visual <b>Slicer</b> na página"))
story.append(li("Campo: <b>dim_calendario_atual[Date]</b>"))
story.append(li("Formato → Slicer → Estilo: <b>Entre</b>"))
story.append(li("Renomeie o título para <b>Data Atual</b>"))
story.append(sp(0.3))
story.append(Paragraph("<b>Slicer 2 — Data Comparativa:</b>", corpo))
story.append(li("Insira um segundo visual <b>Slicer</b> na página"))
story.append(li("Campo: <b>dim_calendario_comp[Date]</b>"))
story.append(li("Formato → Slicer → Estilo: <b>Entre</b>"))
story.append(li("Renomeie o título para <b>Data Comparativa</b>"))
story.append(sp(0.2))
story.append(Paragraph(
    "Como cada slicer usa uma tabela de calendário diferente, eles são 100% independentes "
    "— selecionar datas em um não afeta o outro.",
    nota,
))
story.append(sp(0.4))

story.append(passo("8", "Criar os Cartões de KPI"))
story.append(sp(0.2))
story.append(Paragraph("Insira visuais de <b>Cartão</b> para cada medida:", corpo))
story.append(sp(0.2))

cards = [
    ["Cartão", "Medida", "Formato sugerido"],
    ["Faturamento Atual",      "Fat Data Atual",        "Moeda R$"],
    ["Faturamento Comparativo","Fat Data Comparativa",   "Moeda R$"],
    ["Variação Fat.",          "Variação Fat %",         "Percentual"],
    ["Pedidos Atual",          "Pedidos Pagos Atual",    "Número inteiro"],
    ["Pedidos Comparativo",    "Pedidos Pagos Comp",     "Número inteiro"],
    ["Variação Pedidos",       "Variação Pedidos %",     "Percentual"],
    ["Ticket Médio Atual",     "Ticket Médio Atual",     "Moeda R$"],
    ["Ticket Médio Comp.",     "Ticket Médio Comp",      "Moeda R$"],
]
t3 = Table(cards, colWidths=[4.5*cm, 5.5*cm, W - 10*cm])
t3.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t3)
story.append(sp(0.4))

story.append(passo("9", "Criar o gráfico de linha com os dois períodos"))
story.append(sp(0.2))
story.append(Paragraph("Para comparar visualmente os dois períodos no mesmo gráfico:", corpo))
story.append(li("Insira um visual de <b>Gráfico de Linhas</b>"))
story.append(li("Eixo X: <b>dim_calendario_atual[Date]</b> (hierarquia: Ano → Mês → Dia)"))
story.append(li("Valores: <b>Fat Data Atual</b> e <b>Fat Data Comparativa</b>"))
story.append(li("Legenda: deixe vazia (as séries já se diferenciam por cor)"))
story.append(sp(0.2))
story.append(Paragraph(
    "As duas linhas aparecerão no mesmo gráfico. A linha da Data Atual "
    "muda conforme o slicer 'Data Atual'; a linha Comparativa muda conforme o slicer 'Data Comparativa'.",
    nota,
))
story.append(sp(0.4))

story.append(passo("10", "Filtro global de situação (excluir cancelados)"))
story.append(sp(0.2))
story.append(Paragraph("Para garantir que cancelados não entrem em nenhum visual da página:", corpo))
story.append(li("Abra o painel <b>Filtros</b> (lado direito)"))
story.append(li("Arraste <b>pedidos[situacao_valor]</b> para <b>Filtros nesta página</b>"))
story.append(li("Selecione <b>Filtragem básica</b> e desmarque o valor <b>2</b> (Cancelado)"))
story.append(sp(0.2))
story.append(Paragraph(
    "As medidas DAX já filtram situacao_valor <> 2 internamente, mas esse filtro "
    "de página garante consistência em todos os outros visuais.",
    nota,
))

# ------------------------------------------------------------------ Dicas finais
story.append(PageBreak())
story.append(secao("  Dicas Finais", cor="#16213e"))
story.append(sp(0.4))

dicas = [
    ("Formatação de moeda",
     "Selecione a medida em _Medidas → Ferramentas de Medida → Formato → Moeda → R$ Português (Brasil)"),
    ("Formatação de percentual",
     "Selecione a medida → Formato → Percentual. Para mostrar +10,5% com sinal, "
     "use formato personalizado: +0,0%;-0,0%;0,0%"),
    ("Atualização dos dados",
     "Os arquivos Parquet são atualizados automaticamente a cada hora. "
     "No Power BI Desktop, clique em Página Inicial → Atualizar para recarregar. "
     "No Power BI Service, configure atualização agendada via gateway."),
    ("Renomear medidas",
     "Clique com botão direito na medida em _Medidas → Renomear. "
     "O nome aparece nos cartões e legendas dos gráficos."),
    ("Adicionar mais canais",
     "Para incluir um novo canal de venda, edite o arquivo canais_template.csv "
     "e clique em Atualizar no Power BI."),
]

for titulo_dica, texto_dica in dicas:
    data = [[
        Paragraph(f"<b>{titulo_dica}</b>", ParagraphStyle("dt",
            fontSize=10, textColor=colors.HexColor("#0f3460"),
            fontName="Helvetica-Bold", leading=14,
        )),
        Paragraph(texto_dica, corpo),
    ]]
    td = Table(data, colWidths=[4*cm, W - 4*cm])
    td.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#e8f0fe")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ]))
    story.append(td)
    story.append(sp(0.15))

story.append(sp(1))
story.append(HRFlowable(width=W, thickness=1, color=colors.HexColor("#0f3460")))
story.append(sp(0.2))
story.append(Paragraph("Guia gerado automaticamente — Dashboard Bling / Cicatribem", subtitulo_doc))

# ------------------------------------------------------------------
doc.build(story)
print(f"PDF gerado: {OUT}")
