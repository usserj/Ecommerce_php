# 📱 Guía de Acceso desde Móvil

Guía rápida para acceder al servidor Flask desde tu smartphone.

---

## 🚀 CONFIGURACIÓN INICIAL (Solo una vez)

### 1. Configura el Firewall de Windows

Abre **PowerShell como Administrador** y ejecuta:

```powershell
New-NetFirewallRule -DisplayName "Flask Server - Puerto 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private,Public
```

✅ Esto permite que dispositivos en tu red local accedan al servidor Flask.

---

## 🌐 TU CONFIGURACIÓN DE RED

### IP de tu PC Windows:
```
192.168.3.12
```

### Tu red WiFi:
```
Red: 192.168.3.x
Gateway: 192.168.3.1
Máscara: 255.255.255.0
```

---

## 📱 ACCESO DESDE MÓVIL

### URL Principal:
```
http://192.168.3.12:5000
```

### URLs Disponibles:

#### Frontend (Tienda):
- **Home:** http://192.168.3.12:5000
- **Tienda:** http://192.168.3.12:5000/shop
- **Ofertas:** http://192.168.3.12:5000/ofertas
- **Carrito:** http://192.168.3.12:5000/cart
- **Perfil:** http://192.168.3.12:5000/profile

#### Panel Admin:
- **Login:** http://192.168.3.12:5000/admin/login
- **Dashboard:** http://192.168.3.12:5000/admin/dashboard
- **Productos:** http://192.168.3.12:5000/admin/products
- **Órdenes:** http://192.168.3.12:5000/admin/orders
- **Comentarios:** http://192.168.3.12:5000/admin/comments

---

## ✅ CHECKLIST ANTES DE ACCEDER

### En tu PC Windows:

- [ ] **XAMPP corriendo**
  - Apache: Running (verde)
  - MySQL: Running (verde)

- [ ] **Servidor Flask iniciado**
  ```powershell
  cd C:\Users\jorge.ulloa\Documents\claude_dev\flask_ecommerce\flask-app
  python run.py
  ```

- [ ] **Verificar que el servidor muestre:**
  ```
  * Running on all addresses (0.0.0.0)
  * Running on http://192.168.3.12:5000
  ```

- [ ] **Firewall configurado** (solo primera vez)

### En tu Móvil:

- [ ] **Conectado al mismo WiFi**
  - Tu móvil debe tener IP: 192.168.3.xxx
  - Verifica en: Ajustes > WiFi > (info de red)

- [ ] **Navegador abierto**
  - Chrome, Safari, Firefox, Edge, etc.

---

## 🔍 VERIFICACIÓN PASO A PASO

### 1. Verifica que el servidor esté escuchando en la red

En PowerShell:
```powershell
netstat -ano | findstr :5000
```

**Debes ver:**
```
TCP    0.0.0.0:5000          0.0.0.0:0              LISTENING
TCP    192.168.3.12:5000     0.0.0.0:0              LISTENING
```

Si ves `0.0.0.0:5000`, ✅ el servidor está escuchando en todas las interfaces.

### 2. Verifica la regla del Firewall

En PowerShell:
```powershell
Get-NetFirewallRule -DisplayName "Flask Server*" | Select-Object DisplayName, Enabled, Action
```

**Debes ver:**
```
DisplayName                   Enabled Action
-----------                   ------- ------
Flask Server - Puerto 5000    True    Allow
```

### 3. Prueba desde tu PC primero

Abre un navegador en tu PC y visita:
```
http://192.168.3.12:5000
```

Si funciona en tu PC, debería funcionar en el móvil ✅

### 4. Accede desde el móvil

En el navegador de tu móvil:
```
http://192.168.3.12:5000
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No se puede acceder al sitio"

#### Solución 1: Verifica que ambos estén en la misma red WiFi
```
PC:    192.168.3.12
Móvil: 192.168.3.xxx (debe empezar con 192.168.3)
```

#### Solución 2: Reinicia el servidor Flask
```powershell
# Presiona Ctrl+C en la ventana de PowerShell
# Luego vuelve a ejecutar:
python run.py
```

#### Solución 3: Desactiva temporalmente el Firewall (para probar)
```powershell
# PowerShell como Administrador
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

Prueba en el móvil. Si funciona, el problema es el Firewall.

**IMPORTANTE:** Vuelve a activarlo:
```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

Luego agrega la regla correcta:
```powershell
New-NetFirewallRule -DisplayName "Flask Server 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private,Public
```

#### Solución 4: Verifica que MySQL esté corriendo
```
- Abre XAMPP Control Panel
- MySQL debe estar en "Running" (verde)
```

#### Solución 5: Verifica los logs del servidor
Mira la ventana de PowerShell donde corre `python run.py`.

Si ves errores como:
```
Can't connect to MySQL server
```

Significa que MySQL no está corriendo en XAMPP.

---

## 📝 COMANDOS RÁPIDOS

### Iniciar servidor:
```powershell
cd C:\Users\jorge.ulloa\Documents\claude_dev\flask_ecommerce\flask-app
python run.py
```

### Ver IP actual:
```powershell
ipconfig
```
Busca "Adaptador de LAN inalámbrica Wi-Fi" > "Dirección IPv4"

### Verificar puerto 5000:
```powershell
netstat -ano | findstr :5000
```

### Ver reglas de Firewall:
```powershell
Get-NetFirewallRule -DisplayName "*Flask*"
```

---

## 💡 TIPS

### 1. Guardar en marcadores del móvil
Guarda `http://192.168.3.12:5000` en favoritos para acceso rápido.

### 2. Agregar a pantalla de inicio (PWA)

**Android Chrome:**
- Menú (⋮) > "Agregar a pantalla de inicio"

**iPhone Safari:**
- Compartir (📤) > "Añadir a pantalla de inicio"

### 3. Modo desarrollador en móvil

Para depurar:

**Android:**
1. Ajustes > Opciones de desarrollador > Depuración USB
2. Conecta el móvil al PC por USB
3. En Chrome PC: `chrome://inspect`
4. Verás tu móvil y podrás inspeccionar

**iPhone:**
1. Ajustes > Safari > Avanzado > Inspector Web (ON)
2. Conecta a Mac por USB
3. Safari Mac > Desarrollador > [Tu iPhone]

---

## ⚠️ NOTAS IMPORTANTES

### La IP puede cambiar si:
- Reinicias el router
- Reinicias tu PC
- El router asigna IPs dinámicamente (DHCP)

**Si la IP cambia:**
1. Ejecuta `ipconfig` en PowerShell
2. Busca la nueva IP en "Adaptador de LAN inalámbrica Wi-Fi"
3. Usa la nueva IP en tu móvil

### Para IP fija:
Configura una IP estática en tu router para tu PC (MAC: busca en ipconfig "Dirección física")

---

## 🎯 RESUMEN RÁPIDO

```
1. PC: Inicia XAMPP (Apache + MySQL)
2. PC: python run.py
3. Móvil: Conecta al mismo WiFi
4. Móvil: http://192.168.3.12:5000
5. ¡Listo! 🎉
```

---

## 🔒 SEGURIDAD

**⚠️ Este servidor es SOLO para desarrollo local.**

**NO expongas este servidor a Internet sin:**
- Cambiar SECRET_KEY
- Configurar HTTPS
- Activar todas las medidas de seguridad
- Usar un servidor WSGI en producción

---

**Actualizado:** 2025-01-19
**Tu IP:** 192.168.3.12
**Puerto:** 5000
