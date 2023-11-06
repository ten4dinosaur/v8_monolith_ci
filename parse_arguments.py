#!/usr/bin/env python3

import urllib.request
import json
import os
import sys
import base64
import re

arguments=["platform", "architecture", "channel"]
platforms=["android", "ios", "unix", "mac", "win"]
architectures=["arm", "arm64", "mips", "mips64", "ppc", "s390", "x86", "x64"]
channels=["extended", "stable", "beta", "dev", "canary"]

def main():
    message=""
    parsed={}
    arguments_count=len(sys.argv)-1
    for i in range(1, 4):
        argument_name=arguments[i-1]
        argument_values=eval(argument_name+"s")
        if arguments_count < i or sys.argv[i] == "":
            message=message + f'Argument "{argument_name}"[{i}]. Value is empty/unexistent. Must be one of: [{", ".join(argument_values)}]' + "\n"
        else:
            argument=sys.argv[i].lower()
            if not argument in argument_values:
                message=message + f'Argument "{argument_name}"[{i}]. Value "{argument}" is unknown. Must be one of: [{", ".join(argument_values)}]' + "\n"
            else:
                parsed[argument_name]=argument
    if message == "":
        parsed["status"]="ok"
        print(json.dumps(parsed))
    else:
        print(json.dumps({"status": "error", "method": f'{main=}'.partition('=')[0], "message":message}))

if __name__ == "__main__":
    main()
