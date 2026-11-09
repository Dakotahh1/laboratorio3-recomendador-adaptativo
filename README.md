# Laboratorio 3: Aplicación inteligente adaptativa

Recomendador de recursos de aprendizaje basado en contenido. Cada usuario declara sus intereses, el sistema le sugiere recursos del catálogo y, cuando marca uno con **Me interesa**, su perfil se actualiza y las recomendaciones se recalculan en la misma ejecución. El núcleo está hecho en Python y se usa por consola.

## Identificación

- **Integrantes:** Vicente Palma, Diego Alvarado, Lucas Pinto
- **Asignatura:** Ingeniería Web Avanzada (OII436-1), Laboratorio 3
- **Repositorio:** https://github.com/Dakotahh1/laboratorio3-recomendador-adaptativo
- **Fecha:** 9 de noviembre de 2026

## Contenido del repositorio

| Archivo o carpeta | Contenido |
|---|---|
| `motor.py` | Motor de recomendación. Completamos `crear_perfil`, `calcular_puntuaciones`, `recomendar` y `actualizar_perfil`. |
| `app.py` | Aplicación de consola del material base (modos `--comprobar`, `--demo` e interactivo). No la modificamos. |
| `datos/recursos.csv` | Catálogo de 12 recursos con `id`, `titulo`, `descripcion` y `etiquetas`. |
| `datos/perfiles.json` | Intereses iniciales de u1, u2, u3 y u4. |
| `evidencias/reporte_demo.json` | Registro generado por `--demo`: perfiles, historiales, recomendaciones y comprobaciones de T1 a T4. |
| `evidencias/puntuaciones_antes_despues.csv` | Puntuaciones de los 12 recursos para u1 antes y después de valorar R04. |
| `evidencias/salida_demo.txt` | Salida de consola de `--demo`. |
| `evidencias/sesion_interactiva.txt` | Sesión del modo interactivo (detalle en la sección 2). |
| `requirements.txt` | Dependencias con versión fija, generadas con `pip freeze`. |
| `.gitignore` | Excluye `.venv/`, `__pycache__/`, archivos `.env` y temporales. |

Trabajamos sobre el material base: solo completamos los cuatro bloques TODO de `motor.py`. No cambiamos `app.py` ni los datos de prueba.

## 1. Preparación del entorno

Versión usada: **Python 3.13.1**, en Windows 11 con PowerShell.

```powershell
# Crear el entorno virtual dentro de la carpeta del proyecto
py -m venv .venv            # o bien: python -m venv .venv

# Activarlo (este es el comando que usamos)
.venv\Scripts\Activate.ps1

# Instalar dependencias y comprobar
python -m pip install -r requirements.txt
python -c "import sys; print(sys.executable)"
python app.py --comprobar
```

| Terminal | Comando de activación |
|---|---|
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows CMD | `.venv\Scripts\activate.bat` |
| macOS o Linux | `source .venv/bin/activate` |

