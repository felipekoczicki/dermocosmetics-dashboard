// ============================================================
// POWER QUERY M — Integração Bling para Power BI
// Copie cada bloco no editor avançado da respectiva consulta
// Caminho base: ajuste RAIZ_EXPORTS se mover os arquivos
// ============================================================

// ── PASSO 1: Parâmetro de caminho (crie um Parâmetro no Power BI)
// Nome: RAIZ_EXPORTS  |  Tipo: Texto  |  Valor atual:
// C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\


// ============================================================
// CONSULTA: Pedidos
// ============================================================
let
    Fonte = Parquet.Document(
        File.Contents(RAIZ_EXPORTS & "pedidos.parquet")
    ),

    // Tipos corretos
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"id",                  Int64.Type},
        {"conta",               type text},
        {"numero",              Int64.Type},
        {"data",                type date},
        {"data_saida",          type date},
        {"data_prevista",       type date},
        {"total_produtos",      type number},
        {"total",               type number},
        {"outras_despesas",     type number},
        {"desconto_valor",      type number},
        {"situacao_id",         Int64.Type},
        {"situacao_valor",      Int64.Type},
        {"contato_id",          Int64.Type},
        {"contato_nome",        type text},
        {"contato_tipo_pessoa", type text},
        {"contato_documento",   type text},
        {"loja_id",             Int64.Type},
        {"frete",               type number},
        {"custo_frete",         type number},
        {"entrega_uf",          type text},
        {"entrega_municipio",   type text},
        {"intermediador_cnpj",  type text},
        {"intermediador_usuario", type text},
        {"detalhado",           Int64.Type}
    }),

    // Coluna: Nome da situação (lookup local)
    AdicionaSituacao = Table.AddColumn(Tipos, "situacao_nome", each
        let s = [situacao_valor]
        in if s = 0  then "Em Aberto"
          else if s = 1  then "Atendido"
          else if s = 2  then "Cancelado"
          else if s = 3  then "Em Andamento"
          else if s = 10 then "Verificado"
          else if s = 11 then "Em Envio"
          else if s = 12 then "Enviado"
          else "Outros (" & Text.From(s) & ")"
    , type text),

    // Coluna: Nome do canal pela loja_id
    AdicionaCanal = Table.AddColumn(AdicionaSituacao, "canal_nome", each
        let id = [loja_id]
        in if id = 0          then "Sem Loja"
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

    // Coluna: Marketplace pelo CNPJ do intermediador
    AdicionaMarketplace = Table.AddColumn(AdicionaCanal, "marketplace", each
        let c = [intermediador_cnpj]
        in if c = "27.415.911/0001-36" then "Mercado Livre"
          else if c = "35.635.824/0001-12" then "Shopee"
          else if c = "03.007.331/0001-41" then "B2W / Americanas"
          else if c = "15.436.940/0001-03" then "Olist"
          else if c = "47.960.950/0001-21" then "Shein"
          else if c = "39.420.373/0002-38" then "Magazine Luiza"
          else if c = "39.420.373/0001-57" then "Magazine Luiza"
          else if c = "01.239.313/0001-60" then "Amazon"
          else if c = null or c = ""        then "Loja Própria"
          else "Outros"
    , type text),

    // Coluna: Ano e Mês para filtros
    AdicionaAno = Table.AddColumn(AdicionaMarketplace, "ano",
        each Date.Year([data]), Int64.Type),

    AdicionaMes = Table.AddColumn(AdicionaAno, "mes",
        each Date.Month([data]), Int64.Type),

    AdicionaAnoMes = Table.AddColumn(AdicionaMes, "ano_mes",
        each Text.PadStart(Text.From([mes]), 2, "0") & "/" & Text.From([ano]),
        type text),

    // Remove colunas desnecessárias para aliviar o modelo
    RemoveColunas = Table.RemoveColumns(AdicionaAnoMes, {
        "numero_loja", "numero_pedido_compra", "data_prevista",
        "desconto_unidade", "vendedor_id", "categoria_id", "nota_fiscal_id",
        "total_icms", "total_ipi", "taxa_comissao", "valor_base",
        "frete_por_conta", "qtd_volumes", "peso_bruto", "prazo_entrega",
        "transportador_id", "transportador_nome",
        "entrega_nome", "entrega_endereco", "entrega_numero",
        "entrega_complemento", "entrega_bairro", "entrega_cep",
        "observacoes", "observacoes_internas", "synced_at"
    })
in
    RemoveColunas


// ============================================================
// CONSULTA: Itens
// ============================================================
let
    Fonte = Parquet.Document(
        File.Contents(RAIZ_EXPORTS & "itens.parquet")
    ),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"pedido_id",      Int64.Type},
        {"conta",          type text},
        {"pedido_data",    type date},
        {"item_id",        Int64.Type},
        {"codigo",         type text},
        {"descricao",      type text},
        {"unidade",        type text},
        {"quantidade",     type number},
        {"valor_unitario", type number},
        {"desconto",       type number},
        {"produto_id",     Int64.Type},
        {"valor_total",    type number}
    }),
    RemoveColunas = Table.RemoveColumns(Tipos, {
        "descricao_detalhada", "aliquota_ipi",
        "comissao_base", "comissao_aliquota", "comissao_valor",
        "natureza_operacao_id"
    })
in
    RemoveColunas


// ============================================================
// CONSULTA: Parcelas
// ============================================================
let
    Fonte = Parquet.Document(
        File.Contents(RAIZ_EXPORTS & "parcelas.parquet")
    ),
    Tipos = Table.TransformColumnTypes(Fonte, {
        {"pedido_id",         Int64.Type},
        {"conta",             type text},
        {"parcela_id",        Int64.Type},
        {"data_vencimento",   type date},
        {"valor",             type number},
        {"forma_pagamento_id", Int64.Type}
    })
in
    Tipos


// ============================================================
// CONSULTA: Calendário (tabela de datas)
// Crie uma consulta em branco e cole este código
// ============================================================
let
    DataInicio  = #date(2025, 1, 1),
    DataFim     = Date.From(DateTime.LocalNow()),
    ListaDatas  = List.Dates(DataInicio, Duration.Days(DataFim - DataInicio) + 1, #duration(1,0,0,0)),
    Tabela      = Table.FromList(ListaDatas, Splitter.SplitByNothing(), {"Data"}),
    Tipo        = Table.TransformColumnTypes(Tabela, {{"Data", type date}}),
    Ano         = Table.AddColumn(Tipo,   "Ano",          each Date.Year([Data]),             Int64.Type),
    Mes         = Table.AddColumn(Ano,    "Mês",          each Date.Month([Data]),            Int64.Type),
    NomeMes     = Table.AddColumn(Mes,    "Nome Mês",     each Date.ToText([Data], "MMMM", "pt-BR"), type text),
    Trimestre   = Table.AddColumn(NomeMes,"Trimestre",    each "T" & Text.From(Date.QuarterOfYear([Data])), type text),
    Semana      = Table.AddColumn(Trimestre,"Semana Ano", each Date.WeekOfYear([Data]),       Int64.Type),
    DiaSemana   = Table.AddColumn(Semana, "Dia Semana",   each Date.DayOfWeekName([Data], "pt-BR"), type text),
    AnoMes      = Table.AddColumn(DiaSemana, "Ano-Mês",   each Text.PadStart(Text.From([Mês]),2,"0") & "/" & Text.From([Ano]), type text)
in
    AnoMes
