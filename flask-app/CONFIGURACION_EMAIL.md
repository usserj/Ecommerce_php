# 📧 Configuración del Sistema de Emails

## Problema Identificado
Los emails de verificación no se envían porque faltan las variables de entorno de configuración SMTP.

## Solución

### 1. Copiar el archivo de ejemplo
```bash
cp .env.example .env
```

### 2. Configurar Gmail (Recomendado para desarrollo)

#### Paso 1: Obtener contraseña de aplicación de Gmail
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Selecciona "Seguridad"
3. Activa "Verificación en dos pasos" (si no está activada)
4. Busca "Contraseñas de aplicación"
5. Genera una nueva contraseña para "Correo" y "Otro (nombre personalizado)"
6. Copia la contraseña generada (16 caracteres)

#### Paso 2: Editar .env
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # La contraseña de 16 dígitos
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

### 3. Alternativas a Gmail

#### SendGrid (Gratis hasta 100 emails/día)
1. Registro en: https://sendgrid.com/
2. Crear API Key en Settings → API Keys
3. Configurar:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxx
MAIL_DEFAULT_SENDER=noreply@tudominio.com
```

#### Mailgun (Gratis 5000 emails/mes)
1. Registro en: https://www.mailgun.com/
2. Verificar dominio o usar sandbox
3. Obtener credenciales SMTP
4. Configurar:
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=postmaster@sandboxXXXX.mailgun.org
MAIL_PASSWORD=tu_password
MAIL_DEFAULT_SENDER=noreply@tudominio.com
```

### 4. Verificar la configuración

```bash
cd /home/user/Ecommerce_php/flask-app
python3 test_email.py
```

### 5. Reiniciar la aplicación
```bash
flask run
```

## Funcionalidades que Requieren Email

1. ✅ **Registro de usuarios** - Envía email de verificación
2. ✅ **Recuperación de contraseña** - Envía link de recuperación
3. ✅ **Notificaciones de pedidos** - Confirma órdenes
4. ⚠️ **Notificaciones admin** - Alertas de nuevos pedidos

## OAuth (Google/Facebook Login)

Para que funcione el login con Google/Facebook, también necesitas configurar:

### Google OAuth
1. Ve a: https://console.cloud.google.com/
2. Crea un nuevo proyecto
3. Habilita Google+ API
4. Crear credenciales OAuth 2.0
5. Agregar URIs autorizados:
   - `http://localhost:5000/auth/google/callback`
   - `https://tudominio.com/auth/google/callback`
6. Configurar en .env:
```env
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx
```

### Facebook OAuth
1. Ve a: https://developers.facebook.com/
2. Crea una app
3. Configurar "Facebook Login"
4. Agregar URIs de redirección:
   - `http://localhost:5000/auth/facebook/callback`
5. Configurar en .env:
```env
FACEBOOK_CLIENT_ID=tu_app_id
FACEBOOK_CLIENT_SECRET=tu_app_secret
```

## Troubleshooting

### Error: "Authentication failed"
- Verifica que la contraseña de aplicación sea correcta
- Asegúrate de tener la verificación en dos pasos activada (Gmail)

### Error: "Connection refused"
- Verifica el puerto (587 para TLS, 465 para SSL)
- Verifica que no haya firewall bloqueando SMTP

### Error: "Emails no llegan"
- Verifica la carpeta de SPAM
- Verifica que MAIL_DEFAULT_SENDER esté configurado correctamente
- Revisa los logs de Flask para ver errores específicos

## Testing Rápido

Crea este archivo para probar:

```python
# test_email.py
from app import create_app
from app.extensions import mail
from flask_mail import Message

app = create_app()

with app.app_context():
    msg = Message(
        'Test Email',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=['destinatario@example.com']
    )
    msg.body = 'Este es un email de prueba'
    mail.send(msg)
    print('Email enviado exitosamente!')
```

```bash
python3 test_email.py
```

## Estado Actual

- ✅ Código de envío de emails implementado
- ✅ Configuración SMTP en config.py
- ❌ Variables de entorno no configuradas
- ❌ .env file no existe (usar .env.example como base)

**Próximos pasos:** Configurar .env con tus credenciales SMTP.
