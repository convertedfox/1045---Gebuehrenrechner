# Korrigierter Streamlit Code
import json
from typing import Any, Dict, List, TypedDict

import pandas as pd
import streamlit as st

from kosten import nackte_semesterkosten

## Gebührensatzung ausblenden für externe Nutzung
## Wording anpassen
## ERLEDIGT - Langzeitgebühren in Spalte 2 einrechnen
## ERLEDIGT - Alphabetische Sortierung der Studiengänge
## für intern: Kommentarspalte mit Infos einbauen, zb. bei Nacherhebung bei kürzerem Studium


# -----------------------------
# Typen
# -----------------------------
class StudiengangEintrag(TypedDict, total=False):
    Studiengang: str
    Fachbereich: str

    # Gebühren-/Kostenfelder (je nach JSON ggf. optional)
    Studiengebühren: float
    Anmeldegebühr: float

    DB1: float
    DB2: float
    DB3: float


DataType = Dict[str, List[StudiengangEintrag]]  # gebührensatzung -> liste von einträgen


# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data() -> DataType:
    """
    lädt die JSON-Datei
    """
    with open("studiengänge.json", "r", encoding="utf-8") as file:
        data: DataType = json.load(file)
    return data


@st.cache_data
def load_studiengänge(data: DataType, gebührensatzung: str) -> List[str]:
    """
    Lädt die Studiengänge aus der JSON-Datei und gibt sie als Liste zurück.
    Vorher muss load_data() aufgerufen werden, um die Daten zu laden, damit diese Funktion darauf zugreifen kann.
    """
    return sorted(
        eintrag["Studiengang"]
        for eintrag in data[gebührensatzung]
        if "Studiengang" in eintrag
    )


@st.cache_data
def load_gebührensatzung(data: DataType) -> List[str]:
    """
    Lädt die Gebührensatzung aus der JSON-Datei und gibt sie als Liste zurück.
    Vorher muss load_data() aufgerufen werden, um die Daten zu laden, damit diese Funktion darauf zugreifen kann.
    """
    return list(data.keys())


# -----------------------------
# App
# -----------------------------
data: DataType = load_data()
flag_rabatt: bool = False  # Flag, ob Rabatt durch externe ECTS gewährt wurde

st.title("Gebührenrechner 💰")
with st.sidebar:
    modus = st.selectbox(
        "Modus",
        ("extern", "intern"),
        index=0,
    )
    gebührensatzung: str = st.selectbox(
        "Welche Gebührensatzung soll verwendet werden?",
        load_gebührensatzung(data),
        index=2,
        disabled=True,
    )

# Stammdaten

# In welchem Studiengang wird absolviert?
st.write("## In welchem Studiengang wird absolviert? 👨🏻‍🎓")
abs_studiengang: str = st.selectbox(
    "Worin will man absolvieren?",
    load_studiengänge(data, gebührensatzung),
    index=0,
)

# Studiengang-Daten gleich abspeichern
studiengang_data: StudiengangEintrag | None = next(
    (
        eintrag
        for eintrag in data[gebührensatzung]
        if eintrag.get("Studiengang") == abs_studiengang
    ),
    None,
)

if studiengang_data is None:
    st.error("Für den ausgewählten Studiengang wurden keine Stammdaten gefunden.")
    st.stop()

# Initialwert
geschätzte_gesamtgebühr: float = float(studiengang_data.get("Studiengebühren", 0.0)) * 4

st.write("Diese Daten liegen vor - nur zur Demo:")
st.write(studiengang_data)

fachbereich: str | None = studiengang_data.get("Fachbereich")

# Wieviele Semester werden am CAS studiert?
anzahl_semester_cas: int = st.number_input(
    f"Anzahl durchlaufener Semester am CAS im Studiengang {abs_studiengang}",
    min_value=4,
    max_value=10,
    value=4,
)

st.write("---")

# Hat man vorher etwas anderes gemacht?
st.write("## Anrechnung externer Leistungen 🏫")
if fachbereich in {"Sozialwesen", "Gesundheit"}:
    st.write(
        "Bei Studiengängen im Fachbereich Sozialwesen/Gesundheit können keine Gebühren von externen Leistungen erstattet werden."
    )
else:
    st.write("Wurden ECTS ausserhalb des DHBW CAS erworben?")
    v1: str = st.radio(
        "Wurde Semester an einer anderen Hochschule studiert oder absolviert, die angerechnet werden können?",
        ("Ja", "Nein"),
        index=1,
    )
    if v1 == "Ja":
        ects_extern: int = st.number_input(
            "Wieviel ECTS wurden extern erworben, die angerechnet werden sollen?",
            min_value=15,
            max_value=90,
            step=1,
        )

        db3: float = float(studiengang_data.get("DB3", 0.0))
        db1: float = float(studiengang_data.get("DB1", 0.0))
        db2: float = float(studiengang_data.get("DB2", 0.0))
        studiengebuehren: float = float(studiengang_data.get("Studiengebühren", 0.0))

        geschätzte_gesamtgebühr = db3 * 4 + (((db1 + db2) * 4) / 90.0) * (90 - ects_extern)
        rabatt: float = studiengebuehren * 4 - geschätzte_gesamtgebühr

        if ects_extern > 0:
            st.write(f"Für die externen ECTS wird die Gebühr um {rabatt:,.2f} € gesenkt.")
            flag_rabatt = True
        else:
            st.write("Es werden keine Gebühren reduziert.")
            rabatt = 0.0

