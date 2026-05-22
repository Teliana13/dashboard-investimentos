import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Dashboard de Investimentos",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# TÍTULO
# ==========================================================

st.title("📊 Dashboard de Investimentos")
st.markdown("Análise de carteira, diversificação e rebalanceamento")

# ==========================================================
# UPLOAD DA PLANILHA
# ==========================================================

arquivo = st.file_uploader(
    "Faça upload da sua planilha Excel",
    type=["xlsx"]
)

if arquivo is not None:

    # ======================================================
    # LEITURA DOS DADOS
    # ======================================================

    df = pd.read_excel(arquivo)

    st.subheader("📋 Dados carregados")
    st.dataframe(df)

    # ======================================================
    # LIMPEZA DOS DADOS
    # ======================================================

    df.columns = [str(col).strip() for col in df.columns]

    # Detecta colunas automaticamente
    col_categoria = None
    col_ativo = None
    col_valor = None

    for col in df.columns:

        nome = col.lower()

        if "categoria" in nome or "classe" in nome:
            col_categoria = col

        if "ativo" in nome or "invest" in nome:
            col_ativo = col

        if "valor" in nome:
            col_valor = col

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if col_categoria is None or col_valor is None:
        st.error("Não foi possível identificar as colunas principais da planilha.")
        st.stop()

    # ======================================================
    # TRATAMENTO
    # ======================================================

    df = df[[col_categoria, col_valor]].copy()

    df = df.dropna()

    df[col_valor] = (
        df[col_valor]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")

    df = df.dropna()

    # ======================================================
    # AGRUPAMENTO
    # ======================================================

    resumo = (
        df.groupby(col_categoria)[col_valor]
        .sum()
        .reset_index()
    )

    total = resumo[col_valor].sum()

    resumo["Percentual"] = (
        resumo[col_valor] / total * 100
    )

    # ======================================================
    # MÉTRICAS
    # ======================================================

    st.subheader("💰 Resumo Geral")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Patrimônio Total",
            f"R$ {total:,.2f}"
        )

    with col2:
        st.metric(
            "Número de Categorias",
            resumo.shape[0]
        )

else:
    st.info("Envie sua planilha para iniciar a análise.")
