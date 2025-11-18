# Fix: Database Schema Mismatch - Stock Columns

## Problema Identificado

Despues de poblar la base de datos con datos de Ecuador, la aplicacion Flask mostraba el siguiente error:

```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1054, "Columna desconocida 'productos.stock' en 'lista de campos'")
```

## Causa

El modelo `Producto` en `app/models/product.py` define las columnas `stock` y `stock_minimo` (lineas 37-38), pero estas columnas no existian en la tabla `productos` de la base de datos.

Esto ocurrio porque:
- Los modelos fueron actualizados en commits remotos para incluir estas columnas
- La base de datos local no fue migrada para agregar las nuevas columnas
- El script de seed data de Ecuador esperaba estas columnas

## Solucion

Se creo el script `add_stock_columns.py` que:

1. **Carga las variables de entorno** desde `.env` para usar credenciales locales correctas
2. **Verifica si las columnas existen** antes de intentar agregarlas
3. **Agrega las columnas faltantes** con los valores por defecto apropiados:
   - `stock` INTEGER DEFAULT 0 COMMENT 'Stock disponible'
   - `stock_minimo` INTEGER DEFAULT 5 COMMENT 'Alerta de stock bajo'
4. **Verifica el exito** confirmando que las columnas fueron agregadas

## Como Usar

```bash
cd flask-app
python add_stock_columns.py
```

### Salida Esperada

```
============================================================
AGREGAR COLUMNAS DE STOCK A PRODUCTOS
============================================================

Columnas actuales en tabla 'productos': 27

[*] Agregando columna 'stock'...
[OK] Columna 'stock' agregada exitosamente.

[*] Agregando columna 'stock_minimo'...
[OK] Columna 'stock_minimo' agregada exitosamente.

============================================================
[OK] MIGRACION COMPLETADA EXITOSAMENTE
============================================================

Columnas en tabla 'productos': 29

[OK] Columnas 'stock' y 'stock_minimo' verificadas en la base de datos.

Ahora puedes ejecutar la aplicacion sin errores:
  python run.py
============================================================
```

## Verificacion

Despues de ejecutar el script, la aplicacion Flask inicia correctamente:

```bash
python run.py
```

La aplicacion estara disponible en:
- http://127.0.0.1:5000
- http://192.168.3.12:5000

## Columnas Agregadas

### stock
- **Tipo**: INTEGER
- **Default**: 0
- **Proposito**: Almacenar la cantidad disponible del producto
- **Usado en**:
  - `app/models/product.py` linea 37
  - Metodos: `tiene_stock()`, `decrementar_stock()`, `incrementar_stock()`, `agotado()`

### stock_minimo
- **Tipo**: INTEGER
- **Default**: 5
- **Proposito**: Umbral de alerta para stock bajo
- **Usado en**:
  - `app/models/product.py` linea 38
  - Metodo: `stock_bajo()`

## Notas Tecnicas

- El script usa `sqlalchemy.inspect()` para verificar las columnas existentes
- Ejecuta sentencias SQL directas con `db.session.execute(db.text(...))`
- Maneja transacciones con commit/rollback automatico
- Compatible con Windows (sin emojis en la salida)
- Carga explicitamente el archivo `.env` para evitar usar credenciales por defecto

## Prevencion Futura

Para evitar este problema en el futuro:

1. **Usar migraciones de Alembic**:
   ```bash
   flask db migrate -m "Add stock columns"
   flask db upgrade
   ```

2. **Sincronizar siempre la base de datos** despues de pull:
   ```bash
   git pull
   python add_stock_columns.py  # o flask db upgrade
   ```

3. **Verificar modelos vs base de datos** antes de ejecutar seed data

---

**Fecha**: 2025-11-18
**Autor**: Claude Code Assistant
**Archivo relacionado**: `add_stock_columns.py`
