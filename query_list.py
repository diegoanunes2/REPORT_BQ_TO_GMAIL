# ====================================================#
# ================ Query do relatorio ================#
# ====================================================#
# Aqui se passa a query do BQ entre aspas triplas, Obs: testar antes no Bigquery

report_query = f'''
SELECT 
CAMPO1,
CAMPO2,
CAMPO3
FROM tabela_teste
WHERE CAMPO1 IS NOT NULL
'''
