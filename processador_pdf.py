# processador_pdf.py

import os
import re
import pdfplumber
from pprint import pprint

def limpar_valor_monetario(valor_str: str) -> float:
    """
    Função auxiliar para converter uma string de moeda (ex: '1.234.567,89')
    em um número float (ex: 1234567.89).
    """
    if not isinstance(valor_str, str):
        return 0.0
    valor_limpo = re.sub(r'[R$\s.]', '', valor_str).replace(',', '.')
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0

def processar_pdfs_e_filtrar(pasta_pdfs: str) -> list[dict]:
    """
    Lê todos os arquivos PDF em uma pasta, extrai os dados dos imóveis,
    aplica o filtro de provisão e retorna uma lista de imóveis aprovados.
    """
    imoveis_aprovados = []
    
    if not os.path.isdir(pasta_pdfs):
        print(f"Erro: A pasta '{pasta_pdfs}' não foi encontrada.")
        return []

    print(f">>> Iniciando processamento de PDFs na pasta '{pasta_pdfs}'...")

    for nome_arquivo in os.listdir(pasta_pdfs):
        if nome_arquivo.lower().endswith(".pdf"):
            caminho_completo = os.path.join(pasta_pdfs, nome_arquivo)
            print(f"\n  - Lendo arquivo: {nome_arquivo}")

            try:
                with pdfplumber.open(caminho_completo) as pdf:
                    texto_completo = ""
                    # Começa a extração a partir da página do Anexo II (geralmente por volta da pág. 23)
                    # Isso evita ler o texto inicial do edital desnecessariamente
                    for page in pdf.pages[22:]: # Ajuste o número da página se necessário
                        texto_pagina = page.extract_text(layout=True) # layout=True ajuda a manter a formatação
                        if texto_pagina:
                            texto_completo += texto_pagina + "\n"
                
                # Encontrar a seção do Anexo II
                anexo_match = re.search(r"Anexo II - RELAÇÃO DE IMÓVEIS", texto_completo)
                if not anexo_match:
                    print(f"    AVISO: 'Anexo II' não encontrado em {nome_arquivo}.")
                    continue
                
                # Pega todo o texto a partir do Anexo II
                texto_imoveis = texto_completo[anexo_match.start():]

                # Regex para encontrar cada bloco de imóvel, que começa com um número no início da linha.
                # Ex: "1 ", "2 ", "3 "
                # O (?!CIDADE) garante que não pegue números de CEP ou outros que não sejam de item.
                lotes_texto = re.split(r'\n(\d+)\s(?!CIDADE)', texto_imoveis)
                
                estado_atual = ""
                cidade_atual = ""

                # Itera sobre o texto dos lotes
                for i in range(1, len(lotes_texto), 2):
                    numero_lote = lotes_texto[i]
                    texto_lote = lotes_texto[i+1]
                    
                    # Atualiza estado e cidade se encontrados no trecho
                    estado_match = re.search(r"ESTADO: (\w{2})", texto_lote)
                    cidade_match = re.search(r"CIDADE: (.*?)\n", texto_lote)
                    if estado_match: estado_atual = estado_match.group(1).strip()
                    if cidade_match: cidade_atual = cidade_match.group(1).strip()
                    
                    # Padrões de Regex ajustados para o formato da tabela do seu PDF
                    # Usamos re.DOTALL para que o '.' também capture quebras de linha
                    # As colunas são extraídas de forma mais robusta
                    
                    # Tentamos extrair o endereço de forma mais completa
                    endereco_match = re.search(r'\n(.*?)\n(.*?)\n(.*?)\n(.*?)\n', texto_lote)
                    
                    # Extrai os valores das colunas de leilão
                    valores = re.findall(r'([\d.,]+)', texto_lote)
                    
                    if len(valores) >= 3:
                        valor1_str = valores[-3] # Terceiro último número na sequência
                        valor2_str = valores[-2] # Penúltimo número na sequência
                        
                        valor1 = limpar_valor_monetario(valor1_str)
                        valor2 = limpar_valor_monetario(valor2_str)
                        
                        # Tenta montar um endereço mais limpo, se possível
                        endereco = "Endereço não extraído"
                        if endereco_match:
                            partes_endereco = [p.strip() for p in endereco_match.groups() if p]
                            endereco = " ".join(partes_endereco)
                        
                        # Aplica a sua regra de negócio
                        provisao = valor1 - valor2
                        
                        if provisao >= 5000:
                            imovel_aprovado = {
                                "id_lote": int(numero_lote),
                                "estado": estado_atual,
                                "cidade": cidade_atual,
                                "endereco": endereco,
                                "valor_1_leilao": valor1,
                                "valor_2_leilao": valor2,
                                "provisao": round(provisao, 2),
                                "origem_edital": nome_arquivo
                            }
                            imoveis_aprovados.append(imovel_aprovado)

            except Exception as e:
                print(f"    ERRO: Falha ao processar o arquivo {nome_arquivo}. Erro: {e}")
    
    print(f"\n>>> Processamento finalizado. {len(imoveis_aprovados)} imóveis aprovados.")
    return imoveis_aprovados

# --- Bloco de Teste ---
if __name__ == "__main__":
    PASTA_DOS_EDITAIS = "editais_baixados" # Pasta onde o scraper salvou os PDFs

    print("--- INICIANDO TESTE DO SCRIPT processador_pdf.py ---")
    
    # Criar um arquivo PDF de teste se a pasta não existir
    if not os.path.exists(PASTA_DOS_EDITAIS):
        os.makedirs(PASTA_DOS_EDITAIS)
        print(f"Pasta '{PASTA_DOS_EDITAIS}' criada para teste.")
        # Simula a existência de um arquivo. Para um teste real, coloque seu PDF lá.
        # Ex: open(os.path.join(PASTA_DOS_EDITAIS, 'EL00480225CPARE.pdf'), 'a').close()

    imoveis_encontrados = processar_pdfs_e_filtrar(PASTA_DOS_EDITAIS)
    
    if imoveis_encontrados:
        print("\n--- IMÓVEIS APROVADOS ENCONTRADOS ---")
        pprint(imoveis_encontrados)
    else:
        print("\n--- NENHUM IMÓVEL APROVADO FOI ENCONTRADO ---")
        print("Verifique se há arquivos PDF na pasta 'editais_baixados' e se eles seguem o formato esperado.")
    
    print("\n--- TESTE FINALIZADO ---")