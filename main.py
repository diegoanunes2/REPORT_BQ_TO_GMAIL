# =============================#
#    Bibliotecas utilizadas   #
# =============================#
from google.oauth2 import service_account
import pandas as pd
import locale
from datetime import datetime, timedelta
import functions as fn
import query_list as query
# import config as cf
from configparser import ConfigParser

# seta codificação da biblioteca locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# ===========================================#
# === Ler os dados do arquivo config.ini  ===#
# ===========================================#

# Inicializa o ConfigParser sem interpolação
config = ConfigParser(interpolation=None)

# Le o arquivo e passa a codificação UTF-8
config.read('config.ini', encoding='utf-8')

# Cria as variaveis com as informações do config.ini
# Sessão [mail_config]
# intervalo para captação de dados exemplo 90 dias para tras apartir de hoje

intervalo = config.get('mail_config', 'intervalo')
smtp_server = config.get('mail_config', 'server')
smtp_port = config.get('mail_config', 'port')
sender_email = config.get('mail_config', 'sender')
smtp_username = config.get('mail_config', 'sender')
receiver_email = config['mail_config']['destinatarios'].split(',')
subject = config.get('mail_config', 'assunto_mail')

# Sessão [report_config]
nomes_colunas = config['report_config']['nomes_colunas'].split(',')
file_name = config.get('report_config', 'file_name')
colunas_data = config.get('report_config', 'colunas_data')

# Sessão [credentials]
smtp_password = config.get('credentials', 'sender_password')
credentials_path = config.get('credentials', 'gbq_token')

# =============================================================#
# =========================== Datas ===========================#
# =============================================================#

data_atual = datetime.now()  # Data atual

# Subtrair N dias de uma data *usando a variavel intervalo definida no inicio
data_subtraida = data_atual - timedelta(days=int(intervalo))

data_subtraida_formatada = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
    data_subtraida.year, data_subtraida.month, data_subtraida.day, data_subtraida.hour, data_subtraida.minute, data_subtraida.second)

data_atual_formatada = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
    data_atual.year, data_atual.month, data_atual.day, data_atual.hour, data_atual.minute, data_subtraida.second)

data_subtraida_formatada_br = '{:02d}-{:02d}-{:04d}'.format(
    data_subtraida.day, data_subtraida.month, data_subtraida.year)

data_atual_formatada_br = '{:02d}-{:02d}-{:04d}'.format(
    data_atual.day, data_atual.month, data_atual.year)

# =========================================#
#         Configurações do E-mail         #
# =========================================#
# cria a mensagem de saudação
saudacao = fn.saudacao()

# ajusta a data no assunto
subject = f'{subject} - {data_atual_formatada_br}'

# aqui se passa a mensagem do corpo do email, usar quebra de linha \n e injetar variaveis conforme necessário
mensagem_mail = f'{saudacao},\nSegue relatório em anexo referente ao dia {data_atual_formatada_br}'

# Mensagem do corpo do E-mail Dinamica
# mensagem_mail = f'{saudacao},\nSegue relatório em anexo.'
body = mensagem_mail
# Nome e local do xls gerado
file_name = f'{file_name}{data_atual_formatada_br}.xlsx'
file_path = f'temp/{file_name}'
excel_filename = file_name

credentials = service_account.Credentials.from_service_account_file(
    filename=credentials_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])

# ===========================#
#   Recebe os dados do BQ   #
# ===========================#

# Executa a chamada de api solicitando os dados daquery e adiciona na variavel dados
dados = pd.read_gbq(credentials=credentials, query=query.report_query)

# ===============================#
# Converte o SQL para Dataframe #
# ===============================#

dados = pd.DataFrame(dados)  # transforma a variavel dados em um Dataframe

## Descomente caso necessário ##

# ===============================#
# Remove os Timezones das datas #
# ===============================#

# fn.remove_timezone(dados=dados)

# ===================(Timestamp)====================
# if not colunas_data:
# print("Lista de dados do tipo Timestamp vazia")
# else:
# for coluna in colunas_data:
# fn.adjust_type_timestamp(column=coluna, df=dados)
# print("Dados Timestamp ajustados com Sucesso!")
#
# dados.to_csv('teste.csv')
# ===============================#
#  Ajusta as colunas de valores #
# ===============================#
# if not colunas_float:
# print("Sem colunas a ajustar")
# else:
# for coluna in colunas_float:
# dados[coluna] = dados[coluna].apply(fn.converter_formato)

# ===============================#
#  Ajusta os nomes de colunas   #  # Para personalizar ex NR_PROCESSO > Numero Processo, pois se puxar direto do banco não tem espaços nem formatações
# ===============================#

dados_ajustados = fn.rename_columns(df=dados, new_column_names=nomes_colunas)

# ===============================#
#    Ajusta o XLS para envio    #
# ===============================#
fn.ajusta_xls(excel_filename=file_name, df=dados_ajustados)

# ===============================#
#        Enviando o email       #  Passar os parametros que constam no arquivo config.py
# ===============================#  São eles remetente, destinatario,nome do arquivo, servidor smtp, porta smtp, assunto e o corpo do email

fn.envia_mail(sender_email, receiver_email, excel_filename,
              smtp_server, smtp_port, subject, body=mensagem_mail)
