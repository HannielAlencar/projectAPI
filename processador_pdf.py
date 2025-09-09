# processador_pdf.py (VERSÃO CORRIGIDA E MELHORADA)

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
    except (ValueError, TypeError):
        return 0.0

def extrair_imoveis_do_texto(texto_completo: str, nome_arquivo: str) -> list:
    imoveis_extraidos = []
    estado_atual, cidade_atual = "", ""
    
    # Novo padrão para capturar a Matrícula
    padrao_matricula = re.compile(r"Matricula:\s*(\w+)\s*")
    
    # Padrão para encontrar um bloco de imóvel:
    # Começa com um número no início da linha, seguido por texto e pelos valores de leilão.
    # Esta regex captura o número do item, todo o texto descritivo, e os três valores no final.
    padrao_bloco = re.compile(
        r"^\s*(\d+)\s+(.*?)"  # 1: Número do item, 2: Todo o texto de descrição
        r"([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s*$",  # 3, 4, 5: Valor 1º Leilão, Valor 2º Leilão, Valor Avaliação
        re.MULTILINE | re.DOTALL # MULTILINE para ^ funcionar em cada linha, DOTALL para . capturar quebras de linha
    )

    for trecho in texto_completo.split("Estado:")[1:]:
        estado_match = re.search(r"(\w{2})", trecho)
        if estado_match:
            estado_atual = estado_match.group(1).strip()

        for sub_trecho in trecho.split("Cidade:")[1:]:
            cidade_match = re.search(r"([^\n]+)", sub_trecho)
            if cidade_match:
                cidade_atual = cidade_match.group(1).strip()
            
            for match in padrao_bloco.finditer(sub_trecho):
                id_lote_str, descricao, valor1_str, valor2_str, _ = match.groups()
                
                # Encontra a matrícula no texto da descrição
                matricula_match = padrao_matricula.search(descricao)
                matricula = matricula_match.group(1).strip() if matricula_match else None
                
                imovel = {
                    "id_lote": int(id_lote_str),
                    "estado": estado_atual,
                    "cidade": cidade_atual,
                    "endereco": ' '.join(descricao.replace('\n', ' ').split()),
                    "matricula": matricula, # Adicionamos o campo de matrícula
                    "valor1_str": valor1_str,
                    "valor2_str": valor2_str,
                    "origem_edital": nome_arquivo
                }
                imoveis_extraidos.append(imovel)

    return imoveis_extraidos


def processar_pdfs_e_filtrar(pasta_pdfs: str, arquivos_ja_processados: set) -> list[dict]:
    imoveis_aprovados = []
    if not os.path.isdir(pasta_pdfs):
        print(f"Erro: A pasta '{pasta_pdfs}' não foi encontrada.")
        return []

    print(f"\n>>> Iniciando processamento de PDFs na pasta '{pasta_pdfs}'...")
    for nome_arquivo in os.listdir(pasta_pdfs):
        # Ignora arquivos que já foram processados
        if nome_arquivo in arquivos_ja_processados:
            print(f"  - Ignorando arquivo já processado: {nome_arquivo}")
            continue

        if nome_arquivo.lower().endswith(".pdf"):
            caminho_completo = os.path.join(pasta_pdfs, nome_arquivo)
            print(f"  - Lendo arquivo: {nome_arquivo}")

            try:
                with pdfplumber.open(caminho_completo) as pdf:
                    texto_completo = ""
                    # Começa a extrair o texto de onde os imóveis começam a ser listados
                    for page in pdf.pages[21:]: 
                        texto_pagina = page.extract_text()
                        if texto_pagina:
                            texto_completo += texto_pagina + "\n"
                
                imoveis_brutos = extrair_imoveis_do_texto(texto_completo, nome_arquivo)

                for imovel_data in imoveis_brutos:
                    valor1 = limpar_valor_monetario(imovel_data["valor1_str"])
                    valor2 = limpar_valor_monetario(imovel_data["valor2_str"])

                    if valor1 > 0 and valor2 > 0:
                        provisao = valor1 - valor2
                        
                        if provisao >= 5000:
                            imovel_aprovado = {
                                "id_lote": imovel_data["id_lote"],
                                "estado": imovel_data["estado"],
                                "cidade": imovel_data["cidade"],
                                "endereco": imovel_data["descricao_completa"], # A descrição agora serve como endereço
                                "matricula": imovel_data["matricula"], # Adicionamos a matricula ao objeto
                                "valor_1_leilao": valor1,
                                "valor_2_leilao": valor2,
                                "provisao": round(provisao, 2),
                                "origem_edital": imovel_data["origem_edital"]
                            }
                            imoveis_aprovados.append(imovel_aprovado)
            except Exception as e:
                print(f"    ERRO: Falha ao processar o arquivo {nome_arquivo}. Erro: {e}")
    
    print(f">>> Processamento finalizado. {len(imoveis_aprovados)} imóveis aprovados.")
    return imoveis_aprovados


if __name__ == "__main__":
    PASTA_DOS_EDITAIS = "editais_baixados"

    if not os.path.exists(PASTA_DOS_EDITAIS):
        os.makedirs(PASTA_DOS_EDITAIS)
        print(f"Pasta '{PASTA_DOS_EDITAIS}' criada para teste. Por favor, adicione seu PDF nela.")

    imoveis_encontrados = processar_pdfs_e_filtrar(PASTA_DOS_EDITAIS, set())
    
    if imoveis_encontrados:
        print("\n--- IMÓVEIS APROVADOS ENCONTRADOS ---")
        pprint(imoveis_encontrados)
    else:
        print("\n--- NENHUM IMÓVEL APROVADO FOI ENCONTRADO ---")