import pandas as pd
import unicodedata
import re

# ========= CONFIGURAÇÕES =========
ARQUIVO = "./dados/ClassificacaoRacialRendaSexo.csv"  
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
    try:
        df = pd.read_csv(caminho, encoding="latin1", sep=";")
        print("Arquivo lido com latin1 e separador ';'")
        print("Shape:", df.shape)
        return df
    except Exception as e:
        print("Erro ao ler CSV:", e)
        raise

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

def ler_csv_flexivel(caminho):
    try:
        df = pd.read_csv(caminho, encoding="latin1", sep=";")
        print("Arquivo lido com latin1 e separador ';'")
        print("Shape:", df.shape)
        return df
    except Exception as e:
        print("Erro ao ler CSV:", e)
        raise

# ========= MAPEAMENTO =========
col_ano = encontrar_coluna(df, ["ANO"])
col_instituicao_nome = encontrar_coluna(df, ["INSTITUICAO"])
col_sexo = encontrar_coluna(df, ["SEXO"])
col_unidade = encontrar_coluna(df, ["NOME", "UNID"])  # se existir
col_vagas = None

for c in df.columns:
    c_norm = normalizar_texto(c)
    if "VAGAS" in c_norm:
        col_vagas = c
        break

# colunas numéricas possíveis (quantidades)
colunas_numericas = []
for c in df.columns:
    if c not in [col_ano, col_instituicao_nome, col_sexo, col_unidade]:
        try:
            pd.to_numeric(df[c], errors="raise")
            colunas_numericas.append(c)
        except:
            pass

print("\nMapeamento:")
print("Ano:", col_ano)
print("Instituição:", col_instituicao_nome)
print("Sexo:", col_sexo)
print("Unidade:", col_unidade)
print("Colunas numéricas:", colunas_numericas)

# ========= NORMALIZAÇÃO =========
for col in [col_instituicao_nome, col_sexo, col_unidade]:
    if col:
        df[f"{col}_NORM"] = df[col].apply(normalizar_texto)

# ========= FILTROS =========
if col_ano:
    df = df[df[col_ano].isin(ANOS)]

if col_instituicao_nome:
    df = df[df[f"{col_instituicao_nome}_NORM"].str.contains("PARAIBA|IFPB", na=False)]

if col_sexo:
    df = df[df[f"{col_sexo}_NORM"].str.contains("FEMININO|MASCULINO", na=False)]

if col_unidade:
    padrao_campi = "|".join([re.escape(c) for c in CAMPI_SERTAO])
    df = df[df[f"{col_unidade}_NORM"].str.contains(padrao_campi, na=False)]

print(f"\nTotal após filtros: {len(df)}")

df.to_excel("sexo_filtrado.xlsx", index=False)

# ========= RESUMO POR ANO E SEXO =========
if col_ano and col_sexo:
    if colunas_numericas:
        # usa a primeira coluna numérica útil como quantidade
        col_valor = colunas_numericas[0]
        resumo = (
            df.groupby([col_ano, col_sexo])[col_valor]
            .sum()
            .reset_index()
            .sort_values([col_ano, col_sexo])
        )
    else:
        resumo = (
            df.groupby([col_ano, col_sexo])
            .size()
            .reset_index(name="quantidade")
            .sort_values([col_ano, col_sexo])
        )

    resumo.to_excel("resumo_sexo_ano.xlsx", index=False)
    print("\nArquivos gerados:")
    print("- sexo_filtrado.xlsx")
    print("- resumo_sexo_ano.xlsx")
else:
    print("\nNão foi possível gerar resumo por ano e sexo.")