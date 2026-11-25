# Dockerfile para Laboratorio de Ciberseguridad
FROM python:3.11-slim

LABEL maintainer="Proyecto Final Ciberseguridad"
LABEL description="Aplicación de laboratorio vulnerable para demostración académica"

# Evitar buffer de stdout para logs en tiempo real
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development
ENV SECRET_KEY=lab-secret-key-dev-change-in-production

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app.py .

# Crear directorio para logs
RUN mkdir -p /var/log/lab

# Exponer puerto
EXPOSE 5000

# Usuario no privilegiado
RUN useradd -m -u 1000 labuser && chown -R labuser:labuser /app /var/log/lab
USER labuser

# Comando de ejecución
CMD ["python", "app.py"]