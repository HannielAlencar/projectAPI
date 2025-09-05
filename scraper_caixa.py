# Importa as ferramentas necessárias do Selenium
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configurações ---
URL = "https://venda-imoveis.caixa.gov.br/sistema/busca-documentos.asp"

# --- Início do Scraper ---
print("Iniciando o scraper...")

# Configura o driver do Chrome automaticamente
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window() # Maximiza a janela para melhor visualização

# Cria um "esperador" que aguardará até 20 segundos para os elementos aparecerem
wait = WebDriverWait(driver, 20)

try:
    # 1. Acessar a página alvo
    print(f"Acessando a URL: {URL}")
    driver.get(URL)

    # 2. Preencher o formulário de busca (com os dados da sua imagem)
    # Espera o formulário carregar
    wait.until(EC.presence_of_element_located((By.NAME, "cmb_tipo_documento")))
    print("Preenchendo o formulário de busca...")

    # Seleciona "Edital de Publicação do Leilão SFI - Edital Único"
    Select(driver.find_element(By.NAME, "cmb_tipo_documento")).select_by_visible_text("Edital de Publicação do Leilão SFI - Edital Único")
    
    # Seleciona o Estado "SP"
    Select(driver.find_element(By.NAME, "cmb_estado")).select_by_value("SP")
    
    # Seleciona o Mês "Setembro"
    Select(driver.find_element(By.NAME, "cmb_mes_referencia")).select_by_visible_text("Setembro")
    
    # Seleciona o Ano "2025"
    Select(driver.find_element(By.NAME, "cmb_ano_referencia")).select_by_visible_text("2025")

    time.sleep(3) # Pausa para você ver o formulário preenchido

    # 3. Clicar no botão "Próximo" para realizar a busca
    print("Clicando em 'Próximo' para buscar os documentos...")
    driver.find_element(By.ID, "btn_next0").click()

    # 4. Achar e clicar no botão azul do edital (a parte mais importante)
    print("Aguardando os resultados da busca...")
    
    # Texto que vamos usar para encontrar o botão
    texto_do_botao_azul = "Edital de Publicação do Leilão SFI"
    
    # O robô vai esperar até que o elemento com esse texto esteja PRONTO PARA SER CLICADO
    botao_edital = wait.until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, texto_do_botao_azul))
    )
    
    print(f"Botão do edital encontrado: '{botao_edital.text}'")
    print("Clicando no botão azul...")
    
    # Ação de clicar no botão
    botao_edital.click()
    
    # Pausa longa para você ver o resultado (o download do PDF deve iniciar)
    print("Ação finalizada! O navegador ficará aberto por 30 segundos para observação.")
    time.sleep(30)

finally:
    # 5. Fechar o navegador no final de tudo
    print("Fechando o scraper.")
    driver.quit()