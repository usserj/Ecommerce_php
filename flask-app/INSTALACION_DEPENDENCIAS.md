# 📦 INSTALACIÓN DE DEPENDENCIAS

**Nota:** Este archivo contiene instrucciones para instalar todas las dependencias necesarias del proyecto Flask.

---

## ⚠️ IMPORTANTE: Primera vez

Si es la **primera vez** que ejecutas el proyecto, o si ves el error:
```
ModuleNotFoundError: No module named 'dotenv'
```

Debes instalar las dependencias Python **una sola vez**.

---

## 🔧 INSTALACIÓN (Windows)

### Opción 1: Instalación Completa (Recomendado)

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
# Navegar a la carpeta flask-app
cd flask-app

# Instalar todas las dependencias
pip install -r requirements.txt
```

**Tiempo estimado:** 2-5 minutos dependiendo de tu conexión

---

### Opción 2: Instalación Mínima (Solo lo necesario)

Si solo quieres instalar lo mínimo para que funcione:

```powershell
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install PyMySQL==1.1.0
pip install Flask-Login==0.6.3
pip install Flask-Bcrypt==1.0.1
pip install Flask-WTF==1.2.1
pip install python-dotenv==1.0.0
pip install Flask-Limiter==3.5.0
pip install Flask-Mail==0.9.1
pip install paypalrestsdk==1.13.1
```

---

## ✅ VERIFICAR INSTALACIÓN

Después de instalar, verifica que funcione:

```powershell
# Verificar que Flask está instalado
python -c "import flask; print(f'Flask {flask.__version__} instalado correctamente')"

# Verificar que dotenv está instalado
python -c "import dotenv; print('python-dotenv instalado correctamente')"

# Verificar que PyMySQL está instalado
python -c "import pymysql; print('PyMySQL instalado correctamente')"
```

Si todos los comandos ejecutan sin errores, **las dependencias están instaladas correctamente**.

---

## 📋 DEPENDENCIAS INCLUIDAS EN requirements.txt

### Core (Obligatorias):
- ✅ Flask 3.0.0 - Framework web
- ✅ Flask-SQLAlchemy - ORM para base de datos
- ✅ PyMySQL - Conector MySQL
- ✅ python-dotenv - Manejo de variables de entorno
- ✅ Flask-Login - Autenticación de usuarios
- ✅ Flask-Bcrypt - Hash de contraseñas

### Formularios y Validación:
- ✅ Flask-WTF - Formularios con CSRF
- ✅ WTForms - Validación de formularios
- ✅ email-validator - Validación de emails

### Email:
- ✅ Flask-Mail - Envío de correos

### Seguridad:
- ✅ Flask-Limiter - Rate limiting
- ✅ Flask-Talisman - Headers de seguridad
- ✅ passlib - Hash de contraseñas

### Pagos:
- ✅ paypalrestsdk - Integración PayPal

### Utilidades:
- ✅ Pillow - Procesamiento de imágenes
- ✅ requests - HTTP client
- ✅ python-slugify - Generación de URLs amigables

### Opcionales (para producción):
- Redis - Cache
- Celery - Tareas asíncronas
- Gunicorn - Servidor WSGI

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "pip no se reconoce como un comando..."

**Solución:** Agrega Python al PATH de Windows o usa la ruta completa:
```powershell
C:\Users\jorge.ulloa\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r requirements.txt
```

---

### Error: "Could not find a version that satisfies..."

**Causa:** Versión de Python muy antigua

**Solución:** Actualiza a Python 3.10 o superior
```powershell
python --version  # Debe ser 3.10+
```

---

### Error: "Access denied" al instalar

**Solución:** Instala para el usuario actual (sin permisos de admin):
```powershell
pip install --user -r requirements.txt
```

---

### Error: "error: Microsoft Visual C++ 14.0 is required"

**Causa:** Falta compilador de C++ para algunos paquetes

**Solución:** Descarga e instala Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

O instala versiones pre-compiladas:
```powershell
pip install --only-binary :all: -r requirements.txt
```

---

### Error al instalar `psycopg2-binary`

**Nota:** Este paquete es para PostgreSQL, no es necesario si usas MySQL

**Solución:** Comentar la línea en requirements.txt:
```
# psycopg2-binary==2.9.9  # Solo si usas PostgreSQL
```

Luego reinstala:
```powershell
pip install -r requirements.txt
```

---

## 🔄 ACTUALIZAR DEPENDENCIAS

Si actualizas el código y hay nuevas dependencias:

```powershell
# Actualizar paquetes existentes
pip install --upgrade -r requirements.txt

# O instalar solo nuevos paquetes
pip install -r requirements.txt
```

---

## 🧹 LIMPIAR Y REINSTALAR

Si algo sale mal y quieres empezar de cero:

```powershell
# Desinstalar todos los paquetes
pip freeze > uninstall.txt
pip uninstall -y -r uninstall.txt

# Reinstalar desde requirements.txt
pip install -r requirements.txt
```

---

## 📌 ENTORNOS VIRTUALES (Recomendado)

Para evitar conflictos con otros proyectos Python:

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\activate

# Instalar dependencias en el entorno
pip install -r requirements.txt

# Ahora puedes ejecutar el servidor
python run.py

# Desactivar cuando termines
deactivate
```

**Ventajas:**
- ✅ Dependencias aisladas por proyecto
- ✅ No contamina tu Python global
- ✅ Fácil de eliminar (solo borra la carpeta venv/)

---

## ✅ CHECKLIST DE INSTALACIÓN

Marca cada paso a medida que lo completes:

- [ ] Python 3.10+ instalado
- [ ] pip funcionando
- [ ] Navegado a carpeta flask-app
- [ ] Ejecutado `pip install -r requirements.txt`
- [ ] Sin errores en la instalación
- [ ] Verificado con `python -c "import flask"`
- [ ] Migración de BD aplicada (`python fix_database.py`)
- [ ] Archivo .env configurado
- [ ] Servidor inicia sin errores (`python run.py`)

---

## 🚀 DESPUÉS DE INSTALAR

Una vez instaladas las dependencias, sigue estos pasos:

1. **Aplica la migración de base de datos:**
   ```powershell
   python fix_database.py
   ```

2. **Inicia el servidor:**
   ```powershell
   python run.py
   ```

3. **Accede al sistema:**
   - Frontend: http://localhost:5000
   - Admin: http://localhost:5000/admin/login

---

## 📞 AYUDA

Si después de seguir estas instrucciones sigues teniendo problemas:

1. Copia el error completo de PowerShell
2. Verifica la versión de Python: `python --version`
3. Verifica qué paquetes están instalados: `pip list`
4. Comparte el error para obtener ayuda específica

---

**¡Las dependencias solo se instalan una vez!**

Después de la primera instalación exitosa, solo necesitas ejecutar `python run.py` para iniciar el servidor.
