# 🚀 CÓMO INICIAR EL SERVIDOR FLASK

**IMPORTANTE:** Debes ejecutar estos comandos en **TU MÁQUINA WINDOWS**, no aquí.

---

## ⚠️ PREREQUISITOS

Antes de iniciar el servidor, asegúrate de que:

### 1. ✅ XAMPP está corriendo
```
- Abre XAMPP Control Panel
- Inicia "Apache"
- Inicia "MySQL"
- Verifica que ambos estén en estado "Running" (verde)
```

### 2. ✅ Dependencias Python instaladas

Abre PowerShell en la carpeta `flask-app` y ejecuta:

```powershell
# Verificar instalación
python -c "from app import create_app; print('✅ OK')"
```

**Si dice "ModuleNotFoundError"**, instala las dependencias:
```powershell
pip install -r requirements.txt
```

---

## 🚀 INICIAR EL SERVIDOR

### Paso 1: Navegar a la carpeta

```powershell
cd C:\Users\jorge.ulloa\Documents\claude_dev\flask_ecommerce\flask-app
```

### Paso 2: Verificar que MySQL está corriendo

```powershell
# Probar conexión a MySQL
python fix_database.py
```

**Deberías ver:**
```
✅ Conexión exitosa
⊘ Migración ya aplicada (omitida)
```

### Paso 3: Iniciar el servidor Flask

```powershell
python run.py
```

**Deberías ver:**
```
============================================================
🚀 SERVIDOR FLASK INICIANDO
============================================================

🌐 Accede al servidor en:

   Local:    http://localhost:5000
   Red:      http://192.168.208.153:5000

📊 Panel Admin:
   Admin:    http://192.168.208.153:5000/admin/login

🔥 Hot-reload: ACTIVADO
============================================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.208.153:5000
```

---

## 🌐 ACCEDER AL SERVIDOR

Una vez que el servidor está corriendo, abre tu navegador y ve a:

### Frontend (Tienda):
- **Local:** http://localhost:5000
- **Red:** http://192.168.208.153:5000

### Panel de Administración:
- **Admin:** http://192.168.208.153:5000/admin/login

---

## 🛑 DETENER EL SERVIDOR

Para detener el servidor:

1. Ve a la ventana de PowerShell donde está corriendo
2. Presiona `Ctrl + C`
3. Confirma si te pregunta

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### Error: "ERR_CONNECTION_TIMED_OUT"

**Causa:** El servidor NO está corriendo

**Solución:**
1. Abre PowerShell
2. Navega a `flask-app`
3. Ejecuta `python run.py`
4. Espera a que diga "Running on..."
5. Refresca el navegador

---

### Error: "Can't connect to MySQL server"

**Causa:** XAMPP MySQL no está iniciado

**Solución:**
1. Abre XAMPP Control Panel
2. Presiona "Start" en MySQL
3. Espera a que diga "Running"
4. Ejecuta `python run.py` de nuevo

---

### Error: "Address already in use"

**Causa:** Ya hay otro servidor corriendo en el puerto 5000

**Solución Opción 1 - Cerrar el otro servidor:**
```powershell
# En Windows, busca el proceso
netstat -ano | findstr :5000

# Mata el proceso (reemplaza PID con el número que viste)
taskkill /PID <número> /F
```

**Solución Opción 2 - Usar otro puerto:**
```powershell
# Ejecuta en otro puerto
$env:PORT=5001; python run.py
```

---

### Error: "ModuleNotFoundError: No module named 'flask'"

**Causa:** Dependencias no instaladas

**Solución:**
```powershell
pip install -r requirements.txt
```

---

### Error: "Access denied for user 'root'@'localhost'"

**Causa:** Contraseña de MySQL incorrecta en `.env`

**Solución:**
1. Abre `.env`
2. En la línea `DATABASE_URL`, si tienes contraseña:
   ```
   # ANTES (sin contraseña)
   DATABASE_URL=mysql+pymysql://root:@localhost/Ecommerce_Ec

   # DESPUÉS (con contraseña)
   DATABASE_URL=mysql+pymysql://root:tu_contraseña@localhost/Ecommerce_Ec
   ```
3. Guarda y ejecuta `python run.py` de nuevo

---

## ✅ VERIFICAR QUE FUNCIONA

Una vez que el servidor esté corriendo:

### 1. Verificar Frontend
- Ve a: http://localhost:5000
- Deberías ver la tienda

### 2. Verificar Admin
- Ve a: http://localhost:5000/admin/login
- Deberías ver el formulario de login de admin

### 3. Verificar Base de Datos
- El servidor muestra mensajes en la consola
- No debería haber errores de "Can't connect to MySQL"

---

## 📝 COMANDOS RÁPIDOS

```powershell
# 1. Navegar a carpeta
cd C:\Users\jorge.ulloa\Documents\claude_dev\flask_ecommerce\flask-app

# 2. Verificar XAMPP MySQL
# (manualmente en XAMPP Control Panel)

# 3. Iniciar servidor
python run.py

# 4. Abrir navegador
start http://localhost:5000
```

---

## 🎯 RESUMEN

| Paso | Acción | Verificación |
|------|--------|--------------|
| 1 | Abrir XAMPP | MySQL debe estar verde |
| 2 | Abrir PowerShell | Estar en carpeta flask-app |
| 3 | Ejecutar `python run.py` | Ver "Running on..." |
| 4 | Abrir navegador | Acceder a localhost:5000 |

---

## 💡 TIPS

1. **Mantén la ventana de PowerShell abierta** mientras usas el servidor
2. **No cierres PowerShell** o el servidor se detendrá
3. **Hot-reload está activado** - Los cambios en el código se aplican automáticamente
4. **Mira los logs en PowerShell** para debugging

---

## 🆘 SI NADA FUNCIONA

1. Cierra todas las ventanas de PowerShell
2. Reinicia XAMPP (Stop All > Start All)
3. Abre PowerShell fresca
4. Ejecuta los comandos en orden:
   ```powershell
   cd C:\Users\jorge.ulloa\Documents\claude_dev\flask_ecommerce\flask-app
   python fix_database.py
   python run.py
   ```

---

**🚀 ¡El servidor está listo para usarse!**

Una vez que veas "Running on http://192.168.208.153:5000" en PowerShell, accede desde tu navegador.
