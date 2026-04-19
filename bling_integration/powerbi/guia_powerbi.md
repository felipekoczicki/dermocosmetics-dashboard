# Guia Power BI — Integração Bling
## Tabelas: Pedidos + Itens | Comparativo de dois períodos

---

## 1. PARÂMETROS DE DATA

Crie 4 parâmetros em **Início → Transformar dados → Gerenciar Parâmetros → Novo**:

| Nome            | Tipo | Valor sugerido |
|-----------------|------|----------------|
| `Data1_Inicio`  | Data | 01/01/2025     |
| `Data1_Fim`     | Data | 31/01/2025     |
| `Data2_Inicio`  | Data | 01/01/2026     |
| `Data2_Fim`     | Data | 31/01/2026     |

---

## 2. POWER QUERY — CONSULTAS

### Tabela: Pedidos

Cole no **Editor Avançado**:

```
let
    Fonte = Parquet.Document(File.Contents("C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\pedidos.parquet"), [Compression=null, LegacyColumnNameEncoding=false, MaxDepth=null]),
    #"Tipo Alterado" = Table.TransformColumnTypes(Fonte,{
        {"id",              type text},
        {"numero",          type text},
        {"total_produtos",  Currency.Type},
        {"total",           Currency.Type},
        {"outras_despesas", Currency.Type},
        {"loja_id",         Int64.Type},
        {"situacao_id",     Int64.Type}
    }),
    #"Dividir Data" = Table.SplitColumn(
        Table.TransformColumnTypes(#"Tipo Alterado", {{"data", type text}}, "pt-BR"),
        "data", Splitter.SplitTextByDelimiter(" ", QuoteStyle.Csv), {"data.1", "data.2"}
    ),
    #"Tipo Data" = Table.TransformColumnTypes(#"Dividir Data",{{"data.1", type date}, {"data.2", type time}}),
    #"Renomear Data" = Table.RenameColumns(#"Tipo Data",{{"data.1", "data"}}),
    #"Remover Colunas" = Table.RemoveColumns(#"Renomear Data",{
        "data.2", "numero_loja", "numero_pedido_compra", "data_saida", "data_prevista",
        "outras_despesas", "desconto_valor", "desconto_unidade", "contato_id",
        "contato_tipo_pessoa", "vendedor_id", "categoria_id", "nota_fiscal_id",
        "total_icms", "total_ipi", "taxa_comissao", "custo_frete", "valor_base",
        "frete_por_conta", "frete", "qtd_volumes", "peso_bruto", "prazo_entrega",
        "transportador_id", "transportador_nome", "entrega_nome", "entrega_endereco",
        "entrega_numero", "entrega_complemento", "entrega_bairro", "entrega_cep",
        "intermediador_cnpj", "intermediador_usuario", "observacoes",
        "observacoes_internas", "detalhado", "synced_at", "situacao_valor"
    }),
    #"Status Pedido" = Table.AddColumn(#"Remover Colunas", "status_pedido", each
        if [situacao_id] = 6      then "Em Aberto"
        else if [situacao_id] = 9      then "Atendido"
        else if [situacao_id] = 12     then "Cancelado"
        else if [situacao_id] = 15     then "Em Andamento"
        else if [situacao_id] = 21     then "Em Digitação"
        else if [situacao_id] = 24     then "Verificado"
        else if [situacao_id] = 126724 then "Checkout Parcial"
        else if [situacao_id] = 25249  then "NFC-e"
        else if [situacao_id] = 32685  then "Marketplace"
        else if [situacao_id] = 327281 then "Expedição"
        else if [situacao_id] = 466428 then "Gerando Etiqueta"
        else if [situacao_id] = 467795 then "Em Ajuste"
        else if [situacao_id] = 467975 then "Chargeback"
        else if [situacao_id] = 468045 then "Confirmar Endereço"
        else if [situacao_id] = 533963 then "Devolvido"
        else if [situacao_id] = 658110 then "Recebido na Stokki"
        else if [situacao_id] = 658111 then "Erro de Integração"
        else if [situacao_id] = 658112 then "Aguardando Transportador"
        else if [situacao_id] = 658113 then "Finalizado"
        else if [situacao_id] = 685918 then "Enviar para Stokki"
        else if [situacao_id] = 742050 then "Full Shopee"
        else "Outros"
    , type text),
    #"Canal Nome" = Table.AddColumn(#"Status Pedido", "canal_nome", each
        let id = [loja_id]
        in if id = 0              then "Sem Loja"
          else if id = 203517871  then "Pedido Manual - Matriz"
          else if id = 203537101  then "Woocommerce 1 - Matriz"
          else if id = 203546568  then "Woocommerce 2 - Matriz"
          else if id = 203645900  then "Mercado Livre - Matriz"
          else if id = 203674668  then "Shopee - Matriz"
          else if id = 203736743  then "Magalu - Matriz"
          else if id = 203787491  then "Casas Bahia - Matriz"
          else if id = 203805899  then "Woocommerce 2 - Matriz"
          else if id = 204869938  then "Yampi - Matriz"
          else if id = 204872143  then "Shopify - Matriz"
          else if id = 204879236  then "Amazon - Matriz"
          else if id = 204882412  then "Época Cosméticos - Matriz"
          else if id = 205155589  then "Uappi - Matriz"
          else if id = 205163053  then "Beleza na Web - Matriz"
          else if id = 205346798  then "Yampi 2 - Matriz"
          else if id = 205410647  then "TikTok Shop - Matriz"
          else if id = 205445683  then "Influencers - Matriz"
          else if id = 205446112  then "Assinatura - Matriz"
          else if id = 205446121  then "Monetizze - Matriz"
          else if id = 205446125  then "B4YOU - Matriz"
          else if id = 205470702  then "Payt - Matriz"
          else if id = 205702648  then "Afilistar - Matriz"
          else if id = 205834757  then "Base - Matriz"
          else if id = 205856775  then "TikTok Shop - Filial"
          else if id = 205864553  then "Shopee - Filial"
          else if id = 205948946  then "Pedido Manual - Filial"
          else if id = 205978634  then "Shopify API - Matriz"
          else if id = 205979534  then "Shopify API - Filial"
          else if id = 206013577  then "Reenvio - Matriz"
          else "Outros"
    , type text),
    #"Filtro Períodos" = Table.SelectRows(#"Canal Nome", each
        ([data] >= Data1_Inicio and [data] <= Data1_Fim) or
        ([data] >= Data2_Inicio and [data] <= Data2_Fim)
    ),
    #"Período Label" = Table.AddColumn(#"Filtro Períodos", "periodo", each
        if [data] >= Data1_Inicio and [data] <= Data1_Fim then "Período 1"
        else "Período 2"
    , type text)
in
    #"Período Label"
```

