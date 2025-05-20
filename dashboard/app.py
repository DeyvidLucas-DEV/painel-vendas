import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import plotly.express as px
from etl.transformacao import carregar_dados

# ✅ TÍTULO DA PÁGINA DO NAVEGADOR
st.set_page_config(
    page_title="Painel Analítico de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


df = carregar_dados()

st.title("Painel Analítico de Vendas")
aba = st.sidebar.selectbox("Selecione a aba:", ["📈 Vendas", "🛒 Produtos e Clientes", "📍 Relatórios"])

# 📈 Aba de Vendas
if aba == "📈 Vendas":
    st.markdown("## 📈 Análise de Vendas")
    st.markdown("---")
    df["valor_total"] = df["quantidade"] * df["valor_unitario"]

    vendedor_selecionado = st.selectbox("Selecione o Vendedor", df["vendedor"].unique())
    df_filtrado = df[df["vendedor"] == vendedor_selecionado]

    total_vendido = df_filtrado["valor_total"].sum()
    numero_vendas = len(df_filtrado)
    ticket_medio = total_vendido / numero_vendas if numero_vendas > 0 else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("💰 Total Vendido", f"R$ {total_vendido:,.2f}")
    k2.metric("🧾 Nº de Vendas", f"{numero_vendas}")
    k3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("### 📅 Vendas por Data")
    vendas_data = (
        df_filtrado.groupby("data_venda")["valor_total"]
        .sum()
        .reset_index()
        .sort_values("data_venda")
    )
    fig = px.bar(
        vendas_data,
        x="data_venda",
        y="valor_total",
        title=f"Vendas por Data - {vendedor_selecionado}",
        text_auto=True,
        template="plotly_white"
    )
    fig.update_layout(xaxis_title="Data", yaxis_title="Total Vendido (R$)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📄 Detalhamento das Vendas")
    st.dataframe(
        df_filtrado[[ "data_venda", "produto", "cliente", "quantidade", "valor_unitario",
                      "valor_total", "meio_pagamento", "status" ]].sort_values("data_venda", ascending=False),
        use_container_width=True,
        height=400
    )

# 🛒 Aba Produtos e Clientes
elif aba == "🛒 Produtos e Clientes":
    st.markdown("## 🛒 Produtos e Clientes")
    st.markdown("---")
    df["valor_total"] = df["quantidade"] * df["valor_unitario"]

    st.markdown("### 📌 Indicadores de Desempenho")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("💰 Total Vendido", f"R$ {df['valor_total'].sum():,.2f}")
    kpi2.metric("👥 Clientes Únicos", df["cliente"].nunique())
    kpi3.metric("📦 Produtos Vendidos", df["produto"].nunique())
    st.markdown("---")

    st.markdown("### 🏆 Top 5 Produtos Mais Vendidos")
    top_produtos = df.groupby("produto")["valor_total"].sum().nlargest(5).reset_index()
    fig_prod = px.bar(top_produtos, x="produto", y="valor_total", text_auto=True,
                      color="valor_total", title="Ranking de Produtos", template="plotly_white")
    fig_prod.update_layout(xaxis_title="Produto", yaxis_title="Receita Total (R$)")
    st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("### 👑 Top 5 Clientes por Receita")
    top_clientes = df.groupby("cliente")["valor_total"].sum().nlargest(5).reset_index()
    fig_cli = px.bar(top_clientes, x="cliente", y="valor_total", text_auto=True,
                     color="valor_total", title="Ranking de Clientes", template="plotly_white")
    fig_cli.update_layout(xaxis_title="Cliente", yaxis_title="Total Comprado (R$)")
    st.plotly_chart(fig_cli, use_container_width=True)

    st.markdown("### 💳 Ticket Médio por Produto")
    ticket_produto = (
        df.groupby("produto")[["valor_total", "quantidade"]]
        .sum()
        .assign(ticket_medio=lambda d: d["valor_total"] / d["quantidade"])
        .nlargest(5, "ticket_medio")
        .reset_index()
    )
    fig_ticket = px.bar(ticket_produto, x="produto", y="ticket_medio", text_auto=".2f",
                        color="ticket_medio", title="Produtos com Maior Ticket Médio", template="plotly_white")
    fig_ticket.update_layout(xaxis_title="Produto", yaxis_title="Ticket Médio (R$)")
    st.plotly_chart(fig_ticket, use_container_width=True)

    st.markdown("### 📄 Detalhamento das Vendas")
    st.dataframe(
        df[[ "data_venda", "cliente", "produto", "quantidade",
             "valor_unitario", "valor_total", "meio_pagamento", "status" ]].sort_values("data_venda", ascending=False),
        use_container_width=True,
        height=400
    )

# 📍 Aba Relatórios
elif aba == "📍 Relatórios":
    st.markdown("## 📍 Relatórios Estratégicos de Vendas")
    st.markdown("---")
    df["valor_total"] = df["quantidade"] * df["valor_unitario"]
    df["receita_liquida"] = df["valor_total"] - df["desconto_aplicado"]
    df["data_venda"] = pd.to_datetime(df["data_venda"])

    # 🎛️ Filtros interativos
    st.sidebar.markdown("## 🎛️ Filtros Avançados")
    vendedores = st.sidebar.multiselect("Vendedor", options=df["vendedor"].unique(), default=list(df["vendedor"].unique()))
    equipes = st.sidebar.multiselect("Equipe", options=df["equipe"].unique(), default=list(df["equipe"].unique()))
    categorias = st.sidebar.multiselect("Categoria", options=df["categoria"].unique(), default=list(df["categoria"].unique()))
    status = st.sidebar.multiselect("Status da Venda", options=df["status"].unique(), default=list(df["status"].unique()))
    data_inicio = st.sidebar.date_input("Data Inicial", df["data_venda"].min())
    data_fim = st.sidebar.date_input("Data Final", df["data_venda"].max())

    df_filtrado = df[
        (df["vendedor"].isin(vendedores)) &
        (df["equipe"].isin(equipes)) &
        (df["categoria"].isin(categorias)) &
        (df["status"].isin(status)) &
        (df["data_venda"] >= pd.to_datetime(data_inicio)) &
        (df["data_venda"] <= pd.to_datetime(data_fim))
    ]

    # KPIs
    total_receita = df_filtrado["receita_liquida"].sum()
    pedidos = len(df_filtrado)
    ticket_medio = total_receita / pedidos if pedidos > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Receita Total", f"R$ {total_receita:,.2f}")
    c2.metric("📦 Total de Pedidos", f"{pedidos}")
    c3.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        receita_categoria = df_filtrado.groupby("categoria")["receita_liquida"].sum().reset_index()
        fig1 = px.bar(receita_categoria, x="categoria", y="receita_liquida",
                      title="💼 Receita por Categoria de Produto", template="plotly_white",
                      color="receita_liquida", text_auto=".2s")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(df_filtrado, names="status", title="📊 Distribuição por Status da Venda", template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        receita_vendedor = df_filtrado.groupby("vendedor")["receita_liquida"].sum().reset_index()
        fig3 = px.bar(receita_vendedor.sort_values("receita_liquida", ascending=False),
                      x="vendedor", y="receita_liquida", title="🧑‍💼 Receita por Vendedor",
                      template="plotly_white", color="receita_liquida", text_auto=".2s")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        receita_pagamento = df_filtrado.groupby("meio_pagamento")["receita_liquida"].sum().reset_index()
        fig4 = px.bar(receita_pagamento, x="meio_pagamento", y="receita_liquida",
                      title="💳 Receita por Meio de Pagamento", template="plotly_white",
                      color="receita_liquida", text_auto=".2s")
        st.plotly_chart(fig4, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        receita_estado = df_filtrado.groupby("estado")["receita_liquida"].sum().reset_index()
        fig5 = px.bar(receita_estado, x="estado", y="receita_liquida",
                      title="🌎 Receita por Estado (Cliente)", template="plotly_white",
                      color="receita_liquida", text_auto=".2s")
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        receita_equipe = df_filtrado.groupby("equipe")["receita_liquida"].sum().reset_index()
        fig6 = px.bar(receita_equipe, x="equipe", y="receita_liquida",
                      title="🏅 Receita por Equipe de Vendas", template="plotly_white",
                      color="receita_liquida", text_auto=".2s")
        st.plotly_chart(fig6, use_container_width=True)
