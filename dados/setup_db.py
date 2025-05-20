import sqlite3
import pandas as pd

# Caminho do banco
conn = sqlite3.connect('dados/vendas_realistas.db')  # Caminho e nome atualizados

# Carregar CSVs
clientes = pd.read_csv('dados/dim_clientes.csv')
produtos = pd.read_csv('dados/dim_produtos.csv')
vendedores = pd.read_csv('dados/dim_vendedores.csv')
fornecedores = pd.read_csv('dados/dim_fornecedores.csv')
vendas = pd.read_csv('dados/fato_vendas.csv')


# Criar tabelas no banco
clientes.to_sql('dim_clientes', conn, index=False, if_exists='replace')
produtos.to_sql('dim_produtos', conn, index=False, if_exists='replace')
vendedores.to_sql('dim_vendedores', conn, index=False, if_exists='replace')
vendas.to_sql('fato_vendas', conn, index=False, if_exists='replace')

conn.close()
print("✅ Banco populado com sucesso.")
