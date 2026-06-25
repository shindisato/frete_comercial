from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import math
import httpx

app = FastAPI(title="Calculadora de Cubagem Multitens - Revisada")

# Configurações de Origem da sua Empresa
CEP_ORIGEM_PADRAO = "37642162"
ENDERECO_ORIGEM = "Rua das Flores, 123 - Distrito Industrial, Extrema - MG"

# Liberação de segurança para o HTML local conversar com o Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Matriz de Caixas oficiais da sua planilha
MATRIZ_CAIXAS = {
    "1": {"nome": "CX 1", "comprimento": 16, "largura": 10, "altura": 5, "peso_vazia_g": 50},
    "2": {"nome": "CX 2", "comprimento": 18, "largura": 11, "altura": 12, "peso_vazia_g": 70},
    "3": {"nome": "CX 3", "comprimento": 25.5, "largura": 23.5, "altura": 9, "peso_vazia_g": 150},
    "4": {"nome": "CX 4", "comprimento": 33, "largura": 21, "altura": 16, "peso_vazia_g": 240},
    "5": {"nome": "CX 5", "comprimento": 43, "largura": 26, "altura": 19, "peso_vazia_g": 340},
    "6": {"nome": "CX 6 (Lumini)", "comprimento": 43, "largura": 26, "altura": 23, "peso_vazia_g": 420}
}

