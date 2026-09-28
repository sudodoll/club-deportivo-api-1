# Club Deportivo API

API REST en Python y Flask para gestionar las canchas, los socios y las reservas del Club Deportivo Encuentro.

## Integrantes

Contreras Franco Leandro, 116585, imthegarbage
Nieto Valentina, 109046, sudodoll

## Motivación

El Club Deportivo Encuentro dispone de canchas de fútbol, tenis y pádel que sus socios pueden reservar.
Actualmente, el personal recibe las solicitudes por teléfono y mensajes, y registra los turnos en una
planilla compartida.
Este procedimiento genera reservas superpuestas, dificultades para consultar los horarios disponibles y
cancelaciones que no se reflejan correctamente. Además, los cambios de tarifas dificultan reconstruir el
importe acordado para una reserva anterior.
El club solicita una API que centralice la información de sus canchas y socios, permita gestionar reservas
y conserve el historial de las operaciones.

## Versiones utilizadas

| Herramienta | Versión |
|---|---|
| Python | 3.10 o superior (probado con 3.11) |
| MySQL | 8 (imagen `mysql:8` de Docker) |
| Flask | 2.3.2 |
| Werkzeug | 2.3.6 |
| SQLAlchemy | 2.0.36 |
| mysql-connector-python | 9.0.0 |
| flask-cors | 4.0.0 |
| python-dotenv | 1.1.0 |

Las dependencias de Python están en `requirements.txt`.

## Arquitectura

La API está organizada en capas, cada una con una responsabilidad:

```
Pedido HTTP
    │
    ▼
routes/         Reciben el pedido HTTP y devuelven la respuesta (JSON y código de estado)
    │
    ▼
validators/     Validan los datos de entrada: tipos, formatos, campos y parámetros permitidos
    │
    ▼
services/       Aplican las reglas de negocio: superposiciones, importes, transiciones de estado
    │
    ▼
db.py y         Acceden a MySQL. Todas las consultas reciben los datos mediante parámetros
repositories/
    │
    ▼
MySQL
```

