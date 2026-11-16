import pandas as pd
import gc
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
    "CO_CURSO",
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

def exportar_dados(df, ano):
    destino = Path("data/processed")
    destino.mkdir(parents=True, exist_ok=True)
    
    df.to_parquet(
        destino / f"censo_superior_{ano}.parquet",
        engine="pyarrow",
        compression=None,
        index=False
    )
    
    print("\nArquivo consolidado gerado com sucesso!")

def executar_etl():
    for ano in ANOS:
        print(f"\nProcessando {ano}...")

        df_ano = carregar_dados(ano)
        df_ano = tratar_tipos_dados(df_ano)
        
        exportar_dados(df_ano, ano)
        
        print(f"{ano}: {len(df_ano):,} registros salvos.")
        del df_ano
        gc.collect()

if __name__ == "__main__":
    executar_etl()
