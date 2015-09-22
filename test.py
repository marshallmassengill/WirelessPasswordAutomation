#!/usr/bin/python

import pexpect
import sys
#import pxssh

wlc = '10.15.10.91'
username = 'tfxscript'
passGen = 'setmetosomethingnew'
password = '5133pD@T@5133p'

#test = pexpect.spawn('ssh '+wlc)
#if (test.expect('.*Are you sure you want to continue connecting.*')):
#  test.sendline('yes')
#out = open('wlc' + wlc + '.txt', 'wb')
#test.logfile = fout
timeoutItterator = 0

while timeoutItterator <= 3:
  try: 
    test = pexpect.spawn('ssh '+wlc)
    fout = open('wlc' + wlc + '.txt', 'wb')
    test.logfile = fout
    newkeyMessage = '.*Are you sure you want to continue connecting.*'
    i = test.expect([newkeyMessage,'.*User:.*'])
    if i==0:
      test.sendline('yes')
      i = test.expect([newkeyMessage,'.*User:.*'])
    if i==1:
      test.sendline(username)
      test.expect('.*Passwrd:')
      test.sendline(password)
      test.expect('.*>')
      test.sendline('config wlan disable 2')
      test.expect('.*>')
      test.sendline('config wlan security wpa akm psk set-key ascii ' + passGen  + ' 2')
      test.expect('.*>')
      test.sendline('config wlan enable 2')
      test.expect('.*>')
      test.sendline('save config')
      test.expect('.*Are you sure you want to save?.*')
      test.sendline('y')
      test.expect('.*Configuration Saved.*>')
      test.sendline('logout')
      print 'Great Success'
      break
    elif i==2:
      #log something about a random error
      print 'How did you end up here?'
  except (pexpect.TIMEOUT or pexpect.EOF):
    test.close()
    timeoutItterator+=1
    print 'Timeout Error2'

#Logging
#test.logfile = sys.stdout

