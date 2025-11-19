# ANÁLISIS COMPLETO DEL SISTEMA ECOMMERCE EN PHP
## Branch: claude/flask-migration-strategy-01AbqvPsGS3Qw69ZkwX2LWJQ

---

## 1. ARQUITECTURA GENERAL DEL SISTEMA

### 1.1 Estructura de Directorios

```
/home/user/Ecommerce_php/
├── backend/                          # Panel Administrativo
│   ├── ajax/                        # Controladores AJAX del admin
│   ├── controladores/               # Controladores MVC del admin
│   ├── modelos/                     # Modelos/BD del admin
│   ├── vistas/                      # Vistas/interfaces del admin
│   └── index.php                    # Punto de entrada admin
├── frontend/                         # Tienda Pública
│   ├── ajax/                        # Controladores AJAX del frontend
│   ├── controladores/               # Controladores MVC del frontend
│   ├── modelos/                     # Modelos/BD del frontend
│   ├── vistas/                      # Vistas/interfaces del frontend
│   ├── extensiones/                 # Librerías externas (PHPMailer, PayPal)
│   └── index.php                    # Punto de entrada frontend
└── ecommerce.sql                    # Base de datos SQL
```

### 1.2 Patrón Arquitectónico
- **Patrón MVC (Modelo-Vista-Controlador)**
- Separación clara entre lógica (controladores) y datos (modelos)
- Vistas con lógica de presentación
- Controladores AJAX para operaciones asincrónicas
- Sistema modular por funcionalidad

### 1.3 Conexión a Base de Datos
- **Archivo**: `/backend/modelos/conexion.php` y `/frontend/modelos/conexion.php`
- **Tipo**: PDO (PHP Data Objects)
- **Método**: `Conexion::conectar()`
- **Base de datos**: `ayuda`

---

## 2. MÓDULOS DEL BACKEND (PANEL ADMINISTRATIVO)

### 2.1 MÓDULO DE ADMINISTRADORES (Login y Perfiles)

#### Archivos:
- `/backend/controladores/administradores.controlador.php`
- `/backend/modelos/administradores.modelo.php`
- `/backend/ajax/administradores.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrIngresoAdministrador()         - Login de administrador
• ctrMostrarAdministradores()       - Listar administradores
• ctrCrearPerfil()                  - Crear nuevo perfil
• ctrEditarPerfil()                 - Editar perfil existente
• ctrEliminarPerfil()               - Eliminar perfil

MODELOS:
• mdlMostrarAdministradores()       - SELECT administradores
• mdlActualizarPerfil()             - UPDATE perfil
• mdlIngresarPerfil()               - INSERT nuevo perfil
• mdlEditarPerfil()                 - UPDATE datos perfil
• mdlEliminarPerfil()               - DELETE perfil
```

#### Operaciones Soportadas:
- Login con email y contraseña (encriptación bcrypt)
- Gestión de perfiles de usuario (foto de perfil con resize)
- Control de estados (activo/inactivo)

---

### 2.2 MÓDULO DE PRODUCTOS

#### Archivos:
- `/backend/controladores/productos.controlador.php`
- `/backend/modelos/productos.modelo.php`
- `/backend/ajax/productos.ajax.php`
- `/backend/ajax/tablaProductos.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrMostrarTotalProductos()        - Obtener total de productos
• ctrMostrarSumaVentas()            - Sumar total de ventas
• ctrMostrarProductos()             - Listar productos
• ctrSubirMultimedia()              - Upload de imágenes (resize)
• ctrCrearProducto()                - Crear nuevo producto
• ctrEditarProducto()               - Editar producto
• ctrEliminarProducto()             - Eliminar producto

MODELOS:
• mdlMostrarTotalProductos()        - SELECT productos con orden
• mdlMostrarSumaVentas()            - SUM(ventas)
• mdlActualizarProductos()          - UPDATE producto
• mdlActualizarOfertaProductos()    - UPDATE oferta
• mdlMostrarProductos()             - SELECT específico
• mdlIngresarProducto()             - INSERT producto
• mdlEditarProducto()               - UPDATE completo
• mdlEliminarProducto()             - DELETE producto
```

