# Usa una imagen base de Python ligera (Alpine es eficiente)
FROM python:3.11-slim

# Establece el directorio de trabajo en /app
WORKDIR /usr/src/app

# Copia los requisitos e instala las dependencias
# Se hace en dos pasos para aprovechar el cache de Docker (si requirements.txt no cambia, es más rápido)
COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
# El directorio 'app' está en la raíz, así que se copia todo el código.
COPY . .

# Expón el puerto que usará Gunicorn
EXPOSE 5000

# Comando para iniciar la aplicación con Gunicorn.
# Asume que la instancia de Flask se llama 'app' en el módulo 'app.main'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]
