import pandas as pd
import matplotlib.pyplot as plt
import os
import unicodedata
import re

# =========================
# CONFIGURAÇÕES
# =========================
ARQUIVO = r"Respostas do Formulario.csv"

PASTA_SAIDA = "results_forms"
os.makedirs(PASTA_SAIDA, exist_ok=True)

# =========================
# FUNÇÕES AUXILIARES
# =========================
def normalizar(txt):
    if pd.isna(txt):
        return ""
    txt = str(txt)
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8")
    txt = txt.strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt

def encontrar_coluna(df, trecho):
    for c in df.columns:
        if trecho.lower() in c.lower():
            return c
    return None

def salvar_tabela(df, nome):
    caminho = os.path.join(PASTA_SAIDA, nome)
    df.to_excel(caminho, index=False)
    print(f"Tabela salva: {caminho}")

def salvar_grafico(nome):
    caminho = os.path.join(PASTA_SAIDA, nome)
    plt.tight_layout()
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Gráfico salvo: {caminho}")

# =========================
# LEITURA
# =========================
df = pd.read_csv(ARQUIVO)

print("Shape:", df.shape)
print("\nColunas:")
for c in df.columns:
    print("-", c)

# =========================
# MAPEAR COLUNAS
# =========================
col_curso = encontrar_coluna(df, "Curso que você está cursando")
col_idade = encontrar_coluna(df, "faixa etária")
col_etapa = encontrar_coluna(df, "Em que etapa")
col_contato = encontrar_coluna(df, "Antes de entrar no curso")
col_primeira = encontrar_coluna(df, "primeira opção")
col_conforto = encontrar_coluna(df, "me sinto confortável")
col_isolada = encontrar_coluna(df, "me senti deslocada")
col_acolhedor = encontrar_coluna(df, "mais mulheres")
col_igualdade = encontrar_coluna(df, "tratam homens e mulheres")
col_desistencia = encontrar_coluna(df, "já pensou em desistir")
col_motivo = encontrar_coluna(df, "principal motivo")
col_desafios = encontrar_coluna(df, "principais desafios")
col_incentivo = encontrar_coluna(df, "O que poderia ser feito")

# =========================
# LIMPEZA GERAL
# =========================
for c in df.columns:
    if df[c].dtype == object:
        df[c] = df[c].apply(lambda x: normalizar(x) if pd.notna(x) else x)

# =========================
# TABELAS DE PERFIL
# =========================
for coluna, nome in [
    (col_curso, "tabela_curso.xlsx"),
    (col_idade, "tabela_idade.xlsx"),
    (col_etapa, "tabela_etapa.xlsx"),
    (col_contato, "tabela_contato_previo.xlsx"),
    (col_primeira, "tabela_primeira_opcao.xlsx"),
    (col_desistencia, "tabela_desistencia.xlsx"),
    (col_motivo, "tabela_motivo_desistencia.xlsx"),
]:
    if coluna:
        tabela = df[coluna].value_counts(dropna=False).reset_index()
        tabela.columns = ["Categoria", "Quantidade"]
        tabela["Percentual"] = (tabela["Quantidade"] / tabela["Quantidade"].sum()) * 100
        salvar_tabela(tabela, nome)

# =========================
# GRÁFICO 1 — CONTATO PRÉVIO
# =========================
if col_contato:
    tabela_contato = df[col_contato].value_counts().reset_index()
    tabela_contato.columns = ["Categoria", "Quantidade"]

    plt.figure(figsize=(6,4))
    plt.bar(tabela_contato["Categoria"], tabela_contato["Quantidade"])
    plt.title("Contato prévio com programação ou tecnologia")
    plt.xlabel("Resposta")
    plt.ylabel("Quantidade")
    salvar_grafico("grafico_contato_previo.png")

# =========================
# GRÁFICO 2 — DESISTÊNCIA
# =========================
if col_desistencia:
    tabela_desistencia = df[col_desistencia].value_counts().reset_index()
    tabela_desistencia.columns = ["Categoria", "Quantidade"]

    plt.figure(figsize=(6,4))
    plt.bar(tabela_desistencia["Categoria"], tabela_desistencia["Quantidade"])
    plt.title("Participantes que já pensaram em desistir do curso")
    plt.xlabel("Resposta")
    plt.ylabel("Quantidade")
    salvar_grafico("grafico_desistencia.png")

# =========================
# LIKERT
# =========================
likert_map = {
    "DISCORDO TOTALMENTE": 1,
    "DISCORDO": 2,
    "NEUTRO": 3,
    "CONCORDO": 4,
    "CONCORDO TOTALMENTE": 5
}

perguntas_likert = {
    "Conforto em ambiente masculino": col_conforto,
    "Sentimento de isolamento": col_isolada,
    "Ambiente mais acolhedor com mais mulheres": col_acolhedor,
    "Igualdade de tratamento": col_igualdade
}

resumo_likert = []

for nome_pergunta, coluna in perguntas_likert.items():
    if coluna:
        temp = df[coluna].dropna().map(likert_map)
        media = temp.mean()
        resumo_likert.append({
            "Pergunta": nome_pergunta,
            "Média": round(media, 2),
            "N": temp.count()
        })

resumo_likert = pd.DataFrame(resumo_likert)
if not resumo_likert.empty:
    salvar_tabela(resumo_likert, "tabela_resumo_likert.xlsx")

    plt.figure(figsize=(9,4))
    plt.bar(resumo_likert["Pergunta"], resumo_likert["Média"])
    plt.ylim(0,5)
    plt.title("Média das respostas em escala Likert")
    plt.ylabel("Média (1 a 5)")
    plt.xticks(rotation=20, ha="right")
    salvar_grafico("grafico_likert_medias.png")

# =========================
# TABELAS DETALHADAS DAS PERGUNTAS LIKERT
# =========================
for nome_pergunta, coluna in perguntas_likert.items():
    if coluna:
        tabela = df[coluna].value_counts().reset_index()
        tabela.columns = ["Resposta", "Quantidade"]
        tabela["Pergunta"] = nome_pergunta
        salvar_tabela(tabela, f"tabela_{normalizar(nome_pergunta).lower().replace(' ','_')}.xlsx")

# =========================
# EXPORTAR RESPOSTAS ABERTAS
# =========================
if col_desafios:
    tabela_desafios = df[[col_desafios]].dropna().copy()
    tabela_desafios.columns = ["Resposta"]
    salvar_tabela(tabela_desafios, "respostas_abertas_desafios.xlsx")

if col_incentivo:
    tabela_incentivo = df[[col_incentivo]].dropna().copy()
    tabela_incentivo.columns = ["Resposta"]
    salvar_tabela(tabela_incentivo, "respostas_abertas_incentivos.xlsx")

print("\nProcessamento finalizado.")