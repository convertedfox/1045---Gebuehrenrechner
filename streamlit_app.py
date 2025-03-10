import streamlit as st
import json
import os
from ects_umrechner import etcsumrechner

# Load data
with open("studiengänge.json", 'r', encoding='utf-8') as file:
  studiengaenge = json.load(file)
studiengang_namen = [studiengang["name"] for studiengang in studiengaenge["studiengaenge"]]

# Title
st.title('Gebührenkostenrechner 💰')
st.write('Prototyp, ist in Entwicklung')

# In welchem Studiengang wird absolviert?
st.write('## Erbrachte Leistungen')
st.write('### In welchem Studiengang wird absolviert? 👨🏻‍🎓')
abs_studiengang = st.selectbox('Worin will man absolvieren?', studiengang_namen)

# Wieviele Semester werden am CAS studiert?
anzahl_semester_cas = st.number_input(f'Anzahl durchlaufener Semester am CAS im Studiengang {abs_studiengang}', min_value=1, max_value=10, value=4)

# Hat man vorher etwas anderes gemacht?
st.write('### Anrechnung von externen Semestern 🏫')
v1 = st.radio('Wurde Semester an einer anderen Hochschule studiert oder absolviert, die angerechnet werden können?', ('Ja', 'Nein'), index=1)
if v1 == 'Ja':
  anzahl_semester_extern = st.number_input('Anzahl Semester, die angerechnet werden können', min_value=1, max_value=3, value=1)

st.write('### Anrechnung von Zeit am CAS 🕕')
v2 = st.selectbox('Wurde vorher schon etwas am CAS erbracht, was angerechnet werden kann (wie Semester in anderen Studiengaängen oder Zertifikate?)', ('Nein', 'Ja, anderer Studiengang', "Ja, Zertifikate"), index=0)
if v2 == 'Ja, anderer Studiengang':
  st.write('#### Anrechnung von CAS Semestern aus anderem Studiengang')
  v2_studiengang = st.selectbox('Welcher Studiengang wurde vorher absolviert?', studiengang_namen)
  anzahl_semester_vorher_cas = st.number_input('Anzahl Semester, die angerechnet werden können', min_value=1, max_value=3, value=1)
elif v2 == 'Ja, Zertifikate':
  st.write('#### Anrechnung von Zertifikaten')
  ECTS_vorher_cas = st.number_input('Anzahl ECTS, die angerechnet werden können', min_value=1, max_value=90, value=17)
  st.write(f'Anzahl Semester, die durch {ECTS_vorher_cas} ECTS angerechnet werden können: {etcsumrechner(ECTS_vorher_cas)}')

# Welche Kosten sind damit verbunden?
st.write('## Kosten')
st.write("Hier kommt dann eine Tabelle mit den Semestern und damit verbundenen Kosten hin...")