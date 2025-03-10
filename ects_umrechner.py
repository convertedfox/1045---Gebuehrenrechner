def etcsumrechner(ects):
    '''
    Gibt Anzahl der Semester
    zurück, die durch die Anzahl
    der ECTS angerechnet werden können.

    ects: int
    return: int
    '''
    if ects < 17.5:
        return 0
    elif ects < 40:
        return 1
    elif ects < 62.5:
        return 2
    elif ects > 62.5:
        return 3

if __name__ == '__main__':
    etcsumrechner(90)