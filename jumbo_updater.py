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


LOGOPATH = './jumbo.png'
TESTINGMODE = True
FIRSTPOPTITLE = 'unsupported macOS Version'
FIRSTPOP = '''Your macOS needs security updates.

Press the Update button below, you will have one more screen to confirm before this runs.'''
FIRSTPOPBTN = 'Update'
SECONDPOP = 'Save your work because unless you press Postpone, your updates will begin in 30 seconds...'

def adminRightsAchieved():
    username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0]; username = [username,""][username in [u"loginwindow", None, u""]]; sys.stdout.write(username + "\n")
    print(username, " is online")

    #construct query for currentuser
    job = ['id', '-G' ]
    job.append(username)

    data = subprocess.Popen(job, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = data.communicate()
    print stdout
    if (stdout.find('80') != -1):
        print 'found 80'
        return True
    else:
        print 'fail'
        return False

class popupWindow:
    # build class
    def __init__(self):
        self.icon = "{}".format(LOGOPATH)  #icon failover business
        if not os.path.exists(self.icon):
            self.icon = "/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns"        
        
    def buildWindow(self, windowStyle, heading, title, message, *args):
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
            self.icon,
            "-defaultbutton", #action button
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

class lookForUpdates:
    # build class
    def __init__(self):
    # set vars
        self.datafile = '/tmp/jumboupdater.log'


    def createDataFile(self):
        if path.exists(self.datafile) != True: #only works if datafile not yet created
            data = subprocess.Popen(['softwareupdate', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout,stderr = data.communicate()
            print stdout
            f = open(self.datafile, 'wb')
            f.write(stdout)
            f.close()
        else:
            print("data file already exists we will not waste time re-checking update status")            

    def updatesAvailable(self):
        f = open(self.datafile, 'r')
        stdout = f.readlines()
        stdout = '#'.join(stdout)
        if "restart" in stdout:
        #    print('<result>true</result>')
            return True
        else:
            print('<result>false</result>')
            return False
            


def runJob(*args):
        commands = []
        for t in args:
            commands.append(t)
        data = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = data.communicate()
        print(stdout)

def main():
    l = lookForUpdates() #instanciate class
    l.createDataFile()
    l.updatesAvailable()
    if adminRightsAchieved and l.updatesAvailable:
        p = popupWindow()
        p = p.fireWindow(p.buildWindow(
            'hud',
            FIRSTPOPTITLE,
            'Update Required',
            FIRSTPOP,
            '-button1',
            FIRSTPOPBTN
        ))
    try:
        SECONDPOP
    except NameError: SECONDPOP = None
    if SECONDPOP is None and adminRightsAchieved:
        print 'do stuff'
        runJob('open', '-a', 'Google Chrome')
    if SECONDPOP and adminRightsAchieved and l.updatesAvailable and p:
        u = popupWindow() #2nd chance window
        u = u.fireWindow(u.buildWindow(
            'hud', 
            'Countdown Started', 
            'Restart Pending', 
            SECONDPOP,
            '-button1', #user clicks 1
            'Proceed', 
            '-button2', #user clicks 2
            'Postpone', 
            '-countdown', 
            '-timeout', 
            '30'
        ))
    if SECONDPOP and adminRightsAchieved and l.updatesAvailable and p and u:
        if TESTINGMODE:
            print('testing mode just doing a thing...')
            runJob('softwareupdate', '-l')
        else:
            #u.runJob('jamf', 'policy', '-event', 'doUpdates')
            runJob('softwareupdate', '-iRa')

if __name__ == "__main__":
#    buildPromptVars(typeOneWindow)
    main()
