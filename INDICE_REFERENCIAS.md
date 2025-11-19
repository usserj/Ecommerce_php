# ÍNDICE RÁPIDO DE ARCHIVOS Y FUNCIONALIDADES

## BACKEND - ARCHIVOS Y MÉTODOS POR MÓDULO

### MÓDULO: ADMINISTRADORES
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/administradores.controlador.php` | ctrIngresoAdministrador(), ctrMostrarAdministradores(), ctrCrearPerfil(), ctrEditarPerfil(), ctrEliminarPerfil() | CRUD |
| `/backend/modelos/administradores.modelo.php` | mdlMostrarAdministradores(), mdlActualizarPerfil(), mdlIngresarPerfil(), mdlEditarPerfil(), mdlEliminarPerfil() | CRUD |
| `/backend/ajax/administradores.ajax.php` | AJAX handlers para activación | - |

### MÓDULO: PRODUCTOS
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/productos.controlador.php` | ctrMostrarTotalProductos(), ctrMostrarSumaVentas(), ctrMostrarProductos(), ctrSubirMultimedia(), ctrCrearProducto(), ctrEditarProducto(), ctrEliminarProducto() | CRUD |
| `/backend/modelos/productos.modelo.php` | mdlMostrarTotalProductos(), mdlMostrarSumaVentas(), mdlActualizarProductos(), mdlActualizarOfertaProductos(), mdlMostrarProductos(), mdlIngresarProducto(), mdlEditarProducto(), mdlEliminarProducto() | CRUD |
| `/backend/ajax/productos.ajax.php` | Validación, activación, cambios estado | - |
| `/backend/ajax/tablaProductos.ajax.php` | Renderizar tabla AJAX de productos | - |

### MÓDULO: CATEGORÍAS
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/categorias.controlador.php` | ctrMostrarCategorias(), ctrCrearCategoria(), ctrEditarCategoria(), ctrEliminarCategoria() | CRUD |
| `/backend/modelos/categorias.modelo.php` | mdlMostrarCategorias(), mdlActualizarCategoria(), mdlIngresarCategoria(), mdlEditarCategoria(), mdlEliminarCategoria() | CRUD |
| `/backend/ajax/categorias.ajax.php` | Validación y cambios estado | - |
| `/backend/ajax/tablaCategorias.ajax.php` | Tabla dinámico de categorías | - |

### MÓDULO: SUBCATEGORÍAS
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/subcategorias.controlador.php` | ctrMostrarSubCategorias(), ctrCrearSubCategoria(), ctreditarSubCategoria(), ctrEliminarSubCategoria() | CRUD |
| `/backend/modelos/subcategorias.modelo.php` | mdlActualizarSubCategorias(), mdlActualizarOfertaSubcategorias(), mdlMostrarSubCategorias(), mdlIngresarSubCategoria(), mdlEditarSubCategoria(), mdlEliminarSubCategoria() | CRUD |
| `/backend/ajax/subCategorias.ajax.php` | Operaciones AJAX | - |
| `/backend/ajax/tablaSubCategorias.ajax.php` | Tabla subcategorías | - |

### MÓDULO: USUARIOS (Backend)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/usuarios.controlador.php` | ctrMostrarTotalUsuarios(), ctrMostrarUsuarios() | READ |
| `/backend/modelos/usuarios.modelo.php` | mdlMostrarTotalUsuarios(), mdlMostrarUsuarios(), mdlActualizarUsuario() | READ/UPDATE |
| `/backend/ajax/usuarios.ajax.php` | Activación de usuarios | UPDATE |
| `/backend/ajax/tablaUsuarios.ajax.php` | Tabla dinámica usuarios | - |

