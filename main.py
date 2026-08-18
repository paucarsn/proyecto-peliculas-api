from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import UsuarioDB, ProductoDB, Libro, Tecnologia, Ropa
from auth import hash_password, verificar_password, crear_token, obtener_usuario_actual, obtener_superusuario_actual
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, Literal, Annotated

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductoBase(BaseModel):
    nombre: str
    precio: float



class ProductoRopa(ProductoBase):
    tipo: Literal["ropa"]
    talla: str
    color: str

class ProductoTecnologia(ProductoBase):
    tipo: Literal["tecnologia"]
    marca: str
    modelo: str

class ProductoLibro(ProductoBase):
    tipo: Literal["libro"]
    autor: str
    paginas: int

class Usuario(BaseModel):
    username: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

######################### PRODUCTOS RELATED ################################

@app.get("/productos")
def obtener_productos(db: Session = Depends(get_db), usuario:str = Depends(obtener_usuario_actual)):
    return db.query(ProductoDB).all()
   
@app.get("/productos/{id}")
def obtener_producto(id: int, db: Session = Depends(get_db), usuario:str = Depends(obtener_usuario_actual)):
    producto = db.query(ProductoDB).filter(ProductoDB.id == id).first()
    if producto:
        return producto
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado")

@app.post("/productos")
def agregar_producto(producto: producto: Annotated[
        Union[
            ProductoRopa,
            ProductoTecnologia,
            ProductoLibro
        ],
        Body(discriminator="tipo")
    ], db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):

    nuevo_producto = ProductoDB(nombre=producto.nombre, precio=producto.precio, tipo=producto.tipo)
    tipo = producto.tipo.lower()
    if tipo == "ropa":
        nuevo_producto = Ropa(
            nombre=producto.nombre,
            precio=producto.precio,
            tipo="ropa",
            talla=producto.talla,
            color=producto.color)

    elif tipo == "tecnologia":
        nuevo_producto = Tecnologia(
            nombre=producto.nombre,
            precio=producto.precio,
            tipo="tecnologia",
            marca=producto.marca,
            modelo=producto.modelo)

    elif tipo == "libro":
        nuevo_producto = Libro(
            nombre=producto.nombre,
            precio=producto.precio,
            tipo="libro",
            autor=producto.autor,
            paginas=producto.paginas)
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Tipo de producto no valido")

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

@app.delete("/productos/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):
    producto = db.query(ProductoDB).filter(ProductoDB.id == id).first()
    if producto:
        db.delete(producto)
        db.commit()
        return {"mensaje": "Producto eliminado"}
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado")

@app.put("/productos/{id}")
def editar_producto(id: int, producto_actualizado: ProductoRequest, db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):
    producto = db.query(ProductoDB).filter(ProductoDB.id == id).first()

    if not producto:
        raise HTTPException(
        status_code=404,
        detail="Producto no encontrado")

    tipo = producto.tipo
    if tipo=="ropa":
        producto.nombre = producto_actualizado.nombre
        producto.precio = producto_actualizado.precio
        producto.talla = producto_actualizado.talla
        producto.color = producto_actualizado.color

        db.commit()
        db.refresh(producto)
        return producto

    elif tipo=="tecnologia":
        producto.nombre = producto_actualizado.nombre
        producto.precio = producto_actualizado.precio
        producto.marca = producto_actualizado.marca
        producto.modelo = producto_actualizado.modelo

        db.commit()
        db.refresh(producto)
        return producto

    elif tipo=="libro":
        producto.nombre = producto_actualizado.nombre
        producto.precio = producto_actualizado.precio
        producto.autor = producto_actualizado.autor
        producto.paginas = producto_actualizado.paginas

        db.commit()
        db.refresh(producto)
        return producto
    else:
        raise HTTPException(
            status_code=400,
            detail="Tipo de producto no válido"
        )

######################### USER RELATED ################################

@app.post("/registro")
def registro(usuario: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first()
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Usuario ya existente")

    nuevo_usuario = UsuarioDB(
        username=usuario.username,
        hashed_password=hash_password(usuario.password),
        is_superuser=False
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Usuario creado correctamente"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario_db = db.query(UsuarioDB).filter(UsuarioDB.username == form_data.username).first()

    if not usuario_db or not verificar_password(form_data.password, usuario_db.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrecto")

    token = crear_token({"sub": usuario_db.username})
    return {"access_token": token, "token_type": "bearer"}
