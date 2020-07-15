#!/usr/bin/python
# finds computers that have minor updates
# does stuff to them
# provides a countdown timer

import os.path
from os import path
import subprocess
import sys

TOO_OLD = '10.14' #set what's too old here
PROPER_INSTALLER = 'Install macOS Mojave.app' #set target os here
USERISADMIN = True
LOGOPATH = ''

class popupWindow:
    # build class
    def __init__(self, name):
        self.name = name
        
    def buildWindow(self, windowStyle, heading, title, message, *args):
        icon = "{}".format(LOGOPATH)    
        if not os.path.exists(icon):
            icon = "/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns"
        window = [
            "/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper",
            "-windowType",
            windowStyle, #hud #utility #fullscreen
            "-heading",
            heading,
            "-title",
            title,
            "-description",
            message, #what do you wanna say
            "-icon",
            icon,
            "-defaultbutton",
            "1",
        ]
        for ar in args:
            window.append(ar)
        return window

    #feed me the popupWindow.buldWindow as an arg
    def fireWindow(self, popup_type):
        self.proc = subprocess.Popen(popup_type, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out, self.err = self.proc.communicate()

        print "User clicks:", self.out
        if self.proc.returncode == 0:
            return True
        if self.proc.returncode == 2:
            return False
        else:
            return False
            print("Error: %s" % self.proc.returncode)

class queryToDetermine:
    # build class
    def __init__(self, name):
        self.name = name

    def isSystemOk(self, TOO_OLD):
        versionResult = subprocess.Popen(['sw_vers', '-productVersion'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = versionResult.communicate()
        print stdout
        if TOO_OLD in stdout:
            print('<result>false</result>')
            return False 
        else:
            print('<result>true</result>')
            return True


class runShellClass: 
    """this class runs bash commands runShellClass.runjob('ls')"""
    def __init__(self, name):
        self.name = name
        
    def runJob(self, *args):
        commands = []
        for t in args:
            commands.append(t)
        data = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = data.communicate()
        print(stdout)

def main():
    v = queryToDetermine('checkSystem')
    if not v.isSystemOk(TOO_OLD):
        if USERISADMIN:
            p = popupWindow('sugguestForAdminsONLY')
            p = p.fireWindow(p.buildWindow(
                'hud',
                'MacOS Version Not Supported',
                'Upgrade Required',
                '''Your computer OS is too old, you have the privlidges to do update it! Go to the APPLICATIONS FOLDER and double click {}... We will open the installer now for you also, the rest is up to you. 

    Once You are Up To Date you will no longer recieve this WARNING...'''.format(PROPER_INSTALLER),
                    '-button1',
                    "TRY NOW"
                ))
            r = runShellClass('runjob')
            r.runJob("open", "/Applications/{}".format(PROPER_INSTALLER))



if __name__ == "__main__":
    main()