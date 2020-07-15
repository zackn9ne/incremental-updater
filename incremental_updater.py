#!/usr/bin/python
# finds computers that have minor updates
# does stuff to them
# provides a countdown timer

import os.path
from os import path
import subprocess
import re
import getpass
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
import sys

#options
TIME = '30'
LOGOPATH = './jumbo.png'
#first
FIRSTPOPTITLE = 'unsupported macOS Version'
FIRSTPOPBAR = 'Update Required'
FIRSTPOP = '''Your macOS needs security updates.

Press the Update button below, you will have one more screen to confirm before this runs.'''
FIRSTPOPBTN = 'Update'
#success
OKPOPTITLE = 'macOS is Secure'
OKPOPBAR = 'Good job'
OKPOP = "Congratulations you're up to date, thanks for clicking."
OKPOPBTN = 'FLEX MODE'
#second
SECONDPOP = 'Save your work because unless you press Postpone, your updates will begin in {} seconds...'.format(TIME)

class minorUpdate():
    # build class
    def __init__(self):
        self.binary = '/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper'
        self.datafile = '/tmp/jumboupdater.log'
    
    def icons(self):
        if LOGOPATH:
            try:
                open(LOGOPATH)
                self.icon = "{}".format(LOGOPATH)  #icon failover business   
            except IOError:
                print("404 icon not found")
                self.icon = "/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns"        
 
    def buildWindow(self, windowStyle, heading, title, message, *args):
        window = [
            self.binary,
            "-windowType",
            windowStyle, #hud #utility #fullscreen
            "-heading",
            heading,
            "-title",
            title,
            "-description",
            message, #what do you wanna say
            "-icon",
            self.icon,
            "-defaultbutton", #action button
            "1",
        ]
        for ar in args:
            window.append(ar)
        return window

    def windowLauncher(self, popup_type): #feed me a buildWindow()
        self.proc = subprocess.Popen(popup_type, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out, self.err = self.proc.communicate()
        self.result = self.proc.returncode
        return self.result

    def handle(self, result):
        print "User clicks:", result
        if result == 0 or result == 2:
            return result
        else:
            print("Error: %s" % result)
            return result

    def doesDataFileExist(self):
        if path.exists(self.datafile):
            return True
    
    def simplemessaging(self, info, noun):
        print(info, noun)
    
    def writeUpdateStatus(self):
        data = subprocess.Popen(['softwareupdate', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = data.communicate()
        self.simplemessaging("writing", self.datafile)            
        f = open(self.datafile, 'wb')
        f.write(stdout)
        f.close()
  
    def readUpdateStatus(self):
        self.simplemessaging("reading", self.datafile)
        f = open(self.datafile, 'r')
        stdout = f.readlines()
        stdout = '#'.join(stdout)
        print stdout
        if "restart" in stdout:
        #    print('<result>true</result>')
            return True
        else:
            print('<result>false</result>')
            return False

    def doUpdates(self):
        if self.readUpdateStatus():
            return True

    def runShellCMD(self, *args):
        commands = []
        for t in args:
            commands.append(t)
        data = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = data.communicate()
        print(stdout)

    def main(self):
        """main here"""
        self.icons() #always
        self.doesDataFileExist() #always

        if not self.doesDataFileExist():
            self.writeUpdateStatus()

        self.readUpdateStatus() #always

        """for window logic 0 is when user clicks default button"""
        if self.doUpdates(): #dostuff
            w = self.buildWindow(
                'hud',
                FIRSTPOPTITLE,
                FIRSTPOPBAR,
                FIRSTPOP,
                '-button1',
                FIRSTPOPBTN
            )

            if self.handle(self.windowLauncher(w)) is 0:
                print 'user clicked 1st window'       

                w = self.buildWindow(
                    'hud', 
                    'Countdown Started', 
                    'Restart Pending', 
                    SECONDPOP,
                    '-button1', #user clicks 0 things happen
                    'Proceed', 
                    '-button2', #user clicks 2 things don't happen
                    'Postpone', 
                    '-countdown', 
                    '-timeout', 
                    TIME
                )
                if self.handle(self.windowLauncher(w)) is 0:
                    print ('user clicked 2nd window or timer of {} expired').format(TIME)
                else:
                    print 'user declined 2nd window'

        if not self.doUpdates(): #allclear
            w = self.buildWindow(
                'hud',
                OKPOPTITLE,
                OKPOPBAR,
                OKPOP,
                '-button1', #user clicks 0
                OKPOPBTN
            )
            if self.handle(self.windowLauncher(w)) is 0:
                print 'user ragreed'        



if __name__ == "__main__":
#    buildPromptVars(typeOneWindow)
    minorUpdate().main()