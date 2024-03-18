FROM python:3.10.13-alpine

# Dependencia de Zona Horaria
RUN apk add tzdata
# Establecer zona horaria
ENV TZ="America/Lima"

# Directorio de la App en la instancia
WORKDIR /app

# Copiar archivos de la aplicación a la instancia en Docker
COPY . .

# Actualizar PIP
RUN pip install pip --upgrade

# Instalar dependencias
RUN pip install -r requirements.txt

# Puertos a exponer del servicio
EXPOSE 9000

# Comando de ejecución de API, indicado parámetros de configuración
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "9000", "authx:api"]
