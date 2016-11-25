__author__ = 'MMahdy'
########################################################################################################################
######################This project aims to ease the extraction of zones, ###############################################
######################################### interfacesrelated to certain IPs from SRX ####################################
########################################################################################################################
#Import list
import paramiko
import csv
import getpass
from threading import Thread


###################################################################################################################
################### Functions creation################################
####################################################################################################################
def Interface(k):
        datain, dataout, dataerr = SRX.exec_command('show route forwarding-table matching ' + k + ' extensive | match "Next-hop interface" | trim 22')
        return(dataout.read())

def Zone(y):
    datain, dataout, dataerr = SRX.exec_command("show interface " + y + " | match zone | trim 20 ")
    return(dataout.read())



##Function used to handle the device related info
def SRXinfoextract(x):
    SourceIP = x
    SourceInterface = Interface(x)
    if SourceInterface.strip()=="" :
        print "Interface:"+"Null"+"\r\n"+"Zone:"+"Null"+"\r\n"
    else:
        SourceZone = Zone(SourceInterface)
        print "Interface:"+SourceInterface+"Zone:"+SourceZone+"\r\n"


   
## Connection function
def fwconnect(l):
        SRX.connect(l, username=UN, password=PWD)
        print l
        SRXinfoextract(ip)
        SRX.close()
########################********************#############################**************###############################
########################################Program ********************* Program ########################################
########################********************#############################**************###############################

Check = 'Y'
ip = raw_input("Please enter the IP you want to check: ")
UN = raw_input("Please enter the user name: ")
PWD = getpass.getpass("Please enter the password: ")
firewalls_list = raw_input("Please enter the file containing your firewalls: ")
file = open(firewalls_list,"r")
IP_LIST = file.readlines()
IP_LIST = map(lambda s: s.strip(), IP_LIST)
global SRX

while Check == "Y":
        ip = raw_input("Please enter the IP you want to check: ")
        SRX = paramiko.SSHClient()
        SRX.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for l in IP_LIST:
                th1 = Thread(target=fwconnect, args=(l,))
                th1.start()
                time.sleep(4)   ## This sleep to leave time for ssh communication
                                        ##if the delay is high in your network you can increase this sleep time
        Check = raw_input("Do you want to check any other addresses(Y or N): ")
