# scraper_caixa.py (VERSÃO COM PAUSAS PARA VISUALIZAÇÃO)

import os
import time # Importamos o módulo time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def baixar_editais_por_mes(ano: int, mes_texto: str, estado_sigla: str, pasta_download: str):
    """
    Baixa TODOS os editais encontrados para um mês, ano e estado específicos, com pausas para visualização.
    """
    print(f"--- Buscando editais para {mes_texto}/{ano} em {estado_sigla} ---")
    
    os.makedirs(pasta_download, exist_ok=True)
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    prefs = {
        "download.default_directory": os.path.abspath(pasta_download),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 40)

    try:
        url = "https://venda-imoveis.caixa.gov.br/sistema/busca-documentos.asp"
        driver.get(url)
        print(f"    -> Acessando a URL...")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("    -> Página carregada. Iniciando preenchimento do formulário...")
        
        time.sleep(2) # Pausa inicial

        print("    -> Selecionando 'Tipo de documento'...")
        Select(driver.find_element(By.NAME, "cmb_tipo_documento")).select_by_visible_text("Edital de Publicação do Leilão SFI - Edital Único")
        time.sleep(2) # Pausa para visualização

        print(f"    -> Selecionando Estado '{estado_sigla}'...")
        Select(driver.find_element(By.NAME, "cmb_estado")).select_by_value(estado_sigla)
        time.sleep(2) # Pausa para visualização

        print(f"    -> Selecionando Mês '{mes_texto}'...")
        Select(driver.find_element(By.NAME, "cmb_mes_referencia")).select_by_visible_text(mes_texto)
        time.sleep(2) # Pausa para visualização

        print(f"    -> Selecionando Ano '{ano}'...")
        Select(driver.find_element(By.NAME, "cmb_ano_referencia")).select_by_visible_text(str(ano))
        time.sleep(2) # Pausa para visualização
        
        print("    -> Formulário preenchido.")
        
        print("    -> Clicando em 'Próximo'...")
        driver.find_element(By.ID, "btn_next0").click()
        
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "listadocumentos")))
            print("    -> Página de resultados carregada.")
            time.sleep(2) # Pausa para ver os resultados

            xpath_dos_links = "//div[@id='listadocumentos']//a[contains(@href, '.PDF')]"
            wait.until(EC.presence_of_element_located((By.XPATH, xpath_dos_links)))
            links_pdf = driver.find_elements(By.XPATH, xpath_dos_links)
            
            if not links_pdf:
                print(f"    -> Nenhum edital encontrado para este período.")
                return

            print(f"    -> {len(links_pdf)} edital(is) encontrado(s). Iniciando downloads...")
            for link in links_pdf:
                print(f"    -> Clicando no link para baixar: {link.text}")
                link.click()
                time.sleep(3) # Pausa um pouco maior para garantir que o download inicie

            print("    -> Aguardando conclusão dos downloads...")
            while any(fname.endswith('.crdownload') for fname in os.listdir(pasta_download)):
                time.sleep(1)
        except Exception:
            print(f"    -> Nenhum edital na página de resultados para este período.")
    
    except Exception as e:
        print(f"    ERRO: Falha crítica no scraping.")
        print(f"    Detalhe do erro: {e}")

    finally:
        print(">>> Fechando o navegador.")
        time.sleep(2) # Pausa final antes de fechar
        driver.quit()