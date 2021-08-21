import asyncio

from asyncio import subprocess
from asyncio.subprocess import PIPE

async def create_archive(command, arch_name):

    process = await subprocess.create_subprocess_exec(*command, stdin=PIPE, stdout=PIPE)
    with open(arch_name, 'b+w') as archive:
        while True:
            chunk = await process.stdout.read(500)
            if process.stdout.at_eof():
                break
            archive.write(chunk)

async def main():
    command = ['zip', '-r', '-', 'snap']
    task = asyncio.create_task(create_archive(command, 'snap.zip'))
    await task

if __name__ == "__main__":
    asyncio.run(main())