#### Operaciones Soportadas:
- CREATE: Crear productos con múltiples imágenes (portada, principal, oferta)
- READ: Listar productos con filtros
- UPDATE: Editar datos, precios, ofertas
- DELETE: Eliminar productos e imágenes asociadas
- Upload de imágenes con resize automático (1000x1000, 1280x720, 400x450, 640x430)
- Manejo de multimedia JSON (múltiples fotos)
- Gestión de ofertas (precio, descuento, fecha fin)

#### Tablas Relacionadas:
- `productos` - Datos principales
- `cabeceras` - Metadata SEO
- Imágenes: `/vistas/img/productos/`, `/vistas/img/cabeceras/`, `/vistas/img/ofertas/`

---

### 2.3 MÓDULO DE CATEGORÍAS

#### Archivos:
- `/backend/controladores/categorias.controlador.php`
- `/backend/modelos/categorias.modelo.php`
- `/backend/ajax/categorias.ajax.php`
- `/backend/ajax/tablaCategorias.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrMostrarCategorias()            - Listar categorías
• ctrCrearCategoria()               - Crear categoría
• ctrEditarCategoria()              - Editar categoría
• ctrEliminarCategoria()            - Eliminar categoría

MODELOS:
• mdlMostrarCategorias()            - SELECT categorías
• mdlActualizarCategoria()          - UPDATE estado/atributos
• mdlIngresarCategoria()            - INSERT categoría
• mdlEditarCategoria()              - UPDATE categoría
• mdlEliminarCategoria()            - DELETE categoría
```

#### Operaciones Soportadas:
- CREATE: Categoría con imágenes portada y oferta
- READ: Listar categorías con filtros
- UPDATE: Editar nombre, descripción, imágenes, ofertas
- DELETE: Eliminar categoría e imágenes
- Gestión de ofertas por categoría
- Validación de URL amigable (ruta)

---

### 2.4 MÓDULO DE SUBCATEGORÍAS

#### Archivos:
- `/backend/controladores/subcategorias.controlador.php`
- `/backend/modelos/subcategorias.modelo.php`
- `/backend/ajax/subCategorias.ajax.php`
- `/backend/ajax/tablaSubCategorias.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrMostrarSubCategorias()         - Listar subcategorías
• ctrCrearSubCategoria()            - Crear subcategoría
• ctreditarSubCategoria()           - Editar subcategoría
• ctrEliminarSubCategoria()         - Eliminar subcategoría

MODELOS:
• mdlActualizarSubCategorias()      - UPDATE estado
• mdlActualizarOfertaSubcategorias()- UPDATE oferta
• mdlMostrarSubCategorias()         - SELECT subcategorías
• mdlIngresarSubCategoria()         - INSERT subcategoría
• mdlEditarSubCategoria()           - UPDATE subcategoría
• mdlEliminarSubCategoria()         - DELETE subcategoría
```

#### Operaciones Soportadas:
- Pertenecen a una categoría padre
- Gestión de imágenes portada y oferta
- Control de ofertas especiales
- Activación/desactivación

---

### 2.5 MÓDULO DE USUARIOS (Gestión Backend)

#### Archivos:
- `/backend/controladores/usuarios.controlador.php`
- `/backend/modelos/usuarios.modelo.php`
- `/backend/ajax/usuarios.ajax.php`
- `/backend/ajax/tablaUsuarios.ajax.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarTotalUsuarios()         - Contar usuarios
• ctrMostrarUsuarios()              - Listar usuarios

MODELOS:
• mdlMostrarTotalUsuarios()         - SELECT usuarios ordenados
• mdlMostrarUsuarios()              - SELECT usuario específico
• mdlActualizarUsuario()            - UPDATE usuario (verificación)
```

#### Operaciones Soportadas:
- Listar usuarios registrados
- Activar/desactivar verificación de email
- Ver información de usuarios
- Panel de gestión de usuarios

---

### 2.6 MÓDULO DE VENTAS

#### Archivos:
- `/backend/controladores/ventas.controlador.php`
- `/backend/modelos/ventas.modelo.php`
- `/backend/ajax/ventas.ajax.php`
- `/backend/ajax/tablaVentas.ajax.php`
- `/backend/vistas/modulos/ventas.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarTotalVentas()           - Obtener total de ventas
• ctrMostrarVentas()                - Listar todas las compras

MODELOS:
• mdlMostrarTotalVentas()           - SELECT compras
• mdlMostrarVentas()                - SELECT compras detalladas
• mdlActualizarVenta()              - UPDATE estado venta
```

