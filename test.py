#!/usr/bin/python

import pexpect
import sys
#import pxssh

wlc = '10.15.10.91'
username = 'tfxscript'
passGen = 'setmetosomethingnew'
password = '5133pD@T@5133p'

test = pexpect.spawn('ssh '+wlc)
#if (test.expect('.*Are you sure you want to continue connecting.*')):
#  test.sendline('yes')

#Logging
#test.logfile = sys.stdout

test.expect('.*User:.*')
test.sendline(username)
test.expect('.*Password:.*')
test.sendline(password)
test.expect('.*>.*')
test.sendline('config wlan disable 2')
test.expect('.*>.*')
test.sendline('config wlan security wpa akm psk set-key ascii ' + passGen  + ' 2')
test.expect('.*>.*')
test.sendline('config wlan enable 2')
test.expect('.*>.*')
test.sendline('save config')
test.expect('.*Are you sure you want to save?.*')
test.sendline('y')
test.expect('.*>.*')
test.sendline('logout')

print 'Great Success'

