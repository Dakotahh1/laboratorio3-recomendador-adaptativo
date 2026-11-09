"""Motor de recomendación que el estudiante debe completar.

Se proporcionan carga, validaciones y funciones auxiliares. Complete únicamente
los cuatro bloques señalados. Las puntuaciones de similitud no son probabilidades.
Este ejercicio no entrena un modelo supervisado: representa textos mediante
TF-IDF y actualiza un perfil con una regla explícita.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


def cargar_catalogo(ruta: Path) -> pd.DataFrame:
    """Carga y valida el CSV proporcionado, sin modificar su orden."""
    recursos = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    columnas = ["id", "titulo", "descripcion", "etiquetas"]
    faltantes = set(columnas) - set(recursos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(faltantes))}.")
    if recursos.empty:
        raise ValueError("El catálogo no contiene recursos.")
    for columna in columnas:
        recursos[columna] = recursos[columna].str.strip()
        if (recursos[columna] == "").any():
            raise ValueError(f"La columna {columna} contiene valores vacíos.")
    if recursos["id"].duplicated().any():
        raise ValueError("Los identificadores de recursos deben ser únicos.")
    return recursos.reset_index(drop=True)


def cargar_perfiles(ruta: Path) -> dict:
    """Los intereses vacíos son válidos y se usan en la prueba T4."""
    with ruta.open(encoding="utf-8") as archivo:
        perfiles = json.load(archivo)
    if not isinstance(perfiles, dict) or not perfiles:
        raise ValueError("Se requiere un objeto JSON con perfiles de usuario.")
    for usuario_id, datos in perfiles.items():
        if not isinstance(usuario_id, str) or not usuario_id.strip():
            raise ValueError("Hay un identificador de usuario inválido.")
        if not isinstance(datos, dict):
            raise ValueError(f"El perfil {usuario_id} debe ser un objeto.")
        for campo in ("nombre", "intereses"):
            if not isinstance(datos.get(campo), str):
                raise ValueError(f"El campo {campo} de {usuario_id} debe ser texto.")
    return perfiles


def construir_indice(recursos: pd.DataFrame) -> tuple:
    """El vocabulario se aprende una vez y únicamente a partir de etiquetas."""
    vectorizador = TfidfVectorizer()
    matriz = vectorizador.fit_transform(recursos["etiquetas"]).toarray()
    return vectorizador, matriz


def crear_perfil(intereses: str, vectorizador: TfidfVectorizer) -> np.ndarray:
    """Devuelve un vector de una dimensión con el vocabulario del catálogo."""
    # Se usa transform y no fit_transform: así los intereses quedan en el mismo
    # espacio que el catálogo (mismos 17 términos, mismo orden de columnas y mismos
    # pesos IDF). transform espera una colección de documentos, por eso [intereses].
    # Las palabras fuera del vocabulario se ignoran, de modo que u3 (vacío) y
    # u4 ("zzxyz123") quedan como un vector de ceros.
    matriz_perfil = vectorizador.transform([intereses])
    # La salida es una matriz dispersa de 1 x 17; se pasa a array y se toma la
    # única fila para tener un vector 1D, igual que cada fila de la matriz.
    return matriz_perfil.toarray()[0]


def calcular_puntuaciones(perfil: np.ndarray, matriz: np.ndarray) -> np.ndarray:
    """Devuelve una puntuación por fila del catálogo, en el mismo orden."""
    # cosine_similarity compara filas de matrices 2D. [perfil] convierte el vector
    # en una matriz de una fila; el resultado tiene forma (1, n_recursos) y la
    # fila 0 queda alineada con las filas de la matriz y del DataFrame.
    # Si el perfil es nulo, sklearn no divide por cero y devuelve solo ceros.
    return cosine_similarity([perfil], matriz)[0]


def recomendar(
    perfil: np.ndarray,
    recursos: pd.DataFrame,
    matriz: np.ndarray,
    vectorizador: TfidfVectorizer,
    top_k: int = 3,
) -> list[dict]:
    """Devuelve hasta top_k resultados positivos usando construir_resultado."""
    puntuaciones = calcular_puntuaciones(perfil, matriz)
    ids = recursos["id"].tolist()
    # Clave de orden: (-puntuacion, id). El signo negativo deja las puntuaciones de
    # mayor a menor y, si hay empate, gana el id menor (R05 antes que R06).
    # Se ordena con los valores sin redondear; el redondeo es solo para mostrar.
    orden = sorted(range(len(ids)), key=lambda i: (-puntuaciones[i], ids[i]))
    resultados = []
    for indice in orden:
        # Como la lista ya está ordenada, al llegar al primer valor <= 0 no quedan
        # positivos. Así un perfil nulo devuelve [] y no se rellena con ceros.
        if len(resultados) == top_k or puntuaciones[indice] <= 0:
            break
        resultados.append(construir_resultado(
            indice, puntuaciones[indice], perfil, recursos, matriz, vectorizador
        ))
    return resultados


def actualizar_perfil(perfil: np.ndarray, vector_recurso: np.ndarray) -> np.ndarray:
    """Actualiza el perfil cuando el usuario pulsa Me interesa sobre un recurso."""
    # alpha es el peso de la interacción nueva. 0.6 es el valor didáctico pedido
    # en la guía para que el cambio se note; no viene de un experimento.
    alpha = 0.6
    perfil = np.asarray(perfil, dtype=float)
    vector_recurso = np.asarray(vector_recurso, dtype=float)
    # El perfil anterior conserva el 40 %, por eso no se olvidan los intereses previos.
    mezcla = (1 - alpha) * perfil + alpha * vector_recurso
    # normalize trabaja por filas: [mezcla] es una matriz de una fila. Con norma L2
    # el perfil vuelve a tener largo 1, igual que las filas TF-IDF, y en la próxima
    # actualización el 0.4 y el 0.6 se aplican sobre vectores de la misma magnitud.
    # El coseno solo usa la dirección, así que esto no altera el ranking actual.
    return normalize([mezcla], norm="l2")[0]


def obtener_indice(recursos: pd.DataFrame, recurso_id: str) -> int:
    """Valida el identificador antes de modificar un perfil."""
    coincidencias = recursos.index[recursos["id"] == recurso_id].tolist()
    if not coincidencias:
        raise ValueError(f"No existe el recurso {recurso_id}.")
    return int(coincidencias[0])


def explicar_coincidencias(
    perfil: np.ndarray,
    vector_recurso: np.ndarray,
    vectorizador: TfidfVectorizer,
) -> str:
    """La explicación se limita a términos compartidos con peso positivo."""
    vocabulario = vectorizador.get_feature_names_out()
    mascara = (np.asarray(perfil) > 0) & (np.asarray(vector_recurso) > 0)
    terminos = vocabulario[mascara].tolist()
    if not terminos:
        return "No hay términos compartidos con peso positivo."
    return "Términos compartidos: " + ", ".join(terminos) + "."


def construir_resultado(
    indice: int,
    puntuacion: float,
    perfil: np.ndarray,
    recursos: pd.DataFrame,
    matriz: np.ndarray,
    vectorizador: TfidfVectorizer,
) -> dict:
    """Función auxiliar para usar dentro de recomendar."""
    recurso = recursos.iloc[indice]
    return {
        "id": str(recurso["id"]),
        "titulo": str(recurso["titulo"]),
        "puntuacion": float(puntuacion),
        "explicacion": explicar_coincidencias(perfil, matriz[indice], vectorizador),
    }


def describir_perfil(perfil: np.ndarray, vectorizador: TfidfVectorizer) -> dict:
    """Representación legible del estado; no cambia el vector utilizado."""
    vocabulario = vectorizador.get_feature_names_out()
    pares = [(str(termino), float(peso)) for termino, peso in zip(vocabulario, perfil)
             if peso > 0]
    pares.sort(key=lambda par: (-par[1], par[0]))
    return {termino: round(peso, 6) for termino, peso in pares}
