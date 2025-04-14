def kosten_kalkulieren(semester, studiengang, anzahl_semester_extern, ects_semester, anzahl_semester_vorher_cas,) -> float:
    """
    Berechnet die Kosten für ein einzelnes Semester.

    semester: aktuelles Semester, das berechnet werden soll
    studiengang: Studiengangsdaten, für den die Kosten berechnet werden
    anzahl_semester_extern: Anzahl der externen Semester, die angerechnet werden können
    ects_semester: Semester, die aufgrund von ects angerechnet werden können
    anzahl_semester_vorher_cas: Anzahl der Semester, die am CAS in einem anderen Studiengang angerechnet werden können

    return: float: Kosten für das Semester
    """

    if semester < (anzahl_semester_extern +  ects_semester + anzahl_semester_vorher_cas):
        return 0.0
    else:
        basiskosten = studiengang["Gebühr ab 20271001"]
    
    return basiskosten