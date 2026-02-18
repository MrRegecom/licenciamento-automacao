import streamlit as st
import json
from datetime import datetime
import os

# Caminho absoluto para o arquivo de licenças
ARQUIVO_LICENCAS = os.path.join(os.path.dirname(__file__), "data", "licencas.json")

# -----------------------------
# FUNÇÕES DE LICENCIAMENTO
# -----------------------------

def carregar_licencas():
    try:
        with open(ARQUIVO_LICENCAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def salvar_licencas(licencas):
    with open(ARQUIVO_LICENCAS, "w", encoding="utf-8") as f:
        json.dump(licencas, f, ensure_ascii=False, indent=2)

# Carrega o JSON logo no início
licencas = carregar_licencas()

# -----------------------------
# MODO API
# -----------------------------

def modo_api():
    st.title("API de Licenciamento")

    query = st.query_params
    token = query.get("token", [""])[0]

    if not token:
        st.json({"status": "erro", "motivo": "Token não informado"})
        return

    lic = licencas.get(token)

    if not lic:
        st.json({"status": "invalido", "motivo": "Token não encontrado"})
        return

    # Verifica expiração
    hoje = datetime.now().date()
    expira = datetime.strptime(lic["expira_em"], "%Y-%m-%d").date()

    if expira < hoje:
        st.json({"status": "expirado", "motivo": "Licença expirada"})
        return

    # Licença válida
    st.json({
        "status": "ativo",
        "cliente": lic["cliente"],
        "expira_em": lic["expira_em"]
    })

# -----------------------------
# MODO PAINEL
# -----------------------------

def modo_painel():
    st.title("Painel de Licenciamento")

    st.subheader("Licenças cadastradas")
    st.json(licencas)

    st.subheader("Adicionar nova licença")

    novo_token = st.text_input("Token")
    novo_cliente = st.text_input("Cliente")
    nova_data = st.date_input("Data de expiração")

    if st.button("Salvar"):
        licencas[novo_token] = {
            "cliente": novo_cliente,
            "expira_em": nova_data.strftime("%Y-%m-%d"),
            "status": "ativo"
        }
        salvar_licencas(licencas)
        st.success("Licença salva com sucesso!")

# -----------------------------
# ROTEAMENTO ENTRE API E PAINEL
# -----------------------------

query_root = st.query_params
if query_root.get("api", ["0"])[0] == "1":
    modo_api()
else:
    modo_painel()
