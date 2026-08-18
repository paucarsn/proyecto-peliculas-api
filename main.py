from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import UsuarioDB, ProductoDB
from auth import hash_password, verificar_password, crear_token, obtener_usuario_actual, obtener_superusuario_actual
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Producto(BaseModel):
    nombre: str
    precio: float
    tipo: str

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
    producto = db.query(ProductoDB).filter(ProductosDB.id == id).first()
    if producto:
        return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.post("/productos")
def agregar_producto(producto: Producto, db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):
    nuevo_producto = ProductosDB(titulo=producto.titulo, año=producto.año)
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

@app.delete("/productos/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):
    producto = db.query(ProductosDB).filter(ProductosDB.id == id).first()
    if producto:
        db.delete(producto)
        db.commit()
        return {"mensaje": "Producto eliminado"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.put("/productos/{id}")
def editar_producto(id: int, producto_actualizado: Producto, db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):
    producto = db.query(ProductosDB).filter(ProductosDB.id == id).first()
    if producto:
        producto.titulo = producto_actualizado.titulo
        producto.año = producto_actualizado.año
        db.commit()
        db.refresh(producto)
        return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

######################### USER RELATED ################################

@app.post("/registro")
def registro(usuario: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuario ya existente")

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
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecto")

    token = crear_token({"sub": usuario_db.username})
    return {"access_token": token, "token_type": "bearer"}
