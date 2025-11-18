# DOCUMENTACIÓN COMPLETA DEL PROYECTO ECOMMERCE PHP

## ÍNDICE
1. [Introducción](#introducción)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Backend - Panel de Administración](#backend---panel-de-administración)
4. [Frontend - Tienda Online](#frontend---tienda-online)
5. [Base de Datos](#base-de-datos)
6. [Flujo de Datos](#flujo-de-datos)
7. [Seguridad](#seguridad)
8. [Guía de Funciones Principales](#guía-de-funciones-principales)

---

## INTRODUCCIÓN

Este es un sistema de comercio electrónico completo desarrollado en PHP utilizando el patrón de diseño MVC (Modelo-Vista-Controlador). El proyecto está dividido en dos aplicaciones independientes:

- **Backend**: Panel administrativo para gestionar productos, usuarios, ventas y configuración
- **Frontend**: Tienda en línea donde los clientes pueden comprar productos

### Tecnologías Utilizadas
- PHP 7+ con Programación Orientada a Objetos
- MySQL (PDO para conexión segura)
- JavaScript/jQuery (peticiones AJAX)
- Bootstrap (diseño responsive)
- AdminLTE (panel de administración)
- PHPMailer (envío de correos)
- PayPal y PayU (pasarelas de pago)
- DataTables (tablas dinámicas)
- CKEditor (editor de texto enriquecido)
- Dropzone (subida de archivos)

---

## ARQUITECTURA DEL PROYECTO

### Estructura de Directorios

```
Ecommerce_php/
│
├── backend/                    # Panel de administración
│   ├── index.php              # Punto de entrada del backend
│   ├── controladores/         # Lógica de negocio
│   ├── modelos/               # Acceso a datos (BD)
│   ├── vistas/                # Plantillas HTML
│   │   ├── modulos/          # Páginas del panel
│   │   ├── img/              # Imágenes
│   │   ├── js/               # Scripts JavaScript
│   │   └── css/              # Estilos CSS
│   └── ajax/                  # Peticiones asíncronas
│
├── frontend/                   # Tienda online
│   ├── index.php              # Punto de entrada del frontend
│   ├── controladores/         # Lógica de negocio
│   ├── modelos/               # Acceso a datos (BD)
│   ├── vistas/                # Plantillas HTML
│   │   ├── modulos/          # Páginas de la tienda
│   │   ├── img/              # Imágenes
│   │   ├── js/               # Scripts JavaScript
│   │   └── css/              # Estilos CSS
│   ├── ajax/                  # Peticiones asíncronas
│   └── extensiones/           # Librerías externas
│       ├── PHPMailer/        # Envío de correos
│       └── vendor/           # Composer packages
│
└── ecommerce.sql              # Script de base de datos

```

### Patrón MVC Implementado

#### MODELO (Models)
**Ubicación**: `/modelos/`

**Responsabilidad**: Interactuar con la base de datos

**Características**:
- Métodos estáticos con prefijo `mdl` (ej: `mdlMostrarProductos()`)
- Uso de PDO con prepared statements (prevención de SQL injection)
- Retornan datos al controlador

**Ejemplo**:
```php
// backend/modelos/productos.modelo.php
class ModeloProductos {
    static public function mdlMostrarProductos($tabla, $item, $valor) {
        if($item != null) {
            $stmt = Conexion::conectar()->prepare("SELECT * FROM $tabla WHERE $item = :$item");
            $stmt->bindParam(":".$item, $valor, PDO::PARAM_STR);
            $stmt->execute();
            return $stmt->fetchAll();
        }
    }
}
```

#### VISTA (Views)
**Ubicación**: `/vistas/modulos/`

**Responsabilidad**: Presentación de datos al usuario

**Características**:
- Archivos PHP que generan HTML
- Consumen datos de los controladores
- Incluyen JavaScript para interactividad

#### CONTROLADOR (Controllers)
**Ubicación**: `/controladores/`

**Responsabilidad**: Lógica de negocio y coordinación entre Modelo y Vista

**Características**:
- Métodos estáticos con prefijo `ctr` (ej: `ctrMostrarProductos()`)
- Validación de datos con expresiones regulares
- Procesamiento de imágenes
- Llamadas a modelos para obtener/guardar datos

**Ejemplo**:
```php
// backend/controladores/productos.controlador.php
class ControladorProductos {
    static public function ctrMostrarProductos($item, $valor) {
        $tabla = "productos";
        $respuesta = ModeloProductos::mdlMostrarProductos($tabla, $item, $valor);
        return $respuesta;
    }
}
```

#### AJAX
**Ubicación**: `/ajax/`

**Responsabilidad**: Peticiones asíncronas sin recargar la página

**Características**:
- Procesan formularios dinámicamente
- Activan/desactivan registros
- Cargan datos en tiempo real

---

## BACKEND - PANEL DE ADMINISTRACIÓN

### Punto de Entrada: backend/index.php

Este archivo es el **Front Controller** del backend:

```php
<?php
// Carga de todos los controladores
require_once "controladores/plantilla.controlador.php";
require_once "controladores/administradores.controlador.php";
require_once "controladores/productos.controlador.php";
// ... más controladores

// Carga de todos los modelos
require_once "modelos/administradores.modelo.php";
require_once "modelos/productos.modelo.php";
// ... más modelos

require_once "modelos/rutas.php";

// Inicialización de la plantilla principal
$plantilla = new ControladorPlantilla();
$plantilla->plantilla();
?>
```

**Flujo de Ejecución**:
1. Se cargan todos los controladores y modelos
2. Se instancia `ControladorPlantilla`
3. El método `plantilla()` carga la vista principal
4. La vista analiza el parámetro `?ruta=` de la URL
5. Se carga el módulo correspondiente

---

### CONTROLADORES DEL BACKEND

#### 1. plantilla.controlador.php
**Ubicación**: `backend/controladores/plantilla.controlador.php`

**Clase**: `ControladorPlantilla`

**Métodos**:
- `plantilla()`: Carga la plantilla HTML principal del backend

**Función**: Actúa como el controlador maestro que renderiza la estructura HTML base (cabecera, menú lateral, contenido, footer)

---

#### 2. administradores.controlador.php
**Ubicación**: `backend/controladores/administradores.controlador.php`

**Clase**: `ControladorAdministradores`

**Métodos**:

##### `ctrIngresoAdministrador()`
- **Parámetros**: Ninguno (usa `$_POST`)
- **Función**: Valida login de administradores
- **Proceso**:
  1. Recibe usuario y contraseña del formulario
  2. Valida formato con regex
  3. Encripta contraseña con `crypt()`
  4. Consulta en BD a través del modelo
  5. Inicia sesión si las credenciales son válidas
  6. Redirige al dashboard o muestra error

**Validaciones**:
```php
preg_match('/^[a-zA-Z0-9]+$/', $_POST["usuario"])
preg_match('/^[a-zA-Z0-9]+$/', $_POST["password"])
```

##### `ctrMostrarAdministradores($item, $valor)`
- **Parámetros**:
  - `$item`: Columna a filtrar (ej: "id", "email")
  - `$valor`: Valor a buscar
- **Función**: Obtiene administradores de la BD
- **Retorno**: Array con datos de administradores

##### `ctrCrearAdministrador($datos)`
- **Parámetros**: Array con datos del nuevo admin
- **Función**: Crea un nuevo administrador
- **Proceso**:
  1. Valida campos con regex
  2. Procesa foto de perfil si existe
  3. Redimensiona imagen (200x200px)
  4. Encripta contraseña
  5. Inserta en BD

##### `ctrEditarAdministrador($datos)`
- **Función**: Actualiza datos de un administrador existente
- Similar a crear, pero actualiza registro existente

##### `ctrEliminarAdministrador()`
- **Función**: Elimina un administrador
- Verifica si existe foto de perfil y la elimina del servidor

---

#### 3. productos.controlador.php
**Ubicación**: `backend/controladores/productos.controlador.php`

**Clase**: `ControladorProductos`

Este es uno de los controladores más complejos del sistema.

**Métodos**:

##### `ctrMostrarTotalProductos($orden)`
- **Parámetros**: `$orden` - Campo para ordenar (ej: "ventas", "fecha")
- **Función**: Obtiene todos los productos ordenados
- **Uso**: Dashboard para mostrar estadísticas

##### `ctrMostrarSumaVentas()`
- **Función**: Calcula la suma total de ventas
- **Retorno**: Total de ventas de todos los productos

##### `ctrMostrarProductos($item, $valor)`
- **Función**: Obtiene productos filtrados
- **Ejemplos de uso**:
  ```php
  // Obtener producto por ID
  ctrMostrarProductos("id", 5);

  // Obtener productos de una categoría
  ctrMostrarProductos("id_categoria", 3);

  // Obtener todos los productos
  ctrMostrarProductos(null, null);
  ```

##### `ctrSubirMultimedia($datos, $ruta)`
- **Parámetros**:
  - `$datos`: Array con información del archivo (`$_FILES`)
  - `$ruta`: Directorio donde guardar
- **Función**: Procesa y guarda imágenes de galería del producto
- **Proceso**:
  1. Verifica que el archivo existe
  2. Obtiene dimensiones originales con `getimagesize()`
  3. Define nuevas dimensiones (1000x1000px)
  4. Crea directorio si no existe
  5. Redimensiona según tipo (JPEG o PNG)
  6. Guarda imagen optimizada
- **Retorno**: Ruta de la imagen guardada

**Código de redimensionamiento**:
```php
list($ancho, $alto) = getimagesize($datos["tmp_name"]);
$nuevoAncho = 1000;
$nuevoAlto = 1000;

$directorio = "../vistas/img/multimedia/".$ruta;
if (!file_exists($directorio)) {
    mkdir($directorio, 0755);
}

if($datos["type"] == "image/jpeg") {
    $rutaMultimedia = $directorio."/".$datos["name"];
    $origen = imagecreatefromjpeg($datos["tmp_name"]);
    $destino = imagecreatetruecolor($nuevoAncho, $nuevoAlto);
    imagecopyresized($destino, $origen, 0, 0, 0, 0, $nuevoAncho, $nuevoAlto, $ancho, $alto);
    imagejpeg($destino, $rutaMultimedia);
}
```

##### `ctrCrearProducto($datos)`
- **Función**: Crea un nuevo producto completo
- **Proceso Complejo**:

**1. Validación de datos**:
```php
if(preg_match('/^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ ]+$/', $datos["tituloProducto"]) &&
   preg_match('/^[,\\.\\a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ ]+$/', $_POST["descripcionProducto"])) {
    // Procesar producto
}
```

**2. Procesamiento de imágenes**:

El método procesa 3 tipos de imágenes:

a) **Imagen de Portada** (1280x720px):
```php
$rutaPortada = "../vistas/img/cabeceras/default/default.jpg"; // Default

if(isset($datos["fotoPortada"]["tmp_name"]) && !empty($datos["fotoPortada"]["tmp_name"])) {
    list($ancho, $alto) = getimagesize($datos["fotoPortada"]["tmp_name"]);
    $nuevoAncho = 1280;
    $nuevoAlto = 720;

    if($datos["fotoPortada"]["type"] == "image/jpeg") {
        $rutaPortada = "../vistas/img/cabeceras/".$datos["rutaProducto"].".jpg";
        $origen = imagecreatefromjpeg($datos["fotoPortada"]["tmp_name"]);
        $destino = imagecreatetruecolor($nuevoAncho, $nuevoAlto);
        imagecopyresized($destino, $origen, 0, 0, 0, 0, $nuevoAncho, $nuevoAlto, $ancho, $alto);
        imagejpeg($destino, $rutaPortada);
    }
}
```

b) **Imagen Principal** (400x450px):
- Similar al proceso anterior
- Dimensiones: 400x450px
- Ubicación: `../vistas/img/productos/`

c) **Imagen de Oferta** (640x430px) - Opcional:
- Solo se procesa si el producto tiene oferta
- Dimensiones: 640x430px
- Ubicación: `../vistas/img/ofertas/`

**3. Preparación de datos**:
```php
if($datos["selActivarOferta"] == "oferta") {
    $datosProducto = array(
        "titulo" => $datos["tituloProducto"],
        "idCategoria" => $datos["categoria"],
        "idSubCategoria" => $datos["subCategoria"],
        "tipo" => $datos["tipo"],
        "detalles" => $datos["detalles"],
        "multimedia" => $datos["multimedia"],
        "ruta" => $datos["rutaProducto"],
        "estado" => 1,
        "titular" => substr($datos["descripcionProducto"], 0, 225)."...",
        "descripcion" => $datos["descripcionProducto"],
        "palabrasClaves" => $datos["pClavesProducto"],
        "precio" => $datos["precio"],
        "peso" => $datos["peso"],
        "entrega" => $datos["entrega"],
        "imgPortada" => substr($rutaPortada,3),
        "imgFotoPrincipal" => substr($rutaFotoPrincipal,3),
        "oferta" => 1,
        "precioOferta" => $datos["precioOferta"],
        "descuentoOferta" => $datos["descuentoOferta"],
        "imgOferta" => substr($rutaOferta,3),
        "finOferta" => $datos["finOferta"]
    );
} else {
    // Datos sin oferta (oferta = 0)
}
```

**4. Inserción en base de datos**:
```php
ModeloCabeceras::mdlIngresarCabecera("cabeceras", $datosProducto);
$respuesta = ModeloProductos::mdlIngresarProducto("productos", $datosProducto);
```

##### `ctrEditarProducto($datos)`
- **Función**: Actualiza un producto existente
- **Proceso**:
  1. Elimina fotos antiguas de multimedia que fueron removidas
  2. Compara multimedia antigua vs nueva usando `array_diff()`
  3. Actualiza imágenes solo si se subieron nuevas
  4. Si no hay imagen nueva, mantiene la antigua
  5. Actualiza registro en BD

**Comparación de multimedia**:
```php
$multimediaBD = json_decode($value["multimedia"], true);
$multimediaEditar = json_decode($datos["multimedia"], true);

$objectMultimediaBD = array();
$objectMultimediaEditar = array();

foreach ($multimediaBD as $key => $value) {
    array_push($objectMultimediaBD, $value["foto"]);
}

foreach ($multimediaEditar as $key => $value) {
    array_push($objectMultimediaEditar, $value["foto"]);
}

$borrarFoto = array_diff($objectMultimediaBD, $objectMultimediaEditar);

foreach ($borrarFoto as $key => $value) {
    unlink("../".$value); // Elimina del servidor
}
```

##### `ctrEliminarProducto()`
- **Función**: Elimina un producto completo
- **Proceso**:
  1. Elimina carpeta completa de multimedia con `glob()` y `rmdir()`
  2. Elimina imagen principal
  3. Elimina imagen de oferta (si existe)
  4. Elimina imagen de portada
  5. Elimina cabecera de BD
  6. Elimina producto de BD

**Código de eliminación**:
```php
// Eliminar multimedia
$borrar = glob("vistas/img/multimedia/".$_GET["rutaCabecera"]."/*");
foreach($borrar as $file) {
    unlink($file);
}
rmdir("vistas/img/multimedia/".$_GET["rutaCabecera"]);

// Eliminar imagen principal
if($_GET["imgPrincipal"] != "" && $_GET["imgPrincipal"] != "vistas/img/productos/default/default.jpg") {
    unlink($_GET["imgPrincipal"]);
}

// Eliminar oferta
if($_GET["imgOferta"] != "") {
    unlink($_GET["imgOferta"]);
}

// Eliminar portada
if($_GET["imgPortada"] != "" && $_GET["imgPortada"] != "vistas/img/cabeceras/default/default.jpg") {
    unlink($_GET["imgPortada"]);
}

ModeloCabeceras::mdlEliminarCabecera("cabeceras", $_GET["rutaCabecera"]);
$respuesta = ModeloProductos::mdlEliminarProducto("productos", $datos);
```

---

#### 4. categorias.controlador.php
**Clase**: `ControladorCategorias`

**Métodos**:

##### `ctrMostrarCategorias($item, $valor)`
- **Función**: Obtiene categorías de productos
- **Uso**: Para llenar selectores y listar categorías

##### `ctrCrearCategoria($datos)`
- **Función**: Crea nueva categoría
- **Validaciones**: Solo letras, números y espacios

##### `ctrEditarCategoria($datos)`
- **Función**: Actualiza categoría existente

##### `ctrEliminarCategoria()`
- **Función**: Elimina categoría
- **Importante**: No elimina si tiene productos asociados

---

#### 5. subcategorias.controlador.php
**Clase**: `ControladorSubcategorias`

Similar a categorías, pero para subcategorías.

**Métodos**:
- `ctrMostrarSubcategorias($item, $valor)`
- `ctrCrearSubcategoria($datos)`
- `ctrEditarSubcategoria($datos)`
- `ctrEliminarSubcategoria()`

---

#### 6. usuarios.controlador.php
**Clase**: `ControladorUsuarios`

Gestiona clientes/usuarios de la tienda.

**Métodos**:

##### `ctrMostrarUsuarios($item, $valor)`
- **Función**: Obtiene usuarios registrados

##### `ctrEditarUsuario($datos)`
- **Función**: Actualiza datos de usuario
- **Campos editables**: nombre, email, estado, verificación

##### `ctrEliminarUsuario()`
- **Función**: Elimina cuenta de usuario

---

#### 7. ventas.controlador.php
**Clase**: `ControladorVentas`

**Métodos**:

##### `ctrMostrarVentas($item, $valor)`
- **Función**: Obtiene registro de ventas
- **Uso**: Listado de pedidos en el panel admin

##### `ctrMostrarVentasProducto($item, $valor)`
- **Función**: Ventas filtradas por producto específico

---

#### 8. banner.controlador.php
**Clase**: `ControladorBanner`

Gestiona banners publicitarios del sitio.

**Métodos**:

##### `ctrMostrarBanner($item, $valor)`
- **Función**: Obtiene banners

##### `ctrCrearBanner($datos)`
- **Función**: Crea nuevo banner
- **Proceso**: Sube imagen y guarda en BD

##### `ctrEditarBanner($datos)`
- **Función**: Actualiza banner

##### `ctrEliminarBanner()`
- **Función**: Elimina banner e imagen del servidor

---

#### 9. slide.controlador.php
**Clase**: `ControladorSlide`

Gestiona el slider de imágenes de la página principal.

**Métodos similares a banner**:
- `ctrMostrarSlide($item, $valor)`
- `ctrCrearSlide($datos)`
- `ctrEditarSlide($datos)`
- `ctrEliminarSlide()`

---

#### 10. comercio.controlador.php
**Clase**: `ControladorComercio`

Gestiona la configuración general del ecommerce.

**Métodos**:

##### `ctrMostrarComercio()`
- **Función**: Obtiene configuración actual del comercio
- **Datos**: nombre, dirección, teléfono, email, redes sociales, códigos de pago, etc.

##### `ctrEditarComercio($datos)`
- **Función**: Actualiza configuración
- **Datos editables**:
  - Información del comercio
  - Colores del tema
  - Códigos de PayPal y PayU
  - Enlaces de redes sociales
  - Logotipo
  - Tarifas de envío

---

#### 11. cabeceras.controlador.php
**Clase**: `ControladorCabeceras`

Gestiona metadatos SEO para cada página/producto.

**Métodos**:
- `ctrMostrarCabeceras($item, $valor)`
- `ctrCrearCabecera($datos)` - Título, descripción, keywords
- `ctrEditarCabecera($datos)`
- `ctrEliminarCabecera()`

---

#### 12. mensajes.controlador.php
**Clase**: `ControladorMensajes`

Gestiona mensajes de contacto recibidos.

**Métodos**:
- `ctrMostrarMensajes($item, $valor)`
- `ctrEliminarMensaje()`

---

#### 13. perfiles.controlador.php
**Clase**: `ControladorPerfiles`

Gestiona tipos de perfiles de administrador (Super Admin, Editor, etc.)

**Métodos**:
- `ctrMostrarPerfiles($item, $valor)`
- `ctrCrearPerfil($datos)`
- `ctrEditarPerfil($datos)`
- `ctrEliminarPerfil()`

---

#### 14. visitas.controlador.php
**Clase**: `ControladorVisitas`

Registra y analiza visitas al sitio web.

**Métodos**:

##### `ctrMostrarVisitasPaises($item, $valor)`
- **Función**: Obtiene visitas agrupadas por país

##### `ctrMostrarVisitasPersonas($item, $valor)`
- **Función**: Obtiene visitas individuales con detalles (IP, navegador, etc.)

---

#### 15. notificaciones.controlador.php
**Clase**: `ControladorNotificaciones`

Sistema de notificaciones del panel admin.

**Métodos**:

##### `ctrMostrarNotificaciones()`
- **Función**: Obtiene contador de notificaciones
- **Tipos**: nuevas ventas, nuevos usuarios, nuevos mensajes

##### `ctrActualizarNotificaciones($item, $valor)`
- **Función**: Marca notificaciones como leídas

---

#### 16. reportes.controlador.php
**Clase**: `ControladorReportes`

Genera reportes y estadísticas.

**Métodos**:
- `ctrMostrarReporteVentas()`
- `ctrMostrarReporteProductos()`
- `ctrMostrarGraficoVentas()`

---

### MODELOS DEL BACKEND

Todos los modelos siguen la misma estructura y usan PDO para consultas seguras.

#### conexion.php
**Ubicación**: `backend/modelos/conexion.php`

**Clase**: `Conexion`

**Método**:
```php
static public function conectar() {
    $link = new PDO(
        "mysql:host=localhost;dbname=ferrete5_ecommerce",
        "ferrete5_juanu",
        "*****",
        array(
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8"
        )
    );
    return $link;
}
```

**Características**:
- **PDO::ATTR_ERRMODE**: Lanza excepciones en caso de error
- **PDO::MYSQL_ATTR_INIT_COMMAND**: Establece codificación UTF-8
- **Prepared Statements**: Previene SQL injection

---

#### productos.modelo.php
**Clase**: `ModeloProductos`

**Métodos**:

##### `mdlMostrarTotalProductos($tabla, $orden)`
```php
static public function mdlMostrarTotalProductos($tabla, $orden) {
    $stmt = Conexion::conectar()->prepare("SELECT * FROM $tabla ORDER BY $orden DESC");
    $stmt->execute();
    return $stmt->fetchAll();
    $stmt->close();
    $stmt = null;
}
```

##### `mdlMostrarSumaVentas($tabla)`
```php
static public function mdlMostrarSumaVentas($tabla) {
    $stmt = Conexion::conectar()->prepare("SELECT SUM(ventas) as total FROM $tabla");
    $stmt->execute();
    return $stmt->fetch();
    $stmt->close();
    $stmt = null;
}
```

##### `mdlActualizarProductos($tabla, $item1, $valor1, $item2, $valor2)`
```php
static public function mdlActualizarProductos($tabla, $item1, $valor1, $item2, $valor2) {
    $stmt = Conexion::conectar()->prepare("UPDATE $tabla SET $item1 = :$item1 WHERE $item2 = :$item2");
    $stmt->bindParam(":".$item1, $valor1, PDO::PARAM_STR);
    $stmt->bindParam(":".$item2, $valor2, PDO::PARAM_STR);

    if($stmt->execute()) {
        return "ok";
    } else {
        return "error";
    }

    $stmt->close();
    $stmt = null;
}
```

##### `mdlMostrarProductos($tabla, $item, $valor)`
```php
static public function mdlMostrarProductos($tabla, $item, $valor) {
    if($item != null) {
        $stmt = Conexion::conectar()->prepare("SELECT * FROM $tabla WHERE $item = :$item");
        $stmt->bindParam(":".$item, $valor, PDO::PARAM_STR);
        $stmt->execute();
        return $stmt->fetchAll();
    } else {
        $stmt = Conexion::conectar()->prepare("SELECT * FROM $tabla ORDER BY id DESC");
        $stmt->execute();
        return $stmt->fetchAll();
    }
    $stmt->close();
    $stmt = null;
}
```

##### `mdlIngresarProducto($tabla, $datos)`
```php
static public function mdlIngresarProducto($tabla, $datos) {
    $stmt = Conexion::conectar()->prepare("INSERT INTO $tabla(
        id_categoria, id_subcategoria, tipo, ruta, estado, titulo, titular,
        descripcion, multimedia, detalles, precio, portada, oferta,
        precioOferta, descuentoOferta, imgOferta, finOferta, peso, entrega
    ) VALUES (
        :id_categoria, :id_subcategoria, :tipo, :ruta, :estado, :titulo,
        :titular, :descripcion, :multimedia, :detalles, :precio, :portada,
        :oferta, :precioOferta, :descuentoOferta, :imgOferta, :finOferta,
        :peso, :entrega
    )");

    $stmt->bindParam(":id_categoria", $datos["idCategoria"], PDO::PARAM_STR);
    $stmt->bindParam(":id_subcategoria", $datos["idSubCategoria"], PDO::PARAM_STR);
    // ... más bindParam

    if($stmt->execute()) {
        return "ok";
    } else {
        return "error";
    }

    $stmt->close();
    $stmt = null;
}
```

##### `mdlEditarProducto($tabla, $datos)`
Similar a `mdlIngresarProducto`, pero usa UPDATE en lugar de INSERT.

##### `mdlEliminarProducto($tabla, $datos)`
```php
static public function mdlEliminarProducto($tabla, $datos) {
    $stmt = Conexion::conectar()->prepare("DELETE FROM $tabla WHERE id = :id");
    $stmt->bindParam(":id", $datos, PDO::PARAM_INT);

    if($stmt->execute()) {
        return "ok";
    } else {
        return "error";
    }

    $stmt->close();
    $stmt = null;
}
```

---

#### Otros Modelos del Backend

Los siguientes modelos siguen la misma estructura con métodos similares:

- **administradores.modelo.php**: CRUD de administradores
- **categorias.modelo.php**: CRUD de categorías
- **subcategorias.modelo.php**: CRUD de subcategorías
- **usuarios.modelo.php**: CRUD de usuarios
- **ventas.modelo.php**: Consultas de ventas
- **banner.modelo.php**: CRUD de banners
- **slide.modelo.php**: CRUD de slides
- **comercio.modelo.php**: Configuración del comercio
- **cabeceras.modelo.php**: Metadatos SEO
- **mensajes.modelo.php**: Mensajes de contacto
- **perfiles.modelo.php**: Perfiles de admin
- **visitas.modelo.php**: Registro de visitas
- **notificaciones.modelo.php**: Sistema de notificaciones

Todos usan:
- `mdlMostrar*()` para SELECT
- `mdlIngresar*()` para INSERT
- `mdlEditar*()` para UPDATE
- `mdlEliminar*()` para DELETE
- `mdlActualizar*()` para UPDATE específico

---

### ARCHIVOS AJAX DEL BACKEND

Los archivos AJAX procesan peticiones asíncronas desde JavaScript.

#### productos.ajax.php
**Ubicación**: `backend/ajax/productos.ajax.php`

**Clase**: `AjaxProductos`

**Estructura general**:
```php
<?php
require_once "../controladores/productos.controlador.php";
require_once "../modelos/productos.modelo.php";
// ... más requires

class AjaxProductos {
    // Propiedades públicas para recibir datos
    public $activarProducto;
    public $activarId;

    // Métodos públicos que procesan peticiones
    public function ajaxActivarProducto() {
        $tabla = "productos";
        $item1 = "estado";
        $valor1 = $this->activarProducto;
        $item2 = "id";
        $valor2 = $this->activarId;

        $respuesta = ModeloProductos::mdlActualizarProductos($tabla, $item1, $valor1, $item2, $valor2);
        echo $respuesta;
    }
}

// Instanciación según petición POST
if(isset($_POST["activarProducto"])) {
    $activar = new AjaxProductos();
    $activar->activarProducto = $_POST["activarProducto"];
    $activar->activarId = $_POST["activarId"];
    $activar->ajaxActivarProducto();
}
?>
```

**Métodos**:

##### `ajaxActivarProducto()`
- **Función**: Activa/desactiva producto
- **Parámetros POST**: `activarProducto` (1/0), `activarId`
- **Respuesta**: "ok" o "error"

##### `ajaxValidarProducto()`
- **Función**: Verifica si un título de producto ya existe
- **Parámetros POST**: `validarProducto`
- **Respuesta**: JSON con datos del producto si existe

##### `ajaxRecibirMultimedia()`
- **Función**: Procesa subida de imágenes de galería
- **Parámetros POST**: `imagenMultimedia`, `rutaMultimedia`
- **Respuesta**: Ruta de imagen guardada

##### `ajaxCrearProducto()` y `ajaxEditarProducto()`
- **Función**: Procesa formulario completo de producto
- **Parámetros**: Todos los campos del producto
- **Respuesta**: "ok" o "error" con mensaje SweetAlert

**Ejemplo de uso desde JavaScript**:
```javascript
// Activar/Desactivar producto
$(".btnActivarProducto").click(function() {
    var idProducto = $(this).attr("idProducto");
    var estadoProducto = $(this).attr("estadoProducto");

    var datos = new FormData();
    datos.append("activarId", idProducto);
    datos.append("activarProducto", estadoProducto);

    $.ajax({
        url: "ajax/productos.ajax.php",
        method: "POST",
        data: datos,
        cache: false,
        contentType: false,
        processData: false,
        success: function(respuesta) {
            if(respuesta == "ok") {
                // Actualizar interfaz
            }
        }
    });
});
```

---

#### Otros Archivos AJAX del Backend

- **categorias.ajax.php**: Operaciones de categorías
- **subcategorias.ajax.php**: Operaciones de subcategorías
- **usuarios.ajax.php**: Gestión de usuarios
- **ventas.ajax.php**: Operaciones de ventas
- **banner.ajax.php**: Gestión de banners
- **slide.ajax.php**: Gestión de slides
- **administradores.ajax.php**: Operaciones de administradores
- **cabeceras.ajax.php**: Metadatos SEO
- **comercio.ajax.php**: Configuración del comercio
- **notificaciones.ajax.php**: Notificaciones

**Archivos de DataTables**:
- **tablaProductos.ajax.php**: Genera tabla dinámica de productos
- **tablaUsuarios.ajax.php**: Genera tabla de usuarios
- **tablaCategorias.ajax.php**: Genera tabla de categorías
- **tablaVentas.ajax.php**: Genera tabla de ventas
- **tablaVisitas.ajax.php**: Genera tabla de visitas

---

### VISTAS DEL BACKEND

#### Estructura de vistas/modulos/

##### login.php
- **Función**: Formulario de inicio de sesión
- **Campos**: Usuario, contraseña
- **Validación**: En `administradores.controlador.php`

##### inicio.php (Dashboard)
- **Función**: Panel principal con estadísticas
- **Elementos**:
  - Cajas superiores (total productos, ventas, usuarios, visitas)
  - Gráfico de ventas mensuales
  - Gráfico de visitas por país
  - Lista de productos más vendidos
  - Lista de productos recientes

##### productos.php
- **Función**: Gestión de productos
- **Características**:
  - DataTable con listado de productos
  - Botones para activar/desactivar
  - Formulario modal para crear/editar
  - Integración con CKEditor para descripción
  - Dropzone para galería multimedia
  - Gestión de ofertas

##### categorias.php
- **Función**: Gestión de categorías
- **Características**:
  - Tabla con CRUD completo
  - Validación de duplicados

##### subcategorias.php
Similar a categorías, pero vinculadas a categorías.

##### usuarios.php
- **Función**: Listado de clientes registrados
- **Características**:
  - DataTable
  - Activar/desactivar usuarios
  - Ver compras de cada usuario

##### ventas.php
- **Función**: Registro de pedidos/ventas
- **Información mostrada**:
  - ID de compra
  - Cliente
  - Productos comprados
  - Total
  - Método de pago
  - Estado de entrega
  - Fecha

##### comercio.php
- **Función**: Configuración general
- **Pestañas**:
  1. Información del comercio
  2. Códigos de pago (PayPal, PayU)
  3. Colores del tema
  4. Logotipo
  5. Redes sociales

##### cabezote.php
- **Función**: Barra superior del panel
- **Elementos**:
  - Menú hamburguesa
  - Notificaciones
  - Usuario logueado
  - Cerrar sesión

##### lateral.php
- **Función**: Menú lateral de navegación
- **Secciones**:
  - Dashboard
  - Productos
  - Categorías
  - Subcategorías
  - Usuarios
  - Ventas
  - Banners
  - Slides
  - Comercio
  - Mensajes
  - Perfiles
  - Visitas
  - Reportes

---

## FRONTEND - TIENDA ONLINE

### Punto de Entrada: frontend/index.php

```php
<?php
// Carga de controladores
require_once "controladores/plantilla.controlador.php";
require_once "controladores/productos.controlador.php";
require_once "controladores/slide.controlador.php";
require_once "controladores/usuarios.controlador.php";
require_once "controladores/carrito.controlador.php";
require_once "controladores/visitas.controlador.php";
require_once "controladores/notificaciones.controlador.php";

// Carga de modelos
require_once "modelos/plantilla.modelo.php";
require_once "modelos/productos.modelo.php";
require_once "modelos/slide.modelo.php";
require_once "modelos/usuarios.modelo.php";
require_once "modelos/carrito.modelo.php";
require_once "modelos/visitas.modelo.php";
require_once "modelos/notificaciones.modelo.php";

require_once "modelos/rutas.php";

// Extensiones
require_once "extensiones/PHPMailer/PHPMailerAutoload.php";
require_once "extensiones/vendor/autoload.php";

// Inicialización
$plantilla = new ControladorPlantilla();
$plantilla->plantilla();
?>
```

---

### CONTROLADORES DEL FRONTEND

#### plantilla.controlador.php
**Clase**: `ControladorPlantilla`

**Métodos**:

##### `plantilla()`
- **Función**: Renderiza la plantilla principal del frontend
- **Proceso**:
  1. Inicia sesión si no existe
  2. Carga la estructura HTML base
  3. Identifica la ruta solicitada (`$_GET["ruta"]`)
  4. Carga el módulo correspondiente
  5. Gestiona cabeceras SEO dinámicas

**Routing**:
```php
if(isset($_GET["ruta"])) {
    if($_GET["ruta"] == "inicio" ||
       $_GET["ruta"] == "productos" ||
       $_GET["ruta"] == "infoproducto" ||
       $_GET["ruta"] == "carrito-de-compras" ||
       $_GET["ruta"] == "perfil" ||
       // ... más rutas
    ) {
        include "vistas/modulos/".$_GET["ruta"].".php";
    } else {
        include "vistas/modulos/error404.php";
    }
} else {
    include "vistas/modulos/slide.php";
    include "vistas/modulos/destacados.php";
}
```

##### `ctrMostrarPlantilla()`
- **Función**: Obtiene estilos y configuración visual
- **Retorno**: Colores del tema, logos, etc.

---

#### productos.controlador.php (Frontend)
**Clase**: `ControladorProductos`

Similar al backend, pero enfocado en mostrar productos al público.

**Métodos**:

##### `ctrMostrarProductos($item, $valor)`
- **Función**: Obtiene productos para mostrar en la tienda
- **Diferencia con backend**: Solo muestra productos activos (estado = 1)

##### `ctrMostrarProductosDestacados($orden)`
- **Función**: Obtiene productos destacados
- **Uso**: Página principal, sección de destacados

##### `ctrMostrarProductosOfertas()`
- **Función**: Obtiene productos en oferta
- **Filtro**: `oferta = 1` y `finOferta >= HOY`

##### `ctrMostrarBuscador($buscar)`
- **Función**: Busca productos por palabra clave
- **Campos de búsqueda**: título, descripción, palabras clave

---

#### slide.controlador.php
**Clase**: `ControladorSlide`

**Métodos**:

##### `ctrMostrarSlide()`
- **Función**: Obtiene slides activos para el carrusel principal
- **Ordenamiento**: Por orden de prioridad

---

#### usuarios.controlador.php (Frontend)
**Clase**: `ControladorUsuarios`

Gestiona registro, login y perfil de clientes.

**Métodos**:

##### `ctrRegistroUsuario($datos)`
- **Función**: Registra nuevo cliente
- **Proceso**:
  1. Valida datos con regex
  2. Verifica que email no exista
  3. Encripta contraseña
  4. Genera código de verificación
  5. Inserta en BD
  6. Envía email de verificación con PHPMailer

**Código de envío de email**:
```php
$mail = new PHPMailer;
$mail->CharSet = 'UTF-8';

$mail->isSMTP();
$mail->Host = 'smtp.gmail.com';
$mail->SMTPAuth = true;
$mail->Username = 'tucorreo@gmail.com';
$mail->Password = 'tupassword';
$mail->SMTPSecure = 'tls';
$mail->Port = 587;

$mail->setFrom('noreply@tutienda.com', 'Tu Tienda');
$mail->addAddress($datos["email"], $datos["nombre"]);

$mail->isHTML(true);
$mail->Subject = 'Verifica tu cuenta';
$mail->Body = '
    <h1>Bienvenido a nuestra tienda</h1>
    <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
    <a href="http://tutienda.com/verificar?codigo='.$codigoVerificacion.'">Verificar cuenta</a>
';

$mail->send();
```

##### `ctrIngresoUsuario()`
- **Función**: Login de clientes
- **Proceso**:
  1. Valida email y contraseña
  2. Verifica que cuenta esté verificada
  3. Verifica que cuenta esté activa
  4. Inicia sesión
  5. Crea cookie "remember me" (opcional)

##### `ctrVerificarCuenta($codigo)`
- **Función**: Activa cuenta después de verificación
- **Proceso**:
  1. Busca usuario con código de verificación
  2. Actualiza `verificado = 1`
  3. Elimina código de verificación

##### `ctrRecuperarPassword($email)`
- **Función**: Recuperación de contraseña
- **Proceso**:
  1. Verifica que email existe
  2. Genera nueva contraseña temporal
  3. Actualiza en BD
  4. Envía email con nueva contraseña

##### `ctrEditarPerfil($datos)`
- **Función**: Actualiza datos del perfil de usuario
- **Campos editables**: nombre, email, dirección, teléfono, foto

---

#### carrito.controlador.php
**Clase**: `ControladorCarrito`

Gestiona el carrito de compras y procesamiento de pagos.

**Métodos**:

##### `ctrMostrarTarifas()`
- **Función**: Obtiene tarifas de envío configuradas
- **Retorno**: Array con tarifas por país/región

##### `ctrNuevasCompras($datos)`
- **Función**: Procesa una nueva compra
- **Proceso**:
  1. Recibe datos del pago (PayPal o PayU)
  2. Valida productos y precios
  3. Inserta compra en BD
  4. Actualiza stock de productos
  5. Actualiza contador de ventas
  6. Crea registro de comentarios (para futuras valoraciones)
  7. Incrementa notificación de nuevas ventas
  8. Envía email de confirmación al cliente

**Estructura de datos de compra**:
```php
$datos = array(
    "id_usuario" => $_SESSION["id"],
    "productos" => json_encode($productosComprados),
    "total" => $total,
    "metodo_pago" => "PayPal", // o "PayU"
    "transaccion_id" => $idTransaccion,
    "estado" => "pendiente",
    "fecha" => date("Y-m-d H:i:s")
);
```

##### `ctrVerificarProducto($datos)`
- **Función**: Verifica que un producto fue comprado por el usuario
- **Uso**: Para mostrar curso/producto digital, permitir descargas, etc.
- **Parámetros**: `id_usuario`, `id_producto`
- **Retorno**: true/false

---

#### visitas.controlador.php
**Clase**: `ControladorVisitas`

Registra visitantes del sitio.

**Métodos**:

##### `ctrRegistrarVisita($datos)`
- **Función**: Guarda visita en BD
- **Datos registrados**:
  - IP del visitante
  - País (obtenido de API de geolocalización)
  - Navegador
  - Sistema operativo
  - Dispositivo (desktop/mobile/tablet)
  - Página visitada
  - Fecha y hora

**Detección de datos del visitante**:
```php
$ip = $_SERVER['REMOTE_ADDR'];
$userAgent = $_SERVER['HTTP_USER_AGENT'];

// Geolocalización con API
$apiUrl = "http://ip-api.com/json/".$ip;
$geoData = json_decode(file_get_contents($apiUrl), true);
$pais = $geoData['country'];

// Detección de navegador
if(strpos($userAgent, 'Chrome') !== false) {
    $navegador = 'Chrome';
} elseif(strpos($userAgent, 'Firefox') !== false) {
    $navegador = 'Firefox';
} // ... más navegadores

// Detección de dispositivo
if(preg_match('/(tablet|ipad|playbook)|(android(?!.*(mobi|opera mini)))/i', $userAgent)) {
    $dispositivo = 'tablet';
} elseif(preg_match('/(up\.browser|up\.link|mmp|symbian|smartphone|midp|wap|phone|android|iemobile)/i', $userAgent)) {
    $dispositivo = 'mobile';
} else {
    $dispositivo = 'desktop';
}
```

---

### MODELOS DEL FRONTEND

Los modelos del frontend son similares a los del backend.

#### carrito.modelo.php
**Clase**: `ModeloCarrito`

**Métodos**:

##### `mdlMostrarTarifas($tabla)`
```php
static public function mdlMostrarTarifas($tabla) {
    $stmt = Conexion::conectar()->prepare("SELECT * FROM $tabla");
    $stmt->execute();
    return $stmt->fetch();
    $stmt->close();
    $stmt = null;
}
```

##### `mdlNuevasCompras($tabla, $datos)`
```php
static public function mdlNuevasCompras($tabla, $datos) {
    $stmt = Conexion::conectar()->prepare("INSERT INTO $tabla(
        id_usuario, productos, total, metodo_pago, transaccion_id, estado, fecha
    ) VALUES (
        :id_usuario, :productos, :total, :metodo_pago, :transaccion_id, :estado, :fecha
    )");

    $stmt->bindParam(":id_usuario", $datos["id_usuario"], PDO::PARAM_INT);
    $stmt->bindParam(":productos", $datos["productos"], PDO::PARAM_STR);
    $stmt->bindParam(":total", $datos["total"], PDO::PARAM_STR);
    $stmt->bindParam(":metodo_pago", $datos["metodo_pago"], PDO::PARAM_STR);
    $stmt->bindParam(":transaccion_id", $datos["transaccion_id"], PDO::PARAM_STR);
    $stmt->bindParam(":estado", $datos["estado"], PDO::PARAM_STR);
    $stmt->bindParam(":fecha", $datos["fecha"], PDO::PARAM_STR);

    if($stmt->execute()) {
        return "ok";
    } else {
        return "error";
    }

    $stmt->close();
    $stmt = null;
}
```

##### `mdlVerificarProducto($tabla, $datos)`
```php
static public function mdlVerificarProducto($tabla, $datos) {
    $stmt = Conexion::conectar()->prepare("SELECT * FROM $tabla WHERE id_usuario = :id_usuario AND productos LIKE :id_producto");

    $stmt->bindParam(":id_usuario", $datos["id_usuario"], PDO::PARAM_INT);
    $productoBuscar = '%"id":"'.$datos["id_producto"].'"%';
    $stmt->bindParam(":id_producto", $productoBuscar, PDO::PARAM_STR);

    $stmt->execute();
    return $stmt->fetch();

    $stmt->close();
    $stmt = null;
}
```

---

#### usuarios.modelo.php (Frontend)
**Clase**: `ModeloUsuarios`

Similar al backend, con métodos adicionales:

##### `mdlRegistroUsuario($tabla, $datos)`
- Inserta nuevo usuario
- Incluye código de verificación

##### `mdlMostrarUsuarioEmail($tabla, $email)`
- Busca usuario por email
- Útil para login y recuperación de contraseña

##### `mdlVerificarCuenta($tabla, $codigo)`
- Activa cuenta verificada

##### `mdlIngresoComentarios($tabla, $datos)`
- Crea registro para futuras valoraciones de productos

---

### ARCHIVOS AJAX DEL FRONTEND

#### carrito.ajax.php
**Ubicación**: `frontend/ajax/carrito.ajax.php`

**Funciones principales**:

##### Procesamiento de PayPal
```php
if(isset($_POST["paypalResponse"])) {
    $paypalResponse = json_decode($_POST["paypalResponse"], true);

    // Extraer datos de la transacción
    $idTransaccion = $paypalResponse["id"];
    $total = $paypalResponse["purchase_units"][0]["amount"]["value"];
    $productos = json_decode($_POST["productosCarrito"], true);

    // Verificar que el total coincida
    $totalCalculado = 0;
    foreach($productos as $producto) {
        $totalCalculado += $producto["precio"] * $producto["cantidad"];
    }

    if($total == $totalCalculado) {
        // Procesar compra
        $datos = array(
            "id_usuario" => $_SESSION["id"],
            "productos" => $_POST["productosCarrito"],
            "total" => $total,
            "metodo_pago" => "PayPal",
            "transaccion_id" => $idTransaccion,
            "estado" => "completado",
            "fecha" => date("Y-m-d H:i:s")
        );

        $respuesta = ControladorCarrito::ctrNuevasCompras($datos);
        echo $respuesta;
    } else {
        echo "error_precio";
    }
}
```

##### Procesamiento de PayU
Similar a PayPal, pero adaptado a la API de PayU.

##### Validación de precios
Siempre verifica que los precios enviados desde el frontend coincidan con los de la base de datos:

```php
foreach($productos as $key => $producto) {
    $itemProducto = "id";
    $valorProducto = $producto["id"];

    $productoReal = ControladorProductos::ctrMostrarProductos($itemProducto, $valorProducto);

    if($productoReal[0]["precio"] != $producto["precio"]) {
        echo "error_precio";
        exit();
    }
}
```

---

#### usuarios.ajax.php (Frontend)
**Funciones**:

##### Registro de usuarios
```php
if(isset($_POST["registroNombre"])) {
    $datos = array(
        "nombre" => $_POST["registroNombre"],
        "email" => $_POST["registroEmail"],
        "password" => $_POST["registroPassword"]
    );

    $respuesta = ControladorUsuarios::ctrRegistroUsuario($datos);
    echo $respuesta;
}
```

##### Login
```php
if(isset($_POST["loginEmail"])) {
    $email = $_POST["loginEmail"];
    $password = $_POST["loginPassword"];

    $respuesta = ControladorUsuarios::ctrIngresoUsuario();
    echo $respuesta;
}
```

##### Recuperar contraseña
```php
if(isset($_POST["recuperarEmail"])) {
    $email = $_POST["recuperarEmail"];
    $respuesta = ControladorUsuarios::ctrRecuperarPassword($email);
    echo $respuesta;
}
```

---

### VISTAS DEL FRONTEND

#### Módulos principales

##### cabezote.php / cabezote.html.php
- **Función**: Cabecera del sitio
- **Elementos**:
  - Logo del comercio
  - Menú de navegación
  - Buscador
  - Icono de carrito con contador
  - Botones de login/registro o perfil

##### slide.php / slide.html.php
- **Función**: Carrusel de imágenes principal
- **Librería**: Slick Slider o similar
- **Características**: Autoplay, navegación, responsive

##### destacados.php / destacados.html.php
- **Función**: Sección de productos destacados en homepage
- **Elementos**: Grid de productos con imagen, título, precio

##### productos.php
- **Función**: Listado de productos por categoría
- **Características**:
  - Filtros por categoría/subcategoría
  - Ordenamiento (precio, popularidad, nuevos)
  - Paginación
  - Vista de grilla o lista

##### infoproducto.php
- **Función**: Página de detalle de producto individual
- **Elementos**:
  - Galería de imágenes (slider)
  - Título y descripción completa
  - Precio (con oferta si aplica)
  - Botón "Agregar al carrito"
  - Especificaciones técnicas
  - Comentarios y valoraciones
  - Productos relacionados

##### carrito-de-compras.php / carrito-de-compras.html.php
- **Función**: Vista del carrito
- **Elementos**:
  - Listado de productos agregados
  - Cantidad (editable)
  - Subtotal por producto
  - Total general
  - Botón "Vaciar carrito"
  - Botón "Continuar comprando"
  - Botón "Proceder al pago"

**Código JavaScript del carrito**:
```javascript
// LocalStorage para persistencia
var carrito = JSON.parse(localStorage.getItem("carrito")) || [];

// Agregar producto
function agregarAlCarrito(producto) {
    var existe = false;

    for(var i = 0; i < carrito.length; i++) {
        if(carrito[i].id == producto.id) {
            carrito[i].cantidad++;
            existe = true;
            break;
        }
    }

    if(!existe) {
        producto.cantidad = 1;
        carrito.push(producto);
    }

    localStorage.setItem("carrito", JSON.stringify(carrito));
    actualizarCarrito();
}

// Actualizar interfaz
function actualizarCarrito() {
    var total = 0;
    var html = "";

    for(var i = 0; i < carrito.length; i++) {
        var subtotal = carrito[i].precio * carrito[i].cantidad;
        total += subtotal;

        html += '<tr>';
        html += '<td>'+carrito[i].titulo+'</td>';
        html += '<td><input type="number" value="'+carrito[i].cantidad+'" onchange="cambiarCantidad('+i+', this.value)"></td>';
        html += '<td>$'+carrito[i].precio+'</td>';
        html += '<td>$'+subtotal+'</td>';
        html += '<td><button onclick="eliminarProducto('+i+')">X</button></td>';
        html += '</tr>';
    }

    $("#tablaCarrito tbody").html(html);
    $("#totalCarrito").text("$" + total.toFixed(2));
    $("#contadorCarrito").text(carrito.length);
}
```

##### finalizar-compra.php
- **Función**: Checkout con PayPal
- **Proceso**:
  1. Verifica que usuario esté logueado
  2. Muestra resumen de compra
  3. Formulario de datos de envío
  4. Cálculo de tarifa de envío
  5. Integración de botón PayPal
  6. Procesamiento de pago

**Integración PayPal**:
```javascript
paypal.Buttons({
    createOrder: function(data, actions) {
        return actions.order.create({
            purchase_units: [{
                amount: {
                    value: totalCarrito.toString()
                }
            }]
        });
    },
    onApprove: function(data, actions) {
        return actions.order.capture().then(function(details) {
            // Enviar a servidor para procesar
            var datos = new FormData();
            datos.append("paypalResponse", JSON.stringify(details));
            datos.append("productosCarrito", JSON.stringify(carrito));

            $.ajax({
                url: "ajax/carrito.ajax.php",
                method: "POST",
                data: datos,
                cache: false,
                contentType: false,
                processData: false,
                success: function(respuesta) {
                    if(respuesta == "ok") {
                        // Limpiar carrito
                        localStorage.removeItem("carrito");
                        // Redirigir a página de confirmación
                        window.location = "perfil?compra=exitosa";
                    }
                }
            });
        });
    }
}).render('#paypal-button-container');
```

##### finalizar-compra-payu.php
Similar a PayPal, pero con integración de PayU.

##### perfil.php
- **Función**: Panel de usuario/cliente
- **Secciones**:
  1. Datos personales (editar)
  2. Historial de compras
  3. Lista de deseos
  4. Cambiar contraseña
  5. Cerrar sesión

##### curso.php
- **Función**: Visualización de productos digitales/cursos comprados
- **Acceso**: Solo si el usuario compró el producto
- **Elementos**: Videos, PDFs, recursos descargables

##### verificar.php
- **Función**: Página de verificación de cuenta
- **Proceso**:
  1. Recibe código de verificación (`$_GET["codigo"]`)
  2. Valida código con BD
  3. Activa cuenta
  4. Muestra mensaje de éxito

##### error404.php
- **Función**: Página de error 404
- **Elementos**: Mensaje amigable, enlace a inicio

##### footer.php
- **Función**: Pie de página
- **Elementos**:
  - Enlaces importantes (Sobre nosotros, Contacto, etc.)
  - Redes sociales
  - Newsletter
  - Copyright

---

## BASE DE DATOS

### Archivo: ecommerce.sql

La base de datos consta de **16 tablas**.

#### 1. administradores
**Propósito**: Usuarios del panel de administración

**Estructura**:
```sql
CREATE TABLE administradores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) NOT NULL,
    foto VARCHAR(255),
    estado TINYINT(1) DEFAULT 1,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos**:
- `id`: Identificador único
- `nombre`: Nombre completo del admin
- `email`: Email único para login
- `password`: Contraseña encriptada con `crypt()`
- `perfil`: Tipo de perfil (Super Admin, Editor, etc.)
- `foto`: Ruta de foto de perfil
- `estado`: 1=activo, 0=inactivo
- `fecha`: Fecha de creación

---

#### 2. productos
**Propósito**: Catálogo de productos

**Estructura**:
```sql
CREATE TABLE productos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_categoria INT NOT NULL,
    id_subcategoria INT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    ruta VARCHAR(255) UNIQUE NOT NULL,
    estado TINYINT(1) DEFAULT 1,
    titulo VARCHAR(200) NOT NULL,
    titular VARCHAR(255),
    descripcion TEXT,
    multimedia TEXT,
    detalles TEXT,
    precio DECIMAL(10,2) NOT NULL,
    portada VARCHAR(255),
    oferta TINYINT(1) DEFAULT 0,
    precioOferta DECIMAL(10,2),
    descuentoOferta INT,
    imgOferta VARCHAR(255),
    finOferta DATE,
    peso DECIMAL(10,2),
    entrega INT,
    ventas INT DEFAULT 0,
    vistas INT DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id),
    FOREIGN KEY (id_subcategoria) REFERENCES subcategorias(id)
);
```

**Campos importantes**:
- `tipo`: "fisico" o "digital"
- `ruta`: URL amigable (ej: "laptop-dell-inspiron")
- `multimedia`: JSON con galería de imágenes
- `detalles`: JSON con especificaciones
- `oferta`: 1 si está en oferta
- `precioOferta`: Precio rebajado
- `descuentoOferta`: Porcentaje de descuento
- `finOferta`: Fecha límite de oferta
- `ventas`: Contador de ventas (actualizado automáticamente)
- `vistas`: Contador de vistas

**Ejemplo de campo multimedia**:
```json
[
    {"foto": "vistas/img/multimedia/laptop-dell/img1.jpg"},
    {"foto": "vistas/img/multimedia/laptop-dell/img2.jpg"},
    {"foto": "vistas/img/multimedia/laptop-dell/img3.jpg"}
]
```

**Ejemplo de campo detalles**:
```json
{
    "Procesador": "Intel Core i7",
    "RAM": "16GB",
    "Almacenamiento": "512GB SSD",
    "Pantalla": "15.6 pulgadas Full HD",
    "Sistema Operativo": "Windows 11"
}
```

---

#### 3. categorias
**Propósito**: Categorías de productos

**Estructura**:
```sql
CREATE TABLE categorias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    ruta VARCHAR(255) UNIQUE NOT NULL,
    estado TINYINT(1) DEFAULT 1,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Ejemplos**: Electrónica, Ropa, Hogar, Deportes

---

#### 4. subcategorias
**Propósito**: Subcategorías de productos

**Estructura**:
```sql
CREATE TABLE subcategorias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_categoria INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    ruta VARCHAR(255) UNIQUE NOT NULL,
    estado TINYINT(1) DEFAULT 1,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id)
);
```

**Ejemplos**:
- Categoría: Electrónica → Subcategorías: Laptops, Celulares, Tablets
- Categoría: Ropa → Subcategorías: Hombre, Mujer, Niños

---

#### 5. usuarios
**Propósito**: Clientes registrados

**Estructura**:
```sql
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    foto VARCHAR(255),
    verificado TINYINT(1) DEFAULT 0,
    codigo_verificacion VARCHAR(100),
    estado TINYINT(1) DEFAULT 1,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos importantes**:
- `verificado`: 0=no verificado, 1=verificado (email)
- `codigo_verificacion`: Código único para verificar cuenta
- `estado`: 1=activo, 0=bloqueado

---

#### 6. compras
**Propósito**: Registro de compras/pedidos

**Estructura**:
```sql
CREATE TABLE compras (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    productos TEXT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL,
    transaccion_id VARCHAR(100),
    estado VARCHAR(50) DEFAULT 'pendiente',
    direccion_envio TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);
```

**Campo productos** (JSON):
```json
[
    {
        "id": 5,
        "titulo": "Laptop Dell",
        "precio": 899.99,
        "cantidad": 1
    },
    {
        "id": 12,
        "titulo": "Mouse Logitech",
        "precio": 29.99,
        "cantidad": 2
    }
]
```

**Estados posibles**:
- "pendiente": Pago recibido, preparando envío
- "enviado": Pedido en camino
- "entregado": Pedido entregado
- "cancelado": Pedido cancelado

---

#### 7. deseos
**Propósito**: Lista de deseos de usuarios

**Estructura**:
```sql
CREATE TABLE deseos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_producto INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);
```

---

#### 8. comentarios
**Propósito**: Valoraciones y comentarios de productos

**Estructura**:
```sql
CREATE TABLE comentarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_producto INT NOT NULL,
    comentario TEXT,
    valoracion INT,
    estado TINYINT(1) DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);
