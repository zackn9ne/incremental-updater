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
LOGO_PATH = './jumbo.png'
RUN_SILENTLY = True
#first
FIRST_POP_TITLE = 'unsupported macOS Version'
FIRST_POP_BAR = 'Update Required'
FIRST_POP = '''Your macOS needs security updates.

Press the Update button below, you will have one more screen to confirm before this runs.'''
FIRST_POP_BTN = 'Update'
#success
OK_POP_TITLE = 'macOS is Secure'
OK_POP_BAR = 'Good job'
OK_POP = "Congratulations you're up to date, thanks for clicking."
OK_POP_BTN = 'FLEX MODE'
#second
SECOND_POP = 'Save your work because unless you press Postpone, your updates will begin in {} seconds...'.format(TIME)

class MinorUpdate():
    # build class
    def __init__(self):
        self.binary = '/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper'
        self.datafile = '/tmp/jumboupdater.log'
    
    def simple_messaging(self, verb, noun):
        print(verb, noun)
    
    def icons(self):
        if LOGO_PATH:
            try:
                open(LOGO_PATH)
                self.icon = "{}".format(LOGO_PATH)  #icon failover business   
            except IOError:
                print("404 icon not found")
                self.icon = "/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns"        
 
    def build_window(self, windowStyle, heading, title, message, *args):
        window = [
            self.binary,
            "-windowType",
            windowStyle, #hud #utility #fullscreen
            "-heading",
            heading,
            "-title",
            title,
            "-description",
            message,
            "-icon",
            self.icon,
            "-defaultbutton", #action button
            "1",
        ]
        for ar in args:
            window.append(ar)
        return window

    def fire_window(self, popup_type): #feed me a build_window()
        self.proc = subprocess.Popen(popup_type, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out, self.err = self.proc.communicate()
        self.result = self.proc.returncode
        return self.result

    def handle_window_result(self, result, mode):
        print "User clicks: {}, computer status was {}".format(result, mode)

        if isinstance(result, int):
            return result
        else:
            print("Error: %s" % result)
            return result

    def does_data_file_exist(self):
        if path.exists(self.datafile):
            return True
    
    def write_machine_status(self):
        data = subprocess.Popen(['softwareupdate', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = data.communicate()
        self.simple_messaging("writing", self.datafile)            
        f = open(self.datafile, 'wb')
        f.write(stdout)
        f.close()
  
    def read_machine_status(self):
        self.simple_messaging("reading", self.datafile)
        f = open(self.datafile, 'r')
        raw_file_contents = f.readlines()
        file_contents = '#'.join(raw_file_contents)
        print file_contents
        if "restart" in file_contents:
        #    print('<result>true</result>')
            return True
        else:
            print('<result>false</result>')
            return False

    # def do_updates(self):
    #     if self.read_machine_status():
    #         return True

    def run_shell_CMD(self, *args):
        commands = []
        for t in args:
            commands.append(t)
        data = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = data.communicate()
        print(stdout)

    def main(self):
        """main here"""
        self.icons() #always
        self.does_data_file_exist() #always
        self.first = self.build_window(
                'hud',
                FIRST_POP_TITLE,
                FIRST_POP_BAR,
                FIRST_POP,
                '-button1',
                FIRST_POP_BTN
            )        
        self.second = self.build_window(
                'hud', 
                'Countdown Started', 
                'Restart Pending', 
                SECOND_POP,
                '-button1', #user clicks 0 things happen
                'Proceed', 
                '-button2', #user clicks 2 things don't happen
                'Postpone', 
                '-countdown', 
                '-timeout', 
                TIME
            )
        self.ok = self.build_window(
            'hud',
            OK_POP_TITLE,
            OK_POP_BAR,
            OK_POP,
            '-button1', #user clicks 0
            OK_POP_BTN
        )
        self.update_required = ''

        if not self.does_data_file_exist():
            self.write_machine_status()

        if self.read_machine_status():
            self.update_required = 'True'

        if self.update_required and self.handle_window_result(self.fire_window(self.first), "updates needed") is 0:
            print "user agrees"
            #self.handle_window_result(self.fire_window(self.second), "updates needed")

            if self.update_required and self.handle_window_result(self.fire_window(self.second), "updates needed") is 0:
                print "user wants to really do stuff or timer expired forcing said stuff"
                self.run_shell_CMD("softwareupdate", "-l")
            else:
                print "user bailed at second windwo"
        if not self.update_required and RUN_SILENTLY:
            print "computer is fine RUN_SILENTLY: {}, was enabeled".format(RUN_SILENTLY)
        if not self.update_required and not RUN_SILENTLY:
            #self.fire_window(self.ok) #todo handle_window_result button clicke for this mode
            self.handle_window_result(self.fire_window(self.ok), "celebrating that computer is fine")




if __name__ == "__main__":
#    buildPromptVars(typeOneWindow)
    MinorUpdate().main()