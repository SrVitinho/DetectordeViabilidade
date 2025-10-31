import os

URL_DATABASE = "mssql+pyodbc://SEU_SERVIDOR/SEU_BANCO_DE_DADOS?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

SECRET_KEY = os.environ.get('SECRET_KEY', 'SUA_CHAVE_SECRETA_SUPER_DIFICIL_AQUI ')

ALGORITHM = 'XXXXX'