### MÓDULO: VENTAS
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/ventas.controlador.php` | ctrMostrarTotalVentas(), ctrMostrarVentas() | READ |
| `/backend/modelos/ventas.modelo.php` | mdlMostrarTotalVentas(), mdlMostrarVentas(), mdlActualizarVenta() | READ/UPDATE |
| `/backend/ajax/ventas.ajax.php` | Operaciones AJAX ventas | - |
| `/backend/ajax/tablaVentas.ajax.php` | Tabla dinámico de ventas | - |
| `/backend/vistas/modulos/ventas.php` | Vista HTML/PHP de ventas | - |

### MÓDULO: VISITAS
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/visitas.controlador.php` | ctrMostrarTotalVisitas(), ctrMostrarPaises(), ctrMostrarVisitas() | READ |
| `/backend/modelos/visitas.modelo.php` | mdlMostrarTotalVisitas(), mdlMostrarPaises(), mdlMostrarVisitas() | READ |
| `/backend/ajax/tablaVisitas.ajax.php` | Tabla dinámico de visitas | - |
| `/backend/vistas/modulos/visitas.php` | Vista HTML/PHP de visitas | - |

### MÓDULO: BANNER
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/banner.controlador.php` | ctrMostrarBanner(), ctrCrearBanner(), ctrEditarBanner(), ctrEliminarBanner() | CRUD |
| `/backend/modelos/banner.modelo.php` | mdlMostrarBanner(), mdlActualizarBanner(), mdlIngresarBanner(), mdlEditarBanner(), mdlEliminarBanner() | CRUD |
| `/backend/ajax/banner.ajax.php` | Operaciones AJAX | - |
| `/backend/ajax/tablaBanner.ajax.php` | Tabla banners | - |

### MÓDULO: SLIDE (Carrusel)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/slide.controlador.php` | ctrMostrarSlide(), ctrCrearSlide(), ctrActualizarOrdenSlide(), ctrActualizarSlide(), ctrEliminarSlide() | CRUD |
| `/backend/modelos/slide.modelo.php` | mdlMostrarSlide(), mdlCrearSlide(), mdlActualizarOrdenSlide(), mdlActualizarSlide(), mdlEliminarSlide() | CRUD |
| `/backend/ajax/slide.ajax.php` | Operaciones AJAX | - |
| `/backend/vistas/modulos/slide.php` | Vista HTML/PHP | - |

### MÓDULO: COMERCIO (Configuración)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/comercio.controlador.php` | ctrSeleccionarPlantilla(), ctrActualizarLogoIcono(), ctrActualizarColores(), ctrActualizarScript(), ctrSeleccionarComercio(), ctrActualizarInformacion() | READ/UPDATE |
| `/backend/modelos/comercio.modelo.php` | mdlSeleccionarPlantilla(), mdlActualizarLogoIcono(), mdlActualizarColores(), mdlActualizarScript(), mdlSeleccionarComercio(), mdlActualizarInformacion() | READ/UPDATE |
| `/backend/ajax/comercio.ajax.php` | Operaciones AJAX | - |
| `/backend/vistas/modulos/comercio.php` | Vistas de configuración | - |

### MÓDULO: NOTIFICACIONES
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/notificaciones.controlador.php` | ctrMostrarNotificaciones() | READ |
| `/backend/modelos/notificaciones.modelo.php` | mdlMostrarNotificaciones(), mdlActualizarNotificaciones() | READ/UPDATE |
| `/backend/ajax/notificaciones.ajax.php` | Operaciones AJAX | - |

### MÓDULO: REPORTES
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/reportes.controlador.php` | ctrDescargarReporte() | READ |
| `/backend/modelos/reportes.modelo.php` | mdlDescargarReporte() | READ |
| `/backend/vistas/modulos/reportes.php` | Vista reportes | - |

### MÓDULO: CABECERAS (Headers/SEO)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/backend/controladores/cabeceras.controlador.php` | ctrMostrarCabeceras() | READ |
| `/backend/modelos/cabeceras.modelo.php` | mdlMostrarCabeceras(), mdlIngresarCabecera(), mdlEditarCabecera(), mdlEliminarCabecera() | CRUD |

### OTROS MÓDULOS BACKEND
| Archivo | Propósito |
|---------|----------|
| `/backend/controladores/plantilla.controlador.php` | Renderizar plantilla |
| `/backend/controladores/mensajes.controlador.php` | Gestión de mensajes |
| `/backend/controladores/perfiles.controlador.php` | Perfiles de admin |
| `/backend/vistas/modulos/inicio.php` | Dashboard |
| `/backend/vistas/modulos/login.php` | Login admin |
| `/backend/vistas/plantilla.php` | Plantilla principal |