```

**Campos**:
- `valoracion`: Número de estrellas (1-5)
- `estado`: 0=pendiente aprobación, 1=aprobado

---

#### 9. comercio
**Propósito**: Configuración general del ecommerce

**Estructura**:
```sql
CREATE TABLE comercio (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(200) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    facebook VARCHAR(255),
    instagram VARCHAR(255),
    twitter VARCHAR(255),
    youtube VARCHAR(255),
    codigo_paypal TEXT,
    codigo_payu TEXT,
    tarifa_nacional DECIMAL(10,2),
    tarifa_internacional DECIMAL(10,2),
    logotipo VARCHAR(255),
    color_primario VARCHAR(7),
    color_secundario VARCHAR(7),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

#### 10. plantilla
**Propósito**: Estilos visuales del frontend

**Estructura**:
```sql
CREATE TABLE plantilla (
    id INT PRIMARY KEY AUTO_INCREMENT,
    color_fondo VARCHAR(7),
    color_texto VARCHAR(7),
    color_enlaces VARCHAR(7),
    fuente VARCHAR(100),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

#### 11. banner
**Propósito**: Banners publicitarios

**Estructura**:
```sql
CREATE TABLE banner (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ruta VARCHAR(255) NOT NULL,
    tipo VARCHAR(50),
    imagen VARCHAR(255) NOT NULL,
    estado TINYINT(1) DEFAULT 1,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campo tipo**: "superior", "lateral", "inferior"

---

#### 12. slide
**Propósito**: Imágenes del slider principal

**Estructura**:
```sql
CREATE TABLE slide (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200),
    descripcion TEXT,
    imagen VARCHAR(255) NOT NULL,
    enlace VARCHAR(255),
    orden INT DEFAULT 0,
    estado TINYINT(1) DEFAULT 1,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

#### 13. cabeceras
**Propósito**: Metadatos SEO para cada página/producto

**Estructura**:
```sql
CREATE TABLE cabeceras (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ruta VARCHAR(255) UNIQUE NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    palabras_clave TEXT,
    portada VARCHAR(255),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Uso**:
Cada producto, categoría o página tiene su propia cabecera SEO:

```html
<title><?php echo $cabecera["titulo"]; ?></title>
<meta name="description" content="<?php echo $cabecera["descripcion"]; ?>">
<meta name="keywords" content="<?php echo $cabecera["palabras_clave"]; ?>">
<meta property="og:image" content="<?php echo $cabecera["portada"]; ?>">
```

---

#### 14. notificaciones
**Propósito**: Contadores de notificaciones del panel admin

**Estructura**:
```sql
CREATE TABLE notificaciones (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nuevasVentas INT DEFAULT 0,
    nuevosUsuarios INT DEFAULT 0,
    nuevosMensajes INT DEFAULT 0,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

#### 15. visitaspaises
**Propósito**: Estadísticas de visitas agrupadas por país

**Estructura**:
```sql
CREATE TABLE visitaspaises (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pais VARCHAR(100) NOT NULL,
    cantidad INT DEFAULT 1,
    fecha_ultima_visita TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

#### 16. visitaspersonas
**Propósito**: Registro individual de cada visita

**Estructura**:
```sql
CREATE TABLE visitaspersonas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ip VARCHAR(50) NOT NULL,
    pais VARCHAR(100),
    navegador VARCHAR(100),
    sistema_operativo VARCHAR(100),
    dispositivo VARCHAR(50),
    pagina VARCHAR(255),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## FLUJO DE DATOS

### Ejemplo: Compra de un Producto

**1. Usuario navega productos**
```
Usuario → frontend/index.php?ruta=productos
         → ControladorPlantilla::plantilla()
         → vistas/modulos/productos.php
         → ControladorProductos::ctrMostrarProductos(null, null)
         → ModeloProductos::mdlMostrarProductos("productos", null, null)
         → BD: SELECT * FROM productos WHERE estado = 1
         → Renderiza listado de productos
```

**2. Usuario ve detalle de producto**
```
Usuario → frontend/index.php?ruta=infoproducto&id=5
         → vistas/modulos/infoproducto.php
         → ControladorProductos::ctrMostrarProductos("id", 5)
         → ModeloProductos::mdlMostrarProductos("productos", "id", 5)
         → BD: SELECT * FROM productos WHERE id = 5
         → Muestra galería, descripción, precio
```

**3. Usuario agrega al carrito**
```
JavaScript → localStorage.setItem("carrito", JSON.stringify(carrito))
           → Actualiza contador en header
```

**4. Usuario procede al checkout**
```
Usuario → frontend/index.php?ruta=finalizar-compra
         → Verifica sesión activa
         → Muestra resumen del carrito
         → Carga botón PayPal
```

**5. Usuario completa pago con PayPal**
```
PayPal SDK → paypal.Buttons()
            → onApprove()
            → AJAX → frontend/ajax/carrito.ajax.php
                   → Valida productos y precios
                   → ControladorCarrito::ctrNuevasCompras($datos)
                   → ModeloCarrito::mdlNuevasCompras("compras", $datos)
                   → BD: INSERT INTO compras (...)
                   → Actualiza ventas de productos
                   → Incrementa notificación
                   → Envía email confirmación
                   → Retorna "ok"
            → JavaScript limpia carrito
            → Redirige a perfil
```

**6. Administrador ve nueva venta**
```
Admin → backend/index.php
       → Dashboard muestra notificación de nueva venta
       → Admin → backend/index.php?ruta=ventas
                → ControladorVentas::ctrMostrarVentas(null, null)
                → ModeloVentas::mdlMostrarVentas("compras", null, null)
                → BD: SELECT * FROM compras ORDER BY fecha DESC
                → Muestra listado con detalles
```

---

### Ejemplo: Creación de Producto

**1. Admin accede al formulario**
```
Admin → backend/index.php?ruta=productos
       → vistas/modulos/productos.php
       → Botón "Agregar Producto"
       → Modal con formulario
```

**2. Admin completa formulario**
```
Formulario → Título
           → Categoría
           → Subcategoría
           → Descripción (CKEditor)
           → Precio
           → Imágenes (Portada, Principal, Galería con Dropzone)
           → Detalles técnicos
           → Oferta (opcional)
```

**3. Admin envía formulario**
```
JavaScript → Valida campos
           → AJAX → backend/ajax/productos.ajax.php
                   → Recibe todos los datos
                   → ControladorProductos::ctrCrearProducto($datos)
                         → Valida con regex
                         → Procesa imagen portada (1280x720)
                         → Procesa imagen principal (400x450)
                         → Procesa imágenes galería (1000x1000)
                         → Crea directorio multimedia
                         → Prepara array de datos
                         → ModeloCabeceras::mdlIngresarCabecera("cabeceras", $datos)
                         → ModeloProductos::mdlIngresarProducto("productos", $datos)
                         → BD: INSERT INTO productos (...)
                         → BD: INSERT INTO cabeceras (...)
                         → Retorna "ok"
           → SweetAlert muestra éxito
           → Recarga página con nuevo producto
```

---

## SEGURIDAD

### Medidas de Seguridad Implementadas

#### 1. Prevención de SQL Injection
**Uso de Prepared Statements con PDO**:
```php
// MAL (vulnerable)
$query = "SELECT * FROM usuarios WHERE email = '".$_POST["email"]."'";

// BIEN (seguro)
$stmt = Conexion::conectar()->prepare("SELECT * FROM usuarios WHERE email = :email");
$stmt->bindParam(":email", $_POST["email"], PDO::PARAM_STR);
$stmt->execute();
```

Todas las consultas del proyecto usan prepared statements.

---

#### 2. Validación de Entradas
**Expresiones regulares para validar datos**:

```php
// Validar nombre de producto (solo letras, números, espacios)
if(preg_match('/^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ ]+$/', $datos["tituloProducto"])) {
    // Procesar
} else {
    // Rechazar
}

// Validar email
if(preg_match('/^[^@]+@[^@]+\.[a-z]{2,}$/i', $_POST["email"])) {
    // Procesar
}

// Validar números enteros
if(preg_match('/^[0-9]+$/', $_POST["id"])) {
    // Procesar
}
```

---

#### 3. Encriptación de Contraseñas
**Uso de crypt() con salt**:

```php
// Al registrar/crear
$passwordEncriptado = crypt($_POST["password"], '$2a$07$azybxcags23425sdg$');

// Al validar login
$passwordIngresado = crypt($_POST["password"], '$2a$07$azybxcags23425sdg$');

if($passwordEncriptado == $passwordBD) {
    // Login exitoso
}
```

**Recomendación moderna**: Migrar a `password_hash()` y `password_verify()`:
```php
// Registrar
$hash = password_hash($_POST["password"], PASSWORD_DEFAULT);

// Validar
if(password_verify($_POST["password"], $hashBD)) {
    // Login exitoso
}
```

---

#### 4. Protección de Sesiones
**Validación de sesión en cada página protegida**:

```php
session_start();

if(!isset($_SESSION["validarSesion"]) || $_SESSION["validarSesion"] != "ok") {
    echo '<script>window.location = "login";</script>';
    exit();
}
```

---

#### 5. Protección contra XSS
**Escape de salidas**:

```php
// MAL (vulnerable)
echo $_POST["nombre"];

// BIEN (seguro)
echo htmlspecialchars($_POST["nombre"], ENT_QUOTES, 'UTF-8');
```

**Uso en vistas**:
```php
<h1><?php echo htmlspecialchars($producto["titulo"]); ?></h1>
```

---

#### 6. Validación de Archivos Subidos
**Verificación de tipo MIME y extensión**:

```php
if(isset($_FILES["foto"]["tmp_name"])) {
    $tipoPermitido = array("image/jpeg", "image/png");

    if(!in_array($_FILES["foto"]["type"], $tipoPermitido)) {
        echo "Tipo de archivo no permitido";
        exit();
    }

    $extension = pathinfo($_FILES["foto"]["name"], PATHINFO_EXTENSION);
    if($extension != "jpg" && $extension != "jpeg" && $extension != "png") {
        echo "Extensión no permitida";
        exit();
    }

    // Procesar archivo
}
```

---

#### 7. Protección de Directorios
**Evitar listado de directorios**: Crear archivo `.htaccess` en cada carpeta:

```apache
Options -Indexes
```

---

#### 8. HTTPS
**Forzar HTTPS** en `.htaccess`:

```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

---

#### 9. Validación de Precios en Servidor
**Nunca confiar en precios del frontend**:

```php
// Verificar que precios coincidan con BD
foreach($productosCarrito as $producto) {
    $productoReal = ControladorProductos::ctrMostrarProductos("id", $producto["id"]);

    if($productoReal[0]["precio"] != $producto["precio"]) {
        echo "Error: precio manipulado";
        exit();
    }
}
```

---

#### 10. Protección CSRF
**Tokens CSRF en formularios**:

```php
// Generar token
session_start();
$_SESSION["csrf_token"] = bin2hex(random_bytes(32));

// En formulario
echo '<input type="hidden" name="csrf_token" value="'.$_SESSION["csrf_token"].'">';

// Validar
if(!isset($_POST["csrf_token"]) || $_POST["csrf_token"] != $_SESSION["csrf_token"]) {
    die("Token CSRF inválido");
}
```

---

## GUÍA DE FUNCIONES PRINCIPALES

### Funciones de Imagen

#### getimagesize()
```php
list($ancho, $alto) = getimagesize($rutaImagen);
// Retorna: $ancho = 1920, $alto = 1080
```

#### imagecreatefromjpeg() / imagecreatefrompng()
```php
$imagen = imagecreatefromjpeg("foto.jpg");
// Crea recurso de imagen desde archivo JPEG
```

#### imagecreatetruecolor()
```php
$nuevaImagen = imagecreatetruecolor($nuevoAncho, $nuevoAlto);
// Crea nueva imagen en blanco con dimensiones especificadas
```

#### imagecopyresized()
```php
imagecopyresized($destino, $origen, 0, 0, 0, 0, $nuevoAncho, $nuevoAlto, $anchoOrigen, $altoOrigen);
// Redimensiona imagen de $origen a $destino
```

#### imagejpeg() / imagepng()
```php
imagejpeg($imagen, "ruta/destino.jpg", 90);
// Guarda imagen JPEG con calidad 90%
```

---

### Funciones de Archivos

#### file_exists()
```php
if(file_exists("carpeta/archivo.txt")) {
    // El archivo existe
}
```

#### mkdir()
```php
mkdir("nueva_carpeta", 0755);
// Crea directorio con permisos 755
```

#### unlink()
```php
unlink("archivo.txt");
// Elimina archivo
```

#### rmdir()
```php
rmdir("carpeta_vacia");
// Elimina directorio vacío
```

#### glob()
```php
$archivos = glob("carpeta/*");
// Retorna array con todos los archivos en carpeta/
```

---

### Funciones de Arrays

#### array_push()
```php
$array = array(1, 2, 3);
array_push($array, 4);
// $array = [1, 2, 3, 4]
```

#### array_diff()
```php
$array1 = array("a", "b", "c", "d");
$array2 = array("a", "c");
$diferencia = array_diff($array1, $array2);
// $diferencia = ["b", "d"]
```

---

### Funciones de Strings

#### substr()
```php
$texto = "Hola Mundo";
$corto = substr($texto, 0, 4);
// $corto = "Hola"
```

#### preg_match()
```php
if(preg_match('/^[a-zA-Z]+$/', $texto)) {
    // $texto solo contiene letras
}
```

---

### Funciones de JSON

#### json_encode()
```php
$array = array("nombre" => "Juan", "edad" => 30);
$json = json_encode($array);
// $json = '{"nombre":"Juan","edad":30}'
```

#### json_decode()
```php
$json = '{"nombre":"Juan","edad":30}';
$array = json_decode($json, true);
// $array = ["nombre" => "Juan", "edad" => 30]
```

---

### Funciones de Sesión

#### session_start()
```php
session_start();
// Inicia o reanuda sesión
```

#### $_SESSION
```php
$_SESSION["usuario"] = "Juan";
// Guarda datos en sesión

echo $_SESSION["usuario"];
// Recupera datos de sesión
```

---

### Funciones de Fecha

#### date()
```php
$fecha = date("Y-m-d");
// $fecha = "2024-01-15"

$hora = date("H:i:s");
// $hora = "14:30:45"

$completo = date("Y-m-d H:i:s");
// $completo = "2024-01-15 14:30:45"
```

---

## CONCLUSIÓN

Este sistema de ecommerce es un proyecto completo que implementa:

- ✅ Arquitectura MVC clara y organizada
- ✅ Separación de frontend y backend
- ✅ Seguridad con PDO prepared statements
- ✅ Gestión de imágenes con redimensionamiento
- ✅ Sistema de ofertas y descuentos
- ✅ Carrito de compras con LocalStorage
- ✅ Integración de pasarelas de pago
- ✅ Panel administrativo completo
- ✅ Sistema de usuarios y perfiles
- ✅ Estadísticas y reportes
- ✅ SEO con metadatos dinámicos
- ✅ Registro de visitas
- ✅ Sistema de notificaciones

### Flujo General del Sistema

```
Usuario → Frontend → Controlador → Modelo → Base de Datos
         ↓                                       ↓
    Interfaz Visual  ←  Vista  ←  Datos Procesados
```

### Archivos Clave para Estudiar

1. **backend/index.php**: Punto de entrada del backend
2. **frontend/index.php**: Punto de entrada del frontend
3. **modelos/conexion.php**: Conexión PDO
4. **controladores/productos.controlador.php**: Lógica compleja de productos
5. **ajax/productos.ajax.php**: Procesamiento asíncrono
6. **vistas/modulos/productos.php**: Interfaz de gestión

---

**Autor**: Sistema de Ecommerce PHP
**Versión**: 1.0
**Fecha**: 2024
