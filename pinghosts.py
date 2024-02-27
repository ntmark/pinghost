#!/usr/bin/env python
# ping a list of host IPs read from file separated by new line
# created 2023/02/03 Mark.potter@tvnz.co.nz


import os
import sys
import platform
import subprocess
import argparse
import concurrent.futures

textfile = 'hosts.txt'


# checks version of python, v2 not supported.
def checkVersion():
        myVersion = int(platform.python_version().split(".")[0])
        if myVersion <= 2:
                print("Python Version {0} is not supported".format(myVersion))
                exit()
        if myVersion >= 3:
                print("running")



# reads in text file with list of IPs/hostname to ping
def readfil(textfile):
    try:
        # checks if file exists
        with open(textfile, "r") as text_file:
            #import pdb;pdb.set_trace()
            fh = text_file.read()
            # read each line of file and put dict into list
            endPoints = fh.split("\n")
            #print(endPoints)
            for item in endPoints:
                if item.strip() == '':
                    endPoints.remove(item)
                    continue
                if item[0] == "#":
                    endPoints.remove(item)
                    continue
                if len(item) == 0:
                    endPoints.remove(item)
                    continue

            # log if all read ok

        print('File read OK')
        print("Loaded {} host IPs".format(len(endPoints)))
        #print(endPoints)
        return(endPoints)

    except OSError as e:
        #print(f'Failed to open file {textfile}')
        print('{0}'.format(e))
        parser.print_help()
        sys.exit()
    except:
        print('Unknown error')
        parser.print_help()
        sys.exit()


# ping host ip for multi thread process pingHosts(list)
def pingHost(ip):
    try:
        response = subprocess.check_output(
                ['ping', '-c', '1', ip],
                stderr=subprocess.STDOUT,
                universal_newlines=True
        )
    except subprocess.CalledProcessError:
        response = None
    if response != None:
        # return up if connection is up
        return 'up'
    else:
        return 'down'


# multithread ping, supply list, appends (host,status) to data
def pingHosts(iplist):
    # update max_threads for max threads used in threadding spawns
    max_threads = 30
    data = list()

    # some magic from https://docs.python.org/3/library/concurrent.futures.html
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_ping = {executor.submit(pingHost,host): host for host in iplist}
        for future in concurrent.futures.as_completed(future_to_ping):
            host = future_to_ping[future]
            try:
                data.append((future_to_ping[future],future.result()))
            except Exception as exc:
                return None

    return data


# old pinghosts. not used 2024/02/22 MP
def pinghosts(iplist):
    '''Takes in list of hostnames/IPs terminated by new line
    returns list of tuples, hostname+ [up | down]'''

    # for each item in list go through and ping it and print outcome
    uphosts = 0
    results = list()
    for host in iplist:
        # print(host) # debug
        try:
            response = subprocess.check_output(
                ['ping', '-c', '1', '-w', '1', host],
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
        except subprocess.CalledProcessError:
            response = None

        if response != None:
            results.append((host,'up'))
            uphosts += 1
        else:
            results.append((host,'down'))
    return(results)


# display results
def displayOutput(pingResults,display=False):
    '''print out restuls displayOutput(<list of tuples>,output format)'''
    count = 0
    #import pdb;pdb.set_trace()
    for host in pingResults:
        if display:
            print(f"{host[0]},{host[1]}")
            if host[1] == "up":
                count +=1
        else:
            spaces = 16 - len(host[0])
            print(f"{host[0]}"," "*spaces,f"is {host[1]}")
            if host[1] == "up":
                count +=1

    print(f"{count}/{len(pingResults)} hosts are up")


if __name__ == "__main__":
    checkVersion()

    # setup argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
            description=('''\
example hosts.txt file:
    localhost
    127.0.0.1
    myhostname.mydomain'''))
    parser.add_argument("-f", help="filename with list of IPs: default file = hosts.txt")
    parser.add_argument("-d", action='store_true', help="Display input file data")
    parser.add_argument("-c", action='store_true', help="CSV output to screen")
    args = parser.parse_args()

    # pick which file to load
    if args.f:
        filedata = readfil(args.f)
    else:
        filedata = readfil(textfile)
    if args.d:
        print(filedata)

    # ping hosts
    try:
        #Results = pinghosts(filedata)
        Results = pingHosts(filedata)
        if args.c:
            display = True
        else:
            display = False
        displayOutput(pingResults=Results,display=display)

    except KeyboardInterrupt:
        # quit if escaped
        sys.exit()
