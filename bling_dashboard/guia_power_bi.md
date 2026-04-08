# Guia Power BI — Dashboard Bling

## 1. Importar os arquivos Parquet

No Power BI Desktop:
1. **Obter Dados** → **Parquet**
2. Importe os 3 arquivos (um por vez):
   - `C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\pedidos.parquet`
   - `C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\itens.parquet`
   - `C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\parcelas.parquet`

---

## 2. Transformações no Power Query

Abra o **Power Query Editor** (Transformar Dados) e aplique para cada tabela:

### Tabela `pedidos`
- Coluna `data`: alterar tipo para **Data**
- Coluna `data_saida`: alterar tipo para **Data**
- Coluna `total`: alterar tipo para **Número Decimal**
- Coluna `total_produtos`: alterar tipo para **Número Decimal**
- Coluna `frete`: alterar tipo para **Número Decimal**
- Coluna `situacao_valor`: alterar tipo para **Número Inteiro**

### Tabela `itens`
- Coluna `pedido_data`: alterar tipo para **Data**
- Coluna `quantidade`: alterar tipo para **Número Decimal**
- Coluna `valor_unitario`: alterar tipo para **Número Decimal**
- Coluna `valor_total`: alterar tipo para **Número Decimal**

### Tabela `parcelas`
- Coluna `data_vencimento`: alterar tipo para **Data**
- Coluna `valor`: alterar tipo para **Número Decimal**

---

## 3. Criar tabela auxiliar de Canais

No Power Query, crie uma **Nova Consulta em Branco** e cole o código abaixo:

```
= Table.FromRows(
    {
        {"27.415.911/0001-36", "Mercado Livre"},
        {"35.635.824/0001-12", "Shopee"},
        {"03.007.331/0001-41", "Amazon"},
        {"15.436.940/0001-03", "Amazon"},
        {"39.420.373/0002-38", "Magalu"},
        {"39.420.373/0001-57", "Magalu"},
        {"47.960.950/0001-21", "TikTok Shop"},
        {"01.239.313/0001-60", "Outro"},
        {"33.041.260/0652-90", "Outro"},
        {"", "Venda Direta / Shopify"}
    },
    {"intermediador_cnpj", "canal"}
)
```

Nomeie essa consulta como `dim_canais`.

---

## 4. Criar tabela Calendário (DAX)

No Power BI, vá em **Modelagem** → **Nova Tabela** e cole:

```dax
dim_calendario =
ADDCOLUMNS(
    CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31)),
    "Ano",           YEAR([Date]),
    "Mês Número",    MONTH([Date]),
    "Mês Nome",      FORMAT([Date], "MMMM", "pt-BR"),
    "Mês Abrev",     FORMAT([Date], "MMM", "pt-BR"),
    "Trimestre",     "T" & QUARTER([Date]),
    "Semana",        WEEKNUM([Date], 2),
    "Dia Semana",    FORMAT([Date], "dddd", "pt-BR"),
    "AnoMês",        FORMAT([Date], "YYYY-MM"),
    "AnoTrimestre",  FORMAT([Date], "YYYY") & " T" & QUARTER([Date])
)
```

---

## 5. Relacionamentos

Em **Exibição de Modelo**, crie os relacionamentos abaixo:

| De (tabela) | Campo | Para (tabela) | Campo | Cardinalidade |
|-------------|-------|---------------|-------|---------------|
| `pedidos` | `id` | `itens` | `pedido_id` | 1 : Muitos |
| `pedidos` | `id` | `parcelas` | `pedido_id` | 1 : Muitos |
| `pedidos` | `intermediador_cnpj` | `dim_canais` | `intermediador_cnpj` | Muitos : 1 |
| `dim_calendario` | `Date` | `pedidos` | `data` | 1 : Muitos |

> Marque `dim_calendario` como **Tabela de Datas** (clique direito → Marcar como tabela de datas → coluna `Date`).

---

## 6. Medidas DAX

Crie uma tabela vazia chamada `_Medidas` (para organizar). Vá em **Modelagem** → **Nova Tabela**:

```dax
_Medidas = ROW("x", 1)
```

Depois crie cada medida abaixo clicando em **Nova Medida** dentro da tabela `_Medidas`:

---

### Faturamento

```dax
Faturamento Total =
CALCULATE(
    SUMX(pedidos, pedidos[total]),
    pedidos[situacao_valor] <> 2
)
```

