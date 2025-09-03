# processador_pdf.py (VERSÃO FINAL)

import os
import re
import pdfplumber
from pprint import pprint

def limpar_valor_monetario(valor_str: str) -> float:
    if not isinstance(valor_str, str):
        return 0.0
    valor_limpo = re.sub(r'[R$\s.]', '', valor_str).replace(',', '.')
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0

def processar_pdfs_e_filtrar(pasta_pdfs: str) -> list[dict]:
    imoveis_aprovados = []
    if not os.path.isdir(pasta_pdfs):
        print(f"Erro: A pasta '{pasta_pdfs}' não foi encontrada.")
        return []

    print(f"\n>>> Iniciando processamento de PDFs na pasta '{pasta_pdfs}'...")
    for nome_arquivo in os.listdir(pasta_pdfs):
        if nome_arquivo.lower().endswith(".pdf"):
            caminho_completo = os.path.join(pasta_pdfs, nome_arquivo)
            print(f"  - Lendo arquivo: {nome_arquivo}")
            try:
                with pdfplumber.open(caminho_completo) as pdf:
                    texto_completo = ""
                    for page in pdf.pages[22:]:
                        texto_pagina = page.extract_text(layout=True)
                        if texto_pagina:
                            texto_completo += texto_pagina + "\n"
                
                anexo_match = re.search(r"Anexo II - RELAÇÃO DE IMÓVEIS", texto_completo)
                if not anexo_match: continue
                
                texto_imoveis = texto_completo[anexo_match.start():]
                lotes_texto = re.split(r'\n(\d+)\s(?!CIDADE)', texto_imoveis)
                
                estado_atual, cidade_atual = "", ""
                for i in range(1, len(lotes_texto), 2):
                    numero_lote, texto_lote = lotes_texto[i], lotes_texto[i+1]
                    
                    estado_match = re.search(r"ESTADO: (\w{2})", texto_lote)
                    cidade_match = re.search(r"CIDADE: (.*?)\n", texto_lote)
                    if estado_match: estado_atual = estado_match.group(1).strip()
                    if cidade_match: cidade_atual = cidade_match.group(1).strip()
                    
                    endereco_match = re.search(r'\n(.*?)\n(.*?)\n(.*?)\n(.*?)\n', texto_lote)
                    valores = re.findall(r'([\d.,]+)', texto_lote)
                    
                    if len(valores) >= 3:
                        valor1 = limpar_valor_monetario(valores[-3])
                        valor2 = limpar_valor_monetario(valores[-2])
                        
                        provisao = valor1 - valor2
                        
                        if provisao >= 5000:
                            endereco = " ".join([p.strip() for p in endereco_match.groups() if p]) if endereco_match else "Endereço não extraído"
                            imovel_aprovado = {
                                "id_lote": int(numero_lote), "estado": estado_atual, "cidade": cidade_atual,
                                "endereco": endereco, "valor_1_leilao": valor1, "valor_2_leilao": valor2,
                                "provisao": round(provisao, 2), "origem_edital": nome_arquivo
                            }
                            imoveis_aprovados.append(imovel_aprovado)
            except Exception as e:
                print(f"    ERRO: Falha ao processar o arquivo {nome_arquivo}. Erro: {e}")
    
    print(f">>> Processamento finalizado. {len(imoveis_aprovados)} imóveis aprovados.")
    return imoveis_aprovados