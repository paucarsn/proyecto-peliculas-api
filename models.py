from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class PeliculaDB(Base):
    __tablename__="peliculas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    año = Column(Integer)

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    is_superuser = Column(Boolean, default=False )