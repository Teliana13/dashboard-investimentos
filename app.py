import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

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

    # ======================================================
    # GRÁFICO DE PIZZA
    # ======================================================

    st.subheader("🥧 Distribuição da Carteira")

    fig_pizza = px.pie(
        resumo,
        names=col_categoria,
        values=col_valor,
        hole=0.4
    )
st.plotly_chart(fig_pizza, use_container_width=True)

    # ======================================================
    # GRÁFICO DE BARRAS
    # ======================================================

    st.subheader("📊 Comparação entre Categorias")

    fig_barra = px.bar(
        resumo,
        x=col_categoria,
        y=col_valor,
        text_auto='.2s'
    )

    st.plotly_chart(fig_barra, use_container_width=True)

    # ======================================================
    # TABELA DE PERCENTUAIS
    # ======================================================

    st.subheader("📌 Percentual da Carteira")

    resumo_exibicao = resumo.copy()

    resumo_exibicao["Percentual"] = (resumo_exibicao["Percentual"]
        .round(2)
        .astype(str) + "%"
    )

    resumo_exibicao[col_valor] = (
        resumo_exibicao[col_valor]
        .map(lambda x: f"R$ {x:,.2f}")
    )

    st.dataframe(resumo_exibicao)
 # ======================================================
    # REBALANCEAMENTO
    # ======================================================

    st.subheader("⚖️ Simulador de Rebalanceamento")

    st.markdown(
        "Defina um percentual alvo para cada categoria."
    )

    metas = {}

    for categoria in resumo[col_categoria]:
        metas[categoria] = st.number_input(
            f"Meta (%) para {categoria}",
            min_value=0.0,
            max_value=100.0,
            value=float(100 / resumo.shape[0]),
            step=1.0
        )

    if st.button("Calcular rebalanceamento"):

        rebalanceamento = resumo.copy()
 rebalanceamento["Meta (%)"] = (
            rebalanceamento[col_categoria]
            .map(metas)
        )

        rebalanceamento["Valor Ideal"] = (
            rebalanceamento["Meta (%)"] / 100
        ) * total

        rebalanceamento["Diferença"] = (
            rebalanceamento["Valor Ideal"] -
            rebalanceamento[col_valor]
        )

        def recomendacao(x):
            if x > 0:
                return "Comprar"
            elif x < 0:
                return "Reduzir"
            else:
                return "Balanceado"

        rebalanceamento["Ação"] = (
            rebalanceamento["Diferença"]
            .apply(recomendacao)
        )
st.dataframe(rebalanceamento)

        # ==================================================
        # GRÁFICO DE REBALANCEAMENTO
        # ==================================================

        fig_rebalanceamento = go.Figure()

        fig_rebalanceamento.add_trace(
            go.Bar(
                x=rebalanceamento[col_categoria],
                y=rebalanceamento[col_valor],
                name="Atual"
            )
        )

        fig_rebalanceamento.add_trace(
            go.Bar(
                x=rebalanceamento[col_categoria],
                y=rebalanceamento["Valor Ideal"],
                name="Ideal"
            )
        )

        st.plotly_chart(
            fig_rebalanceamento, use_container_width=True
        )

    # ======================================================
    # CONCENTRAÇÃO DA CARTEIRA
    # ======================================================

    st.subheader("🧠 Análise de Diversificação")

    maior = resumo.loc[
        resumo["Percentual"].idxmax()
    ]

    st.info(
        f"A maior concentração da carteira está em "
        f"{maior[col_categoria]} com "
        f"{maior['Percentual']:.2f}%"
    )
if maior['Percentual'] > 50:
        st.warning(
            "Sua carteira está muito concentrada. "
            "Considere diversificar mais os investimentos."
        )
    else:
        st.success(
            "Sua carteira possui uma boa diversificação."
        )

else:
    st.info("Envie sua planilha para iniciar a análise.")
