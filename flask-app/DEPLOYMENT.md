# Guía de Deployment - Flask E-commerce

Guía completa para hacer deployment de la aplicación Flask E-commerce en producción.

## 📋 Tabla de Contenidos

- [Prerequisitos](#prerequisitos)
- [Deployment Local con Docker](#deployment-local-con-docker)
- [Deployment en Producción](#deployment-en-producción)
- [Configuración de SSL](#configuración-de-ssl)
- [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
- [Backup y Restore](#backup-y-restore)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisitos

### Servidor de Producción

**Requisitos mínimos:**
- Sistema operativo: Ubuntu 20.04 LTS o superior
- RAM: 4 GB mínimo (8 GB recomendado)
- CPU: 2 cores mínimo (4 cores recomendado)
- Disco: 20 GB mínimo (50 GB recomendado)
- Docker: 20.10+
- Docker Compose: 2.0+

### Software Requerido

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### Dominios y DNS

Configurar los siguientes registros DNS:
```
A     example.com         -> IP_DEL_SERVIDOR
A     www.example.com     -> IP_DEL_SERVIDOR
```

## 🐳 Deployment Local con Docker

### 1. Clonar Repositorio

```bash
git clone https://github.com/your-org/ecommerce-flask.git
cd ecommerce-flask/flask-app
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
```

Configurar las siguientes variables:

```env
# Flask
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Database
MYSQL_ROOT_PASSWORD=strong-root-password
MYSQL_PASSWORD=strong-user-password
DATABASE_URL=mysql+pymysql://ecommerce_user:strong-user-password@db:3306/ecommerce_flask

# Redis
REDIS_URL=redis://redis:6379/0

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# PayPal
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=live  # o 'sandbox' para testing

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook OAuth
FACEBOOK_CLIENT_ID=your-facebook-app-id
FACEBOOK_CLIENT_SECRET=your-facebook-app-secret
```

### 3. Construir y Levantar Servicios

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Producción
docker-compose up -d
```

### 4. Ejecutar Migraciones

```bash
docker-compose exec app flask db upgrade
```

### 5. Verificar Deployment

```bash
# Ver logs
docker-compose logs -f app

# Health check
curl http://localhost:5000/health

# Ver servicios corriendo
docker-compose ps
```

## 🚀 Deployment en Producción

### Opción 1: Script Automatizado

```bash
# Dar permisos de ejecución
chmod +x scripts/*.sh

# Ejecutar deployment
./scripts/deploy.sh
```

El script realizará automáticamente:
- ✅ Pull del código más reciente
- ✅ Backup de base de datos
- ✅ Build de imágenes Docker
- ✅ Ejecución de migraciones
- ✅ Inicio de servicios
- ✅ Health check

### Opción 2: Deployment Manual

#### Paso 1: Preparar el Servidor

```bash
# Conectar al servidor
ssh user@your-server.com

# Crear directorio de la aplicación
sudo mkdir -p /var/www/ecommerce-flask
sudo chown $USER:$USER /var/www/ecommerce-flask
cd /var/www/ecommerce-flask

# Clonar repositorio
git clone https://github.com/your-org/ecommerce-flask.git .
cd flask-app
```

#### Paso 2: Configurar Entorno

```bash
# Copiar y editar .env
cp .env.example .env
nano .env

# Configurar las variables según la sección anterior
```

#### Paso 3: Iniciar Servicios

```bash
# Build de imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

#### Paso 4: Migraciones y Data

```bash
# Ejecutar migraciones
docker-compose exec app flask db upgrade

# (Opcional) Migrar datos desde PHP
docker-compose exec app python migrate_data.py
```

#### Paso 5: Verificar

```bash
# Health check
curl http://localhost:5000/health

# Ver servicios
docker-compose ps
```

## 🔒 Configuración de SSL

### Método 1: Let's Encrypt (Recomendado)

```bash
# Ejecutar script de SSL
./scripts/setup-ssl.sh your-domain.com admin@your-domain.com
```

### Método 2: Manual con Certbot

```bash
# Obtener certificado
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@your-domain.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com \
  -d www.your-domain.com

# Reiniciar nginx
docker-compose restart nginx
```

### Renovación Automática

El container de Certbot renueva automáticamente los certificados. Verificar:

```bash
# Ver logs de certbot
docker-compose logs certbot

# Verificar certificado
openssl s_client -connect your-domain.com:443 -servername your-domain.com | openssl x509 -noout -dates
```

## 📊 Monitoreo y Mantenimiento

### Health Checks

La aplicación expone endpoints de health check:

```bash
# Health general
curl https://your-domain.com/health

# Liveness (está viva la app?)
curl https://your-domain.com/health/live

# Readiness (está lista para recibir tráfico?)
curl https://your-domain.com/health/ready
```

### Ver Logs

```bash
# Logs de la aplicación
docker-compose logs -f app

# Logs de nginx
docker-compose logs -f nginx

# Logs de base de datos
docker-compose logs -f db

# Logs de todos los servicios
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100 app
```

### Monitorear Recursos

```bash
# Ver uso de recursos
docker stats

# Ver disco
df -h

# Ver memoria
free -h

# Ver procesos
docker-compose ps
```

### Restart de Servicios

```bash
# Reiniciar aplicación
docker-compose restart app

# Reiniciar todos los servicios
docker-compose restart

# Reiniciar específico
docker-compose restart nginx
```

## 💾 Backup y Restore

### Crear Backup

```bash
# Backup manual
./scripts/backup.sh

# Los backups se guardan en: ./backups/
```

### Backup Automatizado

Agregar a crontab:

```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 2 AM
0 2 * * * cd /var/www/ecommerce-flask/flask-app && ./scripts/backup.sh

# Agregar backup semanal completo los domingos a las 3 AM
0 3 * * 0 cd /var/www/ecommerce-flask/flask-app && ./scripts/backup.sh
```

### Restore desde Backup

```bash
# Listar backups disponibles
ls -lh backups/

# Restaurar backup específico
./scripts/restore.sh

# Seguir las instrucciones del script
```

### Backup Remoto

```bash
# Sincronizar backups a servidor remoto con rsync
rsync -avz backups/ user@backup-server:/backups/ecommerce-flask/

# O usar S3
aws s3 sync backups/ s3://your-bucket/ecommerce-backups/
```

## 🔄 CI/CD Pipeline

### GitHub Actions

El proyecto incluye un workflow de CI/CD completo en `.github/workflows/ci-cd.yml`:

**Proceso:**
1. **Lint**: Verifica calidad de código (flake8, black, isort)
2. **Security**: Escanea vulnerabilidades (bandit, safety)
3. **Test**: Ejecuta suite de tests con coverage
4. **Build**: Construye imagen Docker
5. **Deploy**: Despliega a producción (solo en main)

**Configurar Secrets en GitHub:**

```
Settings > Secrets and variables > Actions > New repository secret
```

Agregar:
```
PRODUCTION_HOST=your-server-ip
PRODUCTION_USER=deploy-user
SSH_PRIVATE_KEY=your-ssh-private-key
SLACK_WEBHOOK=your-slack-webhook-url (opcional)
```

### Deployment Manual desde CI/CD

```bash
# Trigger deployment manualmente
gh workflow run ci-cd.yml

# Ver estado
gh run list
```

## 🔧 Troubleshooting

### Aplicación No Inicia

```bash
# Ver logs detallados
docker-compose logs app

# Verificar contenedor
docker-compose ps

# Reiniciar
docker-compose restart app

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Error de Base de Datos

```bash
# Verificar conexión a MySQL
docker-compose exec db mysql -u root -p

# Ver logs de MySQL
docker-compose logs db

# Verificar usuario y permisos
docker-compose exec db mysql -u root -p -e "SELECT User, Host FROM mysql.user;"
```

### Problemas de SSL

```bash
# Ver logs de certbot
docker-compose logs certbot

# Ver logs de nginx
docker-compose logs nginx

# Verificar configuración nginx
docker-compose exec nginx nginx -t

# Renovar certificado manualmente
docker-compose run --rm certbot renew --dry-run
```

### Puerto 80/443 ya en uso

```bash
# Ver qué está usando el puerto
sudo lsof -i :80
sudo lsof -i :443

# Detener apache/nginx si existe
sudo systemctl stop apache2
sudo systemctl stop nginx

# Deshabilitar inicio automático
sudo systemctl disable apache2
sudo systemctl disable nginx
```

### Disco Lleno

```bash
# Ver uso de disco
df -h

# Limpiar Docker
docker system prune -a --volumes

# Limpiar logs viejos
find logs/ -name "*.log" -mtime +30 -delete

# Limpiar backups viejos (mayores a 30 días)
find backups/ -name "*.sql.gz" -mtime +30 -delete
```

### Performance Issues

```bash
# Ver uso de recursos
docker stats

# Aumentar workers de gunicorn
# Editar docker-compose.yml:
# --workers 8  # Cambiar de 4 a 8

# Verificar memoria disponible
free -h

# Ver procesos más pesados
htop
```

### Migraciones Fallan

```bash
# Ver estado de migraciones
docker-compose exec app flask db current

# Ver historial
docker-compose exec app flask db history

# Forzar a versión específica
docker-compose exec app flask db stamp head

# Re-ejecutar migraciones
docker-compose exec app flask db upgrade
```

## 📈 Optimizaciones de Producción

### 1. Configurar CDN

Usar CloudFlare o similar para:
- Caching de assets estáticos
- DDoS protection
- Geo-distribution

### 2. Optimizar Imágenes

```bash
# Instalar herramientas
sudo apt install optipng jpegoptim

# Optimizar PNGs
find app/static/uploads -name "*.png" -exec optipng {} \;

# Optimizar JPEGs
find app/static/uploads -name "*.jpg" -exec jpegoptim --max=85 {} \;
```

### 3. Configurar Caching

Asegurarse que Redis está configurado:

```python
# En config.py
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://redis:6379/0'
```

### 4. Monitoreo con Prometheus + Grafana

```bash
# Agregar servicios de monitoreo a docker-compose.yml
# Ver ejemplo en: docker-compose.monitoring.yml
```

## 🆘 Soporte y Recursos

- **Documentación**: Ver [README.md](README.md)
- **Tests**: Ver [tests/README.md](tests/README.md)
- **Migración**: Ver [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Issues**: GitHub Issues

## ✅ Checklist de Deployment

Antes de ir a producción:

- [ ] Variables de entorno configuradas (.env)
- [ ] Secretos seguros (SECRET_KEY, passwords)
- [ ] Base de datos configurada y accesible
- [ ] Migraciones ejecutadas
- [ ] SSL configurado (HTTPS)
- [ ] Backups automatizados configurados
- [ ] Logs configurados y rotando
- [ ] Health checks funcionando
- [ ] Tests pasando (pytest)
- [ ] Firewall configurado (UFW)
- [ ] Dominios apuntando correctamente
- [ ] Email funcionando (SMTP)
- [ ] PayPal en modo live (no sandbox)
- [ ] OAuth configurado (Google, Facebook)
- [ ] Monitoreo configurado
- [ ] CI/CD pipeline configurado
- [ ] Documentación actualizada

## 🔐 Seguridad

### Firewall (UFW)

```bash
# Instalar UFW
sudo apt install ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar
sudo ufw enable

# Ver estado
sudo ufw status
```

### Fail2Ban

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Iniciar
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

**¡Deployment Exitoso!** 🎉

Tu aplicación Flask E-commerce está ahora en producción y lista para recibir tráfico.