---

## FRONTEND - ARCHIVOS Y MÉTODOS POR MÓDULO

### MÓDULO: USUARIOS (Cliente)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/usuarios.controlador.php` | ctrRegistroUsuario(), ctrMostrarUsuario(), ctrActualizarUsuario(), ctrIngresoUsuario(), ctrOlvidoPassword(), ctrRegistroRedesSociales(), ctrActualizarPerfil(), ctrMostrarCompras(), ctrMostrarComentariosPerfil(), ctrActualizarComentario(), ctrAgregarDeseo(), ctrMostrarDeseos(), ctrQuitarDeseo(), ctrEliminarUsuario(), ctrFormularioContactenos() | CRUD |
| `/frontend/modelos/usuarios.modelo.php` | mdlRegistroUsuario(), mdlMostrarUsuario(), mdlActualizarUsuario(), mdlActualizarPerfil(), mdlMostrarCompras(), mdlMostrarComentariosPerfil(), mdlActualizarComentario(), mdlAgregarDeseo(), mdlMostrarDeseos(), mdlQuitarDeseo(), mdlEliminarUsuario(), mdlEliminarComentarios(), mdlEliminarCompras(), mdlEliminarListaDeseos(), mdlIngresoComentarios() | CRUD |
| `/frontend/ajax/usuarios.ajax.php` | Operaciones AJAX usuario | - |

### MÓDULO: PRODUCTOS (Frontend)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/productos.controlador.php` | ctrMostrarCategorias(), ctrMostrarSubCategorias(), ctrMostrarProductos(), ctrMostrarInfoProducto(), ctrListarProductos(), ctrMostrarBanner(), ctrBuscarProductos(), ctrListarProductosBusqueda(), ctrActualizarProducto() | READ |
| `/frontend/modelos/productos.modelo.php` | mdlMostrarCategorias(), mdlMostrarSubCategorias(), mdlMostrarProductos(), mdlMostrarInfoProducto(), mdlListarProductos(), mdlMostrarBanner(), mdlBuscarProductos(), mdlListarProductosBusqueda(), mdlActualizarProducto() | READ/UPDATE |
| `/frontend/ajax/producto.ajax.php` | Detalles producto AJAX | - |

### MÓDULO: CARRITO
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/carrito.controlador.php` | ctrMostrarTarifas(), ctrNuevasCompras(), ctrVerificarProducto() | CRUD |
| `/frontend/modelos/carrito.modelo.php` | mdlMostrarTarifas(), mdlNuevasCompras(), mdlVerificarProducto() | CRUD |
| `/frontend/ajax/carrito.ajax.php` | PayPal, compras AJAX | - |

### MÓDULO: NOTIFICACIONES (Frontend)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/notificaciones.controlador.php` | ctrMostrarNotificaciones() | READ |
| `/frontend/modelos/notificaciones.modelo.php` | mdlMostrarNotificaciones(), mdlActualizarNotificaciones() | READ/UPDATE |

### MÓDULO: SLIDE (Frontend)
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/slide.controlador.php` | ctrMostrarSlide() | READ |
| `/frontend/modelos/slide.modelo.php` | mdlMostrarSlide() | READ |

### MÓDULO: PLANTILLA
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/plantilla.controlador.php` | plantilla(), ctrEstiloPlantilla(), ctrTraerCabeceras() | READ |
| `/frontend/modelos/plantilla.modelo.php` | mdlEstiloPlantilla(), mdlTraerCabeceras() | READ |

### MÓDULO: VISITAS
| Archivo | Métodos | CRUD |
|---------|---------|------|
| `/frontend/controladores/visitas.controlador.php` | ctrEnviarIp(), ctrMostrarTotalVisitas(), ctrMostrarPaises() | CREATE/READ |
| `/frontend/modelos/visitas.modelo.php` | mdlSeleccionarIp(), mdlGuardarNuevaIp(), mdlSeleccionarPais(), mdlInsertarPais(), mdlActualizarPais(), mdlMostrarTotalVisitas(), mdlMostrarPaises() | CRUD |

