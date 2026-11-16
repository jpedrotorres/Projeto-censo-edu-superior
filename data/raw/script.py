import re
import shutil
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

# Configurações principais
URL_PAGINA_INEP = (
    "[https://www.gov.br/inep/pt-br/acesso-a-informacao/](https://www.gov.br/inep/pt-br/acesso-a-informacao/)"
    "dados-abertos/microdados/censo-da-educacao-superior"
)
ANOS = [2020, 2021, 2022, 2023]
PASTA_SAIDA = Path("microdados_cursos_inep")
PASTA_TEMP_ZIPS = PASTA_SAIDA / "zips_temporarios"
MANTER_ZIPS = False  # Altere para True se quiser manter os arquivos .zip após extrair

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/[124.0.0.0](http://124.0.0.0) Safari/537.36"
    )
}

def requisicao_get(url: str, stream: bool = False) -> requests.Response:
    """Realiza requisição GET com fallback automático caso o certificado SSL do INEP falhe."""
    try:
        resp = requests.get(url, headers=HEADERS, stream=stream, timeout=60, verify=True)
        resp.raise_for_status()
        return resp
    except requests.exceptions.SSLError:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(url, headers=HEADERS, stream=stream, timeout=60, verify=False)
        resp.raise_for_status()
        return resp


def obter_links_zip(anos: list[int]) -> dict[int, str]:
    """Extrai os links .zip diretamente da página do INEP para os anos desejados."""
    links_encontrados: dict[int, str] = {}

    try:
        print(f"Buscando links atualizados em: {URL_PAGINA_INEP}")
        resposta = requisicao_get(URL_PAGINA_INEP)
        soup = BeautifulSoup(resposta.text, "html.parser")

        for tag_a in soup.find_all("a", href=True):
            href = urljoin(URL_PAGINA_INEP, tag_a["href"].strip())
            caminho_url = urlparse(href).path.lower()

            if not caminho_url.endswith(".zip"):
                continue

            for ano in anos:
                if ano not in links_encontrados and re.search(rf"(?\<!\d){ano}(?!\d)", caminho_url):
                    if "censo" in caminho_url or "educacao_superior" in caminho_url:
                        links_encontrados[ano] = href
    except Exception as erro:
        print(f"Aviso: não foi possível ler o HTML da página ({erro}). Usando URLs padrão.")

    # Fallback para o padrão oficial do servidor [download.inep.gov.br](http://download.inep.gov.br)
    for ano in anos:
        if ano not in links_encontrados:
            links_encontrados[ano] = (
                f"[https://download.inep.gov.br/microdados/](https://download.inep.gov.br/microdados/)"
                f"microdados_censo_da_educacao_superior\_{ano}.zip"
            )

    return links_encontrados


def baixar_zip(url: str, destino_zip: Path) -> None:
    """Baixa o arquivo .zip em blocos (streaming) exibindo o progresso."""
    print(f"Baixando: {url}")
    with requisicao_get(url, stream=True) as resp:
        total_bytes = int(resp.headers.get("content-length", 0))
        baixados = 0

        with open(destino_zip, "wb") as arquivo:
            for chunk in resp.iter_content(chunk_size=1024 \* 1024):  # blocos de 1 MB
                if chunk:
                    arquivo.write(chunk)
                    baixados += len(chunk)
                    if total_bytes > 0:
                        pct = (baixados / total_bytes) \* 100
                        print(
                            f"\r  Progresso: {baixados / (1024\*\*2):.1f} MB / "
                            f"{total_bytes / (1024\*\*2):.1f} MB ({pct:.1f}%)",
                            end="",
                            flush=True,
                        )
                    else:
                        print(f"\r  Baixado: {baixados / (1024\*\*2):.1f} MB", end="", flush=True)
    print()


def extrair_csv_cursos(caminho_zip: Path, ano: int, pasta_destino: Path) -> Path | None:
    """Localiza e extrai apenas o arquivo dados/MICRODADOS_CADASTRO_CURSOS\_{ano}.CSV."""
    nome_alvo = f"microdados_cadastro_cursos\_{ano}.csv"

    with zipfile.ZipFile(caminho_zip, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue

            caminho_interno = info.filename.replace("\\\\", "/")
            partes = caminho_interno.split("/")
            nome_arquivo = partes[-1].lower()
            pastas_pai = [p.lower() for p in partes[:-1]]

            if nome_arquivo == nome_alvo and "dados" in pastas_pai:
                arquivo_saida = pasta_destino / f"MICRODADOS_CADASTRO_CURSOS\_{ano}.CSV"
                with zf.open(info) as origem, open(arquivo_saida, "wb") as destino:
                    shutil.copyfileobj(origem, destino)
                print(f"  Extraído com sucesso: {arquivo_saida}")
                return arquivo_saida

    print(f"  Aviso: '{nome_alvo}' dentro de 'dados/' não encontrado em {[caminho_zip.name](http://caminho_zip.name)}.")
    return None


def main() -> None:
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    PASTA_TEMP_ZIPS.mkdir(parents=True, exist_ok=True)

    links = obter_links_zip(ANOS)

    for ano in ANOS:
        print(f"\n--- Processando ano {ano} ---")
        url_zip = links[ano]
        caminho_zip = PASTA_TEMP_ZIPS / f"censo_superior\_{ano}.zip"

        try:
            baixar_zip(url_zip, caminho_zip)
            extrair_csv_cursos(caminho_zip, ano, PASTA_SAIDA)
        except Exception as erro:
            print(f"  Erro ao processar {ano}: {erro}")
        finally:
            if not MANTER_ZIPS and caminho_zip.exists():
                caminho_zip.unlink()

    if not MANTER_ZIPS and PASTA_TEMP_ZIPS.exists():
        try:
            PASTA_TEMP_ZIPS.rmdir()
        except OSError:
            pass

    print(f"\nConcluído! Os arquivos CSV estão em: {PASTA_SAIDA.resolve()}")


if \_\_name\_\_ == "\_\_main\_\_":
    main()

formate em um arquivo python
