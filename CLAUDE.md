# python-scripts — Contexto del proyecto

## ¿Qué es?
Colección de scripts Python independientes relacionados con el videojuego **Path of Exile (PoE)**. Cada subcarpeta es un script autónomo con su propio propósito.

## Estructura
```
pob-parser/
│   main.py           # Parser de códigos Path of Building (PoB)
│   pob_raw.xml       # Output: XML completo de la última build parseada
│   pob_parsed.json   # Output: JSON con info extraída de la última build
│
poetrade-poc/
    main.py           # PoC cliente de la API oficial de PoE Trade
    requirements.txt  # Lista requests (pero el script usa urllib de stdlib)
```

---

## Script 1: `pob-parser`

### ¿Qué hace?
Decodifica y parsea códigos de exportación de **Path of Building**. Los códigos PoB son cadenas base64 → zlib → XML. El script los convierte en un reporte legible.

### Flujo
1. Recibe el código PoB por argumento CLI o input interactivo
2. Decodifica: `base64.urlsafe_b64decode` → `zlib.decompress` → `xml.etree.ElementTree`
3. Extrae: clase, ascendancia, nivel, items equipados por slot, gemas (nombre/nivel/calidad), stats del personaje (vida, maná, DPS, crit...)
4. Imprime reporte en consola
5. Guarda `pob_raw.xml` (XML completo indentado) y `pob_parsed.json` (datos extraídos)

### Dependencias
Ninguna externa — solo librería estándar (`base64`, `zlib`, `xml.etree.ElementTree`, `json`, `sys`)

### Uso
```bash
py pob-parser/main.py <codigo_pob>
# o sin argumento para input interactivo
```

---

## Script 2: `poetrade-poc`

### ¿Qué hace?
Prueba de concepto para la **API oficial de PoE Trade** (`pathofexile.com/api/trade`). Busca items en el mercado del juego y muestra nombre, precio, ilvl y vendedor.

### Flujo (dos pasos obligatorios de la API)
1. **POST** `/api/trade/search/{league}` → recibe `search_id` + lista de IDs de listings
2. **GET** `/api/trade/fetch/{ids}?query={search_id}` → detalles de los primeros 10 listings

### Configuración (variables en el propio script)
- `LEAGUE` — liga activa (por defecto `"Mirage"`)
- `ITEM` — item a buscar (por defecto `"Fulgurite Tincture"`)

### Notas importantes
- La API de GGG requiere un header `User-Agent` específico para evitar 403
- El `requirements.txt` lista `requests` pero el script usa `urllib` de stdlib
- Genera la URL directa al resultado en el browser al finalizar

### Uso
```bash
py poetrade-poc/main.py
```

---

## Convenciones generales
- Scripts autónomos, sin dependencias externas cuando es posible
- Outputs de datos guardados junto al script que los genera
- Liga activa de PoE: **Mirage**
- Idioma del código y comentarios: **castellano**
