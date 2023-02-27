import re


class CalcError(Exception):
    """Класс ошибки калькулятора"""
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


def calc(expression: str) -> str:
    """Функция каькулятора"""
    try:
        # убираем лишнее из выражения(чтоб что-то не то не выполнили)
        expression = re.sub(r'[^-+/*\.0-9]+', '', expression)
        # считаем через питоновый интерпретатор
        result = eval(expression)
    except Exception as e:
        raise CalcError(f'{type(e).__name__}')
    return result
