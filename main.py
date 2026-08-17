from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import PeliculaDB
from auth import hash_password, verificar_password, crear_token, obtener_usuario_actual, obtener_superusuario_actual
from models import UsuarioDB
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

class Pelicula(BaseModel):
    titulo: str
    año: int

class Usuario(BaseModel):
    username: str
    password: str
    is_superuser: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def inicio():
    return {"mensaje": "Hola desde FastAPI!"}

######################### PELICULAS RELATED ################################

@app.get("/peliculas")
def obtener_peliculas(db: Session = Depends(get_db)):
    return db.query(PeliculaDB).all()
   
@app.get("/peliculas/{id}")
def obtener_pelicula(id: int, db: Session = Depends(get_db)):
    pelicula = db.query(PeliculaDB).filter(PeliculaDB.id == id).first()
    if pelicula:
        return pelicula
    raise HTTPException(status_code=404, detail="Pelicula no encontrada")

@app.post("/peliculas")
def agregar_pelicula(pelicula: Pelicula, db: Session = Depends(get_db), usuario:str = Depends(obtener_superusuario_actual)):
    nueva_pelicula = PeliculaDB(titulo=pelicula.titulo, año=pelicula.año)
    db.add(nueva_pelicula)
    db.commit()
    db.refresh(nueva_pelicula)
    return nueva_pelicula

@app.delete("/peliculas/{id}")
def eliminar_pelicula(id: int, db: Session = Depends(get_db)):
    pelicula = db.query(PeliculaDB).filter(PeliculaDB.id == id).first()
    if pelicula:
        db.delete(pelicula)
        db.commit()
        return {"mensaje": "Pelicula eliminada"}
    raise HTTPException(status_code=404, detail="Pelicula no encontrada")

@app.put("/peliculas/{id}")
def editar_pelicula(id: int, pelicula_actualizada: Pelicula, db: Session = Depends(get_db)):
    pelicula = db.query(PeliculaDB).filter(PeliculaDB.id == id).first()
    if pelicula:
        pelicula.titulo = pelicula_actualizada.titulo
        pelicula.año = pelicula_actualizada.año
        db.commit()
        db.refresh(pelicula)
        return pelicula
    raise HTTPException(status_code=404, detail="Pelicula no encontrada")

######################### USER RELATED ################################

@app.post("/registro")
def registro(usuario: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.username == usuario.username).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuario ya existente")

    nuevo_usuario = UsuarioDB(
        username=usuario.username,
        hashed_password=hash_password(usuario.password)
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Usuario creado correctamente"}

@app.post("/login")
def login(from_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario_db = db.query(UsuarioDB).filter(UsuarioDB.username == from_data.username).first()

    if not usuario_db or not verificar_password(from_data.password, usuario_db.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecto")

    token = crear_token({"sub": usuario_db.username})
    return {"access_token": token, "token_type": "bearer"}
