import pandas as pd
import unicodedata
import re

# ========= CONFIGURAÇÕES =========
ARQUIVO = "./dados/SituacaoMatricula.csv"   
ANOS = list(range(2018, 2025))

CAMPI_SERTAO = [
    "CAJAZEIRAS",
    "SOUSA",
    "PATOS",
    "CATOLE DO ROCHA",
    "ITAPORANGA",
    "PRINCESA ISABEL"
]

# ========= FUNÇÕES =========
def normalizar_texto(txt):
    if pd.isna(txt):
        return ""
    txt = str(txt)
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8")
    txt = txt.upper().strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt

def ler_csv_flexivel(caminho):
    encodings = ["utf-8", "latin1", "cp1252"]
    seps = [";", ","]
    for enc in encodings:
        for sep in seps:
            try:
                df = pd.read_csv(caminho, encoding=enc, sep=sep)
                if df.shape[1] > 3:
                    print(f"Arquivo lido com encoding={enc} e sep='{sep}'")
                    return df
            except Exception:
                pass
    raise ValueError("Não foi possível ler o CSV.")

def encontrar_coluna(df, palavras_chave):
    for col in df.columns:
        col_norm = normalizar_texto(col)
        if all(p in col_norm for p in palavras_chave):
            return col
    return None

# ========= LEITURA =========
df = ler_csv_flexivel(ARQUIVO)

print("\nColunas encontradas:")
for c in df.columns:
    print("-", c)

# ========= MAPEAMENTO =========
col_ano = encontrar_coluna(df, ["ANO"])
col_instituicao = encontrar_coluna(df, ["INSTITUICAO"])
col_unidade = encontrar_coluna(df, ["NOME", "UNID"])
col_categoria = encontrar_coluna(df, ["CATEGORIA"])
col_situacao = encontrar_coluna(df, ["SITUA"])
col_fluxo = encontrar_coluna(df, ["FLUXO"])
col_matriculas = None

for c in df.columns:
    c_norm = normalizar_texto(c)
    if "MATRICULA" in c_norm:
        col_matriculas = c
        break

print("\nMapeamento:")
print("Ano:", col_ano)
print("Instituição:", col_instituicao)
print("Unidade:", col_unidade)
print("Categoria:", col_categoria)
print("Situação:", col_situacao)
print("Fluxo:", col_fluxo)
print("Matrículas:", col_matriculas)

# ========= NORMALIZAÇÃO =========
for col in [col_instituicao, col_unidade, col_categoria, col_situacao, col_fluxo]:
    if col:
        df[f"{col}_NORM"] = df[col].apply(normalizar_texto)

# ========= FILTROS =========
if col_ano:
    df = df[df[col_ano].isin(ANOS)]

if col_instituicao:
    df = df[df[f"{col_instituicao}_NORM"].str.contains("PARAIBA|IFPB", na=False)]

if col_unidade:
    padrao_campi = "|".join([re.escape(c) for c in CAMPI_SERTAO])
    df = df[df[f"{col_unidade}_NORM"].str.contains(padrao_campi, na=False)]

print(f"\nTotal após filtros: {len(df)}")

df.to_excel("situacao_matricula_filtrada.xlsx", index=False)

# ========= RESUMO =========
# queremos algo como: ano x campus x categoria/situação
if col_ano and col_unidade and (col_categoria or col_situacao):
    col_status = col_categoria if col_categoria else col_situacao

    if col_matriculas:
        resumo = (
            df.groupby([col_ano, col_unidade, col_status])[col_matriculas]
            .sum()
            .reset_index()
            .sort_values([col_ano, col_unidade, col_status])
        )
    else:
        resumo = (
            df.groupby([col_ano, col_unidade, col_status])
            .size()
            .reset_index(name="quantidade")
            .sort_values([col_ano, col_unidade, col_status])
        )

    resumo.to_excel("resumo_situacao_matricula.xlsx", index=False)
    print("\nArquivos gerados:")
    print("- situacao_matricula_filtrada.xlsx")
    print("- resumo_situacao_matricula.xlsx")
else:
    print("\nNão foi possível gerar resumo da situação de matrícula.")