- Cada recurso (deportes, canchas, socios y reservas) es un **Blueprint** de Flask registrado en `app.py` bajo la URL base `/club_deportivo_api`.
- `db.py` contiene la conexión a MySQL con SQLAlchemy (`ejecutar_consulta` y `ejecutar_mutacion`) y las consultas de canchas y reservas. Las consultas de socios y deportes están en `repositories/`.
- La creación de reservas se hace dentro de una transacción que bloquea la cancha y el socio (`SELECT ... FOR UPDATE`), para que dos pedidos simultáneos no puedan generar reservas superpuestas.
- Los errores se responden siempre con el mismo formato JSON (ver [Formato de errores](#formato-de-errores)).

## Estructura del proyecto

```
club-deportivo-api/
├── app.py                      Crea la aplicación Flask y registra los Blueprints
├── requirements.txt            Dependencias de Python
├── .env.example                Configuración de ejemplo (sin credenciales reales)
├── docker-compose.yml          Levanta MySQL 8 y carga db/init_db.sql
├── setup_virtualenv.sh         Instalación y ejecución en Linux / macOS
├── setup_virtualenv.bat        Instalación y ejecución en Windows
├── db/
│   └── init_db.sql             Crea la base, las tablas y los datos de prueba
├── docs/
│   └── swagger.yaml            Contrato de la API (OpenAPI 3.0)
└── club_deportivo/
    ├── constants.py            URL base, configuración, reglas y códigos de error
    ├── db.py                   Conexión a MySQL y consultas de canchas y reservas
    ├── utils.py                Funciones comunes: errores, validaciones y paginación
    ├── routes/                 Endpoints de cada recurso
    │   ├── deportes.py
    │   ├── canchas.py
    │   ├── socios.py
    │   └── reservas.py
    ├── validators/             Validación de los datos de entrada de cada recurso
    ├── services/               Reglas de negocio de cada recurso
    └── repositories/           Consultas a MySQL de socios y deportes
```

## Instalación y ejecución

### Requisitos previos

- Python 3.10 o superior.
- Git.
- **Una** de estas dos opciones para MySQL:
  - Docker y Docker Compose (recomendado), o
  - MySQL 8 instalado localmente.

### 1. Clonar el repositorio

```bash
git clone https://github.com/sudodoll/club-deportivo-api-1.git
cd club-deportivo-api-1
```

### 2. Configuración (`.env`)

Copiar el archivo de ejemplo:

```bash
# Linux / macOS / Git Bash
cp .env.example .env

# Windows (cmd o PowerShell)
copy .env.example .env
```

Contenido del `.env`:

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DB_HOST` | `localhost` | Host de MySQL |
| `DB_PORT` | `3306` | Puerto de MySQL |
| `DB_USER` | `root` | Usuario de MySQL |
| `DB_PASSWORD` | `root` | Contraseña de MySQL |
| `DB_NAME` | `club_deportivo` | Nombre de la base de datos |

> **Importante:** `DB_NAME` tiene que ser `club_deportivo`, porque es la base que crea `db/init_db.sql`.
> Si usás MySQL local con otro usuario o contraseña, cambiá `DB_USER` y `DB_PASSWORD`.
> El archivo `.env` no se sube al repositorio (está en `.gitignore`).

### 3. Base de datos

Elegir **una** de las dos opciones.

#### Opción A: con Docker (recomendado)

`docker-compose.yml` levanta MySQL 8 con los datos del `.env` y ejecuta `db/init_db.sql` la **primera vez** que se crea el contenedor:

```bash
docker compose up -d
```

Esperar a que MySQL esté listo (puede tardar unos segundos):

```bash
docker compose logs -f mysql
# Buscar la línea "ready for connections" y salir con Ctrl+C
```

Otros comandos útiles:

```bash
docker compose down      # apaga el contenedor y conserva los datos
docker compose down -v   # apaga y BORRA los datos; al volver a levantarlo se recarga init_db.sql
```

> Si ya habías levantado el contenedor con una versión anterior de `init_db.sql`, ejecutá
> `docker compose down -v` y después `docker compose up -d` para que se cree de nuevo.

#### Opción B: con MySQL instalado localmente

El script crea la base `club_deportivo`, las tablas y los datos de prueba:

```bash
# Linux / macOS / Git Bash
mysql -u root -p < db/init_db.sql
```

```powershell
# Windows PowerShell
Get-Content db\init_db.sql | mysql -u root -p
```

Verificar que se crearon las tablas:

```bash
mysql -u root -p -e "USE club_deportivo; SHOW TABLES;"
```

Se tienen que ver: `canchas`, `deportes`, `reservas` y `socios`.

> El script empieza con `CREATE DATABASE IF NOT EXISTS`, pero las tablas se crean con
> `CREATE TABLE IF NOT EXISTS`: para empezar de cero, borrar antes la base con
> `mysql -u root -p -e "DROP DATABASE club_deportivo;"`.

### 4. Entorno virtual, dependencias y ejecución

**Opción rápida:** los scripts crean el entorno virtual, instalan las dependencias y levantan la API.

```bash
# Linux / macOS
chmod +x setup_virtualenv.sh
./setup_virtualenv.sh

# Windows (cmd)
setup_virtualenv.bat

# Windows (PowerShell)
.\setup_virtualenv.bat
```

**Opción manual:**

```bash
python -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

pip install -r requirements.txt
python app.py
```

La API queda disponible en:

```
http://localhost:5000/club_deportivo_api
```

Para comprobar que funciona: abrir `http://localhost:5000/club_deportivo_api/deportes` en el navegador.

### 5. Documentación del contrato (Swagger)

El contrato completo está en `docs/swagger.yaml` (OpenAPI 3.0). Se puede ver pegando el contenido en
[https://editor.swagger.io](https://editor.swagger.io). Desde ahí también se pueden probar los endpoints
mientras la API está corriendo.

## Datos de prueba

`db/init_db.sql` carga estos datos ficticios:

| Tabla | Datos |
|---|---|
| Deportes | 1 Futbol, 2 Tenis, 3 Padel |
| Canchas | 6 canchas: 1 y 2 de fútbol, 3 y 4 de tenis, 5 y 6 de pádel. La cancha 6 está **inactiva** |
| Socios | 1 Federico, 2 Nicolas (**inactivo**), 3 Santiago |
| Reservas | 1: socio 1, cancha 1, 15/10/2026 de 18 a 20 (confirmada). 2: socio 3, cancha 3, 16/10/2026 de 19 a 20 (cancelada) |

## Endpoints

Todas las rutas empiezan con `/club_deportivo_api`.

| Método | Ruta | Descripción | Respuesta exitosa |
|---|---|---|---|
| GET | `/deportes` | Lista los deportes precargados (sin paginación) | 200 |
| GET | `/canchas` | Lista canchas. Filtros: `id_deporte`, `nombre`, `techada`, `activa` | 200 |
| POST | `/canchas` | Crea una cancha | 201 (cuerpo vacío y header `Location`) |
| GET | `/canchas/{id}` | Obtiene una cancha | 200 |
| PATCH | `/canchas/{id}` | Modifica `nombre`, `precio_hora`, `techada` y/o `activa` | 200 |
| DELETE | `/canchas/{id}` | Elimina una cancha sin reservas | 204 |
| GET | `/canchas/disponibles` | Canchas activas libres. Obligatorios: `fecha`, `hora_inicio`, `hora_fin`. Filtros: `id_deporte`, `techada` | 200 |
| GET | `/socios` | Lista socios. Filtros: `nombre`, `activo` | 200 |
| POST | `/socios` | Crea un socio | 201 |
| GET | `/socios/{id}` | Obtiene un socio | 200 |
| PATCH | `/socios/{id}` | Modifica `nombre`, `email` y/o `activo` | 200 |
| GET | `/reservas` | Lista reservas. Filtros: `id_cancha`, `id_socio`, `estado`, `fecha_desde`, `fecha_hasta` | 200 |
| POST | `/reservas` | Crea una reserva | 201 |
| GET | `/reservas/{id}` | Obtiene una reserva con su estado, tarifa histórica e importe | 200 |
| PUT | `/reservas/{id}/estado` | Cambia el estado de una reserva | 200 |

Los listados (salvo deportes) admiten `_limit` (entre 1 y 100, por defecto 10) y `_offset` (0 o más, por
defecto 0). Los resultados se filtran, se ordenan por `id` y después se paginan.

## Ejemplos de solicitudes

Los ejemplos usan `curl` y los datos de prueba de `init_db.sql`. En Windows se pueden ejecutar desde
Git Bash, o usar Postman con la misma URL, método y cuerpo.

### Listar los deportes

```bash
curl http://localhost:5000/club_deportivo_api/deportes
```

```json
{
    "deportes": [
        { "id": 1, "nombre": "Futbol" },
        { "id": 2, "nombre": "Tenis" },
        { "id": 3, "nombre": "Padel" }
    ]
}
```

### Listar canchas con filtro y paginación

```bash
curl "http://localhost:5000/club_deportivo_api/canchas?id_deporte=2&_limit=1"
```

```json
{
    "canchas": [
        {
            "id": 3,
            "nombre": "Cancha 3 - Tenis",
            "id_deporte": 2,
            "precio_hora": 600000,
            "techada": false,
            "activa": true
        }
    ],
    "_links": {
        "_first": { "href": "http://localhost:5000/club_deportivo_api/canchas?id_deporte=2&_limit=1&_offset=0" },
        "_next":  { "href": "http://localhost:5000/club_deportivo_api/canchas?id_deporte=2&_limit=1&_offset=1" },
        "_last":  { "href": "http://localhost:5000/club_deportivo_api/canchas?id_deporte=2&_limit=1&_offset=1" }
    }
}
```

### Consultar canchas disponibles

La cancha 1 no aparece porque tiene una reserva confirmada en ese horario.

```bash
curl "http://localhost:5000/club_deportivo_api/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00:00&hora_fin=20:00:00&id_deporte=1"
```

```json
{
    "canchas": [
        {
            "id": 2,
            "nombre": "Cancha 2 - Futbol 11",
            "id_deporte": 1,
            "precio_hora": 1800000,
            "techada": false,
            "activa": true
        }
    ],
    "_links": { "_first": { "href": "..." }, "_last": { "href": "..." } }
}
```

### Crear un socio

El email se guarda en minúsculas y sin espacios en los extremos. El servidor asigna `activo: true`.

```bash
curl -X POST http://localhost:5000/club_deportivo_api/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ana Gomez", "email": "  Ana.Gomez@Mail.com "}'
```

```
HTTP/1.1 201 CREATED
Location: http://localhost:5000/club_deportivo_api/socios/4
```
```json
{ "id": 4, "nombre": "Ana Gomez", "email": "ana.gomez@mail.com", "activo": true }
```

### Crear una reserva

La fecha tiene que ser futura al momento de probarlo. El servidor calcula el importe: 2 horas × 600000 = 1200000.

```bash
curl -X POST http://localhost:5000/club_deportivo_api/reservas \
  -H "Content-Type: application/json" \
  -d '{"id_socio": 1, "id_cancha": 3, "fecha_hora_inicio": "2026-12-10T18:00:00.000000-03:00", "fecha_hora_fin": "2026-12-10T20:00:00.000000-03:00"}'
```

```
HTTP/1.1 201 CREATED
Location: http://localhost:5000/club_deportivo_api/reservas/3
```
```json
{
    "id": 3,
    "id_socio": 1,
    "id_cancha": 3,
    "fecha_hora_inicio": "2026-12-10T18:00:00.000000-03:00",
    "fecha_hora_fin": "2026-12-10T20:00:00.000000-03:00",
    "estado": "confirmada",
    "precio_hora": 600000,
    "precio_total": 1200000
}
```

Si se repite el mismo pedido, la cancha ya está ocupada en ese horario:

```
HTTP/1.1 409 CONFLICT
```
```json
{
    "errors": [
        {
            "code": "ERROR_SUPERPOSICION",
            "message": "La cancha ya tiene una reserva confirmada que se superpone con el intervalo",
            "level": "error",
            "description": "La cancha ya tiene una reserva confirmada que se superpone con el intervalo"
        }
    ]
}
```

### Cambiar el precio de una cancha (la reserva conserva su tarifa)

```bash
curl -X PATCH http://localhost:5000/club_deportivo_api/canchas/3 \
  -H "Content-Type: application/json" \
  -d '{"precio_hora": 650000}'
```

```json
{ "id": 3, "nombre": "Cancha 3 - Tenis", "id_deporte": 2, "precio_hora": 650000, "techada": false, "activa": true }
```

La reserva creada antes mantiene `precio_hora: 600000` y `precio_total: 1200000`:

```bash
curl http://localhost:5000/club_deportivo_api/reservas/3
```

### Listar reservas con filtros

```bash
curl "http://localhost:5000/club_deportivo_api/reservas?id_socio=1&estado=confirmada&fecha_desde=2026-10-01&fecha_hasta=2026-12-31&_limit=1"
```

### Cancelar una reserva

```bash
curl -X PUT http://localhost:5000/club_deportivo_api/reservas/3/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "cancelada"}'
```

```json
{
    "id": 3,
    "id_socio": 1,
    "id_cancha": 3,
    "fecha_hora_inicio": "2026-12-10T18:00:00.000000-03:00",
    "fecha_hora_fin": "2026-12-10T20:00:00.000000-03:00",
    "estado": "cancelada",
    "precio_hora": 600000,
    "precio_total": 1200000
}
```

Intentar reactivarla responde 409:

```bash
curl -X PUT http://localhost:5000/club_deportivo_api/reservas/3/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "confirmada"}'
```

```json
{
    "errors": [
        {
            "code": "ERROR_TRANSICION_NO_PERMITIDA",
            "message": "Cambio de estado no permitido",
            "level": "error",
            "description": "Una reserva cancelada no puede pasar a confirmada"
        }
    ]
}
```

### Eliminar una cancha con reservas

```bash
curl -X DELETE http://localhost:5000/club_deportivo_api/canchas/1
```

```
HTTP/1.1 409 CONFLICT
```
```json
{
    "errors": [
        {
            "code": "ERROR_CANCHA_CON_RESERVAS",
            "message": "La cancha tiene reservas asociadas",
            "level": "error",
            "description": "No se puede eliminar la cancha con id '1' porque tiene reservas asociadas. Puede desactivarse mediante PATCH"
        }
    ]
}
```

### Error de validación

```bash
curl -X POST http://localhost:5000/club_deportivo_api/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "", "email": "mal"}'
```

```
HTTP/1.1 400 BAD REQUEST
```
```json
{
    "errors": [
        {
            "code": "ERROR_VALIDACION",
            "message": "Campo requerido: 'nombre'",
            "level": "error",
            "description": "El campo 'nombre' es obligatorio y no puede estar vacio"
        },
        {
            "code": "ERROR_VALIDACION",
            "message": "Formato de 'email' invalido",
            "level": "error",
            "description": "El valor 'mal' no es un email valido (ejemplo: nombre@dominio.com)"
        }
    ]
}
```

## Formato de errores

Todos los errores responden con esta estructura:

```json
{
    "errors": [
        {
            "code": "ERROR_VALIDACION",
            "message": "Resumen breve",
            "level": "error",
            "description": "Detalle del problema"
        }
    ]
}
```

| Código | HTTP | Cuándo |
|---|---|---|
| `ERROR_VALIDACION` | 400 | Datos inválidos, campos o parámetros desconocidos, cuerpo vacío en una actualización |
| `ERROR_BODY_INVALIDO` | 400 | El cuerpo no es un objeto JSON |
| `ERROR_CANCHA_NO_ENCONTRADA` | 404 | La cancha no existe |
| `ERROR_DEPORTE_NO_ENCONTRADO` | 404 | El deporte indicado al crear una cancha no existe |
| `ERROR_SOCIO_NO_ENCONTRADO` | 404 | El socio no existe |
| `ERROR_RESERVA_NO_ENCONTRADA` | 404 | La reserva no existe |
| `ERROR_EMAIL_DUPLICADO` | 409 | El email ya pertenece a otro socio (activo o inactivo) |
| `ERROR_ENTIDAD_INACTIVA` | 409 | La cancha o el socio de una reserva nueva están inactivos |
| `ERROR_SUPERPOSICION` | 409 | La cancha o el socio ya tienen una reserva confirmada que se superpone |
| `ERROR_TRANSICION_NO_PERMITIDA` | 409 | Cambio de estado no permitido o fuera del momento permitido |
| `ERROR_CANCHA_CON_RESERVAS` | 409 | Se intenta eliminar una cancha que tiene reservas |
| `ERROR_INTERNO` | 500 | Error no previsto (por ejemplo, la base de datos no responde) |

## Supuestos adoptados

**Generales**

- No hay autenticación ni notificaciones, como indica el enunciado.
- Todas las fechas y horas se interpretan en GMT-3 y se guardan sin zona horaria en la base.
- Los precios son enteros en centavos (1000000 = $10.000,00).
- Se rechazan con 400 los campos del cuerpo y los parámetros de la URL que no correspondan al endpoint.
- Los filtros booleanos solo admiten `true` o `false` en minúscula. En el cuerpo JSON se exige el tipo booleano (`true`/`false`, sin comillas).
- Los identificadores deben ser enteros positivos. Un id con formato inválido (por ejemplo `abc` o `0`) responde 400; un id válido que no existe responde 404.
- Las búsquedas por `nombre` son parciales y no distinguen mayúsculas de minúsculas.
- Un listado sin resultados, o con un `_offset` mayor a la cantidad de resultados, responde 200 con la lista vacía.
- Los enlaces de `_links` son URLs completas y conservan los filtros aplicados. `_prev` no aparece en la primera página y `_next` no aparece en la última.

**Canchas**

- `POST /canchas` responde 201 con el cuerpo vacío y la URL de la cancha creada en el header `Location`.
- El deporte de una cancha no se puede modificar: enviar `id_deporte` en un PATCH responde 400.
- Una cancha solo se puede eliminar si no tiene ninguna reserva, sin importar su estado. Si tiene, responde 409 y se puede desactivar con PATCH.
- `/canchas/disponibles` recibe `fecha` con formato `YYYY-MM-DD` y `hora_inicio` / `hora_fin` con formato `HH:MM:SS` en horas en punto. El intervalo tiene que cumplir las mismas reglas que una reserva nueva y devuelve solo canchas activas. Solo informa: no reserva ni retiene la cancha.

**Socios**

- El nombre se guarda sin espacios en los extremos (hasta 60 caracteres). El email se guarda en minúsculas y sin espacios en los extremos (hasta 80 caracteres), con el formato `texto@dominio.extension`.
- No puede haber dos socios con el mismo email, aunque uno de ellos esté inactivo. Al modificar un socio, su propio email no cuenta como repetido.
- Todo socio nuevo se crea activo. No hay endpoint para eliminar socios.

**Reservas**

- `fecha_hora_inicio` y `fecha_hora_fin` deben tener exactamente el formato `YYYY-MM-DDTHH:MM:SS.ffffff-03:00` (6 decimales).
- Una reserva dura entre 1 y 3 horas completas, empieza y termina en hora en punto, dentro del horario del club (de 08:00 a 23:00, terminando como máximo a las 23:00), no atraviesa la medianoche y empieza en el futuro.
- Dos intervalos se superponen si uno empieza antes de que el otro termine. Las reservas consecutivas (por ejemplo, 18 a 20 y 20 a 21) están permitidas.
- Solo las reservas **confirmadas** ocupan el horario. Una reserva cancelada lo libera, pero el registro se conserva.
- Si el socio o la cancha no existen, responde 404. Si existen pero están inactivos, responde 409.
- La tarifa por hora y el importe total se guardan al crear la reserva y no cambian si después se modifica el precio de la cancha.
- Desactivar un socio o una cancha no cancela sus reservas existentes.
- Transiciones de estado (`PUT /reservas/{id}/estado`):
  - `confirmada` → `cancelada`: solo si todavía no llegó el horario de inicio.
  - `confirmada` → `finalizada`: solo si ya se alcanzó el horario de fin.
  - Una reserva en curso (ya empezó y todavía no terminó) no se puede cancelar ni finalizar.
  - `cancelada` y `finalizada` no pueden cambiar a otro estado (409).
  - Pedir el estado actual responde 200 sin modificar la reserva.
  - Un estado que no sea `confirmada`, `cancelada` o `finalizada` responde 400.
- Los cambios de estado son explícitos: no hay tareas automáticas que finalicen reservas.
- El filtro `fecha_desde` / `fecha_hasta` se aplica al día de la reserva (el día de `fecha_hora_inicio`) e incluye ambos extremos. Se puede enviar uno solo; si se envían los dos, `fecha_desde` no puede ser posterior a `fecha_hasta`.
