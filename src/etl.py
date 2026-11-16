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

def exportar_dados(df):
    destino = Path("data/processed")
    destino.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        destino / "censo_superior_consolidado.csv",
        sep=";",
        encoding="utf-8-sig",
        index=False
    )
    
    print("\nArquivo consolidado gerado com sucesso!")

def executar_etl():
    bases = [carregar_dados(ano) for ano in ANOS]
    df_cursos = pd.concat(bases, ignore_index=True)

    print(df_cursos.info())
    print(df_cursos.groupby("NU_ANO_CENSO").size())
    
    exportar_dados(df_cursos)
    
    return df_cursos

if __name__ == "__main__":
    df_cursos = executar_etl()
