import pandas as pd
import numpy as np

def gerar_dados():
    np.random.seed(42)

    marcas = [
        "La Roche-Posay", "Vichy", "Eucerin", "Bioderma",
        "Avène", "Cetaphil", "Mantecorp", "Adcos"
    ]

    categorias = ["Hidratante", "Protetor Solar", "Tratamento", "Limpeza"]
    canais = ["Farmácia", "E-commerce", "Supermercado"]
    meses = list(range(1, 13))
    nomes_meses = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    # Peso de faturamento base por marca (simula market share real)
    peso_marca = {
        "La Roche-Posay": 0.28,
        "Vichy": 0.16,
        "Eucerin": 0.14,
        "Bioderma": 0.12,
        "Avène": 0.10,
        "Cetaphil": 0.09,
        "Mantecorp": 0.06,
        "Adcos": 0.05,
    }

    registros = []
    for marca in marcas:
        for mes in meses:
            for categoria in categorias:
                for canal in canais:
                    base_fat = 10_000_000 * peso_marca[marca]
                    sazonalidade = 1.0
                    if mes in [1, 2]:  # verão — protetor solar sobe
                        sazonalidade = 1.3 if categoria == "Protetor Solar" else 1.0
                    elif mes in [6, 7]:  # inverno — hidratante sobe
                        sazonalidade = 1.2 if categoria == "Hidratante" else 0.9

                    faturamento = base_fat * sazonalidade * np.random.uniform(0.85, 1.15)
                    ticket_medio = np.random.uniform(45, 120)
                    pedidos = int(faturamento / ticket_medio)

                    registros.append({
                        "marca": marca,
                        "mes": mes,
                        "mes_nome": nomes_meses[mes],
                        "categoria": categoria,
                        "canal": canal,
                        "faturamento": round(faturamento, 2),
                        "pedidos": pedidos,
                        "ticket_medio": round(ticket_medio, 2),
                    })

    df = pd.DataFrame(registros)

    # Dados do ano anterior (2024) para comparação — 15% menor
    df_2024 = df.copy()
    df_2024["faturamento"] = df_2024["faturamento"] * np.random.uniform(0.82, 0.90, len(df_2024))
    df_2024["pedidos"] = (df_2024["pedidos"] * np.random.uniform(0.80, 0.88, len(df_2024))).astype(int)

    return df, df_2024
