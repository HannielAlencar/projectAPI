# scraper_caixa.py (VERSÃO ATUALIZADA)

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def gerar_meses_anos(data_inicio):
    """Gera uma sequência de (ano, mês_texto) a partir da data de início até a data atual."""
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    data_atual = datetime.now()
    ano_atual, mes_atual = data_atual.year, data_atual.month
    
    ano, mes = data_inicio.year, data_inicio.month
    
    while ano < ano_atual or (ano == ano_atual and mes <= mes_atual):
        yield (ano, meses[mes-1])
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

def baixar_editais_a_partir_de(data_inicio: datetime.date, estados: list, pasta_download: str):
    """
    Automatiza a busca e o download de editais a partir de uma data específica.
    """
    os.makedirs(pasta_download, exist_ok=True)
    
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(pasta_download),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 40)

    print(">>> Iniciando o robô de scraping inteligente...")

    try:
        url = "https://venda-imoveis.caixa.gov.br/sistema/busca-documentos.asp"
        driver.get(url)
        print(f">>> Acessando a URL: {url}")
        
        downloads_realizados = 0

        for estado in estados:
            print(f"\n--- Buscando no estado: {estado} ---")
            for ano, mes_texto in gerar_meses_anos(data_inicio):
                print(f"  - Verificando Mês/Ano: {mes_texto}/{ano}")
                
                driver.get(url) # Reinicia a busca para evitar bugs da página

                wait.until(EC.element_to_be_clickable((By.ID, "cmb_tipo_documento")))
                Select(driver.find_element(By.ID, "cmb_tipo_documento")).select_by_visible_text("Edital de Publicação do Leilão SFI - Edital Único")
                Select(driver.find_element(By.ID, "cmb_estado")).select_by_value(estado)
                Select(driver.find_element(By.ID, "cmb_mes")).select_by_visible_text(mes_texto)
                Select(driver.find_element(By.ID, "cmb_ano")).select_by_visible_text(str(ano))
                
                driver.find_element(By.ID, "btn_next").click()
                
                try:
                    # Aguarda a tabela de resultados aparecer
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dados-resultado")))
                    
                    # Encontra todas as linhas de resultado
                    linhas_resultado = driver.find_elements(By.XPATH, "//tr[contains(@class, 'dados-resultado')]")
                    
                    for linha in linhas_resultado:
                        texto_linha = linha.text
                        
                        # Extrai a data de publicação da linha
                        match_data = re.search(r"publicado em: (\d{2}/\d{2}/\d{4})", texto_linha)
                        if match_data:
                            data_str = match_data.group(1)
                            data_edital = datetime.strptime(data_str, "%d/%m/%Y").date()
                            
                            # A LÓGICA PRINCIPAL: Compara a data do edital com a data de início
                            if data_edital >= data_inicio:
                                print(f"    [ENCONTRADO!] Edital de {data_str}. Baixando...")
                                link_pdf = linha.find_element(By.XPATH, ".//a[contains(@href, '.pdf')]")
                                link_pdf.click()
                                downloads_realizados += 1
                                time.sleep(2) # Pausa para o download iniciar

                except Exception:
                    # Se não encontrar resultados, apenas informa e continua para o próximo mês
                    print(f"    -> Nenhum edital encontrado para {mes_texto}/{ano}.")
                    continue
        
        if downloads_realizados > 0:
            print(f"\n>>> {downloads_realizados} novo(s) edital(is) baixado(s). Aguardando conclusão...")
            while any(fname.endswith('.crdownload') for fname in os.listdir(pasta_download)):
                time.sleep(1)
            print(">>> Downloads concluídos com sucesso!")
        else:
            print("\n>>> Nenhum edital novo encontrado a partir da data especificada.")

    except Exception as e:
        print(f"Ocorreu um erro durante a execução do robô: {e}")

    finally:
        print(">>> Fechando o navegador.")
        driver.quit()