# REPORT_BQ_TO_GMAIL

Este script Python automatiza a geração e envio de relatórios utilizando dados extraídos de um banco de dados BigQuery, formatando-os em um arquivo Excel e enviando-o por e-mail. A configuração é gerenciada através de um arquivo `config.ini`.

## Bibliotecas Utilizadas

- **google.oauth2.service_account**: Para autenticação com o Google Cloud usando credenciais de serviço.
- **pandas**: Para manipulação de dados e conversão de consultas SQL em DataFrame.
- **locale**: Para configuração de localidade (formatação de números e datas).
- **datetime, timedelta**: Para manipulação de datas.
- **functions as fn**: Módulo personalizado para funções auxiliares.
- **query_list as query**: Módulo personalizado contendo a query SQL.
- **configparser**: Para leitura e manipulação do arquivo de configuração `config.ini`.

## Configuração da Localidade

`````python
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
``````
-Define a localidade para formatação de números e datas no formato dos Estados Unidos.

## Leitura do Arquivo de Configuração (config.ini)

- O arquivo **config.ini** contém configurações necessárias para o envio de e-mails e geração de relatórios.<br>
- Utiliza o ConfigParser para ler e extrair as configurações.<br>
## Sessões do Arquivo config.ini
````ini
[mail_config]
intervalo: Intervalo em dias para captação de dados.
smtp_server: Servidor SMTP para envio de e-mails.
smtp_port: Porta do servidor SMTP.
sender_email: Endereço de e-mail do remetente.
receiver_email: Lista de destinatários.
subject: Assunto do e-mail.
[report_config]
nomes_colunas: Nomes personalizados para as colunas do relatório.
file_name: Nome do arquivo Excel gerado.
colunas_data: Colunas que contêm datas.
[credentials]
smtp_password: Senha do e-mail do remetente.
credentials_path: Caminho para o arquivo de credenciais do Google Cloud.
````
## Manipulação de Datas
O script calcula a data atual e subtrai um intervalo definido no arquivo de configuração para gerar a data inicial do relatório.<br>
````python
data_atual = datetime.now()
data_subtraida = data_atual - timedelta(days=int(intervalo))
````
-As datas são formatadas em dois formatos: um para o padrão internacional (YYYY-MM-DD) e outro para o padrão brasileiro (DD-MM-YYYY).

## Configurações de E-mail
-Saudação: Mensagem de saudação personalizada.<br>
-Assunto: O assunto do e-mail é ajustado para incluir a data atual.<br>
-Corpo do e-mail: A mensagem é montada dinamicamente para incluir a data do relatório.<br>
## Autenticação no Google Cloud
Autenticação utilizando o arquivo de credenciais:
````python
credentials = service_account.Credentials.from_service_account_file(
    filename=credentials_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
````
## Extração de Dados do BigQuery
A query SQL é executada e os dados são armazenados em um DataFrame:
````python
dados = pd.read_gbq(credentials=credentials, query=query.report_query)
````
## Ajustes no DataFrame
- Renomeação de Colunas: As colunas do DataFrame são renomeadas de acordo com os nomes personalizados definidos no arquivo config.ini.
````python
dados_ajustados = fn.rename_columns(df=dados, new_column_names=nomes_colunas)
````
- Remoção de Timezones (opcional): Função para remover timezones de colunas de datas, se necessário.<br>
- Ajuste de Tipos de Dados (opcional): Funções para ajustar colunas do tipo Timestamp e colunas numéricas.<br>

## Geração do Arquivo Excel
O DataFrame ajustado é salvo como um arquivo Excel no diretório temp:
````python
fn.ajusta_xls(excel_filename=file_name, df=dados_ajustados)
````
## Envio do E-mail
O arquivo Excel é enviado por e-mail utilizando as configurações definidas no config.ini:
````python
fn.envia_mail(sender_email, receiver_email, excel_filename,
              smtp_server, smtp_port, subject, body=mensagem_mail)
````
## Considerações Finais

Este script é flexível e pode ser adaptado para diferentes necessidades de relatório, bastando ajustar as configurações no arquivo config.ini e as funções auxiliares no módulo functions.py.
