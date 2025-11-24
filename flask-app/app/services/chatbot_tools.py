"""
Herramientas (Tools/Functions) que el chatbot puede usar para realizar acciones

El chatbot puede LLAMAR a estas funciones para:
- Buscar productos
- Ver estado de pedidos
- Calcular costos de envío
- Aplicar cupones
- Validar datos
- Detectar fraude
- Y más...
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import func, or_, and_
from app.extensions import db
from app.models.product import Producto
from app.models.order import Compra
from app.models.user import User
from app.models.categoria import Categoria, Subcategoria
from app.models.coupon import Cupon
from app.models.comment import Comentario
from app.models.analisis_review import AnalisisReview

logger = logging.getLogger(__name__)


# ============================================================================
# 1. VENDER - Recomendaciones y guía de compra
# ============================================================================

# Diccionario de sinónimos para búsqueda semántica
SINONIMOS = {
    'laptop': ['portátil', 'computadora portátil', 'notebook', 'computador'],
    'mouse': ['ratón', 'mouse inalámbrico', 'mouse gaming'],
    'teclado': ['keyboard', 'teclado mecánico', 'teclado gamer'],
    'celular': ['móvil', 'smartphone', 'teléfono', 'phone'],
    'auriculares': ['audífonos', 'headset', 'headphones', 'cascos'],
    'monitor': ['pantalla', 'display', 'screen'],
    'tablet': ['tableta', 'ipad'],
    'ssd': ['disco duro', 'almacenamiento', 'storage'],
    'ram': ['memoria', 'memoria ram'],
    'gaming': ['gamer', 'juegos', 'videojuegos', 'para jugar'],
    'trabajo': ['oficina', 'productividad', 'trabajar'],
    'estudiante': ['estudio', 'escuela', 'universidad'],
    'barato': ['económico', 'bajo precio', 'accesible', 'low cost'],
    'rápido': ['veloz', 'potente', 'alto rendimiento', 'performance']
}

def expandir_query_con_sinonimos(query: str) -> List[str]:
    """Expande query con sinónimos para búsqueda semántica"""
    query_lower = query.lower()
    terminos = [query_lower]

    # Buscar sinónimos
    for palabra_clave, sinonimos in SINONIMOS.items():
        if palabra_clave in query_lower or any(sin in query_lower for sin in sinonimos):
            terminos.append(palabra_clave)
            terminos.extend(sinonimos)

    return list(set(terminos))  # Eliminar duplicados

def buscar_productos(query: str, categoria: str = None, precio_max: float = None,
                     precio_min: float = None, limit: int = 10) -> List[Dict]:
    """
    Busca productos INTELIGENTEMENTE usando sinónimos y búsqueda semántica

    Args:
        query: Término de búsqueda (ej: "laptop", "portátil", "algo para trabajar")
        categoria: Categoría específica
        precio_max: Precio máximo
        precio_min: Precio mínimo
        limit: Cantidad máxima de resultados

    Returns:
        Lista de productos encontrados con TODOS los detalles
    """
    try:
        # Base query
        query_db = Producto.query.filter(Producto.estado == 1)

        # BÚSQUEDA SEMÁNTICA con sinónimos
        if query:
            terminos_busqueda = expandir_query_con_sinonimos(query)

            # Construir condiciones OR para cada término
            condiciones = []
            for termino in terminos_busqueda:
                condiciones.append(Producto.titulo.ilike(f'%{termino}%'))
                condiciones.append(Producto.descripcion.ilike(f'%{termino}%'))

            if condiciones:
                query_db = query_db.filter(or_(*condiciones))

        # Filtro por categoría
        if categoria:
            cat = Categoria.query.filter(Categoria.categoria.ilike(f'%{categoria}%')).first()
            if cat:
                query_db = query_db.filter(Producto.id_categoria == cat.id)

        # Filtros de precio
        if precio_min:
            query_db = query_db.filter(Producto.precio >= precio_min)
        if precio_max:
            query_db = query_db.filter(Producto.precio <= precio_max)

        # Ordenar por relevancia: stock disponible primero, luego ventas
        productos = query_db.order_by(
            Producto.stock.desc(),  # Primero con stock
            (Producto.ventas * 2 + Producto.vistas).desc()  # Luego popularidad
        ).limit(limit * 2).all()  # Buscar más para filtrar inteligente

        # Formatear resultados CON TODOS LOS DATOS para que la IA razone
        resultados = []
        for p in productos:
            # Incluir descripción completa para razonamiento
            descripcion = p.descripcion[:300] if p.descripcion else "Sin descripción"

            resultados.append({
                'id': p.id,
                'nombre': p.titulo,
                'descripcion': descripcion,
                'precio': float(p.get_price()),
                'precio_original': float(p.precio) if p.is_on_offer() else None,
                'descuento': p.descuentoOferta if p.is_on_offer() else 0,
                'categoria': p.categoria.categoria if p.categoria else 'Sin categoría',
                'stock': p.stock,
                'disponible': p.stock > 0,
                'rating': p.get_average_rating(),
                'num_reviews': p.get_comments_count(),
                'ventas': p.ventas,
                'url': f'/tienda/producto/{p.ruta}',
                'en_oferta': p.is_on_offer()
            })

        # Limitar al número solicitado
        resultados = resultados[:limit]

        logger.info(f"✅ Búsqueda semántica '{query}': {len(resultados)} productos (expandido a {len(expandir_query_con_sinonimos(query))} términos)")
        return resultados

    except Exception as e:
        logger.error(f"❌ Error en buscar_productos: {e}")
        return []


def obtener_recomendaciones_personalizadas(usuario_id: int = None,
                                           producto_actual: int = None,
                                           limite: int = 5) -> List[Dict]:
    """
    Obtiene recomendaciones personalizadas basadas en:
    - Historial de compras del usuario
    - Productos vistos recientemente
    - Productos complementarios
    - Productos populares en la misma categoría

    Args:
        usuario_id: ID del usuario (opcional)
        producto_actual: ID del producto que está viendo
        limite: Cantidad de recomendaciones

    Returns:
        Lista de productos recomendados con razón de recomendación
    """
    try:
        recomendaciones = []

        # 1. Si está viendo un producto, recomendar complementarios
        if producto_actual:
            producto = Producto.query.get(producto_actual)
            if producto:
                # Productos de la misma categoría
                similares = Producto.query.filter(
                    Producto.id_categoria == producto.id_categoria,
                    Producto.id != producto.id,
                    Producto.estado == 1,
                    Producto.stock > 0
                ).order_by(Producto.ventas.desc()).limit(3).all()

                for p in similares:
                    recomendaciones.append({
                        'id': p.id,
                        'nombre': p.titulo,
                        'precio': float(p.get_price()),
                        'categoria': p.categoria.categoria if p.categoria else '',
                        'rating': p.get_average_rating(),
                        'razon': f'Complementa bien con {producto.titulo}',
                        'url': f'/tienda/producto/{p.ruta}'
                    })

        # 2. Si tenemos usuario, recomendar basado en historial
        if usuario_id and len(recomendaciones) < limite:
            # Obtener categorías compradas por el usuario
            compras = Compra.query.filter_by(id_usuario=usuario_id).limit(10).all()
            categorias_compradas = set()

            for compra in compras:
                if compra.producto and compra.producto.categoria:
                    categorias_compradas.add(compra.producto.id_categoria)

            # Recomendar productos de categorías que le gustan
            if categorias_compradas:
                productos_recomendados = Producto.query.filter(
                    Producto.id_categoria.in_(list(categorias_compradas)),
                    Producto.estado == 1,
                    Producto.stock > 0
                ).order_by(Producto.ventas.desc()).limit(limite - len(recomendaciones)).all()

                for p in productos_recomendados:
                    recomendaciones.append({
                        'id': p.id,
                        'nombre': p.titulo,
                        'precio': float(p.get_price()),
                        'categoria': p.categoria.categoria if p.categoria else '',
                        'rating': p.get_average_rating(),
                        'razon': 'Basado en tus compras anteriores',
                        'url': f'/tienda/producto/{p.ruta}'
                    })

        # 3. Si aún no hay suficientes, agregar más vendidos
        if len(recomendaciones) < limite:
            mas_vendidos = Producto.query.filter(
                Producto.estado == 1,
                Producto.stock > 0
            ).order_by(Producto.ventas.desc()).limit(limite - len(recomendaciones)).all()

            for p in mas_vendidos:
                recomendaciones.append({
                    'id': p.id,
                    'nombre': p.titulo,
                    'precio': float(p.get_price()),
                    'categoria': p.categoria.categoria if p.categoria else '',
                    'rating': p.get_average_rating(),
                    'razon': 'Producto más vendido',
                    'url': f'/tienda/producto/{p.ruta}'
                })

        return recomendaciones[:limite]

    except Exception as e:
        logger.error(f"❌ Error en obtener_recomendaciones_personalizadas: {e}")
        return []


def comparar_productos(producto_ids: List[int]) -> Dict:
    """
    Compara múltiples productos lado a lado

    Args:
        producto_ids: Lista de IDs de productos a comparar

    Returns:
        Comparación detallada de los productos
    """
    try:
        productos = Producto.query.filter(Producto.id.in_(producto_ids)).all()

        comparacion = {
            'productos': [],
            'mejor_precio': None,
            'mejor_rating': None,
            'mas_vendido': None
        }

        mejor_precio_val = float('inf')
        mejor_rating_val = 0
        mas_ventas = 0

        for p in productos:
            precio = p.get_price()
            rating = p.get_average_rating()

            info = {
                'id': p.id,
                'nombre': p.titulo,
                'precio': float(precio),
                'rating': rating,
                'ventas': p.ventas,
                'stock': p.stock,
                'categoria': p.categoria.categoria if p.categoria else '',
                'num_reviews': p.get_comments_count()
            }

            comparacion['productos'].append(info)

            # Determinar mejores
            if precio < mejor_precio_val:
                mejor_precio_val = precio
                comparacion['mejor_precio'] = p.id

            if rating > mejor_rating_val:
                mejor_rating_val = rating
                comparacion['mejor_rating'] = p.id

            if p.ventas > mas_ventas:
                mas_ventas = p.ventas
                comparacion['mas_vendido'] = p.id

        return comparacion

    except Exception as e:
        logger.error(f"❌ Error en comparar_productos: {e}")
        return {'productos': [], 'error': str(e)}


# ============================================================================
# 2. SOPORTAR - Preguntas, reclamos, tracking
# ============================================================================

def rastrear_pedido(order_id: int = None, usuario_id: int = None, email: str = None) -> Dict:
    """
    Rastrea el estado de un pedido

    Args:
        order_id: ID del pedido
        usuario_id: ID del usuario (para buscar sus pedidos)
        email: Email del usuario

    Returns:
        Estado del pedido con detalles
    """
    try:
        # Buscar pedido
        if order_id:
            pedido = Compra.query.get(order_id)
        elif usuario_id:
            # Obtener el pedido más reciente del usuario
            pedido = Compra.query.filter_by(id_usuario=usuario_id).order_by(Compra.fecha.desc()).first()
        elif email:
            user = User.query.filter_by(email=email).first()
            if user:
                pedido = Compra.query.filter_by(id_usuario=user.id).order_by(Compra.fecha.desc()).first()
            else:
                return {'error': 'Usuario no encontrado', 'encontrado': False}
        else:
            return {'error': 'Debe proporcionar order_id, usuario_id o email', 'encontrado': False}

        if not pedido:
            return {'error': 'Pedido no encontrado', 'encontrado': False}

        # Formatear información del pedido
        resultado = {
            'encontrado': True,
            'order_id': pedido.id,
            'fecha': pedido.fecha.strftime('%Y-%m-%d %H:%M'),
            'estado': pedido.estado,
            'metodo_pago': pedido.metodo_pago,
            'total': float(pedido.precio_total) if pedido.precio_total else float(pedido.precio_unitario * pedido.cantidad),
            'producto': pedido.producto.titulo if pedido.producto else 'Producto no disponible',
            'cantidad': pedido.cantidad,
            'direccion_envio': pedido.direccion_envio,
            'telefono': pedido.telefono,
            'guia_envio': pedido.guia_envio if hasattr(pedido, 'guia_envio') else None
        }

        # Agregar mensaje según estado
        estados_info = {
            'Pendiente': 'Tu pedido está siendo procesado. Te notificaremos cuando se envíe.',
            'Procesando': 'Estamos preparando tu pedido para el envío.',
            'Enviado': f'Tu pedido ha sido enviado. Guía: {resultado.get("guia_envio", "Por asignar")}',
            'Entregado': '¡Tu pedido ha sido entregado! Gracias por tu compra.',
            'Cancelado': 'Este pedido fue cancelado.',
            'Rechazado': 'Hubo un problema con este pedido. Contacta a soporte.'
        }

        resultado['mensaje'] = estados_info.get(pedido.estado, 'Estado desconocido')

        # Estimar días de entrega si está enviado
        if pedido.estado == 'Enviado' or pedido.estado == 'Procesando':
            resultado['estimacion_entrega'] = '2-3 días hábiles'

        return resultado

    except Exception as e:
        logger.error(f"❌ Error en rastrear_pedido: {e}")
        return {'error': str(e), 'encontrado': False}


def obtener_historial_compras(usuario_id: int, limit: int = 5) -> List[Dict]:
    """
    Obtiene el historial de compras de un usuario

    Args:
        usuario_id: ID del usuario
        limit: Cantidad de pedidos a retornar

    Returns:
        Lista de pedidos del usuario
    """
    try:
        pedidos = Compra.query.filter_by(id_usuario=usuario_id).order_by(Compra.fecha.desc()).limit(limit).all()

        historial = []
        for p in pedidos:
            historial.append({
                'order_id': p.id,
                'fecha': p.fecha.strftime('%Y-%m-%d'),
                'producto': p.producto.titulo if p.producto else 'N/A',
                'cantidad': p.cantidad,
                'total': float(p.precio_total) if p.precio_total else float(p.precio_unitario * p.cantidad),
                'estado': p.estado,
                'metodo_pago': p.metodo_pago
            })

        return historial

    except Exception as e:
        logger.error(f"❌ Error en obtener_historial_compras: {e}")
        return []


def procesar_reclamo(usuario_id: int, order_id: int, motivo: str, descripcion: str) -> Dict:
    """
    Registra un reclamo o problema con un pedido

    Args:
        usuario_id: ID del usuario
        order_id: ID del pedido
        motivo: Motivo del reclamo (producto defectuoso, no llegó, etc.)
        descripcion: Descripción detallada del problema

    Returns:
        Información del reclamo registrado
    """
    try:
        # Verificar que el pedido pertenece al usuario
        pedido = Compra.query.filter_by(id=order_id, id_usuario=usuario_id).first()

        if not pedido:
            return {
                'success': False,
                'error': 'Pedido no encontrado o no pertenece al usuario'
            }

        # En una implementación completa, aquí guardarías en tabla de reclamos
        # Por ahora, retornamos información de que se registró

        reclamo_id = f"RCL-{order_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(f"📝 Reclamo registrado: {reclamo_id} - Usuario: {usuario_id}, Pedido: {order_id}, Motivo: {motivo}")

        return {
            'success': True,
            'reclamo_id': reclamo_id,
            'mensaje': 'Tu reclamo ha sido registrado exitosamente. Un representante te contactará en las próximas 24 horas.',
            'tiempo_respuesta_estimado': '24 horas',
            'puede_devolver': pedido.estado in ['Entregado'] and (datetime.now() - pedido.fecha).days <= 30
        }

    except Exception as e:
        logger.error(f"❌ Error en procesar_reclamo: {e}")
        return {'success': False, 'error': str(e)}


# ============================================================================
# 3. COBRAR - Ayuda en checkout y métodos de pago
# ============================================================================

def calcular_costo_envio(ciudad: str, provincia: str = None, peso_kg: float = 1.0) -> Dict:
    """
    Calcula el costo de envío según ubicación

    Args:
        ciudad: Ciudad de destino
        provincia: Provincia de destino
        peso_kg: Peso del paquete en kg

    Returns:
        Costo de envío y tiempo estimado
    """
    try:
        # Tarifas de envío para Ecuador
        tarifas = {
            'Quito': {'costo_base': 3.50, 'dias': '1-2'},
            'Guayaquil': {'costo_base': 4.00, 'dias': '1-2'},
            'Cuenca': {'costo_base': 5.00, 'dias': '2-3'},
            'Ambato': {'costo_base': 4.50, 'dias': '2-3'},
            'Manta': {'costo_base': 5.50, 'dias': '2-3'},
            'Portoviejo': {'costo_base': 5.50, 'dias': '2-3'},
            'Machala': {'costo_base': 5.00, 'dias': '2-3'},
            'Loja': {'costo_base': 6.00, 'dias': '3-4'},
            'Esmeraldas': {'costo_base': 6.00, 'dias': '3-4'},
        }

        # Buscar ciudad (case insensitive)
        ciudad_lower = ciudad.lower()
        tarifa = None
        for c, t in tarifas.items():
            if c.lower() == ciudad_lower:
                tarifa = t
                break

        # Si no encuentra la ciudad exacta, usar tarifa genérica
        if not tarifa:
            tarifa = {'costo_base': 6.00, 'dias': '3-5'}

        # Calcular costo adicional por peso
        costo_base = tarifa['costo_base']
        if peso_kg > 2:
            costo_adicional = (peso_kg - 2) * 1.50
            costo_total = costo_base + costo_adicional
        else:
            costo_total = costo_base

        # Envío gratis para compras sobre $50
        envio_gratis_desde = 50.00

        return {
            'costo': round(costo_total, 2),
            'ciudad': ciudad,
            'tiempo_estimado': tarifa['dias'] + ' días hábiles',
            'envio_gratis_desde': envio_gratis_desde,
            'mensaje': f'Envío gratis en compras sobre ${envio_gratis_desde}'
        }

    except Exception as e:
        logger.error(f"❌ Error en calcular_costo_envio: {e}")
        return {'costo': 5.00, 'error': str(e)}


def validar_aplicar_cupon(codigo_cupon: str, total_compra: float, usuario_id: int = None) -> Dict:
    """
    Valida y aplica un cupón de descuento

    Args:
        codigo_cupon: Código del cupón
        total_compra: Total de la compra
        usuario_id: ID del usuario (opcional)

    Returns:
        Información del cupón y descuento aplicado
    """
    try:
        # Buscar cupón
        cupon = Cupon.query.filter_by(codigo=codigo_cupon).first()

        if not cupon:
            return {
                'valido': False,
                'error': 'Cupón no encontrado',
                'descuento': 0
            }

        # Validar fecha de vigencia
        if cupon.fecha_inicio and datetime.now() < cupon.fecha_inicio:
            return {
                'valido': False,
                'error': f'Este cupón estará disponible desde {cupon.fecha_inicio.strftime("%Y-%m-%d")}',
                'descuento': 0
            }

        if cupon.fecha_fin and datetime.now() > cupon.fecha_fin:
            return {
                'valido': False,
                'error': 'Este cupón ha expirado',
                'descuento': 0
            }

        # Validar compra mínima
        if cupon.compra_minima and total_compra < cupon.compra_minima:
            return {
                'valido': False,
                'error': f'Este cupón requiere una compra mínima de ${cupon.compra_minima}',
                'descuento': 0,
                'falta': float(cupon.compra_minima - total_compra)
            }

        # Calcular descuento
        if cupon.tipo == 'porcentaje':
            descuento = total_compra * (cupon.descuento / 100)
            if cupon.descuento_maximo and descuento > cupon.descuento_maximo:
                descuento = cupon.descuento_maximo
        else:  # tipo fijo
            descuento = cupon.descuento

        nuevo_total = max(0, total_compra - descuento)

        return {
            'valido': True,
            'codigo': cupon.codigo,
            'tipo': cupon.tipo,
            'descuento_aplicado': round(descuento, 2),
            'total_original': round(total_compra, 2),
            'total_con_descuento': round(nuevo_total, 2),
            'ahorro': round(descuento, 2),
            'mensaje': f'¡Cupón aplicado! Ahorras ${round(descuento, 2)}'
        }

    except Exception as e:
        logger.error(f"❌ Error en validar_aplicar_cupon: {e}")
        return {'valido': False, 'error': str(e), 'descuento': 0}


def obtener_metodos_pago_disponibles(total: float) -> Dict:
    """
    Obtiene los métodos de pago disponibles para Ecuador

    Args:
        total: Total de la compra

    Returns:
        Lista de métodos de pago disponibles con detalles
    """
    metodos = {
        'paypal': {
            'nombre': 'PayPal',
            'disponible': True,
            'comision': 0,
            'icono': 'fab fa-paypal',
            'descripcion': 'Paga con tu cuenta PayPal o tarjeta de crédito'
        },
        'paymentez': {
            'nombre': 'Tarjeta de Crédito/Débito',
            'disponible': True,
            'comision': 0,
            'icono': 'fas fa-credit-card',
            'descripcion': 'Visa, Mastercard, American Express, Diners'
        },
        'transferencia': {
            'nombre': 'Transferencia Bancaria',
            'disponible': True,
            'comision': 0,
            'icono': 'fas fa-university',
            'descripcion': 'Banco Pichincha, Guayaquil, Pacífico'
        },
        'contra_entrega': {
            'nombre': 'Pago Contra Entrega',
            'disponible': total <= 200,  # Solo para compras menores a $200
            'comision': 2.00,
            'icono': 'fas fa-hand-holding-usd',
            'descripcion': 'Paga en efectivo cuando recibas tu pedido'
        }
    }

    return {
        'metodos': metodos,
        'recomendado': 'paymentez' if total > 50 else 'contra_entrega'
    }


# ============================================================================
# 4. VALIDAR Y PROTEGER - Detección de fraude y validación
# ============================================================================

def validar_datos_compra(nombre: str, email: str, telefono: str, direccion: str) -> Dict:
    """
    Valida los datos de compra del cliente

    Args:
        nombre: Nombre completo
        email: Email
        telefono: Teléfono
        direccion: Dirección de envío

    Returns:
        Resultado de validación
    """
    errores = []
    warnings = []

    # Validar nombre
    if not nombre or len(nombre) < 3:
        errores.append('El nombre debe tener al menos 3 caracteres')

    # Validar email
    if not email or '@' not in email or '.' not in email:
        errores.append('Email inválido')

    # Validar teléfono (Ecuador)
    telefono_clean = ''.join(filter(str.isdigit, telefono))
    if len(telefono_clean) < 9 or len(telefono_clean) > 10:
        errores.append('Teléfono inválido. Debe tener 9 o 10 dígitos')
    elif not telefono_clean.startswith(('09', '2', '3', '4', '5', '6', '7')):
        warnings.append('El teléfono no parece ser de Ecuador')

    # Validar dirección
    if not direccion or len(direccion) < 10:
        errores.append('La dirección debe ser más específica (mín. 10 caracteres)')

    # Verificar palabras clave en dirección
    palabras_direccion = ['calle', 'avenida', 'av', 'sector', 'barrio', '#', 'nro', 'no']
    if not any(palabra in direccion.lower() for palabra in palabras_direccion):
        warnings.append('La dirección parece incompleta. Incluye calle, número, sector')

    return {
        'valido': len(errores) == 0,
        'errores': errores,
        'warnings': warnings,
        'puntuacion_calidad': 100 - (len(errores) * 25) - (len(warnings) * 10)
    }


def detectar_comportamiento_sospechoso(usuario_id: int = None, email: str = None,
                                       total_compra: float = 0) -> Dict:
    """
    Detecta comportamientos sospechosos o potencial fraude

    Args:
        usuario_id: ID del usuario
        email: Email del usuario
        total_compra: Total de la compra

    Returns:
        Nivel de riesgo y recomendaciones
    """
    try:
        riesgo_score = 0
        alertas = []

        # 1. Verificar historial del usuario
        if usuario_id:
            user = User.query.get(usuario_id)
            if user:
                # Usuario muy nuevo
                dias_registrado = (datetime.now() - user.fecha).days
                if dias_registrado < 1:
                    riesgo_score += 20
                    alertas.append('Usuario registrado recientemente (menos de 1 día)')

                # Verificar compras previas
                compras_previas = Compra.query.filter_by(id_usuario=usuario_id).count()
                if compras_previas == 0 and total_compra > 500:
                    riesgo_score += 30
                    alertas.append('Primera compra con monto alto (>$500)')

                # Verificar rechazos previos
                compras_rechazadas = Compra.query.filter_by(
                    id_usuario=usuario_id,
                    estado='Rechazado'
                ).count()

                if compras_rechazadas > 2:
                    riesgo_score += 40
                    alertas.append('Múltiples pagos rechazados anteriormente')

        # 2. Verificar monto sospechoso
        if total_compra > 1000:
            riesgo_score += 15
            alertas.append('Monto de compra alto (>$1000)')

        # 3. Determinar nivel de riesgo
        if riesgo_score >= 70:
            nivel = 'ALTO'
            accion = 'Requiere verificación manual antes de procesar'
        elif riesgo_score >= 40:
            nivel = 'MEDIO'
            accion = 'Recomendado: Verificar datos de contacto'
        else:
            nivel = 'BAJO'
            accion = 'Puede procesar normalmente'

        return {
            'riesgo_score': riesgo_score,
            'nivel_riesgo': nivel,
            'alertas': alertas,
            'accion_recomendada': accion,
            'requiere_verificacion': riesgo_score >= 70
        }

    except Exception as e:
        logger.error(f"❌ Error en detectar_comportamiento_sospechoso: {e}")
        return {
            'riesgo_score': 0,
            'nivel_riesgo': 'DESCONOCIDO',
            'alertas': ['Error al evaluar riesgo'],
            'accion_recomendada': 'Proceder con precaución'
        }


# ============================================================================
# 5. ANALIZAR - Insights y analytics
# ============================================================================

def obtener_estadisticas_producto(producto_id: int) -> Dict:
    """
    Obtiene estadísticas y análisis de un producto

    Args:
        producto_id: ID del producto

    Returns:
        Estadísticas completas del producto
    """
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return {'error': 'Producto no encontrado'}

        # Reviews y ratings
        comentarios = Comentario.query.filter_by(id_producto=producto_id).all()

        if comentarios:
            ratings = [c.calificacion for c in comentarios if c.calificacion]
            rating_promedio = sum(ratings) / len(ratings) if ratings else 0

            distribucion_ratings = {
                5: sum(1 for r in ratings if r == 5),
                4: sum(1 for r in ratings if r == 4),
                3: sum(1 for r in ratings if r == 3),
                2: sum(1 for r in ratings if r == 2),
                1: sum(1 for r in ratings if r == 1),
            }
        else:
            rating_promedio = 0
            distribucion_ratings = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

        # Análisis de sentimiento (si existe)
        analisis = AnalisisReview.query.filter_by(producto_id=producto_id).first()

        estadisticas = {
            'producto': {
                'id': producto.id,
                'nombre': producto.titulo,
                'precio': float(producto.get_price()),
                'stock': producto.stock,
                'ventas': producto.ventas,
                'vistas': producto.vistas,
                'conversion_rate': round((producto.ventas / producto.vistas * 100), 2) if producto.vistas > 0 else 0
            },
            'reviews': {
                'total': len(comentarios),
                'rating_promedio': round(rating_promedio, 1),
                'distribucion': distribucion_ratings,
                'recomendacion_porcentaje': round((distribucion_ratings[4] + distribucion_ratings[5]) / len(comentarios) * 100, 1) if comentarios else 0
            }
        }

        if analisis:
            estadisticas['sentimiento'] = {
                'positivo': analisis.sentimiento_positivo,
                'neutral': analisis.sentimiento_neutral,
                'negativo': analisis.sentimiento_negativo,
                'aspectos_positivos': analisis.aspectos_positivos,
                'aspectos_negativos': analisis.aspectos_negativos,
                'calidad_score': float(analisis.calidad_score) if analisis.calidad_score else 0
            }

        return estadisticas

    except Exception as e:
        logger.error(f"❌ Error en obtener_estadisticas_producto: {e}")
        return {'error': str(e)}


# ============================================================================
# REGISTRO DE FUNCIONES DISPONIBLES PARA EL CHATBOT
# ============================================================================

CHATBOT_FUNCTIONS = {
    'buscar_productos': {
        'function': buscar_productos,
        'description': 'Busca productos en el catálogo por nombre, categoría, precio',
        'parameters': ['query', 'categoria', 'precio_max', 'precio_min', 'limit']
    },
    'obtener_recomendaciones': {
        'function': obtener_recomendaciones_personalizadas,
        'description': 'Obtiene recomendaciones personalizadas de productos',
        'parameters': ['usuario_id', 'producto_actual', 'limite']
    },
    'comparar_productos': {
        'function': comparar_productos,
        'description': 'Compara múltiples productos lado a lado',
        'parameters': ['producto_ids']
    },
    'rastrear_pedido': {
        'function': rastrear_pedido,
        'description': 'Rastrea el estado de un pedido',
        'parameters': ['order_id', 'usuario_id', 'email']
    },
    'historial_compras': {
        'function': obtener_historial_compras,
        'description': 'Obtiene el historial de compras de un usuario',
        'parameters': ['usuario_id', 'limit']
    },
    'procesar_reclamo': {
        'function': procesar_reclamo,
        'description': 'Registra un reclamo o problema con un pedido',
        'parameters': ['usuario_id', 'order_id', 'motivo', 'descripcion']
    },
    'calcular_envio': {
        'function': calcular_costo_envio,
        'description': 'Calcula el costo de envío según ubicación',
        'parameters': ['ciudad', 'provincia', 'peso_kg']
    },
    'validar_cupon': {
        'function': validar_aplicar_cupon,
        'description': 'Valida y aplica un cupón de descuento',
        'parameters': ['codigo_cupon', 'total_compra', 'usuario_id']
    },
    'metodos_pago': {
        'function': obtener_metodos_pago_disponibles,
        'description': 'Obtiene los métodos de pago disponibles',
        'parameters': ['total']
    },
    'validar_datos': {
        'function': validar_datos_compra,
        'description': 'Valida los datos de compra del cliente',
        'parameters': ['nombre', 'email', 'telefono', 'direccion']
    },
    'detectar_fraude': {
        'function': detectar_comportamiento_sospechoso,
        'description': 'Detecta comportamientos sospechosos o potencial fraude',
        'parameters': ['usuario_id', 'email', 'total_compra']
    },
    'estadisticas_producto': {
        'function': obtener_estadisticas_producto,
        'description': 'Obtiene estadísticas y análisis de un producto',
        'parameters': ['producto_id']
    }
}


def ejecutar_funcion(nombre_funcion: str, parametros: Dict) -> Any:
    """
    Ejecuta una función del chatbot

    Args:
        nombre_funcion: Nombre de la función a ejecutar
        parametros: Parámetros para la función

    Returns:
        Resultado de la función
    """
    if nombre_funcion not in CHATBOT_FUNCTIONS:
        return {'error': f'Función {nombre_funcion} no encontrada'}

    try:
        func = CHATBOT_FUNCTIONS[nombre_funcion]['function']
        resultado = func(**parametros)
        logger.info(f"✅ Función ejecutada: {nombre_funcion}")
        return resultado
    except Exception as e:
        logger.error(f"❌ Error ejecutando función {nombre_funcion}: {e}")
        return {'error': str(e)}
