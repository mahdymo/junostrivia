__author__ = 'MMahdy'
########################################################################################################################
######################This project aims to ease the extraction of zones, ###############################################
######################################### interfacesrelated to certain IPs from SRX with Logical system enabled#########
########################################################################################################################
#Import list
import paramiko
import csv
import pyexcel as pe

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

##Logical system information requires IP as input
def LSYS(x):
    index = 0
    index1 = 0
    datain, dataout1, dataerr = SRX.exec_command(
        "show route forwarding-table matching " + x + " extensive ")
    intf = dataout1.readlines()
    for i in intf:
        if "Destination" in i:
            index = intf.index(i)
        index1 = index - 4

    LSYStemp = intf[index1]
    temp =  LSYStemp[LSYStemp.index(': '):]
    LSYS = temp[temp.index(' '):]
    return (LSYS)

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

##Checking the external interfaces (out towards PE side) requires (Logical system, routing instance, IP)
def ExternalIntf(x,y,z):
    datain, dataout, dataerr = SRX.exec_command("show route logical-system " + x + " table " + y +" " +z +
                                                " | match via | trim 40")
    Exint = dataout.read()
    Exint = Exint[Exint.index(' '):Exint.index('\n')]
    return(Exint)
##Function used to handle the device related info, requires (Input file, output file, Username, password, device IP)
def SRXinfoextract(file,Ofile):
    SourceIP = []
    DestinationIP = []
    i = 0
    SourceInterface = []
    SourceZone = []
    LogicalSystem = []
    RoutingInstance = []
    DestinationInterface = []
    DestinationZone = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            SourceIP.append(row[0])
            DestinationIP.append(row[1])

    while i < len(SourceIP):
        Sintf = Interface(SourceIP[i])
        if Sintf.find('reth') != -1:
            SourceInterface.append(Sintf)
            lsys = LSYS(SourceIP[i])
            LogicalSystem.append(lsys)
            rt = RoutingTable(SourceIP[i])
            RoutingInstance.append(rt)
        else:
            lsys = LSYS(DestinationIP[i])
            LogicalSystem.append(i)
            rt = RoutingTable(DestinationIP[i])
            RoutingInstance.append(rt)
            eXInterface = ExternalIntf(lsys, rt, SourceIP[i])
            SourceInterface.append(eXInterface)
        i += 1
    i = 0
    print SourceIP
    while i < len(DestinationIP):
        Dintf = Interface(DestinationIP[i])
        if Dintf.find('reth') != -1:
            DestinationInterface.append(Dintf)
            rt = RoutingTable(DestinationIP[i])
            RoutingInstance.append(rt)
        else:
            lsys = LSYS(SourceIP[i])
            rt = RoutingTable(SourceIP[i])
            RoutingInstance.append(rt)
            eXInterface = ExternalIntf(lsys, rt, DestinationIP[i])
            DestinationInterface.append(eXInterface)
        i += 1
    print DestinationIP

    for Sintf in SourceInterface:
        Szone = Zone(Sintf)
        SourceZone.append(Szone)
    print SourceZone
    for Dintf in DestinationInterface:
        Dzone = Zone(Dintf)
        DestinationZone.append(Dzone)
    print DestinationZone
    data = [SourceZone, SourceIP, SourceInterface, DestinationZone, DestinationIP, DestinationInterface, LogicalSystem, RoutingInstance]
    print data
    Transdata = zip(*data)
    print Transdata
    sheet = pe.Sheet(Transdata)
    print sheet
    sheet.save_as(Ofile)
    return(Ofile)
########################********************#############################**************###############################
########################################Program ********************* Program ########################################
########################********************#############################**************###############################

Check = 'Y'
file = raw_input("Please enter the source file containing the source and destination IPs: ")
Ofile = raw_input("Please enter the Destination file to send the output: ")
UN = raw_input("Please enter the user name: ")
PWD = raw_input("Please enter the password: ")
while Check =='Y':
    IP = raw_input("Please enter the Firewall IP to be checked: ")
    print "Connecting..."
    SRX = paramiko.SSHClient()
    SRX.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SRX.connect(IP, username=UN, password=PWD)
    print "Connected"
    print "Process in progress it may take few minutes..."
    SRXLSYSinfo = SRXinfoextract(file,Ofile)
    print "Process completed please check the output file location!"
    Check = raw_input("Check another Firewall (Y or N): ")
SRX.close()
