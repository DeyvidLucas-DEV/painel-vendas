import sqlite3
import pandas as pd

import sqlite3
import pandas as pd

def carregar_dados():
    conn = sqlite3.connect('dados/vendas_realistas.db')  # ajuste o caminho se necessário

    query = """
        SELECT
            f.data_venda,
            f.quantidade,
            f.valor_unitario,
            f.desconto_aplicado,
            f.status,
            f.meio_pagamento,
            c.nome AS cliente,
            c.estado AS estado,
            p.nome AS produto,
            p.categoria AS categoria,
            v.nome AS vendedor,
            v.equipe AS equipe
        FROM fato_vendas f
        JOIN dim_clientes c ON f.id_cliente = c.id_cliente
        JOIN dim_produtos p ON f.id_produto = p.id_produto
        JOIN dim_vendedores v ON f.id_vendedor = v.id_vendedor
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
