import pandas as pd
from pathlib import Path

ANOS = [2020, 2021, 2022, 2023]
COLUNAS = [
    "NU_ANO_CENSO",
    "CO_IES",
    "CO_CURSO",
    "TP_CATEGORIA_ADMINISTRATIVA",
    "TP_MODALIDADE_ENSINO",
    "QT_VG_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC",
    "CO_REGIAO",
    "NO_REGIAO"
]

COLUNAS_NUMERICAS = [
    "NU_ANO_CENSO",
    "QT_VG_TOTAL",
    "QT_ING",
    "QT_MAT",
    "QT_CONC"
]

def carregar_dados(ano):
    arquivo = Path(f"data/raw/{ano}/MICRODADOS_CADASTRO_CURSOS_{ano}.CSV")
    
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin1",
        usecols=lambda coluna: coluna in COLUNAS,
        dtype=str,
        low_memory=False
    )
    
    return df

def tratar_tipos_dados(df):
    for coluna in df.columns:
        if coluna in COLUNAS_NUMERICAS:
            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="raise"
            ).astype("Int64")
        else:
            df[coluna] = df[coluna].astype("string").str.strip()

    return df

def exportar_dados(df):
    destino = Path("data/processed")
    destino.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        destino / "censo_superior_consolidado.csv",
        sep=";",
        encoding="utf-8-sig",
        index=False
    )
    
    df.to_parquet(
        destino / "censo_superior_consolidado.parquet",
        engine="pyarrow",
        compression=None,
        index=False
    )
    
    print("\nArquivo consolidado gerado com sucesso!")

def executar_etl():
    bases = [carregar_dados(ano) for ano in ANOS]
    df_cursos = pd.concat(bases, ignore_index=True)
    df_cursos = tratar_tipos_dados(df_cursos)

    print("\nInformações do DataFrame:")
    df_cursos.info()
    
    print("\nQuantidade de registros por ano:")
    print(df_cursos.groupby("NU_ANO_CENSO").size())
    
    exportar_dados(df_cursos)
    
    return df_cursos

if __name__ == "__main__":
    df_cursos = executar_etl()
