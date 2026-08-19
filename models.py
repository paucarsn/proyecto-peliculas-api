from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

######################### USUARIOS RELATED ################################

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
    stock = Column(Integer)
    tipo = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "producto",
        "polymorphic_on": tipo
    }

class Libro(ProductoDB):
    autor = Column(String, nullable=True) 
    paginas = Column(Integer, nullable=True) 
    
    __mapper_args__ = {"polymorphic_identity": "libro"}

class Tecnologia(ProductoDB):
    marca = Column(String, nullable=True)
    modelo = Column(String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "tecnologia"}

class Ropa(ProductoDB):
    talla = Column(String, nullable=True)
    color = Column(String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "ropa"}

######################### PEDIDOS RELATED ################################

class CarritoDB(Base):
    __tablename__ = "carrito"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True, nullable=False)
    producto = Column(String)
    precio = Column(Float)
    estado = Column(String) # Carrito/Comprado/Entregado->(no creo que se implemente)
