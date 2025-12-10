import json
from pathlib import Path

import pandas as pd
import streamlit as st
import re

# ========== CONFIGURACIÓN BÁSICA ==========

# Excel principal (seguidores)
EXCEL_FILE = "Predicciones Game Awards 2025 (Respuestas).xlsx"

# Excel extra solo de amigos
FRIENDS_EXCEL_FILE = "Predicciones Amigos (Respuestas).xlsx"
FRIENDS_NAME_COLUMN = "Tu Nombre"

# Usaremos el nick de Discord como identificador interno
COLUMN_NOMBRE = "Nick de Discord"

# Columnas que NO son categorías
NON_CATEGORY_COLUMNS = {
    "Marca temporal",
    "Nick de Discord",
    "Nick de Twitter",
}

WINNERS_FILE = "winners.json"

# ==================================================
# NOMBRES PERSONALIZADOS (AMIGOS)
# clave = nombre detectado tras limpieza
# valor = nombre que quieres mostrar
# ==================================================
CUSTOM_FRIEND_NAMES = {
    "jose": "Girard",
    "juan": "Tlone",
}

# Sistema de puntuación (según tu tabla de la captura)
# Si quieres ajustar algo, solo cambia los números aquí.
SCORING = {
    "JUEGO DEL AÑO": 6,                          # GOTY
    "MEJOR DIRECCIÓN DE JUEGO": 4,              # Dirección
    "MEJOR NARRATIVA": 4,                       # Narrativa
    "MEJOR DIRECCIÓN DE ARTE": 4,               # Arte
    "MEJOR PARTITURA Y MÚSICA": 3,              # Música
    "MEJOR DISEÑO DE AUDIO": 3,                 # Audio
    "MEJOR PERFORMANCE": 2,                     # Performance
    "JUEGOS DE IMPACTO": 1,                     # Impact
    "MEJOR ONGOING GAME": 1,                    # Ongoing
    "MEJOR JUEGO INDIE": 3,                     # Indie
    "MEJOR JUEGO MÓVIL": 3,                     # Mobile
    "MEJOR SOPORTE DE LA COMUNIDAD": 1,         # Comunidad
    "INNOVACIÓN EN ACCESIBILIDAD": 1,           # Accesibilidad
    "MEJOR VR / AR": 3,                         # VR
    "MEJOR JUEGO DE ACCIÓN": 3,                 # Acción
    "MEJOR ACCIÓN / AVENTURA": 3,               # Acción/Aventura
    "MEJOR RPG": 3,                             # RPG
    "MEJOR JUEGO DE PELEA": 3,                  # Pelea
    "MEJOR JUEGO FAMILIAR": 3,                  # Familiar
    "MEJOR SIMULADOR / ESTRATEGIA": 3,          # Simulador/Estrategia
    "MEJOR JUEGO DE DEPORTE / CARRERA": 3,      # Deporte
    "MEJOR MULTIJUGADOR": 3,                    # Multijugador
    "CREADOR DE CONTENIDO DEL AÑO": 1,          # Creador
    "MEJOR JUEGO INDIE DEBUT": 2,               # Debut Indie
    "MEJOR ADAPTACIÓN": 2,                      # Adaptación
    "JUEGO MÁS ANTICIPADO": 2,                  # Anticipado
    "MEJOR JUEGO DE EASPORTS": 3,               # Juego Esport
    "MEJOR ATLETA DE EASPORTS": 1,              # Atleta Esport
    "MEJOR EQUIPO DE EASPORTS": 1,              # Equipo Esport
}

