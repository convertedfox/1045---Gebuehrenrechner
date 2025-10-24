# Korrigierter Streamlit Code
import streamlit as st
import json
import os
from ects_umrechner import ectsumrechner
from kosten import kosten_kalkulieren


# Load data
@st.cache_data
def load_data() -> dict:
    """
    lädt die JSON-Datei
    """
    with open("studiengänge.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


@st.cache_data
def load_studiengänge(data, gebührensatzung):
    """
    Lädt die Studiengänge aus einer JSON-Datei und gibt sie als Liste zurück.
    """
    return [eintrag["Studiengang"] for eintrag in data[gebührensatzung]]


@st.cache_data
def load_gebührensatzung(data):
    """
    Lädt die Gebührensatzung aus einer JSON-Datei und gibt sie als Liste zurück.
    """
    return list(data.keys())


# Daten laden
data = load_data()

# Title
st.title("Gebührenkostenrechner 💰")
st.write("Prototyp, ist in Entwicklung...")
st.write("## Gültige Gebührensatzung")
gebührensatzung = st.selectbox(
    "Welche Gebührensatzung soll verwendet werden?", load_gebührensatzung(data), index=0
)

# In welchem Studiengang wird absolviert?
st.write("## Erbrachte Leistungen")
st.write("### In welchem Studiengang wird absolviert? 👨🏻‍🎓")
abs_studiengang = st.selectbox(
    "Worin will man absolvieren?", load_studiengänge(data, gebührensatzung), index=0
)

st.write("Diese Daten liegen vor - nur zur Demo:")
st.write(
    next(
        (
            eintrag
            for eintrag in data[gebührensatzung]
            if eintrag["Studiengang"] == abs_studiengang
        ),
        None,
    )
)

# Wieviele Semester werden am CAS studiert?
anzahl_semester_cas = st.number_input(
    f"Anzahl durchlaufener Semester am CAS im Studiengang {abs_studiengang}",
    min_value=1,
    max_value=10,
    value=4,
)

# Hat man vorher etwas anderes gemacht?
st.write("### Anrechnung externer Leistungen 🏫")
st.write("Wurden ECTS ausserhalb des DHBW CAS erworben?")
v1 = st.radio(
    "Wurde Semester an einer anderen Hochschule studiert oder absolviert, die angerechnet werden können?",
    ("Ja", "Nein"),
    index=1,
)
if v1 == "Ja":
    anzahl_semester_extern = st.number_input(
        "Anzahl Semester, die angerechnet werden können",
        min_value=1,
        max_value=3,
        value=1,
    )
else:
    anzahl_semester_extern = 0

st.write("### Anrechnung von Zeit am CAS 🕕")
v2 = st.selectbox(
    "Wurde vorher schon etwas am CAS erbracht, was angerechnet werden kann (wie Semester in anderen Studiengängen oder Zertifikate?)",
    ("Nein", "Ja, anderer Studiengang", "Ja, Zertifikate"),
    index=0,
)
if v2 == "Ja, anderer Studiengang":
    st.write("#### Anrechnung von CAS Semestern aus anderem Studiengang")
    v2_studiengang = st.selectbox(
        "Welcher Studiengang wurde vorher absolviert?",
        load_studiengänge(data, gebührensatzung),
    )
    anzahl_semester_vorher_cas = st.number_input(
        "Anzahl Semester, die hier angerechnet werden können",
        min_value=1,
        max_value=3,
        value=1,
    )
    ECTS_vorher_cas = 0
elif v2 == "Ja, Zertifikate":
    st.write("#### Anrechnung von Zertifikaten")
    ECTS_vorher_cas = st.number_input(
        "Anzahl ECTS, die angerechnet werden können",
        min_value=1,
        max_value=90,
        value=17,
    )
    st.write(
        f"Anzahl Semester, die durch {ECTS_vorher_cas} ECTS angerechnet werden können: {etcsumrechner(ECTS_vorher_cas)}"
    )
    anzahl_semester_vorher_cas = 0
else:
    anzahl_semester_vorher_cas = 0
    ECTS_vorher_cas = 0

# Welche Kosten sind damit verbunden?
st.write("## Kosten 💲")
st.write(
    'Aktuell werden nur die reinen "Studien-Gebühren" berechnet, keine weiteren Kosten (wie Modulgebühren, etc.)'
)
st.write("Das kommt dann demnächst... Und wird hier schick tabelliert.")
gesamtzeit = (
    anzahl_semester_extern
    + anzahl_semester_vorher_cas
    + etcsumrechner(ECTS_vorher_cas)
    + anzahl_semester_cas
)
st.markdown(f"##### Gesamtzeit: {gesamtzeit} Semester")

### Anmeldegebühr
studiengang_data = next(
    (
        eintrag
        for eintrag in data[gebührensatzung]
        if eintrag["Studiengang"] == abs_studiengang
    ),
    None,
)
ANMELDEGEBÜHR = studiengang_data["Anmeldegebühr"]
st.markdown(f"Einmalige Anmeldegebühr: {ANMELDEGEBÜHR:,.2f} €")
st.markdown(
    f"Studentische Beiträge (60 € pro Semester): {anzahl_semester_cas * 60:,.2f} €"
)

GESAMTKOSTEN = 0 + ANMELDEGEBÜHR + anzahl_semester_cas * 60

for semester in range(1, gesamtzeit + 1):
    st.markdown(f"**Semester {semester}**")
    basiskosten_semester, langzeitkosten_semester = kosten_kalkulieren(
        semester,
        studiengang_data,
        anzahl_semester_extern,
        etcsumrechner(ECTS_vorher_cas),
        anzahl_semester_vorher_cas,
    )
    st.write(f"Kosten: {basiskosten_semester:,.2f} €")
    if langzeitkosten_semester > 0:
        st.write(f"Langzeitkosten: {langzeitkosten_semester:,.2f} €")
    GESAMTKOSTEN += basiskosten_semester + langzeitkosten_semester

st.markdown(f"##### Gesamtkosten: {GESAMTKOSTEN:,.2f} €")