Con el entorno activo, `sys.executable` tiene que apuntar al Python de la carpeta `.venv` (`.venv\Scripts\python.exe` en Windows). Si PowerShell no deja ejecutar `Activate.ps1` por la política de ejecución, se puede permitir solo en esa ventana con `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, o usar CMD.

El `requirements.txt` lo generamos al final con `python -m pip freeze > requirements.txt`, así que tiene las versiones exactas con las que probamos: numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1 y scipy 1.18.1, más sus dependencias. **Ojo:** numpy 2.5.4 y scipy 1.18.1 piden Python 3.12 o superior, así que con Python 3.10 o 3.11 esa instalación falla. En ese caso se pueden instalar las tres librerías sin fijar versión: `python -m pip install numpy pandas scikit-learn`.

Salida de `python app.py --comprobar`:

```
Comprobación de preparación completada.
Recursos: 12 | Usuarios: 4
Matriz TF-IDF: 12 filas x 17 términos
Vocabulario: angular, api, componentes, consultas, datos, formularios, funciones, graficos, http, interfaces, pandas, python, sql, tablas, validacion, variables, web
Se cargaron los datos y el índice sin ejecutar los bloques del estudiante.
```

## 2. Ejecución

```powershell
python app.py --demo    # ejecuta T1-T4 desde los perfiles iniciales y escribe evidencias/
python app.py           # modo interactivo
```

`--demo` siempre parte de los perfiles del JSON, así que se puede repetir y entrega los mismos resultados. Termina con código 0 cuando las cuatro pruebas cumplen.

En el modo interactivo se elige un usuario y después: `r` recomendar, `c` ver el catálogo, `m` Me interesa (acepta cualquier id del catálogo, aunque no esté entre los tres primeros), `u` cambiar de usuario y `s` salir. El estado se mantiene mientras el programa está abierto; al reiniciarlo se vuelven a cargar los intereses de `perfiles.json` y los historiales quedan vacíos.

Para dejar registro del modo interactivo guardamos `evidencias/sesion_interactiva.txt`. Las entradas se enviaron por la entrada estándar, por eso no aparecen escritas en el archivo. Fueron, en orden: `u1, r, m, R99, m, r04, u, u2, r, u, u3, r, m, R07, u, u1, s`. En esa sesión se ve que:

- `R99` no existe: aparece `No existe el recurso R99.` y el perfil y el historial de u1 siguen igual.
- `r04` en minúsculas también funciona, porque la app pasa el id a mayúsculas.
- Después de la valoración de u1, u2 mantiene su perfil, su historial vacío y sus recomendaciones.
- u3 no recibe recomendaciones, pero después de marcar R07 su perfil queda igual al vector de R07 y empieza a recibir R07, R08 y R09.
- Al volver a u1, su perfil actualizado y su historial siguen ahí.

Comandos con los que guardamos las dos salidas de consola (en Git Bash; `-X utf8` es para que los acentos queden bien en el archivo):

```bash
python -X utf8 app.py --demo --evidencias evidencias > evidencias/salida_demo.txt
printf 'u1\nr\nm\nR99\nm\nr04\nu\nu2\nr\nu\nu3\nr\nm\nR07\nu\nu1\ns\n' | python -X utf8 app.py > evidencias/sesion_interactiva.txt
```

## 3. Catálogo y perfil inicial

`datos/recursos.csv` tiene 12 recursos (R01 a R12) con las columnas `id`, `titulo`, `descripcion` y `etiquetas`.

- **Campos que entran en el cálculo:** solo `etiquetas`. `construir_indice` aplica `fit_transform` sobre esa columna y arma una matriz TF-IDF de 12 x 17 (hay 17 términos distintos). El `id` sirve para identificar el recurso: validar el id de Me interesa, desempatar y registrar el historial. `titulo` y `descripcion` solo se muestran.
- **Valores vacíos:** `cargar_catalogo` lee todo como texto con `keep_default_na=False` (una celda vacía queda como `""` y no como `NaN`), quita espacios con `strip()` y, si alguna columna tiene un valor vacío, rechaza el archivo con `ValueError`. Lo probamos con un CSV de prueba con una etiqueta vacía y el mensaje fue `La columna etiquetas contiene valores vacíos.`
- **Ids repetidos:** también se rechazan, con `recursos["id"].duplicated()`. Con un CSV que tenía R01 dos veces salió `Los identificadores de recursos deben ser únicos.`
- Además se valida que estén las cuatro columnas y que el catálogo no venga vacío. En todos estos casos `app.py` muestra `Error: ...` y termina con código 1. No se intenta reparar el catálogo ni se descartan filas en silencio.

En `datos/perfiles.json` cada usuario tiene `nombre` e `intereses`, y solo `intereses` se vectoriza. u3 tiene los intereses vacíos y u4 tiene `zzxyz123`, que no está en el vocabulario. Los dos quedan como un vector de ceros, que se ve como perfil `{}`.

Durante la ejecución el perfil de cada usuario tiene tres partes:

1. **Intereses iniciales:** el texto del JSON. Es el punto de partida y no se modifica.
2. **Vector actual:** `estado[usuario_id]` en `app.py`, con 17 pesos (uno por término). Es lo que se actualiza.
3. **Historial:** `historial[usuario_id]`, la lista de eventos Me interesa.

`crear_estado` arma un vector distinto para cada usuario y `registrar_interes` trabaja con copias, por eso modificar a u1 no afecta a u2 (prueba T3).

## 4. Implementación de `motor.py`

| Función | Implementación | Por qué |
|---|---|---|
| `crear_perfil` | `vectorizador.transform([intereses]).toarray()[0]` | `transform` usa el vocabulario y los IDF aprendidos del catálogo, sin volver a ajustar. Se pasa una lista porque el vectorizador espera una colección de documentos, y `[0]` deja un vector 1D de 17 valores. Las palabras que no están en el vocabulario se ignoran. |
| `calcular_puntuaciones` | `cosine_similarity([perfil], matriz)[0]` | `cosine_similarity` trabaja con matrices 2D, por eso `[perfil]`. Devuelve 12 valores en el mismo orden del CSV. Con un perfil nulo devuelve ceros y no `NaN` (lo revisamos con u3 y u4). |
| `recomendar` | Ordena los índices con la clave `(-puntuación, id)`, corta en el primer valor `<= 0` o al llegar a `top_k` y arma cada resultado con `construir_resultado`. | El signo negativo ordena de mayor a menor y el id desempata en orden ascendente. Se ordena con los valores sin redondear. Si no hay puntuaciones positivas devuelve `[]`, sin rellenar con recursos de puntuación cero. |
| `actualizar_perfil` | `normalize([(1 - alpha) * perfil + alpha * vector_recurso])[0]` con `alpha = 0.6` | El perfil anterior conserva un 40 % y el recurso valorado aporta un 60 %. Sin normalizar, la mezcla queda con largo 0.8003 en la prueba de u1 con R04. La norma L2 la deja en 1, igual que las filas TF-IDF, para que en la siguiente actualización el 0.4 y el 0.6 se apliquen sobre vectores de la misma magnitud. Como el coseno solo usa la dirección, normalizar no cambia el ranking de ese momento. |

`alpha = 0.6` es el valor didáctico que pide la guía, no un valor ajustado con datos.

## 5. Resultados de la ejecución

Los valores salen de `evidencias/reporte_demo.json` y `evidencias/puntuaciones_antes_despues.csv`. Aquí se muestran con 4 decimales, pero los cálculos se hicieron sin redondear.

### 5.1 Rankings iniciales (T1)

**u1** (intereses: `python datos pandas`)

| Puesto | id | Título | Puntuación | Explicación |
|---|---|---|---|---|
| 1 | R02 | Análisis de datos con Pandas | 1.0000 | Términos compartidos: datos, pandas, python. |
| 2 | R12 | Conectar Python con datos SQL | 0.4965 | Términos compartidos: datos, python. |
| 3 | R03 | Gráficos con Python | 0.4326 | Términos compartidos: datos, python. |

**u2** (intereses: `angular componentes interfaces`)

| Puesto | id | Título | Puntuación | Explicación |
|---|---|---|---|---|
| 1 | R07 | Componentes e interfaces en Angular | 1.0000 | Términos compartidos: angular, componentes, interfaces. |
| 2 | R08 | Formularios e interfaces en Angular | 0.5677 | Términos compartidos: angular, interfaces. |
| 3 | R09 | Consumir una API desde Angular | 0.3087 | Términos compartidos: angular. |

R02 y R07 tienen 1.0000 porque sus etiquetas son exactamente los intereses declarados. Algo que nos llamó la atención es que R12 queda sobre R03, aunque los dos comparten python y datos con u1. La diferencia está en el tercer término: graficos aparece solo en R03 (IDF 2.8718) y sql aparece en tres recursos (IDF 2.1787). Como graficos es más raro, se lleva más peso dentro del vector de R03 y deja menos para python y datos.

**Desempates.** En los top 3 no hubo empates, así que los revisamos pidiendo más resultados:

```powershell
python -c "import app, motor; r, u, v, m = app.cargar_datos(); p = motor.crear_perfil(u['u1']['intereses'], v); print([(x['id'], round(x['puntuacion'], 4)) for x in motor.recomendar(p, r, m, v, top_k=6)])"
```

```
[('R02', 1.0), ('R12', 0.4965), ('R03', 0.4326), ('R04', 0.251), ('R10', 0.2053), ('R11', 0.2053)]
```

R10 y R11 tienen exactamente la misma puntuación y quedan ordenados por id. Lo mismo pasa con R05 y R06 después de valorar R04: los dos quedan con 0.4378 y el ranking con `top_k=6` termina en `('R05', 0.4378), ('R06', 0.4378)`.

### 5.2 Adaptación de u1 al valorar R04 (T2)

**Historial de u1**

- Antes: `[]`
- Después: `[{"numero": 1, "accion": "Me interesa", "recurso": "R04"}]`

**Perfil de u1 (pesos no nulos)**

| Término | Antes | Después |
|---|---|---|
| python | 0.465091 | 0.637116 |
| api | 0 | 0.446269 |
| web | 0 | 0.446269 |
| pandas | 0.753247 | 0.376477 |
| datos | 0.465091 | 0.232455 |

El vector de R04 es `api 0.595257, web 0.595257, python 0.539758`. Al mezclar 0.4 del perfil con 0.6 de R04 y normalizar, entran web y api, python sube porque está en los dos vectores, y pandas y datos bajan porque solo los aportaba el perfil anterior.

**Recomendaciones de u1**

| Puesto | Antes | Después |
|---|---|---|
| 1 | R02 Análisis de datos con Pandas (1.0000) | R04 API web con Python (0.8752) |
| 2 | R12 Conectar Python con datos SQL (0.4965) | R02 Análisis de datos con Pandas (0.6880) |
| 3 | R03 Gráficos con Python (0.4326) | R09 Consumir una API desde Angular (0.4958) |

**Puntuaciones de los mismos 12 candidatos**

| id | Etiquetas | Antes | Después | Diferencia |
|---|---|---|---|---|
| R01 | python variables funciones | 0.1861 | 0.2549 | +0.0688 |
| R02 | python datos pandas | 1.0000 | 0.6880 | -0.3120 |
| R03 | python datos graficos | 0.4326 | 0.4044 | -0.0282 |
| R04 | python web api | 0.2510 | 0.8752 | +0.6241 (recurso valorado) |
| **R05** | **web api http** | **0.0000** | **0.4378** | **+0.4378** |
| R06 | web api validacion | 0.0000 | 0.4378 | +0.4378 |
| R07 | angular componentes interfaces | 0.0000 | 0.0000 | 0.0000 |
| R08 | angular formularios interfaces | 0.0000 | 0.0000 | 0.0000 |
| **R09** | **angular web api** | **0.0000** | **0.4958** | **+0.4958** |
| R10 | sql datos consultas | 0.2053 | 0.1026 | -0.1027 |
| R11 | sql datos tablas | 0.2053 | 0.1026 | -0.1027 |
| R12 | python sql datos | 0.4965 | 0.4642 | -0.0324 |

La diferencia se calculó con los valores completos y después se redondeó, por eso en algunas filas no coincide exacto con restar las columnas redondeadas.

**Recurso no valorado: R05 (Principios de una API HTTP).** u1 nunca interactuó con R05 y aun así su puntuación pasó de 0.0000 a 0.4378. Antes de la interacción el perfil solo tenía python, datos y pandas, y R05 no tiene ninguno de esos términos, así que el coseno era 0. Al valorar R04 el perfil incorporó web y api con 0.446269 cada uno. R05 tiene justamente web y api (0.490485 cada uno en su vector), entonces ahora el producto da 0.446269 × 0.490485 × 2 ≈ 0.4378. R05 no cambió en nada; lo que cambió fue el perfil, y eso es lo que muestra que la interacción tuvo efecto en el cálculo y no solo en la pantalla.

**R09** es el caso más visible: pasa de 0 a 0.4958 y entra al top 3, desplazando a R12 y R03. Comparte con el perfil los mismos dos términos que R05 (web y api), pero queda más arriba porque su tercer término, angular, es más común en el catálogo (IDF 2.1787) que http en R05 (IDF 2.8718). Después de normalizar, R09 le deja más peso a web y api (0.555449 contra 0.490485).

Otros cambios que se explican igual: R02 baja de 1.0000 a 0.6880, pero sigue segundo porque el perfil conserva el 40 % de los intereses anteriores. R01 sube porque python ganó peso, y R10 y R11 bajan a la mitad porque datos perdió peso. R07 y R08 se quedan en 0 porque no comparten términos ni con el perfil ni con R04. Los 12 candidatos son los mismos antes y después: R04 no se saca del catálogo.

### 5.3 u2 antes y después de la interacción de u1 (T3)

| Elemento | Antes | Después |
|---|---|---|
| Perfil | componentes 0.657512, interfaces 0.564679, angular 0.498813 | componentes 0.657512, interfaces 0.564679, angular 0.498813 |
| Historial | `[]` | `[]` |
| Recomendaciones | R07 (1.0000), R08 (0.5677), R09 (0.3087) | R07 (1.0000), R08 (0.5677), R09 (0.3087) |
| Puntuaciones de los 12 recursos | calculadas antes de la interacción de u1 | iguales a las anteriores (`puntuaciones_sin_cambios: true`) |

### 5.4 Usuarios sin términos reconocidos (T4)

| Usuario | Intereses | Perfil | Puntuaciones | Recomendaciones | Mensaje mostrado |
|---|---|---|---|---|---|
| u3 | `""` | `{}` | las 12 en 0 | `[]` | No hay coincidencias positivas. Declare intereses presentes en el catálogo. |
| u4 | `zzxyz123` | `{}` | las 12 en 0 | `[]` | No hay coincidencias positivas. Declare intereses presentes en el catálogo. |

u3 no tiene texto y la palabra de u4 no existe en el vocabulario de 17 términos, así que `transform` entrega un vector de ceros en los dos casos. La aplicación no falla y no recomienda recursos con puntuación 0; el mensaje le pide al usuario declarar intereses conocidos, y con la opción `c` puede explorar el catálogo.

## 6. Tabla de pruebas T1 a T4

| Caso | Entrada o interacción | Resultado esperado | Resultado observado | Estado | Interpretación |
|---|---|---|---|---|---|
| T1 | Recomendaciones iniciales para u1 y u2 | Rankings coherentes con intereses distintos, hasta tres resultados positivos, orden descendente y desempate por id | u1: R02 (1.0000), R12 (0.4965), R03 (0.4326). u2: R07 (1.0000), R08 (0.5677), R09 (0.3087). Las cuatro condiciones del reporte en `true` | Cumple | Cada perfil apunta a una zona distinta del catálogo y no hay recursos en común. Los empates (R10/R11) quedan por id. |
| T2 | u1 marca Me interesa en R04 y se vuelve a recomendar en la misma ejecución | Cambia el vector de u1 y la puntuación de al menos un recurso no valorado, con los mismos 12 candidatos | El perfil incorpora web y api. R04 pasa de 0.2510 a 0.8752 (primer lugar), R05 de 0 a 0.4378 y R09 de 0 a 0.4958. Hay 12 candidatos antes y después, y el evento queda en el historial | Cumple | El cambio en R05 y R09 viene solo de la actualización del perfil, porque sus vectores no cambiaron. |
| T3 | Consultar u2 después de la interacción de u1 | Vector, historial y puntuaciones de u2 iguales a los anteriores | Perfil, historial (`[]`), puntuaciones y recomendaciones idénticos | Cumple | Cada usuario tiene su propio estado. La interacción de u1 no se mezcla con u2. |
| T4 | Recomendar para u3 (vacío) y u4 (`zzxyz123`) | Lista vacía y mensaje informativo, sin errores y sin recursos de puntuación cero | Vector nulo, 12 puntuaciones en 0, lista `[]` y el mensaje "No hay coincidencias positivas..." para ambos | Cumple | Sin términos reconocidos no hay base para recomendar, y la app lo informa en vez de inventar un ranking. |

Además de mirar el "Cumple" que imprime la aplicación, revisamos los números del JSON y del CSV, que son los que aparecen en las tablas de la sección 5.

## 7. Problemas detectados y observaciones

Ninguna prueba falló. Igual anotamos lo que nos encontramos en el camino:

1. **Versión de Python y `requirements.txt`.** El README del material dice Python 3.10 o posterior, pero después de `pip freeze` quedaron fijadas versiones (numpy 2.5.4 y scipy 1.18.1) que exigen Python 3.12 o más. Lo dejamos indicado en la sección 1 junto con la alternativa para versiones anteriores.
2. **Puntuación 1.0000000000000002.** En el JSON y el CSV, R02 aparece con 1.0000000000000002 para u1. Es error de redondeo de punto flotante: los vectores son iguales y en teoría el coseno sería 1. No afecta el orden y en pantalla se ve como 1.0000. No lo recortamos para no alterar los valores calculados.
3. **Empates exactos.** R10 y R11 (para u1) y R05 y R06 (después de valorar R04) tienen exactamente la misma puntuación, porque sus etiquetas tienen la misma estructura: dos términos compartidos con el perfil y un tercero que aparece solo en ese recurso. El desempate por id funciona en ambos casos (sección 5.1).
4. **Acentos al redirigir la salida.** Al redirigir la salida de Python en Git Bash, los acentos salían mal (`T�rminos compartidos`), porque en una redirección Python usa la codificación de Windows en vez de UTF-8. Para guardar los archivos de `evidencias/` ejecutamos con `python -X utf8`.
5. **El recurso valorado sigue apareciendo.** Después de valorar R04, R04 queda primero en las recomendaciones. Es parte del diseño del laboratorio (se conservan los 12 candidatos para poder comparar), pero en una plataforma real convendría ocultar lo que el usuario ya marcó (ver pregunta 6).

## 8. Respuestas a las preguntas

**Pregunta 1. ¿Qué información describe el contenido de los recursos y qué información constituye el perfil del usuario? Identifique ambas en los archivos del proyecto.**

El contenido de los recursos está en `datos/recursos.csv`, y de sus cuatro columnas solo `etiquetas` describe el recurso para el cálculo. En `motor.py`, `construir_indice` aplica `fit_transform` sobre `recursos["etiquetas"]` y genera la matriz TF-IDF de 12 x 17, donde cada fila es un recurso. `id` solo lo identifica, y `titulo` y `descripcion` se usan para mostrarlo.

El perfil del usuario parte de `datos/perfiles.json`, del campo `intereses` (`nombre` es solo descriptivo). Ese texto se transforma con `crear_perfil` en un vector de 17 pesos en el mismo vocabulario del catálogo. En la ejecución, el perfil lo forman los intereses iniciales del JSON, el vector actual (`estado[usuario_id]` en `app.py`) y el historial de interacciones (`historial[usuario_id]`). Por ejemplo, u1 parte de `python datos pandas`, que queda como `{pandas: 0.7532, datos: 0.4651, python: 0.4651}`.

**Pregunta 2. ¿Por qué se utiliza fit_transform sobre el catálogo y transform sobre los intereses del usuario? ¿Qué problema causaría ajustar un vectorizador diferente para cada perfil?**

`fit_transform` se aplica una sola vez sobre el catálogo porque ahí se define el espacio de comparación: el vocabulario (los 17 términos y el orden de las columnas) y el IDF de cada término, que depende de en cuántos recursos aparece. Por ejemplo, pandas está en un solo recurso (IDF 2.8718) y python en cinco (IDF 1.7732). Los intereses se pasan por `transform` para ubicarlos en ese mismo espacio sin cambiarlo. Así, cada posición del vector del usuario corresponde al mismo término que en la matriz, y los pesos usan la rareza medida en el catálogo.

Si se ajustara un vectorizador para cada perfil, cada usuario tendría su propio vocabulario. Lo probamos con u1: su vectorizador queda con 3 columnas (datos, pandas, python), todas con IDF 1.0, y `cosine_similarity` contra la matriz del catálogo falla con `Incompatible dimension for X and Y matrices: X.shape[1] == 3 while Y.shape[1] == 17`. Peor todavía es cuando el largo coincide: los vectores de u1 y u2 ajustados por separado tienen 3 columnas cada uno, pero cada columna significa otra palabra, y su coseno da 1.0 aunque no comparten ningún interés. Con u3 ni siquiera se puede ajustar, porque el texto vacío produce `empty vocabulary`. Además, la actualización del perfil mezcla el vector del usuario con el de un recurso, y eso solo tiene sentido si los dos están en el mismo espacio.

**Pregunta 3. ¿Por qué el mismo catálogo puede producir recomendaciones distintas para u1 y u2? ¿Una similitud de 0,80 significa que existe un 80 % de probabilidad de que el recurso guste? Justifique.**

La matriz del catálogo es la misma para todos; lo que cambia es el vector con el que se compara. El coseno mide qué tan alineadas están las direcciones de dos vectores, así que depende de en qué términos tiene peso cada perfil. u1 tiene peso solo en python, datos y pandas, y u2 solo en angular, componentes e interfaces. Como no comparten ningún término, sus rankings no se cruzan: u1 recibe R02, R12 y R03, y u2 recibe R07, R08 y R09. Para u1, los tres recursos de Angular tienen puntuación 0.

Una similitud de 0,80 no significa un 80 % de probabilidad de que el recurso guste. Es el coseno del ángulo entre dos vectores de etiquetas e indica que comparten términos con pesos altos, nada más. No se obtuvo a partir de lo que usuarios reales eligieron ni está calibrado contra eso. Tampoco se comporta como una probabilidad: las puntuaciones de u1 sobre los 12 recursos suman 2.78, y el mismo par de textos puede cambiar de puntuación si se agregan recursos al catálogo, porque cambian los IDF. Sirve para ordenar candidatos. Para hablar de probabilidad haría falta un modelo entrenado y calibrado con interacciones reales, como clics o valoraciones.

**Pregunta 4. ¿En qué se diferencia modificar manualmente los intereses iniciales de la adaptación implementada? Identifique el evento que provoca el cambio, el estado modificado y su efecto observable.**

Modificar los intereses a mano es un cambio externo: alguien edita `perfiles.json` y reinicia la aplicación. El sistema no observa nada, solo carga otro punto de partida; no queda historial y el texto nuevo reemplaza por completo al anterior.

En la adaptación implementada el cambio lo hace el propio sistema a partir de una acción del usuario:

- **Evento:** u1 marca Me interesa en R04 (opción `m` del modo interactivo, o `registrar_interes(estado, "u1", "R04", ...)` dentro de `--demo`).
- **Estado modificado:** solo el vector actual de u1 (`estado["u1"]`), que pasa a ser `normalize(0.4 * perfil + 0.6 * R04)`, y su historial, que registra `{"numero": 1, "accion": "Me interesa", "recurso": "R04"}`. Los intereses del JSON y el estado de u2 no cambian.
- **Efecto observable en la misma ejecución:** el perfil incorpora web y api (0.4463 cada uno), python sube de 0.4651 a 0.6371 y pandas baja de 0.7532 a 0.3765. Al recalcular, R04 sube de 0.2510 a 0.8752 y pasa al primer lugar, y R09, que nunca fue valorado, entra al top 3 con 0.4958.

Además, la adaptación es gradual: los intereses anteriores se mantienen con un 40 %, por eso R02 sigue segundo. Y como el estado vive en memoria, al reiniciar se vuelve al perfil del JSON.

**Pregunta 5. Relacione su implementación con las etapas del ciclo MAPE-K: Monitorizar, Analizar, Planificar, Ejecutar y Conocimiento.**

| Etapa | En nuestro programa |
|---|---|
| Monitorizar | Captura de la interacción: la opción `m` de `interactivo()` lee el id del recurso y `registrar_interes()` recibe el par usuario y recurso. En `--demo` el evento es u1 con R04. |
| Analizar | `motor.obtener_indice()` valida que el recurso exista (si no existe, muestra un mensaje y el estado no cambia) y ubica su fila. `matriz[indice]` entrega los términos que caracterizan lo que le interesó al usuario. |
| Planificar | `motor.actualizar_perfil()` decide el perfil nuevo con la regla `0.4 * perfil + 0.6 * recurso` y normalización L2. `alpha = 0.6` es el parámetro de esa regla. |
| Ejecutar | `registrar_interes()` reemplaza `estado[usuario_id]` por el vector nuevo y agrega el evento al historial. Después, `motor.recomendar()` recalcula y muestra el ranking. |
| Conocimiento | Lo que comparten las etapas: `vectorizador` (vocabulario e IDF), la `matriz` TF-IDF, el DataFrame `recursos`, `estado` con los vectores actuales, `historial` y los perfiles iniciales de `perfiles.json`. |

**Pregunta 6. Indique una limitación del mecanismo implementado y proponga una mejora concreta. Explique qué dato adicional o qué cambio del algoritmo exigiría esa mejora.**

**Limitación:** el sistema solo aprende de retroalimentación positiva y le da un peso fijo de 0.6 a cada interacción. Un solo Me interesa mueve mucho el perfil (en nuestra prueba, pandas quedó con la mitad de su peso después de una interacción), y si fue un clic por error o el usuario se arrepiente, no hay forma de corregirlo: no existe una acción para decir que algo no le interesa. Con varias valoraciones seguidas de otros temas, los intereses iniciales prácticamente desaparecen: sin contar las normalizaciones, después de tres valoraciones el perfil original queda multiplicado por 0.4³ = 0.064.

**Mejora propuesta:** agregar una acción "No me interesa" y cambiar la actualización a una regla tipo Rocchio, donde los recursos valorados positivamente suman y los rechazados restan:

```
mezcla = a * perfil + b * recurso_positivo        # Me interesa
mezcla = a * perfil - c * recurso_negativo        # No me interesa
mezcla = np.clip(mezcla, 0, None)                 # sin pesos negativos
perfil_nuevo = normalize([mezcla])[0]
```

Para hacerla se necesita:

- **Dato adicional:** registrar en el historial el tipo de valoración (positiva o negativa). El campo `accion` ya existe, solo habría que admitir un segundo valor y agregar la opción en la consola.
- **Cambio del algoritmo:** `actualizar_perfil` tendría que recibir el tipo de evento para sumar o restar, y recortar los valores negativos antes de normalizar para que el coseno siga entre 0 y 1. También se podría hacer que el peso dependa del número de interacciones del usuario (por ejemplo `alpha = 1 / (n + 1)`, que equivale a promediar), para que un solo clic no domine el perfil. Ese número ya se puede sacar de `len(historial[usuario])`.
- **Para elegir los pesos con fundamento**, y no solo como valores didácticos, harían falta datos de interacciones reales para comparar configuraciones con alguna métrica, por ejemplo cuántas de las tres recomendaciones terminan siendo valoradas.

Otra mejora más simple, relacionada con el punto 5 de la sección 7, sería no mostrar en las recomendaciones los recursos que ya están en el historial del usuario, sin sacarlos del cálculo de puntuaciones.

## 9. Reproducción desde una copia nueva

Para comprobar que el repositorio se puede ejecutar solo con los archivos entregados, lo clonamos en otra carpeta y seguimos las instrucciones de la sección 1 desde cero: creamos `.venv`, instalamos con `requirements.txt` y ejecutamos `--comprobar` y `--demo`. Las cuatro pruebas dieron Cumple, y al regenerar `reporte_demo.json` y `puntuaciones_antes_despues.csv` quedaron idénticos a los del repositorio (`git status` no mostró cambios). La única condición adicional es usar Python 3.12 o superior por las versiones fijadas en `requirements.txt`.

## Referencias

- Google for Developers. Content-based filtering. https://developers.google.com/machine-learning/recommendation/content-based/basics
- scikit-learn. TfidfVectorizer. https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- scikit-learn. cosine_similarity. https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html
- scikit-learn. normalize. https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.normalize.html
