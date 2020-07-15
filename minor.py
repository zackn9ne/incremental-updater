#!/usr/bin/python
# finds computers that have minor updates

import os.path
from os import path
import subprocess
import re

datafile = '/tmp/updatesavail.log'

def createCache():
    data = subprocess.Popen(['softwareupdate', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = data.communicate()
    print stdout
    f = open(datafile, 'wb')
    f.write(stdout)
    f.close()

def readCache():
    f = open(datafile, 'r')
    stdout = f.readlines()
    stdout = '#'.join(stdout)
    if "restart" in stdout:
        print('<result>true</result>')
    else:
        print('<result>false</result>')


def main():
    if path.exists(datafile) != True:
        createCache()
        readCache()
    else:
        readCache()


if __name__ == "__main__":
    main()