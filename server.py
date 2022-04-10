import asyncio
import websockets
import websockets.server as wserver
import json

from parsing.bufferio import StringContainer
from parsing.commander import Commander
from parsing.lexer import Lexer
from parsing.parser import AST
from turing.environment import TheTape
from turing.machine import TuringMachine


test = """
print_name:
{
write 'A';
right 1;write 'a';
right 1;write 'r';
right 1;write 'o'; 
right 1;write 'n';
right 1;
}
goto print_name;
right 5;
left 20;
goto print_name;
while(= read '0') { write '1'; right 1; }
halt;
"""


async def hello(websocket: wserver.WebSocketServerProtocol, path):
    keep_going = True
    data_q = asyncio.Queue(10)
    stop_q = asyncio.Queue(10)

    async def io_loop(q: asyncio.Queue, sq: asyncio.Queue):
        while True:
            name = await websocket.recv()
            obj = json.loads(name)
            print("< {}".format(name))
            if 'stop' in obj:
                await q.put(False)
            else:
                await q.put(obj)

    async def main_loop(q: asyncio.Queue, sq: asyncio.Queue):
        while True:
            try:
                jobj = await q.get()
                print(jobj)
                if jobj:
                    tape = TheTape()
                    machine = TuringMachine(tape)

                    if 'initial_string' in jobj and len(jobj['initial_string']) > 0:
                        tape.initialize_tape(jobj['initial_string'])

                    if 'code' in jobj and len(jobj['code']) > 0:
                        code = jobj['code']
                    else:
                        code = test

                    tape.reset(True)

                    code = AST(Lexer(StringContainer(code)))
                    code.build_tree()

                    commander = Commander(code)
                    sobj = {}
                    while commander.has_next():
                        try:
                            qobj = q.get_nowait()
                            if not qobj:
                                print('Halting execution')
                                if isinstance(qobj, dict):
                                    await q.put(qobj)
                                break
                        except asyncio.QueueEmpty:
                            pass

                        commander.run_next(machine)
                        sobj = machine.to_dict()
                        sobj['last'] = False
                        print('> {}'.format(json.dumps(sobj)))
                        await websocket.send(json.dumps(sobj))
                    sobj['last'] = True
                    print('> {}'.format(json.dumps(sobj)))
                    await websocket.send(json.dumps(sobj))
            except asyncio.QueueEmpty:
                continue

    await asyncio.gather(
        io_loop(data_q, stop_q),
        main_loop(data_q, stop_q)
    )


if __name__ == '__main__':
    start_server = websockets.serve(hello, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
