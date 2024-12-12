# Google Sheets to DynamoDB Integration

Este projeto foi desenvolvido para integrar planilhas do Google Drive ao DynamoDB de forma automatizada. Ele identifica todas as planilhas em uma pasta específica no Google Drive, cria tabelas no DynamoDB e insere os dados contidos nas planilhas. 

## Funcionalidades
- **Listagem de planilhas:** Localiza todas as planilhas em uma pasta específica do Google Drive.
- **Criação de tabelas no DynamoDB:** Cria tabelas baseadas nos nomes das planilhas com suporte à sanitização.
- **Inserção de dados:** Converte os dados das planilhas para string antes de inseri-los no DynamoDB.
- **Verificação de tabelas existentes:** Garante que apenas planilhas não inseridas previamente sejam processadas.
- **Mensagens informativas:** Exibe logs para cada etapa do processo, como tabelas criadas ou ignoradas.

## Pré-requisitos
- Python 3.10 ou superior.
- AWS CLI configurado com permissões para o DynamoDB.
- Arquivo de credenciais (`credenciais.json`) para o Google Drive e Google Sheets.

## Como usar
1. Clone este repositório:
   ```bash
   git clone https://github.com/usuario/sheets-to-dynamodb.git
   cd sheets-to-dynamodb


2. Configure um ambiente virtual:

python3 -m venv venv 
source venv/bin/activate   # No Windows: venv\Scripts\activate

3. Instalar Dependências:
Instale os pacotes necessários listados no arquivo requirements.txt.

pip install -r requirements.txt 

4. Configurar Credenciais do Google:
Crie ou forneça o arquivo credenciais.json com as credenciais do Google para acessar as APIs do Drive e Sheets.

5. Configurar Variáveis do Script:

DRIVE_FOLDER_NAME: Nome da pasta no Google Drive contendo as planilhas.
DYNAMODB_REGION: Região do DynamoDB onde as tabelas serão criadas.

6.  Executar o Script:
Execute o script para começar a transferência das planilhas para o DynamoDB:

python sheets_to_db.py 

7.  Desativar o Ambiente Virtual:
Quando terminar, desative o ambiente virtual:

deactivate 




