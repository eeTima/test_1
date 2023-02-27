#!/usr/bin/env python3
import asyncio
import argparse
import json
import sys
from asyncio import BaseTransport
import logging

from calc import calc, CalcError

log = logging.getLogger('CalcServer')
# Устанавливаем уровень логирования
log.setLevel(logging.DEBUG)

# Парсим командную строку
parser = argparse.ArgumentParser(description='Calculator server')
parser.add_argument('--host', type=str, default='127.0.0.1', help='Bind host [127.0.0.1]')
parser.add_argument('--port', type=int, default=9876, help='Bind port [9876]')
parser.add_argument('--log', type=str, default='server.txt', help='Log file')
args = parser.parse_args()

if args.log:
    logging.basicConfig(
        filename=args.log,
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )


class CalcServer(asyncio.Protocol):
    """Класс обработчик сокета"""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport: BaseTransport) -> None:
        """Конект и получение траспорта"""
        self.transport = transport
        peername = transport.get_extra_info('peername')
        log.info(f'Connection: {peername}')

    def data_received(self, data: bytes) -> None:
        """Обработка данных"""
        log.info(f'Incomming: {data.decode()}')
        try:
            # Распаковывает входной JSON
            request = json.loads(data.decode())
            expression = request.get('expression', '')
            # Пробуем посчитать
            result = dict(error=False, ok=True, result=calc(expression))
            log.info(f'Result: {result}')
        except CalcError as e:
            # Ошибка калткулятора
            log.error(f'Calc error: {e}')
            result = dict(error=True, ok=False, msg=f'Calc error: {e}')
        except json.JSONDecodeError as e:
            # Неправильный JSON на входе
            log.error(f'Invalid JSON: {e}')
            result = dict(error=True, ok=False, msg=f'Invalid JSON: {e}')
        except Exception as e:
            # Что-то пошло не по плану
            log.error(f'Unknown error "{type(e).__name__}": {e}')
            result = dict(error=True, ok=False, msg=f'Unknown error "{type(e).__name__}": {e}')

        # Отправляем результат
        self.transport.write(json.dumps(result, indent=4).encode())
        # Закрываем сокет
        self.transport.close()
        log.info('socket closed')


def main():
    # Инициируем asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запускаем наш сервер
    calc_server = loop.create_server(CalcServer, args.host, args.port)
    try:
        server = loop.run_until_complete(calc_server)
    except Exception as e:
        log.fatal(f'Error {type(e).__name__}: {e}')
        sys.exit(-1)
    log.info(f'Listening {args.host} {args.port}')

    try:
        # Поехали!
        loop.run_forever()
    except KeyboardInterrupt:
        log.info('exit')
    finally:
        # Приехали!
        server.close()
        loop.close()


# проверяет, был ли файл запущен напрямую
if __name__ == '__main__':
    main()
