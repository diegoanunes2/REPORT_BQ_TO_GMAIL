import pandas as pd
from datetime import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email import encoders
import smtplib
import locale


def saudacao():
    hora_atual = datetime.now().hour

    if 6 <= hora_atual < 12:
        return "Bom dia"
    elif 12 <= hora_atual < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

# =======================================================================##
# = Remove Timezone das Colunas Necessário para criar o xls com o pandas =#
# =======================================================================##


def remove_timezone(dados):

    for col in dados.columns:
        # Verifica se a coluna é de data e hora
        if pd.api.types.is_datetime64_any_dtype(dados[col]):
            dados[col] = dados[col].dt.tz_localize(
                None)  # Remove o fuso horário

    return dados

# =======================================#
# = Renomeia as colunas de um DataFrame =#
# =======================================#


def rename_columns(df, new_column_names):
    """
    Renomeia as colunas de um DataFrame.

    Parâmetros:
        dataframe (pandas.DataFrame): O DataFrame cujas colunas serão renomeadas.
        new_column_names (list): Uma lista contendo os novos nomes das colunas na ordem correspondente.

    Retorna:
        pandas.DataFrame: O DataFrame com as colunas renomeadas.
    """
    df.columns = new_column_names
    return df


# Ajusta Xls

def ajusta_xls(excel_filename, df):
    writer = pd.ExcelWriter(excel_filename, engine='xlsxwriter')
    # Salvar o DataFrame no Excel
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    # Obter a instância do objeto Workbook da biblioteca XlsxWriter
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    ## =====================================================================##
    # Ajustar automaticamente a largura das colunas
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).apply(len).max(), len(col))
        worksheet.set_column(i, i, max_len + 4)  # Adicione um espaço extra
    # Salvar o arquivo Excel
    writer.close()
    print(f'DataFrame salvo em {excel_filename} com sucesso.')
    return excel_filename

# =============================================================#
# ===== Função para ajuste dos tipos de dados das colunas =====#
# ======================== (String) ===========================#
# =============================================================#


def adjust_type_string(column, df):
    if not df.empty:
        if column in df.columns:
            df[column] = df[column].astype("str", errors='ignore')
        else:
            df[column] = ''
            df[column] = df[column].astype("str", errors='ignore')
    else:
        print(f"Dataframe {df} Vazio, não será ajustado")


# =============================================================#
# ===== Função para ajuste dos tipos de dados das colunas =====#
# ====================== (Timestamp - Day First) ==========================#
# =============================================================#


def adjust_type_timestamp(column, df):
    if not df.empty:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column], dayfirst=True, errors='coerce')
        else:
            df[column] = pd.NaT
            df[column] = pd.to_datetime(
                df[column], dayfirst=True, errors='coerce')
    else:
        print(f"Dataframe {df} Vazio, não será ajustado")

# ===========================================================#
# ===========Função para converter o formato de Moeda =======#
# ===========================================================#

def converter_formato(valor):
    valor_float = float(valor)
    valor_formatado = locale.currency(valor_float, grouping=True, symbol=False)
    valor_formatado = valor_formatado.replace('R$', '').strip()
    return valor_formatado

# Envia Mail

def envia_mail(sender_email, receiver_email, excel_filename, smtp_server, smtp_port, subject, body):
    # Configurando o MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_email)
    msg['Subject'] = subject
    # Adicionando corpo ao email
    msg.attach(MIMEText(body, 'plain'))

    # Anexando a planilha
    # Caminho real da planilha
    path = excel_filename
    # Abre o arquivo para ser usado no python
    attachment = open(path, 'rb')
    # Configura o Base
    part = MIMEBase('application', 'octet-stream')
    # Lê o anexo que foi aberto
    part.set_payload(attachment.read())
    # Codificação do email
    encoders.encode_base64(part)
    # Adiciona o Anexo ao header
    part.add_header('Content-Disposition', f'attachment; filename= {path}')
    # Adiciona o Anexo
    msg.attach(part)

    # Configuração da conexão SMTP e envio do e-mail
    server = smtplib.SMTP(smtp_server, smtp_port)
    # Conectar-se explicitamente ao servidor SMTP
    server.connect(smtp_server, smtp_port)
    server.sendmail(sender_email, receiver_email, msg.as_string())

    # Encerrando a conexão
    server.quit()
    if os.path.exists(path):
        os.remove(path)
        print(f'Arquivo {path} removido com sucesso.')
    else:
        print(f'O arquivo {path} não existe ou já foi removido anteriormente.')

    print('Email enviado com sucesso!')