#### Operaciones Soportadas:
- Ver historial de compras
- Actualizar estado de compra
- Reportes de ventas
- Gráficos de ventas

---

### 2.7 MÓDULO DE VISITAS Y ANALYTICS

#### Archivos:
- `/backend/controladores/visitas.controlador.php`
- `/backend/modelos/visitas.modelo.php`
- `/backend/ajax/tablaVisitas.ajax.php`
- `/backend/vistas/modulos/visitas.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarTotalVisitas()          - Contar visitas totales
• ctrMostrarPaises()                - Visitas por país
• ctrMostrarVisitas()               - Listar visitas

MODELOS:
• mdlMostrarTotalVisitas()          - SELECT visitas
• mdlMostrarPaises()                - SELECT paises ordenados
• mdlMostrarVisitas()               - SELECT visitas detalladas
```

#### Operaciones Soportadas:
- Tracking de visitas por IP
- Localización por país
- Estadísticas de tráfico
- Gráficos de visitas

---

### 2.8 MÓDULO DE BANNER

#### Archivos:
- `/backend/controladores/banner.controlador.php`
- `/backend/modelos/banner.modelo.php`
- `/backend/ajax/banner.ajax.php`
- `/backend/ajax/tablaBanner.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrMostrarBanner()                - Listar banners
• ctrCrearBanner()                  - Crear banner
• ctrEditarBanner()                 - Editar banner
• ctrEliminarBanner()               - Eliminar banner

MODELOS:
• mdlMostrarBanner()                - SELECT banners
• mdlActualizarBanner()             - UPDATE estado
• mdlIngresarBanner()               - INSERT banner
• mdlEditarBanner()                 - UPDATE banner
• mdlEliminarBanner()               - DELETE banner
```

#### Operaciones Soportadas:
- Crear banners por categoría/subcategoría
- Upload de imágenes de banner
- Activar/desactivar banners
- Gestión de tipos de banner

---

### 2.9 MÓDULO DE SLIDE (Carrusel)

#### Archivos:
- `/backend/controladores/slide.controlador.php`
- `/backend/modelos/slide.modelo.php`
- `/backend/ajax/slide.ajax.php`
- `/backend/vistas/modulos/slide.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrMostrarSlide()                 - Listar slides
• ctrCrearSlide()                   - Crear slide
• ctrActualizarOrdenSlide()         - Reordenar slides
• ctrActualizarSlide()              - Editar slide
• ctrEliminarSlide()                - Eliminar slide

MODELOS:
• mdlMostrarSlide()                 - SELECT slides
• mdlCrearSlide()                   - INSERT slide
• mdlActualizarOrdenSlide()         - UPDATE orden
• mdlActualizarSlide()              - UPDATE slide
• mdlEliminarSlide()                - DELETE slide
```

#### Operaciones Soportadas:
- Crear carrusel con imágenes fondo y producto
- Reordenar slides mediante drag & drop
- Upload de imágenes con resize
- Activar/desactivar slides

---

### 2.10 MÓDULO DE CONFIGURACIÓN COMERCIAL

#### Archivos:
- `/backend/controladores/comercio.controlador.php`
- `/backend/modelos/comercio.modelo.php`
- `/backend/ajax/comercio.ajax.php`
- `/backend/vistas/modulos/comercio.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrSeleccionarPlantilla()         - Obtener tema actual
• ctrActualizarLogoIcono()          - Cambiar logo/favicon
• ctrActualizarColores()            - Cambiar paleta de colores
• ctrActualizarScript()             - Agregar scripts custom
• ctrSeleccionarComercio()          - Obtener datos comercio
• ctrActualizarInformacion()        - Actualizar información

MODELOS:
• mdlSeleccionarPlantilla()         - SELECT plantilla
• mdlActualizarLogoIcono()          - UPDATE logo
• mdlActualizarColores()            - UPDATE colores
• mdlActualizarScript()             - UPDATE scripts
• mdlSeleccionarComercio()          - SELECT comercio
• mdlActualizarInformacion()        - UPDATE información
```

#### Operaciones Soportadas:
- Cambiar tema/plantilla
- Gestionar logo y favicon
- Personalizar colores de la tienda
- Agregar códigos personalizados
- Gestionar información del comercio (redes sociales, contacto)

