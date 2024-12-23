def strings_parsing(s: str) -> list:
    """
    Парсит пары по два числа. Числа разделены пробелом. Пары - запятой.
    Возвращает список пар [число1, число2] или пустой список, если строка некорректна.
    """
    ans = []
    for item in s.split(','):
        try:
            num1, num2 = map(int, item.split())
            ans.append([num1, num2])
        except ValueError:
            return []
    return ans


def two_numbers_parsing(s: str) -> list:
    """
    Парсит строку из двух чисел, разделенных пробелом.
    Возвращает пару [число1, число2] или пустой список, если строка некорректна.
    """
    try:
        length, width = map(int, s.split())
        return [length, width]
    except ValueError:
        return []
