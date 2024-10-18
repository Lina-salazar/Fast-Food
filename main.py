from fastapi import FastAPI, HTTPException
import pymysql
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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