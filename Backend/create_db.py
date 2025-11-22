from database import Base, engine
from models import User

print("Iniciando a criação das tabelas no banco de dados...")
print(f"Conectando ao banco de dados com o engine: {engine.url}")

try:    
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")