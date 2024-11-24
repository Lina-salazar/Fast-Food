from fastapi import FastAPI, HTTPException
import pymysql
from typing import Optional, List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt # type: ignore

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserLogin(BaseModel):
    username : str
    password : str

users = {
    "admin": {
        "username": "admin",
        "email": "usuario@email.com",
        "password": "123"
    }
}

# Simula la generación de un token
def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, key="secret", algorithm="HS256")
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        data = jwt.decode(token, key="secret", algorithms="HS256") 
        return data
    except jwt.JWTerror as e:
        raise HTTPException(status_code=401, detail="invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Ruta de inicio de sesión
@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Busca al usuario en el diccionario
    user = users.get(form_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Genera el token
    token = encode_token({"username": user["username"], "email": user["email"]})

    return {"access_token": token, "token_type": "bearer"}

# Ruta de inicio de sesión
@app.post("/login_json")
async def login(form_data:UserLogin):
    # Busca al usuario en el diccionario
    user = users.get(form_data.username)
    if not user or form_data.password != user["password"]:
        raise HTTPException(status_code=404, detail="incorret username or password")

    # Genera el token
    token = encode_token({"username": user["username"], "email": user["email"]})

    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/profile")
def profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user

@app.get("/users", dependencies=[Depends(decode_token)])
def user_list():
    return users

app = FastAPI()

# Configuración del CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para configurar la conexión a MySQL
def connection_mysql():
    conexion = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="api",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conexion

# Definir un modelo para los datos del usuario
class User(BaseModel):
    email: str
    password: str

################################################################ CRUD PARA LOGIN ########################################################################
# Ruta POST para iniciar sesión
@app.post("/users")
async def login(user: User):
    connection = connection_mysql()

    try:
        with connection.cursor() as cursor:
            # Consulta SQL para verificar si el usuario y la contraseña coinciden
            sql = "SELECT email, password FROM users WHERE email = %s"
            cursor.execute(sql, (user.email,))
            result = cursor.fetchone()  # Obtener un solo resultado

            # Verificar si el usuario existe y la contraseña es correcta
            if result is None:
                raise HTTPException(status_code=400, detail="User not found")
            
            if result['password'] != user.password:
                raise HTTPException(status_code=400, detail="Invalid credentials")

            # Si todo es correcto, devolver el mensaje de éxito
            return {"message": "Login successful"}

    except Exception as e:
        print(f"Error: {e}")  # Imprimir el error en la consola para depurar
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        connection.close()  # Cerrar la conexión

############################################################### CRUD PARA INVENTARIO BEBIDAS  ############################################################

class Producto(BaseModel):
    id: int
    nombre: str
    descripcion: str
    precio: float
    cantidad: int
    
class Producto_post(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    cantidad: int

@app.get("/bebidas", response_model=List[Producto])
async def bebidas():
    connection = connection_mysql()

    try:
        with connection.cursor() as cursor:
            # Consulta SQL para obtener todos los productos
            sql = "SELECT id, nombre, descripcion, precio, cantidad FROM bebidas"
            cursor.execute(sql)
            result = cursor.fetchall()  # Obtener todos los resultados de la consulta

            # Devolver los resultados como JSON (FastAPI lo hace automáticamente)
            return result

    except Exception as e:
        print(f"Error: {e}")  # Imprimir el error en la consola para depurar
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        connection.close()  # Cerrar la conexión


 # Método para agregar productos
@app.post("/bebidas", response_model=dict)
async def crear_bebida(bebida: Producto_post):
    """
    Agrega un nuevo producto.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Insertar los datos
            query = """
            INSERT INTO bebidas (nombre, descripcion, precio, cantidad)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (bebida.nombre, bebida.descripcion, bebida.precio, bebida.cantidad))
            connection.commit()

            # Recuperar el id del nuevo producto
            new_id = cursor.lastrowid
            
            return {
                "id": new_id,
                "nombre": bebida.nombre,
                "descripcion": bebida.descripcion,
                "precio": bebida.precio,
                "cantidad": bebida.cantidad
            }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()
        
# Método para eliminar productos
@app.delete("/bebidas/{id}", response_model=dict)
async def eliminar_bebida(id: int):
    """
    Elimina un producto por su ID.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Intentar eliminar el producto con el ID especificado
            sql = "DELETE FROM bebidas WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()

            # Verificar si realmente se eliminó alguna fila
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            return {"mensaje": f"Producto con ID {id} eliminado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()

# Método para actualizar productos
@app.put("/bebidas/{id}", response_model=dict)
async def actualizar_bebida(id: int, bebida: Producto_post):
    """
    Actualiza los datos de un producto por su ID.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Actualizar el producto con los nuevos datos
            sql = """
                UPDATE bebidas
                SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s
                WHERE id = %s
            """
            cursor.execute(sql, (bebida.nombre, bebida.descripcion,bebida.precio, bebida.cantidad, id))
            connection.commit()

            # Verificar si realmente se actualizó alguna fila
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            return {"mensaje": f"Producto con ID {id} actualizado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()




###################################################### CRUD PARA HAMBURGUESAS ################################################
@app.get("/hamburguesas", response_model=List[Producto])
async def hamburguesa():
    connection = connection_mysql()

    try:
        with connection.cursor() as cursor:
            # Consulta SQL para obtener todos los productos
            sql = "SELECT id, nombre, descripcion, precio, cantidad FROM hamburguesas"
            cursor.execute(sql)
            result = cursor.fetchall()  # Obtener todos los resultados de la consulta

            # Devolver los resultados como JSON (FastAPI lo hace automáticamente)
            return result

    except Exception as e:
        print(f"Error: {e}")  # Imprimir el error en la consola para depurar
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        connection.close()  # Cerrar la conexión


 # Método para agregar productos
@app.post("/hamburguesas", response_model=dict)
async def crear_hamburguesa(hamburguesa: Producto_post):
    """
    Agrega un nuevo producto.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Insertar los datos
            query = """
            INSERT INTO hamburguesas (nombre, descripcion, precio, cantidad)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (hamburguesa.nombre, hamburguesa.descripcion, hamburguesa.precio, hamburguesa.cantidad))
            connection.commit()

            # Recuperar el id del nuevo producto
            new_id = cursor.lastrowid
            
            return {
                "id": new_id,
                "nombre":hamburguesa.nombre,
                "descripcion": hamburguesa.descripcion,
                "precio": hamburguesa.precio,
                "cantidad": hamburguesa.cantidad
            }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()
        
# Método para eliminar productos
@app.delete("/hamburguesas/{id}", response_model=dict)
async def eliminar_hamburguesa(id: int):
    """
    Elimina un producto por su ID.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Intentar eliminar el producto con el ID especificado
            sql = "DELETE FROM hamburguesas WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()

            # Verificar si realmente se eliminó alguna fila
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            return {"mensaje": f"Producto con ID {id} eliminado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()

# Método para actualizar productos
@app.put("/hamburguesas/{id}", response_model=dict)
async def actualizar_bebida(id: int, hamburguesa: Producto_post):
    """
    Actualiza los datos de un producto por su ID.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Actualizar el producto con los nuevos datos
            sql = """
                UPDATE hamburguesas
                SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s
                WHERE id = %s
            """
            cursor.execute(sql, (hamburguesa.nombre, hamburguesa.descripcion,hamburguesa.precio, hamburguesa.cantidad, id))
            connection.commit()

            # Verificar si realmente se actualizó alguna fila
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            return {"mensaje": f"Producto con ID {id} actualizado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()


########################################################## CRUD PARA PERROS ##################################################################
@app.get("/perros", response_model=List[Producto])
async def perro():
    connection = connection_mysql()

    try:
        with connection.cursor() as cursor:
            # Consulta SQL para obtener todos los productos
            sql = "SELECT id, nombre, descripcion, precio, cantidad FROM perros"
            cursor.execute(sql)
            result = cursor.fetchall()  # Obtener todos los resultados de la consulta

            # Devolver los resultados como JSON (FastAPI lo hace automáticamente)
            return result

    except Exception as e:
        print(f"Error: {e}")  # Imprimir el error en la consola para depurar
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        connection.close()  # Cerrar la conexión


 # Método para agregar productos
@app.post("/perros", response_model=dict)
async def crear_perro(perro: Producto_post):
    """
    Agrega un nuevo producto.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Insertar los datos
            query = """
            INSERT INTO perros (nombre, descripcion, precio, cantidad)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (perro.nombre, perro.descripcion, perro.precio, perro.cantidad))
            connection.commit()

            # Recuperar el id del nuevo producto
            new_id = cursor.lastrowid
            
            return {
                "id": new_id,
                "nombre":perro.nombre,
                "descripcion": perro.descripcion,
                "precio": perro.precio,
                "cantidad": perro.cantidad
            }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()
        
# Método para eliminar productos
@app.delete("/perros/{id}", response_model=dict)
async def eliminar_perro(id: int):
    """
    Elimina un producto por su ID.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Intentar eliminar el producto con el ID especificado
            sql = "DELETE FROM perros WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()

            # Verificar si realmente se eliminó alguna fila
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            return {"mensaje": f"Producto con ID {id} eliminado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()

# Método para actualizar productos
@app.put("/perros/{id}", response_model=dict)
async def actualizar_perro(id: int, perro: Producto_post):
    """
    Actualiza los datos de un producto por su ID.
    """
    connection = connection_mysql()
    try:
        with connection.cursor() as cursor:
            # Actualizar el producto con los nuevos datos
            sql = """
                UPDATE perros
                SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s
                WHERE id = %s
            """
            cursor.execute(sql, (perro.nombre, perro.descripcion,perro.precio, perro.cantidad, id))
            connection.commit()

            # Verificar si realmente se actualizó alguna fila
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            
            return {"mensaje": f"Producto con ID {id} actualizado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        connection.close()