st.write("## Anrechnung von Zeit am CAS 🕕")
v2: str = st.radio(
    "Wurde vorher schon etwas am CAS erbracht, was angerechnet werden kann (wie Semester in anderen Studiengängen oder Zertifikate?)",
    ("Ja", "Nein"),
    index=1,
)

if v2 == "Ja":
    st.write("#### Anrechnung von Gebühren, die bisher am CAS bezahlt wurden")
    st.write(
        "Wenn Sie Module oder Zertifikate am CAS absolviert haben, die angerechnet werden können in Ihrem aktuellen Studiengang, geben Sie bitte die bisher bezahlten Gebühren an."
    )
    vorher_bezahlte_gebühren: float = st.number_input(
        "Gebühren für anrechenbare Leistungen",
        value=0.0,
        min_value=0.0,
        step=1.0,
    )

    if vorher_bezahlte_gebühren > 0:
        st.write(
            f"Die bisher bezahlten Gebühren von {vorher_bezahlte_gebühren:,.2f} € werden angerechnet."
        )
        geschätzte_gesamtgebühr -= vorher_bezahlte_gebühren
        flag_rabatt = True

# Welche Kosten sind damit verbunden?
st.write("## Kosten 💲")
st.write(
    'Aktuell werden nur die reinen "Studien-Gebühren" berechnet, keine weiteren Kosten (wie Modulgebühren, etc.)'
)

gesamtzeit: int = anzahl_semester_cas  # braucht es evtl. nicht
st.markdown(f"##### Gesamtzeit: {anzahl_semester_cas} Semester")

# Anmeldegebühr
anmeldegebühr: float = float(studiengang_data.get("Anmeldegebühr", 0.0))

GESAMTKOSTEN: float = 0.0 + anmeldegebühr + anzahl_semester_cas * 60.0
# Warum die 60? Weil studentische Beiträge 60 euro pro semester sind

# Semestertabelle erzeugen
semester_rows: List[Dict[str, Any]] = []
semester: int = 0
langzeitkosten_gesamt: float = 0.0

for _ in range(anzahl_semester_cas):
    semester += 1
    hinweis: str = ""

    basiskosten_semester, langzeitkosten_semester = nackte_semesterkosten(
        semester,
        studiengang_data,
    )
    basiskosten_semester = float(basiskosten_semester)
    langzeitkosten_semester = float(langzeitkosten_semester)

    if flag_rabatt:
        if geschätzte_gesamtgebühr > 0:
            if geschätzte_gesamtgebühr > basiskosten_semester:
                geschätzte_gesamtgebühr -= basiskosten_semester
            else:
                hinweis = "durch Anrechnungen (teilweise) gedeckt"
                basiskosten_semester = float(geschätzte_gesamtgebühr)
                geschätzte_gesamtgebühr = 0.0
        else:
            hinweis = "durch Anrechnungen vollständig gedeckt"
            basiskosten_semester = 0.0

    semester_rows.append(
        {
            "Semester": semester,
            "Semestergebühren (€)": basiskosten_semester,
            "Langzeitkosten (€)": langzeitkosten_semester,
            # "Hinweis": hinweis,  # optional: falls du die Spalte anzeigen willst
        }
    )

    langzeitkosten_gesamt += langzeitkosten_semester
    GESAMTKOSTEN += basiskosten_semester + langzeitkosten_semester

semester_df: pd.DataFrame = pd.DataFrame(semester_rows)

st.dataframe(
    semester_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Semestergebühren (€)": st.column_config.NumberColumn(format="%.2f €"),
        "Langzeitkosten (€)": st.column_config.NumberColumn(format="%.2f €"),
        # "Hinweis": st.column_config.TextColumn(),
    },
)

container_gesamtkosten = st.container(border=True)
container_gesamtkosten.write(f"➕ Einmalige Anmeldegebühr: {anmeldegebühr:,.2f} €")
container_gesamtkosten.write(
    f"➕ Verfasste Studierenschaft- und Studierendenwerksbeiträge (64 € pro Semester): {anzahl_semester_cas * 64:,.2f} €"
)
container_gesamtkosten.markdown("---")
container_gesamtkosten.markdown(f"##### 🟰 Gesamtkosten: {GESAMTKOSTEN:,.2f} €")

st.write(
    "DISCLAIMER: Dies ist ein Prototyp und die Berechnungen sind ohne Gewähr. Für verbindliche Auskünfte wenden Sie sich bitte an das Studiengangsmanagement."
)