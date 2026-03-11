import pandas as pd
import matplotlib.pyplot as plt
import unicodedata
import re
import os

PASTA = "results"

ARQ_GERAIS = os.path.join(PASTA, "resumo_dados_gerais.xlsx")
ARQ_SITUACAO = os.path.join(PASTA, "resumo_situacao_matricula.xlsx")

# =========================
# FUNÇÕES
# =========================

def normalizar(txt):
    if pd.isna(txt):
        return ""
    txt = str(txt)
    txt = unicodedata.normalize("NFKD", txt).encode("ascii","ignore").decode("utf-8")
    txt = txt.upper().strip()
    return txt

def salvar_excel(df, nome):
    caminho = os.path.join(PASTA, nome)
    df.to_excel(caminho, index=False)
    print("Arquivo salvo:", caminho)

def salvar_grafico(nome):
    caminho = os.path.join(PASTA, nome)
    plt.tight_layout()
    plt.savefig(caminho, dpi=300)
    plt.close()
    print("Gráfico salvo:", caminho)

# =========================
# 1 DADOS GERAIS
# =========================

print("\nLendo dados gerais...")

df = pd.read_excel(ARQ_GERAIS)

df.columns = [c.strip() for c in df.columns]

col_ano = "Ano"
col_campus = [c for c in df.columns if "Unidade" in c][0]
col_curso = [c for c in df.columns if "Curso" in c][0]
col_matriculas = [c for c in df.columns if "Matr" in c][0]

# normalizar cursos
df["curso_norm"] = df[col_curso].apply(normalizar)

PALAVRAS_TI = [
"INFORMATICA",
"COMPUTACAO",
"SISTEMAS",
"ANALISE E DESENVOLVIMENTO",
"ADS"
]

padrao = "|".join(PALAVRAS_TI)

df = df[df["curso_norm"].str.contains(padrao, na=False)]

# =========================
# IDENTIFICAR NÍVEL DO CURSO
# =========================

def classificar_nivel(curso):
    curso = normalizar(curso)

    if "TECNICO" in curso:
        return "Técnico"

    if (
        "TECNOLOGIA" in curso
        or "BACHARELADO" in curso
        or "LICENCIATURA" in curso
        or "ANALISE E DESENVOLVIMENTO" in curso
        or "SISTEMAS PARA INTERNET" in curso
        or "ENGENHARIA" in curso
    ):
        return "Graduação"

    return None

df["nivel"] = df[col_curso].apply(classificar_nivel)

print("\nValores únicos de nível encontrados:")
print(df["nivel"].value_counts(dropna=False))

df = df[df["nivel"].notna()].copy()

# =========================
# MATRÍCULAS POR ANO
# =========================

tabela_ano = df.groupby(col_ano)[col_matriculas].sum().reset_index()

salvar_excel(tabela_ano,"tabela_matriculas_ano.xlsx")

plt.figure()

plt.plot(tabela_ano[col_ano], tabela_ano[col_matriculas], marker="o")

plt.title("Evolução das matrículas em cursos de computação")
plt.xlabel("Ano")
plt.ylabel("Matrículas")

salvar_grafico("grafico_matriculas_ano.png")

# =========================
# MATRÍCULAS POR CAMPUS
# =========================

tabela_campus = df.groupby(col_campus)[col_matriculas].sum().reset_index()

tabela_campus = tabela_campus.sort_values(col_matriculas,ascending=False)

salvar_excel(tabela_campus,"tabela_matriculas_campus.xlsx")

plt.figure()

plt.bar(tabela_campus[col_campus], tabela_campus[col_matriculas])

plt.xticks(rotation=45)

plt.title("Matrículas por campus")

salvar_grafico("grafico_matriculas_campus.png")

# =========================
# MATRÍCULAS POR CURSO
# =========================

tabela_curso = df.groupby(col_curso)[col_matriculas].sum().reset_index()

tabela_curso = tabela_curso.sort_values(col_matriculas,ascending=False)

salvar_excel(tabela_curso,"tabela_matriculas_curso.xlsx")

# =========================
# MATRÍCULAS POR NÍVEL
# =========================

tabela_nivel = df.groupby("nivel")[col_matriculas].sum().reset_index()

salvar_excel(tabela_nivel,"tabela_matriculas_nivel.xlsx")

plt.figure()

plt.bar(tabela_nivel["nivel"], tabela_nivel[col_matriculas])

plt.title("Distribuição por nível de ensino")

salvar_grafico("grafico_nivel.png")

# =========================
# MATRÍCULAS POR ANO E NÍVEL
# =========================

tabela_nivel_ano = df.groupby([col_ano,"nivel"])[col_matriculas].sum().reset_index()

salvar_excel(tabela_nivel_ano,"tabela_nivel_ano.xlsx")

pivot_nivel = tabela_nivel_ano.pivot(index=col_ano,columns="nivel",values=col_matriculas)

plt.figure()

for col in pivot_nivel.columns:
    plt.plot(pivot_nivel.index,pivot_nivel[col],marker="o",label=col)

plt.legend()

plt.title("Matrículas por nível ao longo do tempo")

salvar_grafico("grafico_nivel_ano.png")

# =========================
# SITUAÇÃO DE MATRÍCULA
# =========================

print("\nLendo situação de matrícula...")

df_sit = pd.read_excel(ARQ_SITUACAO)

df_sit.columns = [c.strip() for c in df_sit.columns]

col_ano_s = "Ano"
col_campus_s = [c for c in df_sit.columns if "Campus" in c or "Unidade" in c][0]
col_status = [c for c in df_sit.columns if "curso" in c.lower() or "situ" in c.lower()][0]
col_qtd = [c for c in df_sit.columns if "matr" in c.lower() or "numero" in c.lower()][0]

df_sit["status_norm"] = df_sit[col_status].apply(normalizar)

status_validos = ["EM CURSO","EVADIDOS","CONCLUINTE"]

df_sit = df_sit[df_sit["status_norm"].isin(status_validos)]

tabela_status = df_sit.groupby([col_ano_s,col_status])[col_qtd].sum().reset_index()

salvar_excel(tabela_status,"tabela_situacao.xlsx")

pivot = tabela_status.pivot(index=col_ano_s,columns=col_status,values=col_qtd)

plt.figure()

for c in pivot.columns:
    plt.plot(pivot.index,pivot[c],marker="o",label=c)

plt.legend()

plt.title("Situação de matrícula ao longo dos anos")

salvar_grafico("grafico_situacao.png")

# =========================
# TAXA DE EVASÃO APROXIMADA
# =========================

if "Evadidos" in pivot.columns and "Em curso" in pivot.columns:

    pivot["taxa_evasao"] = pivot["Evadidos"]/(pivot["Evadidos"]+pivot["Em curso"])*100

    evasao = pivot.reset_index()[[col_ano_s,"taxa_evasao"]]

    salvar_excel(evasao,"tabela_taxa_evasao.xlsx")

    plt.figure()

    plt.plot(evasao[col_ano_s],evasao["taxa_evasao"],marker="o")

    plt.title("Taxa aproximada de evasão")

    plt.ylabel("%")

    salvar_grafico("grafico_taxa_evasao.png")

print("\nProcessamento finalizado.")