### VISTAS FRONTEND
| Archivo | Propósito |
|---------|----------|
| `/frontend/vistas/modulos/productos.php` | Catálogo productos |
| `/frontend/vistas/modulos/infoproducto.php` | Detalle producto |
| `/frontend/vistas/modulos/carrito-de-compras.php` | Carrito |
| `/frontend/vistas/modulos/finalizar-compra.php` | Checkout |
| `/frontend/vistas/modulos/perfil.php` | Perfil cliente |
| `/frontend/vistas/modulos/ofertas.php` | Página ofertas |
| `/frontend/vistas/modulos/buscador.php` | Búsqueda productos |
| `/frontend/vistas/modulos/cabezote.php` | Header principal |
| `/frontend/vistas/modulos/footer.php` | Footer |
| `/frontend/vistas/modulos/slide.php` | Carrusel |
| `/frontend/vistas/plantilla.php` | Plantilla principal |

---

## CONFIGURACIÓN Y LIBRERÍAS

| Archivo | Propósito |
|---------|----------|
| `/backend/modelos/conexion.php` | Conexión PDO MySQL |
| `/backend/modelos/rutas.php` | URLs de la aplicación |
| `/frontend/modelos/conexion.php` | Conexión PDO MySQL |
| `/frontend/modelos/rutas.php` | URLs del frontend |
| `/frontend/extensiones/PHPMailer/` | Envío de correos |
| `/frontend/extensiones/paypal.controlador.php` | Integración PayPal |
| `/frontend/extensiones/bootstrap.php` | Inicialización |

---

## RESUMEN DE FUNCIONALIDADES DISPONIBLES

### OPERACIONES POR ENTIDAD

#### ADMINISTRADORES
- Login/Logout
- Crear perfil admin
- Editar perfil
- Eliminar perfil
- Foto de perfil con resize

#### USUARIOS (Cliente)
- Registrarse
- Login/Logout
- Editar perfil
- Ver compras
- Comentarios en productos
- Lista de deseos
- Recuperar contraseña
- Verificación email
- Login social

#### PRODUCTOS
- Crear (con 3 imágenes)
- Listar (paginado)
- Editar
- Eliminar
- Activar/Desactivar
- Gestionar ofertas
- Multimedia JSON
- Contadores de venta

#### CATEGORÍAS
- Crear
- Listar
- Editar
- Eliminar
- Ofer

tas
- Portada e imagen oferta

#### SUBCATEGORÍAS
- Crear
- Listar
- Editar
- Eliminar
- Ofertas
- Relación con categoría padre

#### COMPRAS
- Nueva compra
- Verificar compra
- Actualizar estado
- PayPal integration
- PayU integration
- Historial de compras

#### COMENTARIOS
- Agregar comentario
- Editar comentario
- Calificación (estrellas)
- Ver por producto
- Ver por usuario

#### LISTA DESEOS
- Agregar a deseos
- Ver deseos
- Eliminar de deseos
- Persistencia en BD

#### SLIDE/CARRUSEL
- Crear slide
- Reordenar (drag & drop)
- Editar
- Eliminar
- Imágenes fondo y producto

#### BANNER
- Crear banner
- Editar
- Eliminar
- Por categoría/subcategoría
- Activar/Desactivar

#### COMERCIO (Tienda)
- Cambiar logo
- Cambiar favicon
- Personalizar colores
- Agregar scripts custom
- Información de contacto
- Redes sociales

#### REPORTES
- Descarga reportes
- Filtros por fecha
- Estadísticas de ventas

#### ANALYTICS
- Tracking de visitas
- Geolocalización
- Gráficos de venta
- Gráficos de visitas
- Estadísticas por país

---

## ARCHIVOS TOTALES POR TIPO

**Backend:**
- 15 Controladores
- 15 Modelos
- 14 AJAX handlers
- 19 Vistas
- 2 Configuración

**Frontend:**
- 6 Controladores
- 8 Modelos
- 4 AJAX handlers
- 23 Vistas
- 2 Configuración
- ~100 archivos librerías

**Total: 115+ archivos PHP principales**

