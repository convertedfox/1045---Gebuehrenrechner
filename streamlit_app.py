# Korrigierter Streamlit Code
from decimal import DefaultContext
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

# Title
st.title("Gebührenkostenrechner 💰")
st.write("Prototyp, ist in Entwicklung...")

# Stammdaten
tab_studiengang, tab_gebühren = st.tabs(["Studiengang", "Gebührensatzung"])
# Gebührensatzung
with tab_gebühren:
    st.write("Aktuell werden DBs nur bei Gebührensatzung ab 01.04.2026 unterstützt.")
    gebührensatzung = st.selectbox(
        "Welche Gebührensatzung soll verwendet werden?",
        load_gebührensatzung(data),
        index=2,
        disabled=True,
    )

# In welchem Studiengang wird absolviert?
with tab_studiengang:
    st.write("## In welchem Studiengang wird absolviert? 👨🏻‍🎓")
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

    geschätzte_gesamtgebühr = studiengang_data.get("Studiengebühren") * 4  # Initialwert

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
st.write("---")
# Hat man vorher etwas anderes gemacht?
st.write("## Anrechnung externer Leistungen 🏫")
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
        geschätzte_gesamtgebühr = studiengang_data.get("DB3") * 4 + (
            (studiengang_data.get("DB1") + studiengang_data.get("DB2")) * 4 / 90
        ) * (90 - ects_extern)
        rabatt = studiengang_data.get("Studiengebühren") * 4 - geschätzte_gesamtgebühr
        if ects_extern > 0:
            st.write(
                f"Für die externen ECTS wird die Gebühr um {rabatt:,.2f} € gesenkt."
            )
            flag_rabatt = True
        else:
            st.write("Es werden keine Gebühren reduziert.")
            rabatt = 0


st.write("## Anrechnung von Zeit am CAS 🕕")
v2 = st.radio(
    "Wurde vorher schon etwas am CAS erbracht, was angerechnet werden kann (wie Semester in anderen Studiengängen oder Zertifikate?)",
    ("Ja", "Nein"),
    index=1,
)
if v2 == "Ja":
    st.write("#### Anrechnung von Gebühren, die bisher am CAS bezahlt wurden")
    st.write(
        "Wenn Sie Module oder Zertifikate am CAS absolviert haben, die angerechnet werden können in Ihrem aktuellen Studiengang, geben Sie bitte die bisher bezahlten Gebühren an."
    )
    vorher_bezahlte_gebühren = st.number_input(
        "Gebühren für anrechenbare Leistungen",
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
gesamtzeit = anzahl_semester_cas  # braucht es evtl. nicht

st.markdown(f"##### Gesamtzeit: {anzahl_semester_cas} Semester")

# Anmeldegebühr
anmeldegebühr = studiengang_data["Anmeldegebühr"]
GESAMTKOSTEN = 0 + anmeldegebühr + anzahl_semester_cas * 60
# Warum die 60? Weil studentische Beiträge 60 euro pro semester sind

# st.write(geschätzte_gesamtgebühr)

# Semestertabelle erzeugen
row1 = st.columns(anzahl_semester_cas)
semester = 0
for col in row1:
    semester = semester + 1
    semestercontainer = col.container(border=True, height=200)
    semestercontainer.markdown(f"**Semester {semester}**")
    basiskosten_semester, langzeitkosten_semester = nackte_semesterkosten(
        semester,
        studiengang_data,
    )
    if flag_rabatt:
        if geschätzte_gesamtgebühr > 0:
            if geschätzte_gesamtgebühr > basiskosten_semester:
                semestercontainer.write(
                    f"Semestergebühren: {basiskosten_semester:,.2f} €"
                )
                geschätzte_gesamtgebühr -= basiskosten_semester
                semestercontainer.write(geschätzte_gesamtgebühr)
            else:
                semestercontainer.write(
                    f"rabattierte Semestergebühren: {geschätzte_gesamtgebühr:,.2f} € (durch Anrechnungen teilweise gedeckt)"
                )
                basiskosten_semester = geschätzte_gesamtgebühr
                geschätzte_gesamtgebühr = 0
                semestercontainer.write(geschätzte_gesamtgebühr)
        else:
            semestercontainer.write(
                "rabattierte Semestergebühren: 0.00 € (durch Anrechnungen vollständig gedeckt)"
            )
            basiskosten_semester = 0.0
            semestercontainer.write(geschätzte_gesamtgebühr)
    else:
        semestercontainer.write(f"Semestergebühren: {basiskosten_semester:,.2f} €")
    if langzeitkosten_semester > 0:
        st.write(f"Langzeitkosten: {langzeitkosten_semester:,.2f} €")
    GESAMTKOSTEN += basiskosten_semester + langzeitkosten_semester

container_gesamtkosten = st.container(border=True)

container_gesamtkosten.write(f"➕ Einmalige Anmeldegebühr: {anmeldegebühr:,.2f} €")
container_gesamtkosten.write(
    f"➕ Studentische Beiträge (60 € pro Semester): {anzahl_semester_cas * 60:,.2f} €"
)
container_gesamtkosten.markdown("---")
container_gesamtkosten.markdown(f"##### 🟰 Gesamtkosten: {GESAMTKOSTEN:,.2f} €")
