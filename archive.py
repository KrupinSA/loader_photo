from os import error
import subprocess

from subprocess import PIPE

command = ['zip', '-r', '-', 'README.md']
process = subprocess.Popen(command, stdin=PIPE, stdout=PIPE)

data, error = process.communicate()

with open('readme.zip', 'b+w') as archive:
    archive.write(data)