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
##Check interfaces
def Interface(x):
    datain, dataout, dataerr = SRX.exec_command(
        'show route forwarding-table matching ' + x + ' extensive | match "Next-hop interface" | trim 22')
    intf = dataout.read()
    return(intf)

##Zone info for zones at the internal side (Services side)requires IP as input
def Zone(y):
    datain, dataout, dataerr = SRX.exec_command("show interface " + y + " | match zone | trim 20 ")
    zonetmp = dataout.read()
    zonetmp = zonetmp[:zonetmp.index('\n')]
    return(zonetmp)

##provide logical system and interface requires IP as input
def RoutingTable(x):
    datain, dataout1, dataerr = SRX.exec_command(
        "show route forwarding-table matching " + x + " extensive ")
    intf = dataout1.readlines()
    for i in intf:
        if "Destination" in i:
            index= intf.index(i)
            index1 = index -3

    Rinsttemp = intf[index1]
    temp =  Rinsttemp[Rinsttemp.index(': '):Rinsttemp.index('.inet')]
    Rinst = temp[temp.index(' '):]
    return(Rinst)


##Function used to handle the device related info, requires (Input file, output file, Username, password, device IP)
def SRXinfoextract(x):
    SourceIP =[]
    SourceInterface = []
    SourceZone = []
    RoutingInstance = []
    sint = Interface(x)
    SourceInterface.append(sint)
    rt = RoutingTable(x)
    RoutingInstance.append(rt)
    SourceIP.append(x)
    for sinf in SourceInterface:
        Szone = Zone(sinf)
        SourceZone.append(Szone)

    data = [SourceIP,"\t", SourceInterface, "\t", SourceZone,"\t", RoutingInstance]

    return(data)
########################********************#############################**************###############################
########################################Program ********************* Program ########################################
########################********************#############################**************###############################

Check = 'Y'
ip = raw_input("Please enter the IP you want to check: ")
UN = raw_input("Please enter the user name: ")
PWD = getpass.getpass("Please enter the password: ")
IP_LIST = ["10.7.37.140","10.7.37.188","10.7.38.108","10.7.37.228","10.7.37.196","10.7.38.132","10.7.37.252"]


def fwconnect(l):
    SRX = paramiko.SSHClient()
    SRX.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SRX.connect(l, username=UN, password=PWD)
    srx_info = SRXinfoextract(ip)
    SRX.close()
    print l
    print srx_info


for l in IP_LIST:
    th1 = Thread(target=fwconnect, args=(l,))
    th1.start()