---

### 2.11 MÓDULO DE NOTIFICACIONES

#### Archivos:
- `/backend/controladores/notificaciones.controlador.php`
- `/backend/modelos/notificaciones.modelo.php`
- `/backend/ajax/notificaciones.ajax.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarNotificaciones()        - Obtener notificaciones

MODELOS:
• mdlMostrarNotificaciones()        - SELECT notificaciones
• mdlActualizarNotificaciones()     - UPDATE contadores
```

#### Operaciones Soportadas:
- Contador de nuevas ventas
- Contador de nuevos usuarios
- Contador de nuevos mensajes
- Sistema de notificaciones en tiempo real

---

### 2.12 MÓDULO DE REPORTES

#### Archivos:
- `/backend/controladores/reportes.controlador.php`
- `/backend/modelos/reportes.modelo.php`
- `/backend/vistas/modulos/reportes.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrDescargarReporte()             - Generar y descargar reporte

MODELOS:
• mdlDescargarReporte()             - SELECT datos para reporte
```

#### Operaciones Soportadas:
- Generar reportes de ventas
- Exportar datos a archivos
- Filtros por fecha/producto

---

### 2.13 MÓDULO DE MENSAJES

#### Archivos:
- `/backend/controladores/mensajes.controlador.php`
- `/backend/modelos/mensajes.modelo.php`
- `/backend/vistas/modulos/mensajes.php`

#### Funcionalidades:
```
CONTROLADORES y MODELOS:
• Gestión de mensajes de contacto
• Visualización de consultas de clientes
```

---

### 2.14 MÓDULO DE ENCABEZADOS (Cabeceras)

#### Archivos:
- `/backend/controladores/cabeceras.controlador.php`
- `/backend/modelos/cabeceras.modelo.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarCabeceras()             - Obtener cabeceras

MODELOS:
• mdlMostrarCabeceras()             - SELECT cabeceras
• mdlIngresarCabecera()             - INSERT cabecera
• mdlEditarCabecera()               - UPDATE cabecera
• mdlEliminarCabecera()             - DELETE cabecera
```

#### Operaciones Soportadas:
- Gestionar SEO metadata de productos y categorías
- Título, descripción, palabras clave
- Imágenes portada

---

## 3. MÓDULOS DEL FRONTEND (TIENDA PÚBLICA)

### 3.1 MÓDULO DE USUARIOS (Cliente)

#### Archivos:
- `/frontend/controladores/usuarios.controlador.php`
- `/frontend/modelos/usuarios.modelo.php`
- `/frontend/ajax/usuarios.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrRegistroUsuario()              - Registrar nuevo usuario
• ctrMostrarUsuario()               - Obtener datos usuario
• ctrActualizarUsuario()            - Actualizar perfil
• ctrIngresoUsuario()               - Login de cliente
• ctrOlvidoPassword()               - Recuperar contraseña
• ctrRegistroRedesSociales()        - Login social (Facebook/Google)
• ctrActualizarPerfil()             - Editar perfil completo
• ctrMostrarCompras()               - Historial de compras
• ctrMostrarComentariosPerfil()     - Comentarios del usuario
• ctrActualizarComentario()         - Editar comentario
• ctrAgregarDeseo()                 - Agregar a lista de deseos
• ctrMostrarDeseos()                - Ver lista de deseos
• ctrQuitarDeseo()                  - Eliminar de lista de deseos
• ctrEliminarUsuario()              - Eliminar cuenta
• ctrFormularioContactenos()        - Enviar formulario contacto

MODELOS:
• mdlRegistroUsuario()              - INSERT usuario
• mdlMostrarUsuario()               - SELECT usuario
• mdlActualizarUsuario()            - UPDATE campo usuario
• mdlActualizarPerfil()             - UPDATE perfil completo
• mdlMostrarCompras()               - SELECT compras usuario
• mdlMostrarComentariosPerfil()     - SELECT comentarios
• mdlActualizarComentario()         - UPDATE comentario
• mdlAgregarDeseo()                 - INSERT deseo
• mdlMostrarDeseos()                - SELECT deseos
• mdlQuitarDeseo()                  - DELETE deseo
• mdlEliminarUsuario()              - DELETE usuario
• mdlEliminarComentarios()          - DELETE comentarios usuario
• mdlEliminarCompras()              - DELETE compras usuario
• mdlEliminarListaDeseos()          - DELETE deseos usuario
• mdlIngresoComentarios()           - INSERT comentario compra
```