# Banco de Dados de Produtos com pesos e limites de cubagem
PRODUTOS_DB = {
    "ST8210": {"nome": "ST8210 / 8310UM / ST4215U", "peso_g": 78, "max_por_caixa": {"1": 5, "2": 15, "3": 30, "4": 60, "5": 150}},
    "ST340U": {"nome": "ST340U / UR / US", "peso_g": 107, "max_por_caixa": {"1": 4, "2": 10, "3": 25, "4": 50, "5": 110}},
    "ST390": {"nome": "ST390 / 395 / 4315 / 8310 / 8395 / 8380", "peso_g": 100, "max_por_caixa": {"1": 2, "2": 12, "3": 20, "4": 50, "5": 100}},
    "ST4305": {"nome": "ST4305 / 300 / 8300 + CABOS", "peso_g": 198, "max_por_caixa": {"1": 2, "2": 5, "3": 13, "4": 30, "5": 50}},
    "ST4945": {"nome": "ST4945 BAT. 3000 MAH + KIT", "peso_g": 180, "max_por_caixa": {"1": 2, "2": 9, "3": 16, "4": 40, "5": 70}},
    "ST940": {"nome": "ST940 / 4945S BAT. 1500 MAH + KIT", "peso_g": 148, "max_por_caixa": {"1": 2, "2": 6, "3": 15, "4": 30, "5": 65}},
    "ST4410": {"nome": "ST4410 / 4410G", "peso_g": 90, "max_por_caixa": {"1": 8, "2": 21, "3": 38, "4": 105, "5": 180}},
    "ST9730": {"nome": "ST9730 + KIT", "peso_g": 380, "max_por_caixa": {"1": 1, "2": 2, "3": 5, "4": 12, "5": 24}},
    "ST410M": {"nome": "ST410M / MG", "peso_g": 79, "max_por_caixa": {"1": 9, "2": 27, "3": 61, "4": 127, "5": 250}},
    "W16": {"nome": "W16 / LT32 PRO + CABO (Lumini)", "peso_g": 78, "max_por_caixa": {"1": 5, "2": 15, "3": 30, "4": 80, "5": 125}},
    "ST310U": {"nome": "ST310U C/ CONECTOR MICROFIT", "peso_g": 81, "max_por_caixa": {"1": 4, "2": 10, "3": 25, "4": 50, "5": 120}},
    "ST419NG": {"nome": "ST419NG", "peso_g": 80, "max_por_caixa": {"1": 7, "2": 20, "3": 36, "4": 94, "5": 200}},
    "ST449LG": {"nome": "ST449LG", "peso_g": 190, "max_por_caixa": {"1": 2, "2": 8, "3": 30, "4": 50, "5": 75}},
    "ST449G": {"nome": "ST449G", "peso_g": 120, "max_por_caixa": {"1": 5, "2": 14, "3": 35, "4": 80, "5": 144}},
    "ST350": {"nome": "ST350 LC4 - 50 CM", "peso_g": 81, "max_por_caixa": {"1": 6, "2": 15, "3": 34, "4": 66, "5": 150}},
    "ST6560": {"nome": "ST6560", "peso_g": 50, "max_por_caixa": {"1": 8, "2": 26, "3": 52, "4": 130, "5": 250}},
    "ST20": {"nome": "ST20 / ST25 + CABOS", "peso_g": 270, "max_por_caixa": {"1": 1, "2": 5, "3": 10, "4": 20, "5": 35}},
    "ST440": {"nome": "ST440", "peso_g": 235, "max_por_caixa": {"1": 2, "2": 8, "3": 19, "4": 39, "5": 64}},
    "ST70": {"nome": "ST70", "peso_g": 49, "max_por_caixa": {"1": 6, "2": 15, "3": 34, "4": 66, "5": 150}},
    "ST90": {"nome": "ST90", "peso_g": 103, "max_por_caixa": {"1": 4, "2": 13, "3": 39, "4": 80, "5": 130}},
    "ST400": {"nome": "ST400", "peso_g": 82, "max_por_caixa": {"1": 10, "2": 28, "3": 70, "4": 150, "5": 150}},
    "ST420": {"nome": "ST420", "peso_g": 598, "max_por_caixa": {"1": 1, "2": 4, "3": 8, "4": 16, "5": 34}},
    "ST420P": {"nome": "ST420 P", "peso_g": 255, "max_por_caixa": {"1": 0, "2": 2, "3": 5, "4": 12, "5": 20}},
    "ST480A": {"nome": "ST480 - COM ANTENA", "peso_g": 382, "max_por_caixa": {"1": 0, "2": 0, "3": 5, "4": 10, "5": 20}},
    "ST480": {"nome": "ST480", "peso_g": 215, "max_por_caixa": {"1": 4, "2": 13, "3": 30, "4": 61, "5": 118}},
    "ST500": {"nome": "ST500", "peso_g": 68, "max_por_caixa": {"1": 8, "2": 18, "3": 45, "4": 105, "5": 224}},
    "BASE1500": {"nome": "BASE IMANTADA BAT. 1500 MAH", "peso_g": 230, "max_por_caixa": {"1": 10, "2": 20, "3": 40, "4": 80, "5": 150}},
    "BASE3000": {"nome": "BASE IMANTADA BAT. 3000 MAH", "peso_g": 60, "max_por_caixa": {"1": 20, "2": 40, "3": 80, "4": 160, "5": 300}},
    "CABOCONFIG": {"nome": "CABO DE CONFIG. TODOS OS MODELOS", "peso_g": 38, "max_por_caixa": {"1": 20, "2": 50, "3": 100, "4": 200, "5": 400}},
    "CHAVEIRO": {"nome": "CHAVEIRO I - BUTTON", "peso_g": 5, "max_por_caixa": {"1": 100, "2": 200, "3": 500, "4": 1000, "5": 2000}},
    "CHICOTE": {"nome": "CHICOTE I - BUTTON", "peso_g": 57, "max_por_caixa": {"1": 30, "2": 60, "3": 120, "4": 240, "5": 500}},
    "GIGA": {"nome": "GIGA DE TESTE", "peso_g": 200, "max_por_caixa": {"1": 0, "2": 2, "3": 4, "4": 10, "5": 22}},
    "TECLADO": {"nome": "TECLADO C/ SUPORTE DE VIDRO", "peso_g": 551, "max_por_caixa": {"1": 0, "2": 0, "3": 1, "4": 3, "5": 5}},
    "OUTROS": {"nome": "Outros (Configuração Manual)", "peso_g": 100, "max_por_caixa": {"1": 5, "2": 10, "3": 20, "4": 40, "5": 100}}
}

class ItemMultitenant(BaseModel):
    produto_id: str
    quantidade: int

class RequisicaoCubagemLote(BaseModel):
    cep_destino: str
    valor_nf: Optional[float] = 0.0
    itens: List[ItemMultitenant]

