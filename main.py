#!/usr/bin/python
#Teleflex Visitor Wireless Password Key Configuration

###############################################################################
#Import Libraries
###############################################################################
import sys
import time
import syslog
import subprocess
import pexpect

###############################################################################
#Declare Variables
###############################################################################
wlcFile = 'wlc_list.txt'
aapFile = 'aap_list.txt'
logdir = "./logs/"
alertScript = "./alert.sh"
passwordFile = 'current.shtml'
password = ''
timeoutIterator = 0
cliUsername = 'tfxscript'
cliPasswordFile = 'cliPass.txt'
cliPassword = ''

###############################################################################
#Declare Functions
###############################################################################

#Populate the List of Devices
def populateList(deviceFile):
  #Read in the file and strip newlines
  deviceList = [line.rstrip('\n') for line in open(deviceFile)]
  #Return the list
  return deviceList

#Get the password and return it
def getPassword(passwordFile):
  #Get the password
  with open (passwordFile, "r") as f:
    #Return it after trimming any newlines
    return f.read().replace('\n', '')

#Change the config of a Wireless LAN Controller (WLC)
def wlcConfig(wlcName):
  #Wrap the whole thing in a try/except block
  try:
    #Send the introduction stuff and connect to the system
    cli = pexpect.spawn('ssh ' + cliUsername + "@" + wlcName)
    #Establish a log file for each device
    logoutput = open(logdir + 'wlc' + wlcName + '.txt', 'wb')
    cli.logfile = logoutput
    newkeyMessage = '.*Are you sure you want to continue connecting.*'
    i = cli.expect([newkeyMessage,'.*User:.*'])
    #Deal with the new SSH key issue
    if i==0:
      cli.sendline('yes')
      i = cli.expect([newkeyMessage,'.*User:.*'])
    #Login and make the config changes
    elif i==1:
      cli.sendline(cliUsername)
      cli.expect('.*Password:')
      cli.sendline(cliPassword)
      cli.expect('.*>')
      cli.sendline('config wlan disable 2')
      cli.expect('.*>')
      cli.sendline('config wlan security wpa akm psk set-key ascii ' + password  + ' 2')
      cli.expect('.*>')
      cli.sendline('config wlan enable 2')
      cli.expect('.*>')
      cli.sendline('save config')
      cli.expect('.*Are you sure you want to save?.*')
      cli.sendline('y')
      cli.expect('.*Configuration Saved.*>')
      cli.sendline('logout')
      cli.close()
      return True
    #You shouldn't be here, log an error
    elif i==2:
      sendNotification("CRIT", "Script Error in wlcConfig")
  #Something timed out
  except (pexpect.TIMEOUT or pexpect.EOF):
    cli.close()
    return False

#Change the config of an Autonomous Access Point (AAP)
def aapConfig(aapName):
  #Wrap the whole thing in a try/except block
  try:
    #Send the introduction stuff and connect to the system
    cli = pexpect.spawn('ssh ' + cliUsername + "@" + aapName)
    #Establish a log file for each device
    logoutput = open(logdir + 'wlc' + aapName + '.txt', 'wb')
    cli.logfile = logoutput
    newkeyMessage = '.*Are you sure you want to continue connecting.*'
    i = cli.expect([newkeyMessage,'.*Password:.*'])
    #Deal with the new SSH key issue
    if i==0:
      cli.sendline('yes')
      i = cli.expect([newkeyMessage,'.*Password:.*'])
    #Login and make the config changes
    elif i==1:
      cli.sendline(cliPassword)
      cli.expect('.*#')
      cli.sendline('conf t')
      cli.expect('.*#')
      cli.sendline('!')
      cli.expect('.*#')
      cli.sendline('dot11 ssid Visitor')
      cli.expect('.*#')
      cli.sendline('wpa-psk ascii ' + password)
      cli.expect('.*#')
      cli.sendline('!')
      cli.expect('.*#')
      cli.sendline('end')
      cli.expect('.*#')
      cli.sendline('write mem')
      cli.expect('.*#')
      cli.sendline('quit')
      cli.close()
      return True
    #You shouldn't be here, log an error
    elif i==2:
      sendNotification("CRIT", "Script Error in aapConfig")
  #Something timed out
  except (pexpect.TIMEOUT or pexpect.EOF):
    cli.close()
    return False

#Send Notifications to Nagios and Syslog
def sendNotification(status, message):
  #Status should be OK, WARN, or CRIT
  if status == "OK":
    #Send OK to syslog
    syslog.syslog(syslog.LOG_NOTICE, message)
  elif status == "WARN":
    #Send WARN to syslog
    syslog.syslog(syslog.LOG_WARNING, message)
  elif status == "CRIT":
    #Send CRIT to syslog  
    syslog.syslog(syslog.LOG_CRIT, message)
  else:
    #Throw an error message and write to syslog
    message = "Script Error in sendNotification"
    syslog.syslog(syslog.LOG_CRIT, message)
  #Set the return code to the output of the alert script
  rc = subprocess.call([alertScript,status,"'" + message + "'"])
  return rc

#Device Configuration function
def deviceConfig(device):
  #Set the timeout value
  timeoutIterator = 0
  #Iterate while less than 3 tries
  while timeoutIterator < 3:
    #Run the configuration of the device
    out = wlcConfig(device)
    #If the device configuration was successful
    if out == True:
      #Send the notification that everything went well
      sendNotification("OK", "Everything went well for " + device)
      #Break the while loop
      break
    #If the device configuration failed
    elif out == False:
      #Iterate the iterator
      timeoutIterator+=1
      #Send the notification that something failed
      sendNotification("WARN", "The request timed out for device: " + device)
      #Sleep for 10 seconds
      time.sleep(10)
    #Something has gone horribly wrong
    else:
      sendNotification("CRIT", "Script Error on deivce: " + device)
  #Send a Critical error if it fails 3 times
  if (timeoutIterator == 3):
    sendNotification("CRIT", "The request timed out 3 times for deivce: " + device)
  return True

###############################################################################
#Main Loop
###############################################################################
if __name__ == "__main__":
  #Get the generated password and store it
  password = getPassword(passwordFile)
 
  #Get the cliPassword and store it
  cliPassword = getPassword(cliPasswordFile)  
 
  #Deal with the WLCs
  wlcDeviceList = populateList(wlcFile)
  for device in wlcDeviceList:
    deviceConfig(device)

  #Deal with the AAPs
  aapDeviceList = populateList(aapFile)
  for device in aapDeviceList:
    deviceConfig(device)


