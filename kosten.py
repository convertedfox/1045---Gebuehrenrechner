def nackte_semesterkosten(semester, studiengang) -> float:
    """
    Berechnet die Kosten für ein einzelnes Semester ohne sonstige Parameter, nur die Langzeitgebühren werden noch ermittelt.

    semester: aktuelles Semester, das berechnet werden soll
    studiengang: Studiengangsdaten, für den die Kosten berechnet werden
    return: float, float: Kosten für das Semester, langzeitkosten
    """

    basiskosten_für_semester = studiengang["Studiengebühren"]

    if semester < (5):
        return basiskosten_für_semester, 0.0
    else:
        langzeitkosten = studiengang["Langzeitgebühr"]
        return 0.0, langzeitkosten


if __name__ == "__main__":
    # Beispielaufruf 1
    studiengang = {
        "Studiengang": "Bachelor in Informatik",
        "Studiengebühren": 5000.0,
        "Langzeitgebühr": 480.0,
    }
    semester = 3

    kosten = nackte_semesterkosten(semester, studiengang)
    print(f"Kosten für das Semester: {kosten} €")

    # Beispielaufruf 2
    studiengang = {
        "Studiengang": "Bachelor in Informatik",
        "Studiengebühren": 5000.0,
        "Langzeitgebühr": 480.0,
    }
    semester = 5

    kosten = nackte_semesterkosten(semester, studiengang)

    print(f"Kosten für das Semester: {kosten} €")
