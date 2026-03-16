import pandas as pd
import matplotlib.pyplot as plt
import unicodedata
import re
import os

ARQUIVO = "results/sexo_filtrado.xlsx"

def normalizar(txt):
    if pd.isna(txt):
        return ""
    txt = str(txt)
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8")
    txt = txt.upper().strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt

def encontrar_coluna(df, termos):
    for col in df.columns:
        col_norm = normalizar(col)
        if all(t in col_norm for t in termos):
            return col
    return None

df = pd.read_excel(ARQUIVO)
df.columns = [c.strip() for c in df.columns]

print("\nColunas do arquivo:")
for c in df.columns:
    print("-", c)

col_ano = encontrar_coluna(df, ["ANO"])
col_sexo = encontrar_coluna(df, ["SEXO"])
col_matriculas = encontrar_coluna(df, ["MATRICULA"])
col_ingressantes = encontrar_coluna(df, ["INGRESS"])
col_concluintes = encontrar_coluna(df, ["CONCLU"])

print("\nMapeamento encontrado:")
print("Ano:", col_ano)
print("Sexo:", col_sexo)
print("Matrículas:", col_matriculas)
print("Ingressantes:", col_ingressantes)
print("Concluintes:", col_concluintes)

# padronizar sexo
df["sexo_norm"] = df[col_sexo].apply(normalizar)
df = df[df["sexo_norm"].isin(["FEMININO", "MASCULINO"])].copy()

os.makedirs("results/tabelas", exist_ok=True)
os.makedirs("results/graficos", exist_ok=True)

def gerar_tabela_e_grafico(col_valor, nome_base, titulo, ylabel):
    if col_valor is None:
        print(f"\nColuna não encontrada para {nome_base}. Pulando.")
        return

    tabela = (
        df.groupby([col_ano, col_sexo])[col_valor]
        .sum()
        .reset_index()
        .sort_values([col_ano, col_sexo])
    )

    pivot = tabela.pivot(index=col_ano, columns=col_sexo, values=col_valor).fillna(0)

    # detectar feminino/masculino mesmo com nomes variados
    col_fem = None
    col_masc = None
    for c in pivot.columns:
        c_norm = normalizar(c)
        if "FEMININO" in c_norm:
            col_fem = c
        elif "MASCULINO" in c_norm:
            col_masc = c

    if col_fem and col_masc:
        pivot["Total"] = pivot[col_fem] + pivot[col_masc]
        pivot["Percentual Feminino"] = (pivot[col_fem] / pivot["Total"]) * 100

    pivot_reset = pivot.reset_index()

    caminho_tabela = f"results/tabelas/tabela_{nome_base}.xlsx"
    pivot_reset.to_excel(caminho_tabela, index=False)
    print("Tabela salva:", caminho_tabela)

    # gráfico absoluto
    plt.figure()
    if col_fem:
        plt.plot(pivot_reset[col_ano], pivot_reset[col_fem], marker="o", label="Feminino")
    if col_masc:
        plt.plot(pivot_reset[col_ano], pivot_reset[col_masc], marker="o", label="Masculino")
    plt.title(titulo)
    plt.xlabel("Ano")
    plt.ylabel(ylabel)
    plt.legend()
    caminho_grafico = f"results/graficos/grafico_{nome_base}.png"
    plt.savefig(caminho_grafico, dpi=300, bbox_inches="tight")
    plt.close()
    print("Gráfico salvo:", caminho_grafico)

    # gráfico percentual feminino
    if "Percentual Feminino" in pivot_reset.columns:
        plt.figure()
        plt.plot(pivot_reset[col_ano], pivot_reset["Percentual Feminino"], marker="o")
        plt.title(f"Percentual feminino - {titulo.lower()}")
        plt.xlabel("Ano")
        plt.ylabel("%")
        caminho_pct = f"results/graficos/grafico_percentual_feminino_{nome_base}.png"
        plt.savefig(caminho_pct, dpi=300, bbox_inches="tight")
        plt.close()
        print("Gráfico salvo:", caminho_pct)

# gerar três versões
gerar_tabela_e_grafico(
    col_matriculas,
    "sexo_matriculas",
    "Matrículas por sexo ao longo dos anos",
    "Número de matrículas"
)

gerar_tabela_e_grafico(
    col_ingressantes,
    "sexo_ingressantes",
    "Ingressantes por sexo ao longo dos anos",
    "Número de ingressantes"
)

gerar_tabela_e_grafico(
    col_concluintes,
    "sexo_concluintes",
    "Concluintes por sexo ao longo dos anos",
    "Número de concluintes"
)

print("\nProcesso finalizado.")