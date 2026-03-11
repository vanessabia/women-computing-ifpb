import pandas as pd
import unicodedata
import re

# ========= CONFIGURAÇÕES =========
ARQUIVO = "./dados/DadosGerais.csv"  
ANOS = list(range(2018, 2025))

CAMPI_SERTAO = [
    "CAJAZEIRAS",
    "SOUSA",
    "PATOS",
    "CATOLE DO ROCHA",
    "ITAPORANGA",
    "PRINCESA ISABEL"
]

PALAVRAS_CURSO_TI = [
    "INFORMATICA",
    "COMPUTACAO",
    "SISTEMAS",
    "ANALISE E DESENVOLVIMENTO DE SISTEMAS",
    "ADS",
    "SISTEMAS PARA INTERNET",
    "ENGENHARIA DE COMPUTACAO"
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
    raise ValueError("Não foi possível ler o CSV. Verifique encoding e separador.")

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

# ========= TENTAR IDENTIFICAR COLUNAS =========
col_ano = encontrar_coluna(df, ["ANO"])
col_instituicao_nome = encontrar_coluna(df, ["INSTITUICAO", "NOME"])
col_unidade = encontrar_coluna(df, ["NOME", "UNID"])
col_curso = encontrar_coluna(df, ["NOME", "CUR"])
col_tipo_curso = encontrar_coluna(df, ["TIPO", "CURSO"])
col_matriculas = None

# tenta achar coluna de matrículas
for c in df.columns:
    c_norm = normalizar_texto(c)
    if "MATRICULA" in c_norm or "MATRICULAS" in c_norm:
        col_matriculas = c
        break

print("\nMapeamento automático:")
print("Ano:", col_ano)
print("Instituição:", col_instituicao_nome)
print("Campus/Unidade:", col_unidade)
print("Curso:", col_curso)
print("Tipo de curso:", col_tipo_curso)
print("Matrículas:", col_matriculas)

# ========= NORMALIZAÇÃO AUXILIAR =========
for col in [col_instituicao_nome, col_unidade, col_curso, col_tipo_curso]:
    if col is not None:
        df[f"{col}_NORM"] = df[col].apply(normalizar_texto)

# ========= FILTROS =========
# 1. Ano
if col_ano:
    df = df[df[col_ano].isin(ANOS)]

# 2. Instituição = IFPB
if col_instituicao_nome:
    df = df[df[f"{col_instituicao_nome}_NORM"].str.contains("PARAIBA|IFPB", na=False)]

# 3. Campi do sertão
if col_unidade:
    padrao_campi = "|".join([re.escape(c) for c in CAMPI_SERTAO])
    df = df[df[f"{col_unidade}_NORM"].str.contains(padrao_campi, na=False)]

# 4. Cursos da área de TI
if col_curso:
    padrao_cursos = "|".join([re.escape(c) for c in PALAVRAS_CURSO_TI])
    df = df[df[f"{col_curso}_NORM"].str.contains(padrao_cursos, na=False)]

print(f"\nTotal de linhas após filtros: {len(df)}")

# ========= SAÍDAS =========
df.to_excel("dados_gerais_filtrados.xlsx", index=False)

# tabela resumida para o artigo
if all([col_ano, col_unidade, col_curso]):
    col_valor = col_matriculas if col_matriculas else None

    if col_valor:
        resumo = (
            df.groupby([col_ano, col_unidade, col_curso], dropna=False)[col_valor]
            .sum()
            .reset_index()
            .sort_values([col_ano, col_unidade, col_curso])
        )
    else:
        resumo = (
            df.groupby([col_ano, col_unidade, col_curso], dropna=False)
            .size()
            .reset_index(name="quantidade_registros")
            .sort_values([col_ano, col_unidade, col_curso])
        )

    resumo.to_excel("resumo_dados_gerais.xlsx", index=False)
    print("\nArquivos gerados:")
    print("- dados_gerais_filtrados.xlsx")
    print("- resumo_dados_gerais.xlsx")
else:
    print("\nNão foi possível gerar o resumo porque alguma coluna-chave não foi encontrada.")