import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid")

ARQUIVO = "Respostas do Formulario.csv"

df = pd.read_csv(ARQUIVO)

# ===============================
# CONTATO PRÉVIO COM TECNOLOGIA
# ===============================

col_contato = [c for c in df.columns if "contato com programação" in c.lower()][0]

dados_contato = df[col_contato].value_counts()

plt.figure(figsize=(6,6))

plt.pie(
    dados_contato,
    labels=dados_contato.index,
    autopct="%1.0f%%",
    startangle=90,
    colors=["#4C72B0","#DD8452"],
    wedgeprops={"edgecolor":"white"}
)

plt.title("Contato prévio com programação ou tecnologia")

plt.savefig("grafico_contato_previo.png", dpi=300)
plt.close()


# ===============================
# DESISTÊNCIA
# ===============================

col_desistencia = [c for c in df.columns if "pensou em desistir" in c.lower()][0]

dados_desistencia = df[col_desistencia].value_counts()

plt.figure(figsize=(6,6))

plt.pie(
    dados_desistencia,
    labels=dados_desistencia.index,
    autopct="%1.0f%%",
    startangle=90,
    colors=["#4C72B0","#DD8452"],
    wedgeprops={"edgecolor":"white"}
)

plt.title("Participantes que já consideraram desistir do curso")

plt.savefig("grafico_desistencia.png", dpi=300)
plt.close()


# ===============================
# LIKERT
# ===============================

likert_map = {
    "Discordo totalmente":1,
    "Discordo":2,
    "Neutro":3,
    "Concordo":4,
    "Concordo totalmente":5
}

colunas_likert = []

for c in df.columns:
    if any(x in c.lower() for x in [
        "confortável",
        "deslocada",
        "mais mulheres",
        "tratam homens"
    ]):
        colunas_likert.append(c)

resultados = []

for c in colunas_likert:

    temp = df[c].map(likert_map)

    media = temp.mean()

    resultados.append({
        "Pergunta":c,
        "Média":media
    })

df_likert = pd.DataFrame(resultados)

plt.figure(figsize=(8,4))

plt.barh(
    df_likert["Pergunta"],
    df_likert["Média"],
    color="#4C72B0"
)

plt.xlim(1,5)

plt.xlabel("Média das respostas (1–5)")

plt.title("Percepções das estudantes sobre o ambiente do curso")

plt.tight_layout()

plt.savefig("grafico_likert.png", dpi=300)

plt.close()

print("Gráficos gerados com sucesso.")