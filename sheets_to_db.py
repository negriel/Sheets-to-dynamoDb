import boto3
import os
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import pandas as pd

# Configuração
DRIVE_FOLDER_NAME = "Conversas Unificadas"
DYNAMODB_REGION = "us-west-1"
TABLE_NAME_PREFIX = "Tabela_"

# Credenciais e escopos para o Google Drive e Sheets
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "credenciais.json"

# Inicializa as credenciais
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=credentials)

# Função para sanitizar o nome da tabela
def sanitize_table_name(name):
    sanitized_name = re.sub(r"[^a-zA-Z0-9_-]", "", name)  # Remove caracteres inválidos
    return f"{TABLE_NAME_PREFIX}{sanitized_name}"

# Função para listar arquivos na pasta do Google Drive
def list_files_in_folder(folder_name):
    query = f"mimeType='application/vnd.google-apps.spreadsheet' and '{folder_name}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

# Função para baixar arquivos do Google Sheets e converter para DataFrame
def download_sheet_as_dataframe(file_id):
    sheet_service = build("sheets", "v4", credentials=credentials)
    try:
        result = sheet_service.spreadsheets().values().get(spreadsheetId=file_id, range="A1:Z1000").execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame()
        headers = values[0]
        rows = values[1:]
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        print(f"Erro ao acessar a planilha com ID {file_id}: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# Inicializa o cliente do DynamoDB
dynamodb = boto3.client("dynamodb", region_name=DYNAMODB_REGION)

# Função para verificar se a tabela já existe
def table_exists(table_name):
    try:
        response = dynamodb.describe_table(TableName=table_name)
        return True
    except dynamodb.exceptions.ResourceNotFoundException:
        return False

# Função para criar tabela no DynamoDB
def create_dynamodb_table(table_name, headers):
    partition_key = headers[0]
    
    # Criação da tabela
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": partition_key, "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": partition_key, "AttributeType": "S"},
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )
    print(f"Tabela {table_name} criada com sucesso no DynamoDB.")

# Função para converter e inserir itens na tabela DynamoDB
def insert_items_to_dynamodb(table_name, df):
    for _, row in df.iterrows():
        # Converte todos os dados para string antes de inserir no DynamoDB
        item = {key: {"S": str(value)} for key, value in row.items()}
        dynamodb.put_item(TableName=table_name, Item=item)
    print(f"Itens inseridos na tabela {table_name} com sucesso.")

# Fluxo principal
def main():
    # Busca a pasta no Google Drive
    results = drive_service.files().list(q=f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()
    folders = results.get("files", [])

    if not folders:
        print(f"Pasta '{DRIVE_FOLDER_NAME}' não encontrada.")
        return

    folder_id = folders[0]["id"]

    # Lista os arquivos na pasta
    files = list_files_in_folder(folder_id)

    if not files:
        print("Nenhuma planilha encontrada na pasta.")
        return

    for file in files:
        file_id = file["id"]
        file_name = file["name"]

        # Sanitiza o nome da tabela
        table_name = sanitize_table_name(file_name)

        # Verifica se a tabela já existe no DynamoDB
        if table_exists(table_name):
            print(f"A tabela {table_name} já existe. Ignorando a planilha {file_name}.")
            continue

        # Baixa e converte o arquivo para DataFrame
        df = download_sheet_as_dataframe(file_id)

        if df.empty:
            print(f"A planilha {file_name} está vazia. Ignorada.")
            continue

        # Cria a tabela no DynamoDB
        create_dynamodb_table(table_name, df.columns.tolist())

        # Insere os itens na tabela
        insert_items_to_dynamodb(table_name, df)

if __name__ == "__main__":
    main()

