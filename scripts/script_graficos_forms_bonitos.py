import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# CONFIGURAÇÃO
# =========================
ARQUIVO = "Respostas do Formulario.csv"   
PASTA_SAIDA = "results_forms/graficos"
os.makedirs(PASTA_SAIDA, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")

# =========================
# LEITURA
# =========================
df = pd.read_csv(ARQUIVO)

# =========================
# FUNÇÃO PARA ENCONTRAR COLUNA
# =========================
def encontrar_coluna(df, trecho):
    for c in df.columns:
        if trecho.lower() in c.lower():
            return c
    return None

# =========================
# COLUNAS
# =========================
col_contato = encontrar_coluna(df, "Antes de entrar no curso")
col_desistencia = encontrar_coluna(df, "Você já pensou em desistir")

col_conforto = encontrar_coluna(df, "Eu me sinto confortável")
col_isolada = encontrar_coluna(df, "já me senti deslocada")
col_acolhedor = encontrar_coluna(df, "mais mulheres")
col_igualdade = encontrar_coluna(df, "tratam homens e mulheres de forma igual")

# =========================
# FUNÇÃO BARRA HORIZONTAL SIMPLES
# =========================
def grafico_barra_horizontal(coluna, titulo, arquivo):
    dados = df[coluna].value_counts().sort_index()

    plt.figure(figsize=(7, 4))
    plt.barh(dados.index, dados.values)
    plt.title(titulo)
    plt.xlabel("Quantidade")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_SAIDA, arquivo), dpi=300, bbox_inches="tight")
    plt.close()

# =========================
# GRÁFICOS SIMPLES
# =========================
if col_contato:
    grafico_barra_horizontal(
        col_contato,
        "Contato prévio com programação ou tecnologia",
        "grafico_contato_previo_barra.png"
    )

if col_desistencia:
    grafico_barra_horizontal(
        col_desistencia,
        "Participantes que já consideraram desistir do curso",
        "grafico_desistencia_barra.png"
    )

# =========================
# LIKERT EMPILHADO
# =========================
perguntas_likert = {
    "Conforto em ambiente masculino": col_conforto,
    "Sentimento de isolamento": col_isolada,
    "Mais mulheres tornariam o ambiente mais acolhedor": col_acolhedor,
    "Percepção de igualdade de tratamento": col_igualdade,
}

ordem_likert = [
    "Discordo totalmente",
    "Discordo",
    "Neutro",
    "Concordo",
    "Concordo totalmente"
]

dados_plot = []

for nome, coluna in perguntas_likert.items():
    if coluna:
        contagem = df[coluna].value_counts()
        linha = [contagem.get(cat, 0) for cat in ordem_likert]
        dados_plot.append([nome] + linha)

if dados_plot:
    df_plot = pd.DataFrame(
        dados_plot,
        columns=["Pergunta"] + ordem_likert
    )

    plt.figure(figsize=(10, 5))

    left = [0] * len(df_plot)

    for resposta in ordem_likert:
        plt.barh(
            df_plot["Pergunta"],
            df_plot[resposta],
            left=left,
            label=resposta
        )
        left = [l + v for l, v in zip(left, df_plot[resposta])]

    plt.title("Distribuição das respostas em escala Likert")
    plt.xlabel("Quantidade de respostas")
    plt.ylabel("")
    plt.legend(
        title="Resposta",
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(PASTA_SAIDA, "grafico_likert_empilhado.png"),
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

print("Gráficos gerados com sucesso.")