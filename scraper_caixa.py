# scraper_caixa.py

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def baixar_editais(ano: int, mes_texto: str, estado_sigla: str, pasta_download: str):
    """
    Automatiza a busca e o download de editais do site da Caixa.

    Args:
        ano (int): O ano para a busca (ex: 2025).
        mes_texto (str): O nome completo do mês (ex: "Setembro").
        estado_sigla (str): A sigla do estado (ex: "SP").
        pasta_download (str): O caminho da pasta onde os PDFs serão salvos.
    """
    
    # --- 1. Configuração do Navegador e Download ---
    
    # Garante que a pasta de download exista
    os.makedirs(pasta_download, exist_ok=True)
    
    # Configurações do Chrome para fazer o download automático na pasta especificada
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(pasta_download),
        "download.prompt_for_download": False, # Não perguntar onde salvar
        "plugins.always_open_pdf_externally": True # Evita abrir o PDF no navegador
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Instala e gerencia o driver do Chrome automaticamente
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Define uma espera máxima de 20 segundos para os elementos aparecerem
    wait = WebDriverWait(driver, 20)

    print(">>> Iniciando o robô de scraping...")

    try:
        # --- 2. Navegação e Preenchimento do Formulário ---
        
        url = "https://venda-imoveis.caixa.gov.br/sistema/busca-documentos.asp"
        driver.get(url)
        print(f">>> Acessando a URL: {url}")

        # Aguarda o campo "Tipo de documento" ficar clicável e o seleciona
        wait.until(EC.element_to_be_clickable((By.ID, "cmb_tipo_documento")))
        select_tipo = Select(driver.find_element(By.ID, "cmb_tipo_documento"))
        select_tipo.select_by_visible_text("Edital de Publicação do Leilão SFI - Edital Único")
        print("- Tipo de documento selecionado.")

        # Seleciona o Estado
        select_estado = Select(driver.find_element(By.ID, "cmb_estado"))
        select_estado.select_by_value(estado_sigla)
        print(f"- Estado '{estado_sigla}' selecionado.")
        
        # Seleciona o Mês
        select_mes = Select(driver.find_element(By.ID, "cmb_mes"))
        select_mes.select_by_visible_text(mes_texto)
        print(f"- Mês '{mes_texto}' selecionado.")
        
        # Seleciona o Ano
        select_ano = Select(driver.find_element(By.ID, "cmb_ano"))
        select_ano.select_by_visible_text(str(ano))
        print(f"- Ano '{ano}' selecionado.")
        
        # Clica no botão "Próximo"
        driver.find_element(By.ID, "btn_next").click()
        print(">>> Clicando em 'Próximo'. Aguardando resultados...")

        # --- 3. Download dos Arquivos ---

        # Aguarda a aparição dos links de resultado (links que contêm .pdf)
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf')]")))
        
        # Encontra todos os elementos de link que apontam para um PDF
        links_pdf = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        
        if not links_pdf:
            print(">>> Nenhum edital encontrado para os filtros selecionados.")
            return

        print(f">>> {len(links_pdf)} edital(is) encontrado(s). Iniciando downloads...")
        
        for link in links_pdf:
            link_text = link.text.strip()
            print(f"    - Baixando: {link_text}...")
            link.click()
            # Uma pequena pausa para garantir que o download inicie antes de clicar no próximo
            time.sleep(2)

        # --- 4. Aguardar a Conclusão dos Downloads ---
        
        print(">>> Aguardando a finalização de todos os downloads...")
        # Lógica para esperar os arquivos .crdownload (temporários do Chrome) desaparecerem
        while any(fname.endswith('.crdownload') for fname in os.listdir(pasta_download)):
            time.sleep(1)
        
        print(">>> Downloads concluídos com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro durante a execução do robô: {e}")

    finally:
        # --- 5. Fechar o Navegador ---
        print(">>> Fechando o navegador.")
        driver.quit()

# --- Bloco de Teste ---
# Permite que você rode este arquivo diretamente para testar o robô
if __name__ == "__main__":
    # Parâmetros para o teste
    ANO_TESTE = 2025 # O ano atual ou futuro, dependendo do que você busca
    MES_TESTE = "Setembro" # O mês por extenso, com a primeira letra maiúscula
    ESTADO_TESTE = "SP" # A sigla do estado em maiúsculas
    PASTA_DOWNLOADS = "editais_baixados" # Nome da pasta onde os PDFs serão salvos

    print("--- INICIANDO TESTE DO SCRIPT scraper_caixa.py ---")
    baixar_editais(
        ano=ANO_TESTE,
        mes_texto=MES_TESTE,
        estado_sigla=ESTADO_TESTE,
        pasta_download=PASTA_DOWNLOADS
    )
    print("--- TESTE FINALIZADO ---")