#### Operaciones Soportadas:
- CREATE: Registro con validación email
- READ: Perfil, compras, comentarios, deseos
- UPDATE: Datos personales, foto de perfil, contraseña
- DELETE: Cuenta usuario y datos asociados
- Sistema de comentarios en productos
- Lista de deseos (wishlist)
- Historial de compras
- Recuperación de contraseña por email
- Login social (Facebook/Google OAuth)

---

### 3.2 MÓDULO DE PRODUCTOS (Cliente)

#### Archivos:
- `/frontend/controladores/productos.controlador.php`
- `/frontend/modelos/productos.modelo.php`
- `/frontend/ajax/producto.ajax.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarCategorias()            - Listar categorías
• ctrMostrarSubCategorias()         - Listar subcategorías
• ctrMostrarProductos()             - Listar productos paginado
• ctrMostrarInfoProducto()          - Detalle producto
• ctrListarProductos()              - Listado completo
• ctrMostrarBanner()                - Obtener banner
• ctrBuscarProductos()              - Búsqueda con filtros
• ctrListarProductosBusqueda()      - Listar resultados búsqueda
• ctrActualizarProducto()           - Actualizar contador ventas

MODELOS:
• mdlMostrarCategorias()            - SELECT categorías
• mdlMostrarSubCategorias()         - SELECT subcategorías
• mdlMostrarProductos()             - SELECT paginado
• mdlMostrarInfoProducto()          - SELECT detalle
• mdlListarProductos()              - SELECT listado
• mdlMostrarBanner()                - SELECT banner
• mdlBuscarProductos()              - SEARCH + paginación
• mdlListarProductosBusqueda()      - SELECT resultados
• mdlActualizarProducto()           - UPDATE ventas
```

#### Operaciones Soportadas:
- Listar productos con paginación
- Filtrar por categoría/subcategoría
- Búsqueda por texto con destacado
- Ver detalle de producto
- Ordenar por precio, popularidad, fecha
- Mostrar ofertas especiales
- Incrementar contador de visualizaciones

---

### 3.3 MÓDULO DE CARRITO DE COMPRAS

#### Archivos:
- `/frontend/controladores/carrito.controlador.php`
- `/frontend/modelos/carrito.modelo.php`
- `/frontend/ajax/carrito.ajax.php`

#### Funcionalidades CRUD:
```
CONTROLADORES:
• ctrMostrarTarifas()               - Obtener tarifa envío
• ctrNuevasCompras()                - Crear orden de compra
• ctrVerificarProducto()            - Validar compra

MODELOS:
• mdlMostrarTarifas()               - SELECT tarifas comercio
• mdlNuevasCompras()                - INSERT compra
• mdlVerificarProducto()            - SELECT compra producto
```

#### Operaciones Soportadas:
- CREATE: Nueva compra en tabla compras
- READ: Tarifas de envío, verificar compra
- UPDATE: Contador de ventas
- Integración PayPal
- Integración PayU
- Cálculo de impuestos
- Gestión de envío y subtotal
- Validación de transacciones

---

### 3.4 MÓDULO DE NOTIFICACIONES (Cliente)

#### Archivos:
- `/frontend/controladores/notificaciones.controlador.php`
- `/frontend/modelos/notificaciones.modelo.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarNotificaciones()        - Obtener notificaciones

MODELOS:
• mdlMostrarNotificaciones()        - SELECT notificaciones
• mdlActualizarNotificaciones()     - UPDATE contador
```

---

### 3.5 MÓDULO DE SLIDE (Cliente)

#### Archivos:
- `/frontend/controladores/slide.controlador.php`
- `/frontend/modelos/slide.modelo.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrMostrarSlide()                 - Obtener slides

MODELOS:
• mdlMostrarSlide()                 - SELECT slides
```

---

### 3.6 MÓDULO DE PLANTILLA/TEMA

#### Archivos:
- `/frontend/controladores/plantilla.controlador.php`
- `/frontend/modelos/plantilla.modelo.php`

