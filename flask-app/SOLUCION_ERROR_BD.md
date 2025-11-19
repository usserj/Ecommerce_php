# 🔧 SOLUCIÓN AL ERROR DE BASE DE DATOS

## ❌ ERROR ACTUAL:
```
Unknown column 'usuarios.reset_token' in 'field list'
```

---

## ✅ SOLUCIÓN RÁPIDA (2 PASOS):

### **PASO 1: Ejecuta el script de migración**

En la terminal de PowerShell (donde estás ahora), ejecuta:

```powershell
python fix_database.py
```

**Verás algo como esto:**
```
============================================================
🔧 APLICANDO MIGRACIÓN DE BASE DE DATOS
============================================================

📡 Conectando a MySQL (localhost)...
✅ Conexión exitosa

⏳ Ejecutando migración 1/4...
✅ Migración 1 aplicada exitosamente

⏳ Ejecutando migración 2/4...
✅ Migración 2 aplicada exitosamente

⏳ Ejecutando migración 3/4...
✅ Migración 3 aplicada exitosamente

⏳ Ejecutando migración 4/4...
✅ Migración 4 aplicada exitosamente

============================================================
✅ MIGRACIÓN COMPLETADA
   • Aplicadas: 4
   • Omitidas: 0
============================================================

🚀 Ahora puedes reiniciar el servidor Flask:
   python run.py
```

---

### **PASO 2: Reinicia el servidor**

Después de que la migración termine exitosamente:

```powershell
python run.py
```

**El servidor iniciará en:**
```
http://192.168.208.153:5000
```

**Accede al admin:**
```
http://192.168.208.153:5000/admin/login
```

---

## 🆘 SI TIENES ERROR DE CONTRASEÑA

Si ves este error:
```
❌ ERROR DE CONEXIÓN
   (1045, "Access denied for user 'root'@'localhost'")
```

**Solución:**

1. **Abre el archivo:** `fix_database.py`

2. **Busca la línea 8:**
   ```python
   'password': '',  # Cambia si tienes contraseña
   ```

3. **Pon tu contraseña de MySQL:**
   ```python
   'password': 'tu_contraseña_mysql',
   ```

4. **Guarda y ejecuta de nuevo:**
   ```powershell
   python fix_database.py
   ```

---

## 📋 ¿QUÉ HACE ESTE SCRIPT?

Agrega estos campos a tu base de datos:

### Tabla `usuarios`:
- ✅ `reset_token` - Token para recuperar contraseña
- ✅ `reset_token_expiry` - Fecha de expiración del token

### Tabla `comentarios`:
- ✅ `estado` - Estado de moderación (pendiente/aprobado/rechazado)
- ✅ `respuesta_admin` - Respuesta del administrador
- ✅ `fecha_moderacion` - Fecha de moderación
- ✅ Índice en `estado` - Para mejor rendimiento

---

## 🌐 URLS DE ACCESO

Después de que el servidor inicie correctamente:

### **Frontend (tienda):**
```
http://192.168.208.153:5000
http://192.168.208.153:5000/shop
http://192.168.208.153:5000/ofertas
```

### **Admin Panel:**
```
http://192.168.208.153:5000/admin/login
http://192.168.208.153:5000/admin/dashboard
http://192.168.208.153:5000/admin/products
http://192.168.208.153:5000/admin/orders
http://192.168.208.153:5000/admin/comments    ← NUEVO
http://192.168.208.153:5000/admin/users
http://192.168.208.153:5000/admin/coupons
```

### **Autenticación:**
```
http://192.168.208.153:5000/auth/login
http://192.168.208.153:5000/auth/register
http://192.168.208.153:5000/auth/forgot-password    ← NUEVO
```

---

## ✅ VERIFICACIÓN POST-MIGRACIÓN

Después de reiniciar el servidor, prueba:

1. **Login admin:** http://192.168.208.153:5000/admin/login
   - Usuario: (tu usuario admin)
   - Contraseña: (tu contraseña admin)

2. **Módulo de comentarios:** http://192.168.208.153:5000/admin/comments

3. **Sistema de cupones:** Ir a checkout con productos en carrito

4. **Recuperar contraseña:** http://192.168.208.153:5000/auth/forgot-password

---

## 🔍 TROUBLESHOOTING

### Problema: "Connection refused" o timeout
**Causa:** El servidor no está corriendo o hay un firewall bloqueando
**Solución:**
1. Asegúrate de que el servidor está corriendo (deberías ver "Running on...")
2. Verifica que no hay firewall bloqueando el puerto 5000
3. Prueba con `http://localhost:5000` primero

### Problema: "Duplicate column name"
**Esto es NORMAL:** Significa que ya ejecutaste la migración antes
**Solución:** Ignóralo, el script automáticamente lo omite

### Problema: Error al conectar a MySQL
**Solución:**
1. Verifica que XAMPP esté corriendo
2. Verifica que MySQL esté iniciado
3. Prueba la contraseña en phpMyAdmin

---

## 📞 SI SIGUEN LOS ERRORES

Si después de ejecutar `fix_database.py` y reiniciar el servidor **aún** ves errores:

1. **Copia el error completo** de la terminal
2. **Pégalo aquí** para ayudarte

---

**¡Ejecuta `python fix_database.py` ahora!** 🚀
