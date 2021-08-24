import aiofiles
import asyncio

from aiohttp import web
from asyncio import subprocess
from asyncio.subprocess import PIPE
from os import path
from aiohttp.web import HTTPNotFound

INTERVAL_SECS = 0.5
BASE_DIR = 'test_photos'

def check_dir(archive_hash):
    if archive_hash in [".", ".."]:
        return False
    full_dir = path.join(BASE_DIR, archive_hash)
    return path.exists(full_dir)

async def archivate(request):
    archive_hash = request.match_info.get('archive_hash')

    if not check_dir(archive_hash):
        raise HTTPNotFound(text='Файл удален или не существует')

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