#### Funcionalidades:
```
CONTROLADORES:
• plantilla()                       - Renderizar plantilla
• ctrEstiloPlantilla()              - Obtener estilos
• ctrTraerCabeceras()               - Obtener metadata

MODELOS:
• mdlEstiloPlantilla()              - SELECT estilos comercio
• mdlTraerCabeceras()               - SELECT cabeceras
```

---

### 3.7 MÓDULO DE VISITAS (Tracking)

#### Archivos:
- `/frontend/controladores/visitas.controlador.php`
- `/frontend/modelos/visitas.modelo.php`

#### Funcionalidades:
```
CONTROLADORES:
• ctrEnviarIp()                     - Registrar visita
• ctrMostrarTotalVisitas()          - Contar visitas
• ctrMostrarPaises()                - Listar países

MODELOS:
• mdlSeleccionarIp()                - SELECT por IP
• mdlGuardarNuevaIp()               - INSERT IP
• mdlSeleccionarPais()              - SELECT país
• mdlInsertarPais()                 - INSERT país
• mdlActualizarPais()               - UPDATE país
• mdlMostrarTotalVisitas()          - COUNT visitas
• mdlMostrarPaises()                - SELECT países
```

#### Operaciones Soportadas:
- Tracking de IP del visitante
- Geolocalización por país
- Contador de visitas
- Estadísticas por geografía

---

## 4. VISTAS (PÁGINAS/RUTAS)

### Backend (Admin)
```
/inicio                     - Dashboard principal
/usuarios                   - Gestión de usuarios
/productos                  - Gestión de productos
/categorias                 - Gestión de categorías
/subcategorias              - Gestión de subcategorías
/slide                      - Gestión de carrusel
/banner                     - Gestión de banners
/ventas                     - Reporte de ventas
/visitas                    - Estadísticas de visitas
/comercio                   - Configuración de tienda
/perfiles                   - Gestión de perfiles admin
/perfil                     - Perfil del admin
/reportes                   - Generador de reportes
/mensajes                   - Centro de mensajes
/login                      - Login de admin
/salir                      - Logout
```

### Frontend (Tienda Pública)
```
/                           - Página inicio
/productos                  - Catálogo de productos
/categoria/{ruta}           - Productos de categoría
/subcategoria/{ruta}        - Productos de subcategoría
/producto/{ruta}            - Detalle de producto
/carrito-de-compras         - Vista carrito
/finalizar-compra           - Checkout
/ofertas                    - Página de ofertas
/buscador                   - Resultados búsqueda
/verificar/{email}          - Verificación email
/perfil                     - Perfil del cliente
/salir                      - Logout cliente
/error404                   - Página no encontrada
/cancelado                  - Compra cancelada (PayPal)
```

---

## 5. TABLAS DE BASE DE DATOS PRINCIPALES

```
1. administradores
   - id, nombre, email, foto, password, perfil, estado, fecha

2. usuarios
   - id, nombre, email, password, foto, modo, verificacion, 
     celular, fecha_nacimiento, pais, ciudad, direccion, 
     codigoPostal, emailEncriptado, fecha

3. productos
   - id, titulo, idCategoria, idSubCategoria, tipo, detalles,
     multimedia, ruta, estado, idCabecera, titular, descripcion,
     palabrasClaves, precio, peso, entrega, imgPortada,
     imgFotoPrincipal, oferta, precioOferta, descuentoOferta,
     imgOferta, finOferta, ventas, fecha

4. categorias
   - id, categoria, ruta, estado, oferta, precioOferta,
     descuentoOferta, imgOferta, finOferta, fecha

5. subcategorias
   - id, idCategoria, subcategoria, ruta, estado, oferta,
     precioOferta, descuentoOferta, imgOferta, finOferta, fecha

6. cabeceras
   - id, ruta, titulo, descripcion, palabrasClaves, portada, fecha

7. compras
   - id, id_usuario, id_producto, cantidad, descripcion_compra,
     precio, estado, transaccion, fecha

8. comentarios
   - id, id_usuario, id_producto, calificacion, comentario, fecha

9. slide
   - id, ruta, tipo, fondo, producto, estado, orden, fecha

10. banner
    - id, ruta, tipo, img, estado, fecha

11. comercio
    - id, logo, icono, colorPrimario, colorSecundario,
      colorLetras, colorFondo, script, informacion, redes, fecha

12. visitas
    - id, ip, pais, fecha

13. paises
    - id, pais, codigo, cantidad, fecha

14. notificaciones
    - id, nuevasVentas, nuevosUsuarios, nuevosComentarios, fecha

15. listaDeseos
    - id, id_usuario, id_producto, fecha

16. perfiles
    - id, perfil, permiso, estado, fecha
```

