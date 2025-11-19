# RUTAS Y ENDPOINTS DISPONIBLES

## RUTAS DEL BACKEND (Panel Administrativo)

### Autenticación
```
GET/POST /login           - Página login admin
POST     /               - Procesar login
GET      /salir          - Logout admin
```

### Dashboard
```
GET      /inicio         - Dashboard principal con estadísticas
```

### Gestión de Productos
```
GET      /productos      - Listado de productos
POST     /productos      - Crear nuevo producto
GET      /productos?id=X - Editar producto
POST     /productos      - Actualizar producto
GET      /productos?del=X- Eliminar producto
```

### Gestión de Categorías
```
GET      /categorias     - Listado categorías
POST     /categorias     - Crear categoría
GET      /categorias?id=X- Editar categoría
POST     /categorias     - Actualizar categoría
GET      /categorias?del=X- Eliminar categoría
```

### Gestión de Subcategorías
```
GET      /subcategorias     - Listado subcategorías
POST     /subcategorias     - Crear subcategoría
GET      /subcategorias?id=X- Editar subcategoría
POST     /subcategorias     - Actualizar subcategoría
GET      /subcategorias?del=X- Eliminar subcategoría
```

### Gestión de Banner
```
GET      /banner        - Listado banners
POST     /banner        - Crear banner
GET      /banner?id=X   - Editar banner
POST     /banner        - Actualizar banner
GET      /banner?del=X  - Eliminar banner
```

### Gestión de Slide (Carrusel)
```
GET      /slide         - Listado slides
POST     /slide         - Crear slide
GET      /slide?id=X    - Editar slide
POST     /slide         - Actualizar slide
GET      /slide?del=X   - Eliminar slide
POST     /slide         - Reordenar slides
```

### Gestión de Usuarios
```
GET      /usuarios      - Listado usuarios registrados
GET      /usuarios?id=X - Ver detalles usuario
```

### Historial de Ventas
```
GET      /ventas        - Ver todas las compras
```

### Estadísticas de Visitas
```
GET      /visitas       - Ver estadísticas de visitas
GET      /visitas       - Visitas por país
```

### Configuración Comercial
```
GET      /comercio      - Configuración de la tienda
POST     /comercio      - Actualizar logo/favicon
POST     /comercio      - Actualizar colores
POST     /comercio      - Actualizar scripts
POST     /comercio      - Actualizar información
```

### Gestión de Perfiles
```
GET      /perfiles      - Listado perfiles admin
POST     /perfiles      - Crear perfil
GET      /perfiles?id=X - Editar perfil
POST     /perfiles      - Actualizar perfil
GET      /perfiles?del=X- Eliminar perfil
```

### Perfil Personal
```
GET      /perfil        - Ver perfil actual
POST     /perfil        - Editar perfil
```

### Reportes
```
GET      /reportes      - Generar reportes
POST     /reportes      - Descargar reporte
```

### Mensajes
```
GET      /mensajes      - Ver mensajes de contacto
```

---

## RUTAS DEL FRONTEND (Tienda Pública)

### Principal
```
GET      /              - Página inicio con slide y productos destacados
```

### Productos
```
GET      /productos              - Catálogo de todos los productos (paginado)
GET      /productos?pagina=X     - Página X del catálogo
GET      /productos?ordernar=... - Ordenar por (precio, popularidad, etc)
```

### Categorías
```
GET      /categoria/ropa         - Ver productos de categoría
GET      /categoria/{slug}       - Ver productos categoría {slug}
GET      /categoria/{slug}?page=X- Página X de la categoría
```

### Subcategorías
```
GET      /subcategoria/ropa-hombre        - Ver productos subcategoría
GET      /subcategoria/{slug}             - Ver productos subcategoría {slug}
GET      /subcategoria/{slug}?page=X      - Página X de subcategoría
```

### Detalles Producto
```
GET      /producto/nombre-producto        - Detalles de producto
GET      /producto/{slug}                 - Detalles producto {slug}
```

### Búsqueda
```
GET      /buscador                    - Página búsqueda (formulario)
GET      /buscador?busqueda=termino   - Resultados búsqueda
GET      /buscador?busqueda=...&page=X- Página X de resultados
```

### Ofertas
```
GET      /ofertas       - Página con todas las ofertas activas
```

### Carrito
```
GET      /carrito-de-compras      - Ver carrito de compras
POST     /carrito-de-compras      - Actualizar carrito (AJAX)
POST     /carrito-de-compras      - Agregar producto (AJAX)
POST     /carrito-de-compras      - Eliminar producto (AJAX)
```

### Checkout
```
GET      /finalizar-compra         - Formulario checkout
POST     /finalizar-compra         - Procesar compra
POST     /finalizar-compra         - PayPal (AJAX)
POST     /finalizar-compra         - PayU (AJAX)
```

### Autenticación Usuario
```
GET/POST /login           - Login de cliente
POST     /registro        - Registro nuevo usuario
POST     /olvido-password - Recuperar contraseña
GET      /verificar/{hash}- Verificar email
GET      /salir          - Logout cliente
```

### Perfil Usuario
```
GET      /perfil                    - Ver perfil de usuario
POST     /perfil                    - Editar perfil
POST     /perfil                    - Cambiar contraseña
GET      /perfil?seccion=compras    - Historial compras
GET      /perfil?seccion=deseos     - Lista de deseos
GET      /perfil?seccion=comentarios- Mis comentarios
POST     /perfil                    - Agregar comentario (AJAX)
POST     /perfil                    - Editar comentario (AJAX)
POST     /perfil                    - Agregar a deseos (AJAX)
POST     /perfil                    - Eliminar deseo (AJAX)
```

