# scraper_caixa.py (VERSÃO CORRIGIDA PARA DOWNLOAD AUTOMÁTICO)

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- Configurações ---
URL = "https://venda-imoveis.caixa.gov.br/sistema/busca-documentos.asp"

def baixar_editais_por_mes(ano: int, mes_texto: str, estado_sigla: str, pasta_download: str, arquivos_existentes: list):
    """
    Navega no site da Caixa, preenche o formulário e baixa os editais de um 
    determinado mês, ano e estado.
    """
    # Garante que a pasta de download existe
    if not os.path.exists(pasta_download):
        os.makedirs(pasta_download)

    # Verifica se o arquivo já foi baixado ou processado antes de iniciar
    nome_edital_esperado = f"Edital_de_Leilao_Publico_de_Venda_de_Imoveis_{estado_sigla}_{mes_texto}_{ano}.pdf"
    if any(nome_edital_esperado in f for f in arquivos_existentes):
        print(f"Edital para {mes_texto}/{ano} de {estado_sigla} já foi baixado. Ignorando download.")
        return

    # Configura as opções do Chrome para fazer download automático
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(pasta_download),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })

    # Configura o driver do Chrome automaticamente com as opções
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)
    
    arquivos_antes = os.listdir(pasta_download)

    try:
        print("Iniciando o scraper...")
        
        # 1. Acessar a página alvo
        print(f"Acessando a URL: {URL}")
        driver.get(URL)
        
        # 2. Preencher o formulário de busca
        wait.until(EC.presence_of_element_located((By.NAME, "cmb_tipo_documento")))
        print("Preenchendo o formulário de busca...")
        
        Select(driver.find_element(By.NAME, "cmb_tipo_documento")).select_by_visible_text("Edital de Publicação do Leilão SFI - Edital Único")
        Select(driver.find_element(By.NAME, "cmb_estado")).select_by_value(estado_sigla)
        Select(driver.find_element(By.NAME, "cmb_mes_referencia")).select_by_visible_text(mes_texto)
        Select(driver.find_element(By.NAME, "cmb_ano_referencia")).select_by_visible_text(str(ano))
        
        # PAUSA ADICIONADA: Permite que você veja o formulário preenchido
        time.sleep(3)

        # 3. Clicar no botão "Próximo"
        print("Clicando em 'Próximo' para buscar os documentos...")
        driver.find_element(By.ID, "btn_next0").click()
        
        # PAUSA ADICIONADA: Permite que você veja a página de resultados
        time.sleep(3)

        # 4. Encontrar e clicar no botão azul do edital para iniciar o download
        print("Aguardando os resultados da busca...")
        texto_do_botao_azul = "Edital de Publicação do Leilão SFI"
        botao_edital = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, texto_do_botao_azul))
        )
        
        print(f"Botão do edital encontrado: '{botao_edital.text}'")
        print("Iniciando o download...")
        botao_edital.click()
        
        print("Aguardando o arquivo ser baixado...")
        tempo_limite = time.time() + 60
        novo_arquivo = None
        
        while time.time() < tempo_limite:
            arquivos_depois = os.listdir(pasta_download)
            novos_arquivos = list(set(arquivos_depois) - set(arquivos_antes))
            
            novos_arquivos = [f for f in novos_arquivos if not f.endswith('.crdownload')]
            
            if novos_arquivos:
                novo_arquivo = novos_arquivos[0]
                print(f"Download concluído: '{novo_arquivo}'")
                break
            time.sleep(3)
        
        if not novo_arquivo:
            print("Erro: O arquivo não foi baixado dentro do tempo limite.")
            
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")
    finally:
        print("Fechando o navegador.")
        driver.quit()