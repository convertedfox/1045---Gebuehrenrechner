def kosten_kalkulieren(semester, studiengang, anzahl_semester_extern, ects_semester, anzahl_semester_vorher_cas,) -> float:
    """
    Berechnet die Kosten für ein einzelnes Semester.

    semester: aktuelles Semester, das berechnet werden soll
    studiengang: Studiengangsdaten, für den die Kosten berechnet werden
    anzahl_semester_extern: Anzahl der externen Semester, die angerechnet werden können
    ects_semester: Semester, die aufgrund von ects angerechnet werden können
    anzahl_semester_vorher_cas: Anzahl der Semester, die am CAS in einem anderen Studiengang angerechnet werden können

    return: float, float: Kosten für das Semester, langzeitkosten
    """

    if semester < (anzahl_semester_extern +  ects_semester + anzahl_semester_vorher_cas):
        return 0.0, 0.0
    else:
        basiskosten = studiengang["Studiengebühren"]
        if semester > 4:
            langzeitkosten = studiengang["Langzeitgebühr"]
        else:
            langzeitkosten = 0.0
    return basiskosten, langzeitkosten

if __name__ == '__main__':
    # Beispielaufruf
    studiengang = {
        "Studiengang": "Bachelor in Informatik",
        "Gebühr ab 20271001": 5000.0
    }
    semester = 3
    anzahl_semester_extern = 1
    ects_semester = 1
    anzahl_semester_vorher_cas = 0

    kosten = kosten_kalkulieren(semester, studiengang, anzahl_semester_extern, ects_semester, anzahl_semester_vorher_cas)
    print(f"Kosten für das Semester: {kosten} €")