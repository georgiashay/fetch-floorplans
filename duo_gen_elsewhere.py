#!/usr/bin/env python3
# These should be the contents of duo_gen within the duo path

import pyotp
import sys
import os

dirname = os.path.dirname(__file__)
tokenfile = os.path.join(dirname, 'duotoken.hotp')

def generate_next_token(savefile=tokenfile):
    f = open(savefile, "r+")
    secret = f.readline()[0:-1]
    offset = f.tell()
    count = int(f.readline())
    
    hotp = pyotp.HOTP(secret)
    
    f.seek(offset)
    f.write(str(count + 1))
    f.close()
    
    return hotp.at(count)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        file = sys.argv[1]
    else:
        file = tokenfile
        
    print(generate_next_token(file))