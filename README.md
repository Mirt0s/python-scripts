# python-scripts

Colección de scripts Python de utilidad. Cada carpeta es un script o herramienta independiente.

## Scripts disponibles

| Carpeta | Descripción |
|---|---|
| `poetrade-poc` | Prueba de concepto de la API de Path of Exile Trade |

## Estructura

```
python-scripts/
└── nombre-script/
    ├── main.py
    ├── requirements.txt   # solo si tiene dependencias externas
    └── README.md          # solo si necesita explicación extra
```

## Uso

Cada script es independiente. Entra en su carpeta y ejecútalo:

```bash
cd nombre-script
py main.py
```

Si tiene dependencias:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py main.py
```