---

## 6. OPERACIONES CRUD COMPLETAS

### CREATE (Crear)
- Usuarios: Registro, comentarios
- Productos: Nuevo producto con imágenes
- Categorías: Nueva categoría
- Subcategorías: Nueva subcategoría
- Banner: Nuevo banner
- Slide: Nuevo slide
- Compras: Nueva compra/pedido
- Deseos: Agregar a lista de deseos
- Administrador: Crear perfil admin
- Contacto: Enviar mensaje

### READ (Leer)
- Listar usuarios, productos, categorías, compras
- Ver detalle de producto
- Listar órdenes de un usuario
- Ver comentarios de producto
- Listar wishlist
- Ver información de comercio
- Obtener estadísticas y reportes

### UPDATE (Actualizar)
- Perfil de usuario
- Datos de producto
- Estado de categoría/producto
- Oferta de productos
- Estado de compra
- Información comercial
- Colores de tienda
- Logo/favicon
- Comentarios

### DELETE (Eliminar)
- Eliminar usuario y datos asociados
- Eliminar producto e imágenes
- Eliminar categoría
- Eliminar subcategoría
- Eliminar banner
- Eliminar slide
- Eliminar deseo
- Eliminar comentario
- Eliminar perfil admin

---

## 7. FUNCIONALIDADES ESPECIALES

### 7.1 Sistema de Pagos
- **PayPal**: Integración mediante clase `Paypal::mdlPagoPaypal()`
- **PayU**: Soporte para pagos en línea
- **Validación**: MD5 checksum para verificar totales

### 7.2 Sistema de Emails
- **PHPMailer**: Librería para envío de correos
- Verificación de registro por email
- Recuperación de contraseña
- Confirmación de compras
- Ubicación: `/frontend/extensiones/PHPMailer/`

### 7.3 Gestión de Imágenes
- **Resize automático**: GD2 library
- **Formatos**: JPEG, PNG
- **Rutas**:
  - Productos: `/vistas/img/productos/`
  - Categorías: `/vistas/img/cabeceras/`
  - Ofertas: `/vistas/img/ofertas/`
  - Perfiles: `/vistas/img/perfiles/`

### 7.4 Sistema de Seguridad
- **Encriptación**: Bcrypt para contraseñas
- **MD5**: Para emails y validación
- **CSRF**: Protección mediante tokens (implícita)
- **Validación**: Regex en controladores

### 7.5 Sistema de Ofertas
- Ofertas por producto
- Ofertas por categoría
- Ofertas por subcategoría
- Control de fecha de expiración
- Descuentos por porcentaje
- Precio especial de oferta

### 7.6 Sistema de Notificaciones
- Contador de nuevas ventas
- Contador de nuevos usuarios
- Contador de nuevos comentarios
- Panel de notificaciones en admin

### 7.7 Analytics y Reportes
- Tracking de visitas por IP
- Geolocalización por país
- Gráficos de ventas
- Gráficos de visitas
- Reportes descargables

### 7.8 Lista de Deseos (Wishlist)
- Agregar productos a lista de deseos
- Ver wishlist personal
- Eliminar de deseos
- Persistencia en BD

### 7.9 Sistema de Comentarios
- Comentarios en productos
- Calificación (estrellas)
- Moderar comentarios
- Ver comentarios en perfil usuario

### 7.10 Redes Sociales
- Login social (Facebook/Google)
- Sincronización de perfil
- Importar foto de perfil
- Vinculación de cuentas

---

## 8. AJAX ENDPOINTS (Operaciones Asincrónicas)

