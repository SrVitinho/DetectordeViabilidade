from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


try:
    from keys import dbKey
except ImportError:
    print("AVISO: Arquivo 'keys.py' não encontrado. Usando senha padrão 'admin'.")
    print("Crie 'keys.py' com 'dbKey = \"sua_senha\"' na raiz do projeto.")
    dbKey = "admin"
    
URL_DATABASE = f'mysql+pymysql://root:{dbKey}@localhost:3306/detectordeviabilidade'
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass