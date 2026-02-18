import streamlit as st
import json
from datetime import datetime

#ARQUIVO_LICENCAS = "data/licencas.json"
import os
ARQUIVO_LICENCAS = os.path.join(os.path.dirname(__file__), "data", "licencas.json")


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


def validar_token(token: str):
    licencas = carregar_licencas()
    dados = licencas.get(token)

    if not dados:
        return {"status": "invalido", "motivo": "Token não encontrado"}

    # valida expiração
    hoje = datetime.now().date()
    try:
        expira_em = datetime.strptime(dados["expira_em"], "%Y-%m-%d").date()
    except Exception:
        return {"status": "erro", "motivo": "Data de expiração inválida"}

    if dados.get("status") != "ativo":
        return {"status": "inativo", "motivo": "Licença desativada"}

    if hoje > expira_em:
        return {"status": "expirado", "motivo": "Licença expirada"}

    return {
        "status": "ativo",
        "cliente": dados.get("cliente"),
        "expira_em": dados.get("expira_em"),
    }


def modo_api():
    st.set_page_config(page_title="API Licenciamento", layout="centered")
    st.title("API de Licenciamento")

    query_params = st.query_params
    token = query_params.get("token", [None])[0]

    if not token:
        st.json({"erro": "Informe ?token=SEU_TOKEN na URL"})
        return

    resultado = validar_token(token)
    st.json(resultado)


def modo_painel():
    st.set_page_config(page_title="Painel de Licenças", layout="wide")
    st.title("Painel de Licenciamento do Robô")

    licencas = carregar_licencas()

    aba = st.sidebar.radio("Menu", ["Licenças", "Nova licença", "Editar/Remover"])

    if aba == "Licenças":
        st.subheader("Licenças cadastradas")
        if not licencas:
            st.info("Nenhuma licença cadastrada ainda.")
        else:
            linhas = []
            for token, dados in licencas.items():
                linhas.append(
                    {
                        "token": token,
                        "cliente": dados.get("cliente", ""),
                        "expira_em": dados.get("expira_em", ""),
                        "status": dados.get("status", ""),
                        "obs": dados.get("obs", ""),
                    }
                )
            st.dataframe(linhas, use_container_width=True)

    elif aba == "Nova licença":
        st.subheader("Cadastrar nova licença")

        cliente = st.text_input("Nome do cliente")
        token = st.text_input("Token (chave da licença)")
        expira_em = st.date_input("Data de expiração")
        status = st.selectbox("Status", ["ativo", "inativo"])
        obs = st.text_area("Observações", "")

        if st.button("Salvar licença"):
            if not token:
                st.error("Token não pode ser vazio.")
            else:
                licencas[token] = {
                    "cliente": cliente,
                    "expira_em": expira_em.strftime("%Y-%m-%d"),
                    "status": status,
                    "obs": obs,
                }
                salvar_licencas(licencas)
                st.success(f"Licença {token} salva com sucesso!")

    elif aba == "Editar/Remover":
        st.subheader("Editar ou remover licença")

        if not licencas:
            st.info("Nenhuma licença para editar.")
            return

        tokens = list(licencas.keys())
        token_sel = st.selectbox("Selecione o token", tokens)

        dados = licencas[token_sel]
        cliente = st.text_input("Nome do cliente", value=dados.get("cliente", ""))
        expira_em_str = dados.get("expira_em", "2026-12-31")
        try:
            expira_em = datetime.strptime(expira_em_str, "%Y-%m-%d").date()
        except Exception:
            expira_em = datetime.now().date()

        expira_em_novo = st.date_input("Data de expiração", value=expira_em)
        status = st.selectbox(
            "Status", ["ativo", "inativo"], index=0 if dados.get("status") == "ativo" else 1
        )
        obs = st.text_area("Observações", value=dados.get("obs", ""))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Salvar alterações"):
                licencas[token_sel] = {
                    "cliente": cliente,
                    "expira_em": expira_em_novo.strftime("%Y-%m-%d"),
                    "status": status,
                    "obs": obs,
                }
                salvar_licencas(licencas)
                st.success("Licença atualizada.")

        with col2:
            if st.button("Remover licença"):
                del licencas[token_sel]
                salvar_licencas(licencas)
                st.warning("Licença removida.")


# Roteamento simples: se tiver ?api=1 na URL, entra em modo API
query_params_root = st.query_params
if query_params_root.get("api", ["0"])[0] == "1":
    modo_api()
else:
    modo_painel()
