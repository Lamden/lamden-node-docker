from datetime import datetime
from dateutil import parser
import asyncio
import os
import socketio
from sync_blocks import SyncBlocksHandler

async def run_command(args):
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    stdout, _ = await process.communicate()
    if process.returncode != 0 and stdout:
        with open(f'logs/{"_".join(args)}_{datetime.now().strftime("%Y%m%d_%H:%M:%S")}.log', 'w') as f:
            f.write(stdout.decode())
    
    return process.returncode

async def upgrade_handler(data: dict):
    os.environ['LAMDEN_TAG'] = data['lamden_tag']
    os.environ['CONTRACTING_TAG'] = data['contracting_tag']
    os.environ['LAMDEN_BOOTNODES'] = ':'.join(data['bootnode_ips'])
    os.environ.pop('LAMDEN_NETWORK', None)

    if await run_command(['make', 'build']) != 0:
        return

    delta = (parser.parse(data['utc_when']) - datetime.utcnow()).total_seconds()
    if delta > 0:
        await asyncio.sleep(delta)

    await run_command(['make', 'restart'])

async def network_error_handler(data: dict):
    if await run_command(['make', 'stop']) != 0:
        return

    network_is_down = True
    while network_is_down:
        for ip in data['bootnode_ips']:
            if await run_command(['ping', '-c', '1', ip]) == 0:
                network_is_down = False
                break

    os.environ['LAMDEN_BOOTNODES'] = ':'.join(data['bootnode_ips'])
    os.environ.pop('LAMDEN_NETWORK', None)

    await run_command(['make', 'start'])

async def sync_blocks_handler(data: dict):
    start_block = data.get('start_block', '0')
    end_block = data.get('end_block', '0')
    node_ips = data.get('node_ips', [])

    if len(node_ips) == 0:
        return

    sync_blocks_hander = SyncBlocksHandler(start_block, end_block, node_ips)
    await sync_blocks_hander.start()


event_handlers = {
    'upgrade': upgrade_handler,
    'network_error': network_error_handler,
    'sync_blocks': sync_blocks_handler
}

sio = socketio.AsyncClient()

@sio.event
async def connect():
    for room in list(event_handlers.keys()):
        await sio.emit('join', {'room': room})

@sio.event
async def disconnect():
    for room in list(event_handlers.keys()):
        await sio.emit('leave', {'room': room})

@sio.event
async def event(event: dict):
    asyncio.ensure_future(event_handlers[event['event']](event['data']))

async def main():
    await sio.connect(f'http://localhost:17080')
    await sio.wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
