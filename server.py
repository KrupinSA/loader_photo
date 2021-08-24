import aiofiles
import asyncio

from aiohttp import web
from asyncio import subprocess
from asyncio.subprocess import PIPE


INTERVAL_SECS = 0.5
BASE_DIR = 'test_photos'

async def archivate(request):
    archive_hash = request.match_info.get('archive_hash')

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'Attachment'
    response.headers['Content-Disposition'] = f'filename={archive_hash}.zip'

    await response.prepare(request)

    command = ['zip', '-r', '-', archive_hash]
    process = await subprocess.create_subprocess_exec(*command,stdin=PIPE, stdout=PIPE, cwd=BASE_DIR)
    chunk_len = 50000
    while True:
        chunk = await process.stdout.read(chunk_len)
        if not chunk:
            await response.write_eof()
            break
        await response.write(chunk)
        await asyncio.sleep(INTERVAL_SECS)

    return response

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