---

### Tabela: Itens

Cole no **Editor Avançado**:

```
let
    Fonte = Parquet.Document(File.Contents("C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\itens.parquet"), [Compression=null, LegacyColumnNameEncoding=false, MaxDepth=null]),
    #"Tipo Alterado" = Table.TransformColumnTypes(Fonte,{
        {"pedido_id",      type text},
        {"quantidade",     type number},
        {"valor_unitario", Currency.Type},
        {"valor_total",    Currency.Type},
        {"desconto",       Currency.Type}
    }),
    #"Remover Colunas" = Table.RemoveColumns(#"Tipo Alterado",{
        "pedido_data", "descricao_detalhada", "aliquota_ipi",
        "comissao_base", "comissao_aliquota", "comissao_valor",
        "natureza_operacao_id"
    })
in
    #"Remover Colunas"
```

---

## 3. RELACIONAMENTO

Em **Modelagem → Gerenciar relações → Nova**:

| Tabela     | Coluna      | Tabela   | Coluna | Cardinalidade | Direção       |
|------------|-------------|----------|--------|---------------|---------------|
| `itens`    | `pedido_id` | `pedidos`| `id`   | Muitos para 1 | itens→pedidos |

---

## 4. MEDIDAS DAX

Crie uma tabela vazia chamada `_Medidas` e adicione as medidas abaixo.

### Período 1

```
P1 Faturamento =
    CALCULATE(
        SUM(pedidos[total]),
        pedidos[periodo] = "Período 1",
        pedidos[situacao_id] = 9
    )

P1 Pedidos =
    CALCULATE(
        COUNTROWS(pedidos),
        pedidos[periodo] = "Período 1",
        pedidos[situacao_id] = 9
    )

P1 Ticket Médio =
    DIVIDE([P1 Faturamento], [P1 Pedidos])

P1 Itens Vendidos =
    CALCULATE(
        SUM(itens[quantidade]),
        pedidos[periodo] = "Período 1",
        pedidos[situacao_id] = 9
    )

P1 Itens por Pedido =
    DIVIDE([P1 Itens Vendidos], [P1 Pedidos])
```

### Período 2

```
P2 Faturamento =
    CALCULATE(
        SUM(pedidos[total]),
        pedidos[periodo] = "Período 2",
        pedidos[situacao_id] = 9
    )

P2 Pedidos =
    CALCULATE(
        COUNTROWS(pedidos),
        pedidos[periodo] = "Período 2",
        pedidos[situacao_id] = 9
    )

P2 Ticket Médio =
    DIVIDE([P2 Faturamento], [P2 Pedidos])

P2 Itens Vendidos =
    CALCULATE(
        SUM(itens[quantidade]),
        pedidos[periodo] = "Período 2",
        pedidos[situacao_id] = 9
    )

P2 Itens por Pedido =
    DIVIDE([P2 Itens Vendidos], [P2 Pedidos])
```

### Variações (Período 2 vs Período 1)

```
Var Faturamento % =
    DIVIDE([P2 Faturamento] - [P1 Faturamento], [P1 Faturamento])

Var Pedidos % =
    DIVIDE([P2 Pedidos] - [P1 Pedidos], [P1 Pedidos])

Var Ticket % =
    DIVIDE([P2 Ticket Médio] - [P1 Ticket Médio], [P1 Ticket Médio])

Var Itens % =
    DIVIDE([P2 Itens Vendidos] - [P1 Itens Vendidos], [P1 Itens Vendidos])
```

---

## 5. PÁGINAS SUGERIDAS

### Página 1 — Comparativo Geral
- 4 cartões lado a lado: **Faturamento P1** vs **Faturamento P2** + **Var%**
- 4 cartões: **Pedidos**, **Ticket Médio**, **Itens Vendidos**, **Itens por Pedido**
- Gráfico de barras agrupadas por `canal_nome`: P1 vs P2

### Página 2 — Produtos
- Tabela: `descricao` | Qtd P1 | Qtd P2 | Var%
- Top 10 produtos por `valor_total` em cada período

### Página 3 — Geográfico
- Barras por `entrega_uf`: P1 vs P2
- Filtro de `canal_nome` e `status_pedido`

---

## 6. ATUALIZAR OS PERÍODOS

Para mudar as datas basta ir em:
**Início → Transformar dados → Gerenciar Parâmetros**
e alterar os valores de `Data1_Inicio`, `Data1_Fim`, `Data2_Inicio`, `Data2_Fim`.
