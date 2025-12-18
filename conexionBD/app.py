from flask import Flask, render_template, redirect, request
# 1. Importamos la herramienta de base de datos
from flask_sqlalchemy import SQLAlchemy 
import os 
app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL')
if db_url:
    # Corrección para PostgreSQL (Render a veces da urls con 'postgres://' que fallan, hay que cambiarlo a 'postgresql://')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Configuración local (tu archivo en la PC)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mi_base_de_datos.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ------------------------------

db = SQLAlchemy(app)# Inicializamos la base de datos

# --- DEFINIMOS LA TABLA (MODELO) (NUEVO) ---
# Esto es equivalente a un CREATE TABLE comentarios (...)
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(200))

# Creamos la tabla físicamente dentro del contexto de la app
with app.app_context():
    db.create_all()


@app.route("/")
def inicio():
    lista_comentarios = Comentario.query.all()
    return render_template("index.html", comentarios = lista_comentarios)

@app.route("/firmar", methods=["POST"])
def firmar():
    # 1. Recibimos lo que escribió el usuario en el input "texto_comentario"
    mensaje = request.form["texto_comentario"]
    
    # 2. Preparamos el objeto para la DB (Equivalente a INSERT INTO...)
    nuevo_comentario = Comentario(contenido=mensaje)
    
    # 3. Guardamos los cambios
    db.session.add(nuevo_comentario)
    db.session.commit()
    
    return redirect("/")

# Recibimos un número entero <int:id> en la URL
@app.route("/borrar/<int:id_mensaje>")
def borrar(id_mensaje):
    # 1. BUSCAR: Buscamos el comentario por su ID (o falla si no existe)
    comentario_a_borrar = Comentario.query.get_or_404(id_mensaje)
    
    # 2. BORRAR: Le decimos a la DB que lo elimine
    db.session.delete(comentario_a_borrar)
    db.session.commit()
    
    # 3. VOLVER: Regresamos al inicio
    return redirect("/")


# Borrar todos los campos de la tabla
@app.route("/reset")
def reset():
    db.session.query(Comentario).delete()
    db.session.commit()
    # 3. VOLVER: Regresamos al inicio
    return redirect("/")

# RUTA 1: Muestra el formulario con el texto viejo
@app.route("/editar/<int:id>")
def editar(id):
    # Buscamos el comentario que quiere editar
    comentario_a_editar = Comentario.query.get_or_404(id)
    # Le enviamos ese comentario al HTML para que rellene la cajita
    return render_template("editar.html", comentario=comentario_a_editar)

# RUTA 2: Recibe el cambio y actualiza la Base de Datos
@app.route("/actualizar/<int:id>", methods=['POST'])
def actualizar(id):
    # 1. Buscamos el comentario de nuevo
    comentario = Comentario.query.get_or_404(id)
    
    # 2. ACTUALIZAR: Sobreescribimos el contenido viejo con el nuevo que viene del formulario
    comentario.contenido = request.form['texto_nuevo']
    
    # 3. Guardamos (SQLAlchemy detecta que ya existía y hace un UPDATE en vez de INSERT)
    db.session.commit()
    
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)