### Backend AJAX
```
POST /ajax/administradores.ajax.php         - Activar usuario
POST /ajax/usuarios.ajax.php                - Activar usuario
POST /ajax/productos.ajax.php               - Activar/validar producto
POST /ajax/categorias.ajax.php              - Activar categoría
POST /ajax/subcategorias.ajax.php           - Operaciones subcategoría
POST /ajax/slide.ajax.php                   - Operaciones slide
POST /ajax/banner.ajax.php                  - Operaciones banner
POST /ajax/comercio.ajax.php                - Actualizar comercio
POST /ajax/notificaciones.ajax.php          - Notificaciones
POST /ajax/tablaProductos.ajax.php          - Tabla productos
POST /ajax/tablaCategorias.ajax.php         - Tabla categorías
POST /ajax/tablaSubCategorias.ajax.php      - Tabla subcategorías
POST /ajax/tablaUsuarios.ajax.php           - Tabla usuarios
POST /ajax/tablaVentas.ajax.php             - Tabla ventas
POST /ajax/tablaBanner.ajax.php             - Tabla banners
```

### Frontend AJAX
```
POST /ajax/usuarios.ajax.php                - Registro, login, perfil
POST /ajax/producto.ajax.php                - Detalles producto
POST /ajax/carrito.ajax.php                 - PayPal, compras
POST /ajax/plantilla.ajax.php               - Datos plantilla
```

---

## 9. LIBRERÍAS Y EXTENSIONES UTILIZADAS

```
1. PHPMailer                - Envío de correos
   /frontend/extensiones/PHPMailer/

2. PHPSecLib               - Criptografía y SSH
   /frontend/extensiones/vendor/phpseclib/

3. Guzzle/PSR7             - HTTP client
   /frontend/extensiones/vendor/guzzlehttp/

4. Autoload (Composer)     - Cargador automático
   /frontend/extensiones/vendor/autoload.php

5. PayPal SDK              - Pagos PayPal
   /frontend/extensiones/paypal.controlador.php

6. GD2 Library             - Procesamiento de imágenes (built-in PHP)
```

---

## 10. ARCHIVOS CLAVE DE CONFIGURACIÓN

```
/backend/modelos/conexion.php         - Conexión PDO a BD
/backend/modelos/rutas.php            - Rutas de la aplicación
/frontend/modelos/conexion.php        - Conexión PDO (frontend)
/frontend/modelos/rutas.php           - Rutas del frontend
/frontend/extensiones/bootstrap.php   - Bootstrap/inicialización
```

---

## 11. ESTADÍSTICAS DEL PROYECTO

### Archivos PHP
- Backend controladores: 15 archivos
- Backend modelos: 15 archivos
- Backend AJAX: 14 archivos
- Frontend controladores: 6 archivos
- Frontend modelos: 8 archivos
- Frontend AJAX: 4 archivos
- Vistas backend: 18 archivos
- Vistas frontend: 22 archivos
- **Total: 115+ archivos PHP principales**

### Módulos Principales
- 14 módulos de backend
- 7 módulos de frontend
- 30+ funcionalidades de CRUD
- 100+ métodos/funciones principales

### Tablas de Base de Datos
- 16+ tablas principales
- Relaciones: Usuario-Compra, Usuario-Comentario, Producto-Categoría, etc.

---

## 12. FLUJOS PRINCIPALES

### Flujo de Compra (Cliente)
1. Usuario navega productos
2. Busca y filtra por categoría
3. Ve detalles del producto
4. Agrega al carrito
5. Procede a checkout
6. Selecciona método pago (PayPal/PayU)
7. Completa transacción
8. Recibe confirmación por email
9. Puede ver compra en su perfil

### Flujo de Gestión de Productos (Admin)
1. Admin login
2. Accede a módulo productos
3. Crea/edita/elimina producto
4. Carga imágenes (portada, principal, oferta)
5. Configura precio, oferta, entregas
6. Activa/desactiva producto
7. Sistema actualiza catálogo frontend

### Flujo de Reporte (Admin)
1. Admin accede reportes
2. Filtra por fecha/producto
3. Genera reporte
4. Descarga archivo PDF/Excel
5. Analiza datos de ventas

---

## 13. CONCLUSIONES

Este es un **sistema ecommerce completo** con:

✓ Separación clara MVC
✓ Backend administrativo robusto
✓ Frontend de tienda funcional
✓ Gestión completa de productos y categorías
✓ Sistema de pagos integrado
✓ Autenticación de usuarios
✓ Sistema de comentarios y calificaciones
✓ Analytics y reportes
✓ Seguridad básica (encriptación, validación)
✓ Responsive design
✓ Escalabilidad modular

**Ideal para**: Tiendas virtuales pequeñas a medianas