# Lista fija de nominados por categoría (puedes ir completándola tú)
CATEGORY_OPTIONS = {
    "JUEGO DEL AÑO": [
        "Clair Obscur: Expedition 33",
        "Death Stranding 2: On the Beach",
        "Donkey Kong Bananza",
        "Hades II",
        "Hollow Knight: Silksong",
        "Kingdom Come: Deliverance II",
    ],
    "MEJOR DIRECCIÓN DE JUEGO": [
        "Clair Obscur: Expedition 33",
        "Death Stranding 2: On the Beach",
        "Ghost of Yōtei",
        "Hades II",
        "Split Fiction",
    ],
    "MEJOR NARRATIVA": [
        "Clair Obscur: Expedition 33",
        "Death Stranding 2: On the Beach",
        "Ghost of Yōtei",
        "Kingdom Come: Deliverance II",
        "Silent Hill: F",
    ],
    "MEJOR DIRECCIÓN DE ARTE": [
        "Clair Obscur: Expedition 33",
        "Death Stranding 2: On the Beach",
        "Ghost of Yōtei",
        "Hades II",
        "Hollow Knight: Silksong",
    ],
    "MEJOR PARTITURA Y MÚSICA": [
        "Christopher Larkin (Hollow Knight: Silksong)",
        "Darren Korb (Hades II)",
        "Lorien Testard (Clair Obscur: Expedition 33)",
        "Toma Otowa (Ghost of Yōtei)",
        "Woodkid and Ludvig Forssell (Death Stranding 2: On the Beach)",
    ],
    "MEJOR DISEÑO DE AUDIO": [
        "Battlefield 6",
        "Clair Obscur: Expedition 33",
        "Death Stranding 2: On the Beach",
        "Ghost of Yōtei",
        "Silent Hill: F",
    ],
    "MEJOR PERFORMANCE": [
        "Ben Starr (Clair Obscur: Expedition 33)",
        "Charlie Cox (Clair Obscur: Expedition 33)",
        "Erika Ishii (Ghost of Yōtei)",
        "Jennifer English (Clair Obscur: Expedition 33)",
        "Konatsu Kato (Silent Hill F)",
        "Troy Baker (Indiana Jones and The Great Circle)",
    ],
    "INNOVACIÓN EN ACCESIBILIDAD": [
        "Assassin's Creed Shadows",
        "Atomfall",
        "DOOM: The Dark Ages",
        "EA Sports FC 26",
        "South of Midnight",
    ],
    "JUEGOS DE IMPACTO": [
        "Consume Me",
        "Despelote",
        "Lost Records: Bloom & Rage",
        "South of Midnight",
        "Wanderstop",
    ],
    "MEJOR ONGOING GAME": [
        "Final Fantasy XIV",
        "Fortnite",
        "Helldivers 2",
        "Marvel Rivals",
        "No Man's Sky",
    ],
    "MEJOR SOPORTE DE LA COMUNIDAD": [
        "Baldur's Gate 3",
        "Final Fantasy XIV",
        "Fortnite",
        "Helldivers 2",
        "No Man's Sky",
    ],
    "MEJOR JUEGO INDIE": [
        "Absolum",
        "Ball x Pit",
        "Blue Prince",
        "Clair Obscur: Expedition 33",
        "Hades II",
        "Hollow Knight: Silksong",
    ],
    "MEJOR JUEGO INDIE DEBUT": [
        "Blue Prince",
        "Clair Obscur: Expedition 33",
        "Despelote",
        "Dispatch",
    ],
    "MEJOR JUEGO MÓVIL": [
        "Destiny: Rising",
        "Persona 5: The Phantom X",
        "Sonic Rumble",
        "Umamusume: Pretty Derby",
        "Wuthering Waves",
    ],
    "MEJOR VR / AR": [
        "Alien: Rogue Incursion",
        "Arken Age",
        "Ghost Town",
        "Marvel's Deadpool VR",
        "The Midnight Walk",
    ],
    "MEJOR JUEGO DE ACCIÓN": [
        "Battlefield 6",
        "DOOM: The Dark Ages",
        "Hades II",
        "Ninja Gaiden 4",
        "Shinobi: Art of Vengeance",
    ],
    "MEJOR ACCIÓN / AVENTURA": [
        "Death Stranding 2: On The Beach",
        "Ghost of Yotei",
        "Hollow Knight: Silksong",
        "Indiana Jones and The Great Circle",
        "Split Fiction",
    ],
    "MEJOR RPG": [
        "Avowed",
        "Clair Obscur: Expedition 33",
        "Kingdom Come: Deliverance II",
        "Monster Hunter Wilds",
        "The Outer Worlds 2",
    ],
    "MEJOR JUEGO DE PELEA": [
        "2XKO",
        "Capcom Fighting Collection 2",
        "Fatal Fury: City of the Wolves",
        "Mortal Kombat: Legacy Kollection",
        "Virtua Fighter 5 R.E.V.O. World Stage",
    ],
    "MEJOR JUEGO FAMILIAR": [
        "Donkey Kong Bananza",
        "LEGO Party!",
        "LEGO Voyagers",
        "Mario Kart World",
        "Sonic Racing: Crossworlds",
        "Split Fiction",
    ],
    "MEJOR SIMULADOR / ESTRATEGIA": [
        "Final Fantasy Tactics - The Ivalice Chronicles",
        "Jurassic World Evolution 3",
        "Sid Meier's Civilization VII",
        "Tempest Rising",
        "The Alters",
        "Two Point Museum",
    ],
    "MEJOR JUEGO DE DEPORTE / CARRERA": [
        "EA Sports FC 26",
        "F1 25",
        "Mario Kart World",
        "Rematch",
        "Sonic Racing: Crossworlds",
    ],
    "MEJOR MULTIJUGADOR": [
        "ARC Raiders",
        "Battlefield 6",
        "Elden Ring Nightreign",
        "Peak",
        "Split Fiction",
    ],
    "MEJOR ADAPTACIÓN": [
        "A Minecraft Movie",
        "Devil May Cry",
        "Splinter Cell: Deathwatch",
        "The Last of Us: Season 2",
        "Until Dawn",
    ],
    "JUEGO MÁS ANTICIPADO": [
        "007 First Light",
        "Grand Theft Auto VI",
        "Marvel's Wolverine",
        "Resident Evil Requiem",
        "The Witcher IV",
    ],
    "CREADOR DE CONTENIDO DEL AÑO": [
        "Caedrel",
        "Kai Cenat",
        "MoistCr1TiKaL",
        "Sakura Miko",
        "The Burnt Peanut",
    ],
    "MEJOR JUEGO DE EASPORTS": [
        "Counter-Strike 2",
        "Dota 2",
        "League of Legends",
        "Mobile Legends: Bang Bang",
        "Valorant",
    ],
    "MEJOR ATLETA DE EASPORTS": [
        "Brawk - Brock Somerhalder (Valorant)",
        "Chovy - Jeong Ji-Hoon (League of Legends)",
        "F0rsaken - Jason Susanto (Valorant)",
        "Kakeru - Kakeru Watanabe (Street Fighter)",
        "Menard - Saul Leonardo (Street Fighter)",
        "Zyw0O - Mathieu Herbaut (Counter-Strike 2)",
    ],
    "MEJOR EQUIPO DE EASPORTS": [
        "Gen.G (League of Legends)",
        "NRG (Valorant)",
        "Team Falcons (DOTA 2)",
        "Team Liquid PH (Mobile Legends: Bang Bang)",
        "Team Vitality (Counter-Strike 2)",
    ]
}


