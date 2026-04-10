from playwright.sync_api import sync_playwright
from pathlib import Path


url_base = 'https://asloterias.com.br/download-todos-resultados-'
RESULTADOS_DIR = "/app/resultados"


def baixar_resultados(loteria: str = 'lotofacil') -> None:
    Path(RESULTADOS_DIR).mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(f'{url_base}{loteria}')
        page.wait_for_load_state('networkidle')

        # Espera o download gerado pelo submit do formulário
        with page.expect_download() as download_info:
            page.click('a[href^="javascript:document.frm"]')

        download = download_info.value

        if loteria == 'mega-sena':
            loteria = 'megasena'
        caminho = f'{RESULTADOS_DIR}/{loteria}_resultados.xlsx'
        download.save_as(caminho)

        print(f"Download concluído: {caminho}")

        browser.close()


loterias = ['lotofacil', 'mega-sena']
for loteria in loterias:
    baixar_resultados(loteria)
