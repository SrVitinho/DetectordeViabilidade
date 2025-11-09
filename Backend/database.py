from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

try:
    from keys import URL_DATABASE
except ImportError:
    print("AVISO: Arquivo 'keys.py' não encontrado. Certifique-se de que ele existe e contém a variável URL_DATABASE.")


engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass