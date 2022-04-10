import asyncio
import websockets
import json
import time

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


async def hello(websocket, path):
    name = await websocket.recv()
    jobj = json.loads(name)
    print("< {}".format(name))

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
    while commander.has_next():
        commander.run_next(machine)
        await websocket.send(json.dumps(machine.to_dict()))


if __name__ == '__main__':
    start_server = websockets.serve(hello, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
