from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    is_superuser = Column(Boolean, default=False)

######################### PRODUCTOS RELATED ################################
class ProductoDB(Base):
    __tablename__="productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio = Column(Float)
    tipo = Column(String)

    __mapper_args__ = {
        "polymorpthic_identity": "producto"
        "polymorpthic_on": tipo
    }

class LibroDB(ProductoDB):
    autor = Column(String, nullable=True) 
    paginas = Column(Integer, nullable=True) 
    
    __mapper_args__ = {"polymorphic_identity": "libro"}

class Tecnologia(ProductoDB):
    marca = Column(String, nullable=True)
    modelo = Column(String, nullable=True)

    __mapper_args_ = {"polymorphic_identity": "tecnologia"}

class RopaDB(ProductoDB):
    talla = Column(String, nullable=True)
    color = Column(String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "ropa"}


