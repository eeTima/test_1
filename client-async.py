#!/usr/bin/env python3
import argparse
import asyncio
import json
import logging

log = logging.getLogger('CalcClient')
# Устанавливаем уровень логирования
log.setLevel(logging.DEBUG)

# Парсим командную строку
parser = argparse.ArgumentParser(description='Calculator client')
parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host [127.0.0.1]')
parser.add_argument('--port', type=int, default=9876, help='Server port')
parser.add_argument('--log', type=str, default='client.txt', help='Log file')
args = parser.parse_args()

if args.log:
    logging.basicConfig(
        filename=args.log,
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )


async def operate():
    loop = asyncio.get_event_loop()
    while True:
        try:
            expression = await loop.run_in_executor(None, lambda: input('Expression: '))
        except EOFError:
            break

        if expression.lower().strip() == 'exit':
            break
        writer = None
        try:
            reader, writer = await asyncio.open_connection(host=args.host, port=args.port)
            writer.write(json.dumps(dict(expression=expression)).encode())

            data = await reader.read(65536)
            result = json.loads(data.decode())

            if result.get('ok'):
                log.info(f'Result:\n{json.dumps(result["result"], indent=4)}')
                print(f'Result:\n{json.dumps(result["result"], indent=4)}')
            elif result.get('error'):
                log.error(f'Result:\n{result["msg"]}')
                print(f'Result:\n{result["msg"]}')
            else:
                log.error(f'Something wrong!')
                print(f'Something wrong!')
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()


def main():
    # Инициируем asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print('type "exit" or press Ctrl-C twice to exit')

    try:
        # Поехали!
        loop.run_until_complete(operate())
    except KeyboardInterrupt:
        log.info('Exit')
    finally:
        # Приехали!
        loop.close()


if __name__ == '__main__':
    main()