### Redes Sociales (OAuth)
```
GET      /login/facebook  - Iniciar OAuth Facebook
GET      /login/google    - Iniciar OAuth Google
GET      /callback        - Callback OAuth (tokens)
```

### Errores
```
GET      /error404        - Página no encontrada
GET      /error           - Error general
GET      /cancelado       - Compra cancelada (PayPal/PayU)
```

---

## ENDPOINTS AJAX (Operaciones Asincrónicas)

### Backend AJAX

#### Administradores
```
POST /ajax/administradores.ajax.php
  - activarUsuario     : Activar/desactivar admin
```

#### Usuarios
```
POST /ajax/usuarios.ajax.php
  - activarUsuario     : Activar/desactivar usuario
```

#### Productos
```
POST /ajax/productos.ajax.php
  - activarProducto    : Activar/desactivar producto
  - validarProducto    : Validar nombre único
  - actualizarProducto : Cambiar estado

POST /ajax/tablaProductos.ajax.php
  - Renderizar tabla dinámica de productos
```

#### Categorías
```
POST /ajax/categorias.ajax.php
  - activarCategoria   : Activar/desactivar categoría
  - validarCategoria   : Validar nombre único

POST /ajax/tablaCategorias.ajax.php
  - Renderizar tabla categorías
```

#### Subcategorías
```
POST /ajax/subCategorias.ajax.php
  - Operaciones subcategoría

POST /ajax/tablaSubCategorias.ajax.php
  - Renderizar tabla subcategorías
```

#### Banner
```
POST /ajax/banner.ajax.php
  - Operaciones banner

POST /ajax/tablaBanner.ajax.php
  - Renderizar tabla banners
```

#### Slide
```
POST /ajax/slide.ajax.php
  - Operaciones slide
```

#### Comercio
```
POST /ajax/comercio.ajax.php
  - actualizarComercio : Cambios en configuración
```

#### Ventas
```
POST /ajax/tablaVentas.ajax.php
  - Renderizar tabla ventas
```

#### Visitas
```
POST /ajax/tablaVisitas.ajax.php
  - Renderizar tabla visitas
```

#### Notificaciones
```
POST /ajax/notificaciones.ajax.php
  - Obtener notificaciones
  - Actualizar contadores
```

### Frontend AJAX

#### Usuarios
```
POST /ajax/usuarios.ajax.php
  - registroUsuario    : Registrar (validación AJAX)
  - ingresoUsuario     : Login (validación AJAX)
  - actualizarPerfil   : Guardar cambios perfil
  - agregarDeseo       : Agregar a deseos
  - quitarDeseo        : Eliminar de deseos
  - agregarComentario  : Nuevo comentario
```

#### Productos
```
POST /ajax/producto.ajax.php
  - obtenerDetalles    : Detalles producto popup
  - agregarComentario  : Comentario en producto
  - calificar          : Rating de producto
```

#### Carrito
```
POST /ajax/carrito.ajax.php
  - paypal             : Procesar PayPal
  - payu               : Procesar PayU
  - agregarCarrito     : Agregar producto
  - quitarCarrito      : Eliminar producto
  - actualizarCarrito  : Cambiar cantidad
```

#### Plantilla
```
POST /ajax/plantilla.ajax.php
  - obtenerEstilos     : Cargar estilos personalizados
  - obtenerCabecera    : Metadata SEO
```

---

## PARÁMETROS GET COMUNES

| Parámetro | Descripción | Ejemplo |
|-----------|------------|---------|
| `id` | ID de recurso a editar | `?id=5` |
| `del` | ID de recurso a eliminar | `?del=5` |
| `pagina` | Número de página | `?pagina=2` |
| `ordenar` | Criterio ordenamiento | `?ordenar=precio` |
| `busqueda` | Término búsqueda | `?busqueda=pantalon` |
| `categoria` | Filtrar por categoría | `?categoria=ropa` |
| `subcategoria` | Filtrar por subcategoría | `?subcategoria=hombre` |
| `minprecio` | Precio mínimo filtro | `?minprecio=10` |
| `maxprecio` | Precio máximo filtro | `?maxprecio=100` |

---

## MÉTODOS HTTP

```
GET     - Obtener información (visualizar página)
POST    - Enviar datos (crear/actualizar desde formulario)
AJAX    - Solicitud asincrónica (JavaScript)
```

---

## CÓDIGOS DE RESPUESTA

```
200     - Éxito (recurso encontrado/actualizado)
302     - Redirección (login requerido, etc)
404     - No encontrado (página/producto no existe)
405     - Método no permitido
500     - Error servidor
```

---

## SESIONES Y AUTENTICACIÓN

### Backend
```
SESSION["validarSesionBackend"] = "ok"        - Admin autenticado
SESSION["id"]                   = ID admin    - ID del administrador
SESSION["nombre"]               = Nombre      - Nombre del admin
SESSION["perfil"]               = Perfil      - Rol/perfil del admin
```

### Frontend
```
SESSION["id"]                   = ID usuario  - Usuario autenticado
SESSION["nombre"]               = Nombre      - Nombre del cliente
SESSION["email"]                = Email       - Email del cliente
SESSION["verificacion"]         = Estado      - Email verificado (1=sí, 0=no)
```

---

## REDIRECTS Y FLUJOS

```
/login               → /inicio (si ya autenticado)
/productos?del=X     → /productos (después eliminar)
/finalizar-compra    → /cancelado (si pago fallido)
/finalizar-compra    → /perfil (si pago exitoso)
/verificar/{hash}    → /login (después verificar email)
/perfil              → /login (si no autenticado)
```

