import pandas as pd
import numpy as np

pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# =========================
# Leitura do arquivo
# =========================
df = pd.read_csv('cliente_remove_outliers.csv')

print("DataFrame original:\n", df.head())

# =========================
# CORREÇÃO 1 — Garantir que CPF seja string
# Motivo: evitar erro ao usar slicing (cpf[:3], cpf[-2:])
# =========================
df['cpf'] = df['cpf'].astype(str)

# =========================
# CORREÇÃO 2 — Máscara de CPF com validação mínima
# Motivo: evitar erro quando o CPF não tiver tamanho suficiente
# =========================
df['cpf_mascara'] = df['cpf'].apply(
    lambda cpf: f'{cpf[:3]}.***.***-{cpf[-2:]}' if len(cpf) >= 11 else 'CPF inválido'
)

# =========================
# Tratamento de Datas
# =========================

# CORREÇÃO 3 — Conversão robusta para datetime
# Motivo: erros anteriores no .dt eram consequência de NaT não tratados
df['data'] = pd.to_datetime(df['data'], format='%y-%m-%d', errors='coerce')

data_atual = pd.to_datetime('today')

# CORREÇÃO 4 — Padronização do nome da coluna
# Motivo: havia erros como "data_ataulizada" e "data_atualiozada"
df['data_atualizada'] = df['data']

# CORREÇÃO 5 — Tratamento explícito de NaT
# Motivo: .dt não funciona corretamente se houver valores nulos
df.loc[df['data_atualizada'].isna(), 'data_atualizada'] = pd.to_datetime('1900-01-01')

# CORREÇÃO 6 — Tratamento de datas futuras
df.loc[df['data_atualizada'] > data_atual, 'data_atualizada'] = pd.to_datetime('1900-01-01')

# =========================
# Cálculo da idade ajustada
# =========================

# CORREÇÃO 7 — Criação correta da coluna idade_ajustada
# Motivo: anteriormente a coluna era usada antes de ser criada
df['idade_ajustada'] = data_atual.year - df['data_atualizada'].dt.year

# CORREÇÃO 8 — Ajuste lógico do cálculo de aniversário
# Motivo: garantir que subtraia 1 quando o aniversário ainda não ocorreu
df['idade_ajustada'] -= (
    (data_atual.month < df['data_atualizada'].dt.month) |
    (
        (data_atual.month == df['data_atualizada'].dt.month) &
        (data_atual.day < df['data_atualizada'].dt.day)
    )
).astype(int)

# CORREÇÃO 9 — Remover idades irreais
df.loc[df['idade_ajustada'] > 100, 'idade_ajustada'] = np.nan

# =========================
# Tratamento de Endereço
# =========================

# CORREÇÃO 10 — Garantir que endereço seja string
# Motivo: evitar erro em split caso haja valores nulos
df['endereco'] = df['endereco'].astype(str)

# Endereço principal
df['endereco_curto'] = df['endereco'].apply(
    lambda x: x.split('\n')[0].strip() if '\n' in x else x.strip()
)

# Bairro
df['bairro'] = df['endereco'].apply(
    lambda x: x.split('\n')[1].strip() if len(x.split('\n')) > 1 else 'Desconhecido'
)

# CORREÇÃO 11 — Correção de método split e strip
# Motivo: havia erros como .spli() e .striop()
df['estado_sigla'] = df['endereco'].apply(
    lambda x: x.split(' / ')[-1].strip().upper() if ' / ' in x else 'Desconhecido'
)

# CORREÇÃO 12 — Correção de nome de coluna
# Motivo: havia colunas inexistentes como endereco_cuirto e endereco_ciurto
df['endereco_curto'] = df['endereco_curto'].apply(
    lambda x: 'Endereço inválido' if len(x) > 50 or len(x) < 5 else x
)

# =========================
# Validação de Estados
# =========================

estados_br = [
    'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS',
    'MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC',
    'SP','SE','TO'
]

# CORREÇÃO 13 — Validação final da sigla do estado
df['estado_sigla'] = df['estado_sigla'].apply(
    lambda x: x if x in estados_br else 'Desconhecido'
)

# =========================
# Construção do DataFrame Final
# =========================

# CORREÇÃO 14 — Organização explícita das colunas finais
df_final = pd.DataFrame({
    'nome': df['nome'],
    'cpf': df['cpf_mascara'],
    'idade': df['idade_ajustada'],
    'data': df['data'],
    'endereco': df['endereco_curto'],
    'bairro': df['bairro'],
    'estado': df['estado_sigla']
})

# Salvar CSV tratado
df_final.to_csv('clientes_tratados.csv', index=False)

print("\nDados tratados:\n", df_final.head())
print("\nArquivo salvo como clientes_tratados.csv")