@app.get("/api/produtos")
def listar_produtos():
    lista = [{"id": k, "nome": v["nome"]} for k, v in PRODUTOS_DB.items()]
    return sorted(lista, key=lambda x: x["id"] == "OUTROS")

# CORREÇÃO CRÍTICA: Rota do dólar revisada e limpa de erros de sintaxe
@app.get("/api/dolar")
def obter_cotacao_dolar():
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get("https://economia.awesomeapi.com.br/json/last/USD-BRL")
            if response.status_code == 200:
                dados = response.json()
                valor_dolar = float(dados["USDBRL"]["bid"])
                return {"cotacao": valor_dolar, "status": "sucesso"}
    except Exception as e:
        print(f"Erro ao buscar cotação: {e}")
    return {"cotacao": 5.00, "status": "fallback"}

@app.post("/api/sugerir-caixa")
def sugerir_caixa(req: RequisicaoCubagemLote):
    itens_validos = [i for i in req.itens if i.produto_id != ""]
    if not itens_validos:
        raise HTTPException(status_code=400, detail="Nenhum produto selecionado.")
    
    peso_total_produtos_g = 0
    caixa_sugerida_id = "1"
    possui_lumini = False
    
    for item in itens_validos:
        prod_id = item.produto_id
        if prod_id == "W16":
            possui_lumini = True
            
        produto = PRODUTOS_DB.get(prod_id, PRODUTOS_DB["OUTROS"])
        qtd = item.quantidade
        peso_total_produtos_g += (produto["peso_g"] * qtd)
        
        for c_id in ["1", "2", "3", "4", "5", "6"]:
            limite_max = produto["max_por_caixa"].get(c_id, 9999)
            if qtd <= math.floor(float(limite_max)):
                if int(c_id) > int(caixa_sugerida_id):
                    caixa_sugerida_id = c_id
                break
        else:
            caixa_sugerida_id = "5"

    # TRAVA DE ENGENHARIA DA LUMINI (CX 6 é exclusiva)
    if caixa_sugerida_id == "6" and not possui_lumini:
        caixa_sugerida_id = "5"
    elif possui_lumini and caixa_sugerida_id == "5":
        caixa_sugerida_id = "6"

    dados_caixa = MATRIZ_CAIXAS[caixa_sugerida_id]
    peso_final_com_caixa_g = peso_total_produtos_g + dados_caixa["peso_vazia_g"]
    
    # Regra financeira do seguro da Nota Fiscal
    nf_limpa = req.valor_nf if req.valor_nf else 0.0
    taxa_nf = 100.00 if nf_limpa > 10000.00 else (nf_limpa * 0.01)

    prefixo_cep = int(req.cep_destino.replace("-","")[:2]) if len(req.cep_destino) >= 2 else 10
    base = 24.50 if prefixo_cep < 40 else 48.00
    
    valor_final_frete = base + ((peso_final_com_caixa_g/1000) * 3.50) + taxa_nf

    return {
        "caixa_sugerida": dados_caixa["nome"],
        "dimensoes_ordem_correios": f"Altura: {math.ceil(dados_caixa['altura'])} cm | Largura: {math.ceil(dados_caixa['largura'])} cm | Comprimento: {math.ceil(dados_caixa['comprimento'])} cm",
        "cx_l_a": f"{math.ceil(dados_caixa['comprimento'])}x{math.ceil(dados_caixa['largura'])}x{math.ceil(dados_caixa['altura'])} cm",
        "dim_dados": {"c": math.ceil(dados_caixa['comprimento']), "l": math.ceil(dados_caixa['largura']), "a": math.ceil(dados_caixa['altura'])},
        "peso_total_g": peso_final_com_caixa_g,
        "caixa_id": caixa_sugerida_id,
        "preco_estimado": f"{valor_final_frete:.2f}".replace(".", ","),
        "origem": CEP_ORIGEM_PADRAO,
        "endereco_origem": ENDERECO_ORIGEM,
        "valor_nf_formatado": f"R$ {nf_limpa:.2f}".replace(".", ",")
    }

if __name__ == "__main__":
    import uvicorn
    import os
    # O Render vai injetar a porta correta aqui. Se não achar, usa a 8000 como segurança local.
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=porta, reload=False)
