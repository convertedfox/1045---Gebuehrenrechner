# Korrigierter Streamlit Code
import streamlit as st
import json
from kosten import nackte_semesterkosten


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
flag_rabatt = False  # Flag, ob Rabatt durch externe ECTS gewährt wurde
um_ects_reduzierte_gebühren = 0

# Title
st.title("Gebührenkostenrechner 💰")
st.write("Prototyp, ist in Entwicklung...")
st.write("## Gültige Gebührensatzung")
st.write("Aktuell werden DBs nur bei Gebührensatzung ab 01.04.2026 unterstützt.")
gebührensatzung = st.selectbox(
    "Welche Gebührensatzung soll verwendet werden?",
    load_gebührensatzung(data),
    index=2,
    disabled=True,
)

# In welchem Studiengang wird absolviert?
st.write("## Erbrachte Leistungen")
st.write("### In welchem Studiengang wird absolviert? 👨🏻‍🎓")
abs_studiengang = st.selectbox(
    "Worin will man absolvieren?", load_studiengänge(data, gebührensatzung), index=0
)
# Studiengang-Daten gleich abspeichern
studiengang_data = next(
    (
        eintrag
        for eintrag in data[gebührensatzung]
        if eintrag["Studiengang"] == abs_studiengang
    ),
    None,
)

if studiengang_data is None:
    st.error("Für den ausgewählten Studiengang wurden keine Stammdaten gefunden.")
    st.stop()

st.write("Diese Daten liegen vor - nur zur Demo:")
st.write(studiengang_data)

fachbereich = studiengang_data.get("Fachbereich") if studiengang_data else None

# Wieviele Semester werden am CAS studiert?
anzahl_semester_cas = st.number_input(
    f"Anzahl durchlaufener Semester am CAS im Studiengang {abs_studiengang}",
    min_value=1,
    max_value=10,
    value=4,
)

# Hat man vorher etwas anderes gemacht?
st.write("### Anrechnung externer Leistungen 🏫")
if fachbereich in {"Sozialwesen", "Gesundheit"}:
    st.write(
        "Bei Studiengängen im Fachbereich Sozialwesen/Gesundheit können keine ECTS angerechnet werden."
    )

else:
    st.write("Wurden ECTS ausserhalb des DHBW CAS erworben?")
    v1 = st.radio(
        "Wurde Semester an einer anderen Hochschule studiert oder absolviert, die angerechnet werden können?",
        ("Ja", "Nein"),
        index=1,
    )
    if v1 == "Ja":
        ects_extern = st.number_input(
            "Wieviel ECTS wurden extern erworben, die angerechnet werden sollen?",
            min_value=15,
            max_value=90,
            step=1,
        )
        um_ects_reduzierte_gebühren = studiengang_data.get("DB3") * 4 + (
            (studiengang_data.get("DB1") + studiengang_data.get("DB2")) * 4 / 90
        ) * (90 - ects_extern)
        rabatt = (
            studiengang_data.get("Studiengebühren") * 4 - um_ects_reduzierte_gebühren
        )
        if ects_extern > 0:
            st.write(
                f"Für die externen ECTS wird die Gebühr um {rabatt:,.2f} € gesenkt."
            )
            flag_rabatt = True
        else:
            st.write("Es werden keine Gebühren reduziert.")
            rabatt = 0


st.write("### Anrechnung von Zeit am CAS 🕕")
v2 = st.selectbox(
    "Wurde vorher schon etwas am CAS erbracht, was angerechnet werden kann (wie Semester in anderen Studiengängen oder Zertifikate?)",
    ("Nein", "Ja"),
    index=0,
)
if v2 == "Ja":
    st.write("#### Anrechnung von Gebühren, die bisher am CAS bezahlt wurden")
    st.write(
        "Wenn Sie Module oder Zertifikate am CAS absolviert haben, die angerechnet werden können in Ihrem aktuellen Studiengang, geben Sie bitte die bisher bezahlten Gebühren an."
    )
    vorher_bezahlte_gebühren = st.number_input(
        "Gebühren für anrechenbare Leistungen",
    )

# Welche Kosten sind damit verbunden?
st.write("## Kosten 💲")
st.write(
    'Aktuell werden nur die reinen "Studien-Gebühren" berechnet, keine weiteren Kosten (wie Modulgebühren, etc.)'
)
st.write("Das kommt dann demnächst... Und wird hier schick tabelliert.")
gesamtzeit = anzahl_semester_cas

st.markdown(f"##### Gesamtzeit: {gesamtzeit} Semester")

### Anmeldegebühr
ANMELDEGEBÜHR = studiengang_data["Anmeldegebühr"]
st.markdown(f"Einmalige Anmeldegebühr: {ANMELDEGEBÜHR:,.2f} €")
st.markdown(
    f"Studentische Beiträge (60 € pro Semester): {anzahl_semester_cas * 60:,.2f} €"
)

GESAMTKOSTEN = (
    0 + ANMELDEGEBÜHR + anzahl_semester_cas * 60
)  # Warum die 60? Weil studentische Beiträge 60 euro pro semester sind
st.write(um_ects_reduzierte_gebühren)
for semester in range(1, gesamtzeit + 1):
    st.markdown(f"**Semester {semester}**")
    basiskosten_semester, langzeitkosten_semester = nackte_semesterkosten(
        semester,
        studiengang_data,
    )
    if flag_rabatt:
        if um_ects_reduzierte_gebühren > 0:
            if um_ects_reduzierte_gebühren > basiskosten_semester:
                st.write(f"Semestergebühren: {basiskosten_semester:,.2f} €")
                um_ects_reduzierte_gebühren -= basiskosten_semester
                st.write(um_ects_reduzierte_gebühren)
            else:
                st.write(f"Semestergebühren: {um_ects_reduzierte_gebühren:,.2f} €")
                basiskosten_semester = um_ects_reduzierte_gebühren
                um_ects_reduzierte_gebühren = 0
                st.write(um_ects_reduzierte_gebühren)
        else:
            st.write("Semestergebühren: 0.00 € (durch ECTS-Anrechnung gedeckt)")
            basiskosten_semester = 0.0
            st.write(um_ects_reduzierte_gebühren)
    else:
        st.write(f"Semestergebühren: {basiskosten_semester:,.2f} €")
    if langzeitkosten_semester > 0:
        st.write(f"Langzeitkosten: {langzeitkosten_semester:,.2f} €")
    GESAMTKOSTEN += basiskosten_semester + langzeitkosten_semester

st.markdown(f"##### Gesamtkosten: {GESAMTKOSTEN:,.2f} €")
