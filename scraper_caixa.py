# scraper_caixa.py (VERSÃO CORRIGIDA PARA BAIXAR MÚLTIPLOS EDITAIS)

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# --- Configurações ---
URL = "https://venda-imoveis.caixa.gov.br/sistema/busca-documentos.asp"

def baixar_editais_por_mes(ano: int, mes_texto: str, estado_sigla: str, pasta_download: str, arquivos_existentes: list):
    """
    Navega no site da Caixa, preenche o formulário e baixa TODOS os editais de um
    determinado mês, ano e estado.
    """
    # Garante que a pasta de download existe
    if not os.path.exists(pasta_download):
        os.makedirs(pasta_download)

    # Verifica se já existem arquivos baixados para esse período antes de iniciar
    # Esta verificação foi simplificada para evitar downloads repetidos se o script for executado várias vezes
    # No entanto, a lógica original que verifica nomes específicos também é válida.
    # Para o propósito de baixar múltiplos arquivos, esta verificação é mais segura.
    arquivos_periodo = [f for f in arquivos_existentes if f"{estado_sigla}_{mes_texto}_{ano}" in f or f"EL" in f]
    if any(f for f in os.listdir(pasta_download) if f"{estado_sigla}_{mes_texto}_{ano}" in f or f"EL" in f):
        print(f"Arquivos para {mes_texto}/{ano} de {estado_sigla} já parecem ter sido baixados. Ignorando download.")
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
        
        time.sleep(3)

        # 3. Clicar no botão "Próximo"
        print("Clicando em 'Próximo' para buscar os documentos...")
        driver.find_element(By.ID, "btn_next0").click()
        
        time.sleep(3)

        # ------------------- INÍCIO DA SUBSTITUIÇÃO -------------------
        # 4. Encontrar e clicar em TODOS os botões de edital para iniciar os downloads
        print("Aguardando os resultados da busca...")
        texto_do_botao_azul = "Edital de Publicação do Leilão SFI"
        
        try:
            # Espera até que pelo menos UM link de edital esteja visível
            wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, texto_do_botao_azul)))
            
            # Encontra TODOS os elementos (links) que contêm o texto do edital
            botoes_edital = driver.find_elements(By.PARTIAL_LINK_TEXT, texto_do_botao_azul)
            
            num_editais = len(botoes_edital)
            print(f"{num_editais} edital(is) encontrado(s). Iniciando downloads...")

            # Itera (faz um loop) sobre cada botão encontrado para clicar e baixar
            for i in range(num_editais):
                # É crucial encontrar os elementos novamente dentro do loop,
                # pois a página pode ser alterada após um clique.
                botoes_edital = driver.find_elements(By.PARTIAL_LINK_TEXT, texto_do_botao_azul)
                botao_atual = botoes_edital[i]
                
                print(f"Baixando edital {i + 1}/{num_editais}: '{botao_atual.text}'")
                botao_atual.click()
                # Pausa para dar tempo ao início do download antes de prosseguir para o próximo
                time.sleep(5) 

            print("Aguardando a conclusão de todos os downloads...")
            tempo_limite = time.time() + 120  # Aumenta o tempo limite para múltiplos arquivos
            
            while time.time() < tempo_limite:
                arquivos_depois = os.listdir(pasta_download)
                novos_arquivos = [f for f in arquivos_depois if f not in arquivos_antes and not f.endswith('.crdownload')]
                
                # Verifica se o número de novos arquivos é igual ao número de editais encontrados
                if len(novos_arquivos) == num_editais:
                    print(f"Download de {len(novos_arquivos)} arquivo(s) concluído(s): {', '.join(novos_arquivos)}")
                    break
                time.sleep(3)

        except TimeoutException:
            print(f"Nenhum edital encontrado para {mes_texto}/{ano} de {estado_sigla}.")

        # ------------------- FIM DA SUBSTITUIÇÃO -------------------
            
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")
    finally:
        print("Fechando o navegador.")
        driver.quit()