# ========== FUNCIONES AUXILIARES ==========

def normalize(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def load_predictions():
    df = pd.read_excel(EXCEL_FILE)
    if COLUMN_NOMBRE not in df.columns:
        raise ValueError(
            f"No se encontró la columna de nombre '{COLUMN_NOMBRE}' en el Excel.\n"
            f"Columnas disponibles: {list(df.columns)}"
        )
    return df

def load_friends_predictions():
    path = Path(FRIENDS_EXCEL_FILE)
    if not path.exists():
        return None

    df = pd.read_excel(path)

    if FRIENDS_NAME_COLUMN not in df.columns:
        raise ValueError(
            f"No se encontró la columna de nombre '{FRIENDS_NAME_COLUMN}' en el Excel de amigos.\n"
            f"Columnas disponibles: {list(df.columns)}"
        )

    # Renombramos "Tu Nombre" -> "Nick de Discord"
    df = df.rename(columns={FRIENDS_NAME_COLUMN: COLUMN_NOMBRE})

    # ==================================================
    # LIMPIEZA FUERTE DE NOMBRES (AMIGOS)
    # ==================================================
    def limpiar_nombre(nombre):
        if pd.isna(nombre):
            return ""

        nombre = str(nombre).strip()

        # 1️⃣ Quitar signos , . ; : ! ?
        nombre = re.sub(r"[,\.;:!?\(\)\[\]\{\}]", "", nombre)

        # 2️⃣ Tomar solo la primera palabra
        nombre = nombre.split()[0].strip()

        if nombre == "":
            return ""

        # 3️⃣ Reemplazo manual (prioridad absoluta)
        key = nombre.lower()
        if key in CUSTOM_FRIEND_NAMES:
            return CUSTOM_FRIEND_NAMES[key]

        # 4️⃣ Si no hay reemplazo, devolver el nombre limpio
        return nombre

    df[COLUMN_NOMBRE] = df[COLUMN_NOMBRE].apply(limpiar_nombre)

    return df

def infer_categories(df):
    return [c for c in df.columns if c not in NON_CATEGORY_COLUMNS]


def load_winners(categories):
    path = Path(WINNERS_FILE)
    if not path.exists():
        return {cat: "" for cat in categories}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    winners = {}
    for cat in categories:
        winners[cat] = data.get(cat, "")
    return winners


def save_winners(winners):
    Path(WINNERS_FILE).write_text(
        json.dumps(winners, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def compute_improbable_choices(df, categories):
    """
    Para cada categoría, calculamos qué juegos son "resultado improbable":

    - Solo se consideran juegos con >= 1 voto.
    - Se toma el/los juegos con MENOR número de votos.
    - Si hay 1 o 2 juegos con ese mínimo -> son "improbables".
    - Si hay 3 o más empatados en el mínimo -> no hay improbable.
    """
    improbable = {}

    for cat in categories:
        col = df[cat].dropna().astype(str).str.strip()
        if col.empty:
            improbable[cat] = set()
            continue

        counts = col.value_counts()
        # counts ya solo tiene juegos con >=1 voto

        if counts.empty:
            improbable[cat] = set()
            continue

        min_votes = counts.min()
        least = counts[counts == min_votes]

        if 1 <= len(least) <= 2:
            improbable[cat] = {normalize(name) for name in least.index}
        else:
            improbable[cat] = set()

    return improbable


def calculate_scores(df, categories, winners):
    improbable_per_cat = compute_improbable_choices(df, categories)

    results = []

    for _, row in df.iterrows():
        nombre = row[COLUMN_NOMBRE]

        puntos_base = 0
        aciertos = 0
        bonus_improbable = 0

        detalle_categorias = {}
        detalle_bonus = {}

        for cat in categories:
            ganador_real = winners.get(cat, "")
            if not ganador_real:
                # si no hay ganador definido en esta categoría, no cuenta
                detalle_categorias[cat] = 0
                detalle_bonus[cat] = 0
                continue

            prediccion_raw = row.get(cat, "")
            prediccion = normalize(prediccion_raw)
            ganador_normalizado = normalize(ganador_real)

            puntos_cat = 0
            bonus_cat = 0

            if prediccion and prediccion == ganador_normalizado:
                puntos_cat = SCORING.get(cat, 1)
                aciertos += 1

                # ¿Es un resultado improbable?
                if ganador_normalizado in improbable_per_cat.get(cat, set()):
                    bonus_cat = 1

            puntos_base += puntos_cat
            bonus_improbable += bonus_cat

            detalle_categorias[cat] = puntos_cat
            detalle_bonus[cat] = bonus_cat

        puntos_totales = puntos_base + bonus_improbable

        resultado_participante = {
            "Nombre": nombre,
            "Puntos base": puntos_base,
            "Bonos improbables": bonus_improbable,
            "Puntos totales": puntos_totales,
            "Aciertos": aciertos,
        }

        # Si quieres ver los detalles por categoría en el Excel exportado:
        # puntos por categoría
        for cat in categories:
            resultado_participante[f"Puntos - {cat}"] = detalle_categorias[cat]
            resultado_participante[f"Bonus - {cat}"] = detalle_bonus[cat]

        results.append(resultado_participante)

    resultados_df = pd.DataFrame(results)

    # Orden de desempate:
    # 1) Puntos totales
    # 2) Aciertos (categorías acertadas)
    # 3) Puntos base (sin bonus improbable)
    # 4) Nombre (alfabético, solo para que la tabla sea estable)
    resultados_df = resultados_df.sort_values(
        by=["Puntos totales", "Aciertos", "Puntos base", "Nombre"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)

    resultados_df.insert(0, "Posición", resultados_df.index + 1)
    return resultados_df


# ========== APP STREAMLIT ==========

def main():
    st.set_page_config(
        page_title="Predicciones Game Awards 2025",
        layout="wide",
    )

    st.title("📊 Predicciones Game Awards 2025")
    st.caption("Panel para administrar ganadores, puntos y ranking de tus seguidores.")

    # Cargar predicciones
    try:
        df = load_predictions()
    except Exception as e:
        st.error(f"Error al cargar '{EXCEL_FILE}': {e}")
        st.stop()

    # ==================================================
    # Elegir qué nombre usar (Discord / Twitter / Auto)
    # ==================================================
    DISCORD_COL = COLUMN_NOMBRE          # normalmente "Nick de Discord"
    TWITTER_COL = "Nick de Twitter"      # cambia esto si tu columna se llama distinto

    st.sidebar.markdown("### 👤 Nombre a mostrar")
    name_mode = st.sidebar.radio(
        "Elige qué nombre usar en el ranking:",
        [
            "Usar Nick de Discord",
            "Usar Nick de Twitter",
            "Automático (Discord, si dice 'no tengo' usa Twitter)",
        ],
        index=2,  # por defecto el modo automático
    )

    # Hacemos una copia para no tocar el df original fuera de esta ejecución
    df = df.copy()

    def limpiar(texto):
        if pd.isna(texto):
            return ""
        return str(texto).strip()

    if name_mode == "Usar Nick de Discord":
        # No hacemos nada; se queda la columna tal cual
        pass

    elif name_mode == "Usar Nick de Twitter":
        if TWITTER_COL in df.columns:
            df[DISCORD_COL] = df[TWITTER_COL].apply(limpiar)
        else:
            st.sidebar.warning(
                f"No se encontró la columna '{TWITTER_COL}' en el Excel. "
                "Se seguirá usando Nick de Discord."
            )

    elif name_mode == "Automático (Discord, si dice 'no tengo' usa Twitter)":
        if TWITTER_COL in df.columns:
            def elegir_nombre(row):
                disc = limpiar(row.get(DISCORD_COL, ""))
                tw = limpiar(row.get(TWITTER_COL, ""))

                # Si el nick de Discord está vacío o es tipo "no tengo", usamos Twitter
                if (
                    disc == ""
                    or disc.lower() in ["no tengo", "ninguno", "n/a", "no uso discord", "no tengo discord"]
                ):
                    return tw if tw != "" else disc
                return disc

            df[DISCORD_COL] = df.apply(elegir_nombre, axis=1)
        else:
            st.sidebar.warning(
                f"No se encontró la columna '{TWITTER_COL}' en el Excel. "
                "Se seguirá usando Nick de Discord."
            )

    categories = infer_categories(df)

    # Panel lateral: Ganadores
    st.sidebar.header("🏆 Ganadores por categoría")

    # Cargamos los ganadores actuales desde el archivo
    winners = load_winners(categories)

    # -------------------------------
    # 🔐 MODO ADMINISTRADOR
    # -------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Modo administrador")

    admin_password_input = st.sidebar.text_input(
        "Contraseña de administrador",
        type="password",
        help="Solo el admin puede editar los ganadores.",
    )

    # Leemos la contraseña real desde los secretos de Streamlit
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")

    admin_mode = False
    if ADMIN_PASSWORD:
        if admin_password_input == "":
            st.sidebar.caption("Introduce la contraseña para editar los ganadores.")
        elif admin_password_input == ADMIN_PASSWORD:
            admin_mode = True
            st.sidebar.success("Modo administrador activado.")
        else:
            st.sidebar.error("Contraseña incorrecta.")
    else:
        st.sidebar.warning(
            "ADMIN_PASSWORD no está configurado en los secretos de Streamlit."
        )

    # Copia editable de los ganadores actuales
    updated_winners = dict(winners)

    # Solo si estamos en modo admin mostramos los selectores para cambiar ganadores
    if admin_mode:
        for cat in categories:
            # opciones fijas definidas a mano (CATEGORY_OPTIONS)
            fijas = CATEGORY_OPTIONS.get(cat, [])

            # opciones que salieron de las votaciones (por si hay algo raro escrito)
            desde_votos = sorted(
                {str(v).strip() for v in df[cat].dropna().unique()}
            )

            # unimos: fijas + extras desde votos, sin duplicados y manteniendo orden
            todas = list(dict.fromkeys(fijas + desde_votos))
            opciones = ["(Sin definir)"] + todas

            valor_actual = winners.get(cat, "")
            if not valor_actual:
                index_default = 0
            else:
                try:
                    index_default = opciones.index(valor_actual)
                except ValueError:
                    index_default = 0

            seleccionado = st.sidebar.selectbox(
                label=f"{cat}",
                options=opciones,
                index=index_default,
            )

            if seleccionado == "(Sin definir)":
                updated_winners[cat] = ""
            else:
                updated_winners[cat] = seleccionado

        # Botón para guardar ganadores (solo visible en modo admin)
        if st.sidebar.button("💾 Guardar ganadores"):
            save_winners(updated_winners)
            st.sidebar.success("Ganadores guardados.")
            winners = updated_winners
        else:
            winners = updated_winners
    else:
        # Modo solo lectura para el público general
        st.sidebar.caption(
            "Solo lectura. Los ganadores solo pueden ser modificados por el administrador."
        )

    # =========================
    # 1) RANKING (ARRIBA)
    # =========================
    if any(winners[cat] for cat in categories):
        resultados_df = calculate_scores(df, categories, winners)

        st.subheader("🏅 Ranking de participantes")

        # Selector "quién soy" (Nick de Discord / Nombre) con búsqueda
        nombres_disponibles = resultados_df["Nombre"].dropna().unique()
        selected_name = st.selectbox(
            "Elige quién eres (Nick de Discord):",
            options=["(Nadie)"] + sorted(nombres_disponibles),
            index=0,
            help="Puedes escribir para buscar tu nombre.",
        )

        # Columnas que mostraremos en la tabla principal
        display_cols = [
            "Posición",
            "Nombre",
            "Puntos totales",
            "Puntos base",
            "Bonos improbables",
            "Aciertos",
        ]
        df_display = resultados_df[display_cols].copy()

        # Posiciones bonitas (1, 2, 3 con medallas)
        def format_pos(pos):
            if pos == 1:
                return "🥇 1"
            elif pos == 2:
                return "🥈 2"
            elif pos == 3:
                return "🥉 3"
            else:
                return str(pos)

        df_display["Posición"] = df_display["Posición"].apply(format_pos)

        # Usamos "Posición" como índice para que no salga la columna ID 0,1,2,...
        df_display = df_display.set_index("Posición")

        # Estilo: resaltar la fila del usuario seleccionado (fondo clarito y texto negro)
        def highlight_row(row):
            if selected_name != "(Nadie)" and row["Nombre"] == selected_name:
                return ['background-color: #fff3b0; color: black; font-weight: bold;'] * len(row)
            return [''] * len(row)

        styled = df_display.style.apply(highlight_row, axis=1)

        # Tabla completa, scrollable (altura aprox. para ~20 filas)
        st.dataframe(
            styled,
            use_container_width=True,
            height=600,  # ajusta si quieres más/menos alto
        )

        # Bloque especial: siempre mostrar tu fila fija abajo si estás fuera del top ~20
        if selected_name != "(Nadie)":
            # Buscamos la fila original para saber la posición numérica
            tu_registro = resultados_df[resultados_df["Nombre"] == selected_name]
            if not tu_registro.empty:
                pos_num = int(tu_registro["Posición"].iloc[0])
                # solo mostramos fijado si está por debajo del top 20
                if pos_num > 20:
                    st.markdown("### ⭐ Tu posición (fuera del top 20)")
                    # Usamos la vista ya formateada
                    tu_fila_display = df_display[df_display["Nombre"] == selected_name]
                    st.table(tu_fila_display)
            else:
                st.info("No se encontró ese nombre en el ranking.")

        # Botón para descargar CSV completo
        csv = resultados_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Descargar ranking completo (CSV)",
            data=csv,
            file_name="resultados_game_awards_2025.csv",
            mime="text/csv",
        )

        # =========================
        # 1b) RANKING SOLO DE AMIGOS
        # =========================
        st.markdown("---")
        st.subheader("👥 Ranking de amigos")

        try:
            df_amigos = load_friends_predictions()
        except Exception as e:
            st.info(f"No se pudo cargar el Excel de amigos: {e}")
            df_amigos = None

        if df_amigos is not None:
            # Verificamos que tenga las mismas categorías que el Excel principal
            missing_cols = [c for c in categories if c not in df_amigos.columns]
            if missing_cols:
                st.error(
                    "El Excel de amigos no tiene estas columnas esperadas: "
                    + ", ".join(missing_cols)
                )
            else:
                resultados_amigos = calculate_scores(df_amigos, categories, winners)

                # Mismas columnas que el ranking general
                display_cols_amigos = [
                    "Posición",
                    "Nombre",
                    "Puntos totales",
                    "Puntos base",
                    "Bonos improbables",
                    "Aciertos",
                ]
                df_amigos_display = resultados_amigos[display_cols_amigos].copy()

                # Posiciones bonitas (1, 2, 3 con medallas)
                def format_pos_amigos(pos):
                    if pos == 1:
                        return "🥇 1"
                    elif pos == 2:
                        return "🥈 2"
                    elif pos == 3:
                        return "🥉 3"
                    else:
                        return str(pos)

                df_amigos_display["Posición"] = df_amigos_display["Posición"].apply(
                    format_pos_amigos
                )

                # Usamos "Posición" como índice para que no salga la columna 0,1,2...
                df_amigos_display = df_amigos_display.set_index("Posición")

                # Resaltar al usuario seleccionado también en el ranking de amigos
                def highlight_row_amigos(row):
                    if selected_name != "(Nadie)" and row["Nombre"] == selected_name:
                        return [
                            "background-color: #fff3b0; color: black; font-weight: bold;"
                        ] * len(row)
                    return [""] * len(row)

                styled_amigos = df_amigos_display.style.apply(
                    highlight_row_amigos, axis=1
                )

                # Tabla de amigos, un poco más bajita
                st.dataframe(
                    styled_amigos,
                    use_container_width=True,
                    height=400,
                )

                # (Opcional) mostrar tu posición entre amigos si quieres
                if selected_name != "(Nadie)":
                    tu_registro_amigos = resultados_amigos[
                        resultados_amigos["Nombre"] == selected_name
                    ]
                    if not tu_registro_amigos.empty:
                        st.markdown("#### ⭐ Tu posición entre amigos")
                        tu_fila_amigos = df_amigos_display[
                            df_amigos_display["Nombre"] == selected_name
                        ]
                        st.table(tu_fila_amigos)
        else:
            st.caption("No se encontró el archivo de amigos o está vacío.")

    else:
        selected_name = "(Nadie)"
        st.info("Define al menos un ganador en el panel lateral para ver el ranking.")

    # =========================
    # 2) GANADORES (ABAJO)
    # =========================
    st.subheader("🏆 Ganadores actuales por categoría")
    winners_show = {
        cat: (winners[cat] if winners[cat] else "— Sin definir —") for cat in categories
    }
    st.table(
        pd.DataFrame.from_dict(
            winners_show, orient="index", columns=["Ganador"]
        ).rename_axis("Categoría")
    )



if __name__ == "__main__":
    main()
