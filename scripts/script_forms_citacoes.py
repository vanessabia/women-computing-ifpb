import pandas as pd
import os

ARQUIVO_DESAFIOS = r"results_forms\respostas_abertas_desafios.xlsx"
ARQUIVO_INCENTIVOS = r"results_forms\respostas_abertas_incentivos.xlsx"

def preparar_citacoes(arquivo, saida):
    df = pd.read_excel(arquivo)
    df = df.dropna().copy()
    df["ID"] = range(1, len(df) + 1)
    df = df[["ID", "Resposta"]]
    df.to_excel(saida, index=False)
    print(f"Arquivo salvo: {saida}")

if os.path.exists(ARQUIVO_DESAFIOS):
    preparar_citacoes(ARQUIVO_DESAFIOS, r"results_forms\citacoes_desafios.xlsx")

if os.path.exists(ARQUIVO_INCENTIVOS):
    preparar_citacoes(ARQUIVO_INCENTIVOS, r"results_forms\citacoes_incentivos.xlsx")