```dax
Faturamento Produtos Total =
CALCULATE(
    SUMX(pedidos, pedidos[total_produtos]),
    pedidos[situacao_valor] <> 2
)
```

---

### Pedidos

```dax
Qtd Pedidos =
CALCULATE(
    COUNTROWS(pedidos),
    pedidos[situacao_valor] <> 2
)
```

```dax
Qtd Pedidos Pagos =
CALCULATE(
    COUNTROWS(pedidos),
    pedidos[situacao_valor] = 1
)
```

---

### Ticket Médio

```dax
Ticket Médio =
DIVIDE([Faturamento Total], [Qtd Pedidos], 0)
```

```dax
Ticket Médio Pagos =
DIVIDE(
    CALCULATE(SUMX(pedidos, pedidos[total]), pedidos[situacao_valor] = 1),
    CALCULATE(COUNTROWS(pedidos), pedidos[situacao_valor] = 1),
    0
)
```

---

### Comparação entre períodos (usando Slicer de data)

Para comparação entre dois períodos, use **dois slicers de data independentes**.
Crie dois parâmetros de data no Power BI:

**Modelagem → Novo Parâmetro → Campo**

Parâmetro A:
- Nome: `Período A Início` / `Período A Fim`

Parâmetro B:
- Nome: `Período B Início` / `Período B Fim`

Ou use o visual nativo de **Slicer** com o campo `dim_calendario[Date]` — duplique-o para ter dois ranges independentes e desconecte um deles da tabela de fatos usando medidas com CALCULATE + DATESBETWEEN.

Medidas para período fixo com parâmetro (exemplo):

```dax
Fat Período A =
CALCULATE(
    [Faturamento Total],
    DATESBETWEEN(dim_calendario[Date], [Período A Início], [Período A Fim])
)
```

```dax
Fat Período B =
CALCULATE(
    [Faturamento Total],
    DATESBETWEEN(dim_calendario[Date], [Período B Início], [Período B Fim])
)
```

```dax
Variação Fat % =
DIVIDE([Fat Período A] - [Fat Período B], [Fat Período B], 0)
```

```dax
Variação Pedidos % =
DIVIDE(
    CALCULATE([Qtd Pedidos Pagos], DATESBETWEEN(dim_calendario[Date], [Período A Início], [Período A Fim])) -
    CALCULATE([Qtd Pedidos Pagos], DATESBETWEEN(dim_calendario[Date], [Período B Início], [Período B Fim])),
    CALCULATE([Qtd Pedidos Pagos], DATESBETWEEN(dim_calendario[Date], [Período B Início], [Período B Fim])),
    0
)
```

---

### Produtos (tabela `itens`)

```dax
Receita Itens =
SUMX(itens, itens[valor_total])
```

```dax
Qtd Vendida =
SUM(itens[quantidade])
```

```dax
Ticket Médio Item =
DIVIDE([Receita Itens], [Qtd Vendida], 0)
```

---

## 7. Layout sugerido — Página "Receita"

### Visuais recomendados:

| Visual | Campos |
|--------|--------|
| **Cartão** × 3 | Faturamento Total / Qtd Pedidos / Ticket Médio |
| **Gráfico de barras horizontais** | dim_canais[canal] × Faturamento Total |
| **Gráfico de barras horizontais** | dim_canais[canal] × Ticket Médio |
| **Gráfico de barras agrupadas** | dim_canais[canal] × Qtd Pedidos |
| **Gráfico de linhas** | dim_calendario[Date] × Fat Período A + Fat Período B |
| **Gráfico de linhas** | dim_calendario[Date] × Qtd Pedidos Pagos (por período) |
| **Tabela** | itens[descricao] × Receita Itens × Qtd Vendida |
| **Slicer** × 2 | dim_calendario[Date] (para Período A e Período B) |
| **Slicer** | pedidos[conta] |

### Filtros de situação:
- Adicione um **filtro de página** em `pedidos[situacao_valor]` ≠ 2 para excluir cancelados de todos os visuais.

---

## 8. Atualização automática

Os Parquets são atualizados a cada hora automaticamente.
Para o Power BI Desktop atualizar:
- **Página Inicial → Atualizar** (manual)
- Para atualização automática, publique no **Power BI Service** e configure o **gateway de dados** com atualização agendada.
