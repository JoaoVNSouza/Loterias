import os
from playwright.sync_api import sync_playwright
from pathlib import Path
import oci


URL_BASE = 'https://asloterias.com.br/download-todos-resultados-'
CONFIG_PATH = "OracleBucket/config"
PROFILE_NAME = "DEFAULT"
BUCKET_NAME = "loterias"
RESULTADOS_DIR = "./resultados"


def fazer_conexao_bucket():
    try:
        config = oci.config.from_file(CONFIG_PATH, PROFILE_NAME)
        client = oci.object_storage.ObjectStorageClient(config)

        namespace = client.get_namespace().data

        return client, namespace
    except Exception as e:
        print(f"Erro conexão OCI: {e}")
        return None, None


def enviar_excel(caminho_arquivo: str, nome_objeto: str):
    client, namespace = fazer_conexao_bucket()

    if not client:
        return

    try:
        with open(caminho_arquivo, "rb") as f:
            client.put_object(
                namespace,
                BUCKET_NAME,
                f"resultados/{nome_objeto}",
                f
            )

        print(f"✅ Excel enviado: {nome_objeto}")

    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")


def baixar_excel_bucket(nome_objeto: str, destino: str):
    client, namespace = fazer_conexao_bucket()

    if not client:
        return

    try:
        response = client.get_object(
            namespace,
            BUCKET_NAME,
            f"resultados/{nome_objeto}"
        )

        with open(destino, "wb") as f:
            f.write(response.data.content)

        print(f"✅ Baixado: {destino}")

    except Exception as e:
        print(f"❌ Erro ao baixar: {e}")


def baixar_resultados(loteria: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(f'{URL_BASE}{loteria}')
        page.wait_for_load_state('networkidle')

        with page.expect_download() as download_info:
            page.click('a[href^="javascript:document.frm"]')

        download = download_info.value

        if loteria == 'mega-sena':
            nome = 'megasena'
        else:
            nome = loteria

        caminho = f"{RESULTADOS_DIR}/{nome}_resultados.xlsx"
        download.save_as(caminho)

        print(f"Download concluído: {caminho}")

        browser.close()

        # 🔥 envia pro bucket
        enviar_excel(caminho, f"{nome}_resultados.xlsx")

        # opcional: remove local
        os.remove(caminho)


loterias = ['lotofacil', 'mega-sena']

for loteria in loterias:
    baixar_resultados(loteria)
