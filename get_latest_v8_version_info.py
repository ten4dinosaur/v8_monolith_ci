#!/usr/bin/env python3

import urllib.request
import json
import os
import sys
import base64
import re

known_arguments = {
    "platform": {
        "android": "Android",
        "ios": "iOS",
        "unix": "Linux",
        "mac": "Mac",
        "win": "Windows",
    },
    "channel": {
        "extended": "Extended",
        "stable": "Stable",
        "beta": "Beta",
        "dev": "Dev",
        "canary": "Canary",
    },
}

def get_chromium_commit(platform, channel):
    try:
        response = urllib.request.urlopen(f"https://chromiumdash.appspot.com/fetch_releases?channel={channel}&platform={platform}&num=1")
        release = json.loads(response.read().decode('utf-8'))[0]
        return release['hashes']['chromium']
    except Exception as exception:
        print(json.dumps({"status": "error", "method": f'{get_chromium_commit=}'.partition('=')[0], "message": str(exception)}))
        return None

def get_v8_and_tools_commits(chromium_commit):
    try:
        response = urllib.request.urlopen(f"https://chromium.googlesource.com/chromium/src/+/{chromium_commit}/DEPS?format=TEXT")
        chromium_deps = base64.b64decode(response.read()).decode('utf-8');
        return re.search(r"\s*?['\"]v8_revision\s*?['\"]\s*?:.*?(['\"]([a-f0-9]{40})['\"])", chromium_deps, re.DOTALL).group(2), re.search(r"\s*?['\"]src[\/\\]third_party[\/\\]depot_tools['\"]\s*?:.*?(['\"]([a-f0-9]{40})['\"])", chromium_deps, re.DOTALL).group(2)
    except Exception as exception:
        print(json.dumps({"status": "error", "method": f'{get_v8_and_tools_commits=}'.partition('=')[0], "message": str(exception)}))
        return None

def validate_commit_hash(commit_hash):
    return isinstance(commit_hash, str) and len(commit_hash) == 40

def main():
    chromium_commit = get_chromium_commit(known_arguments["platform"][sys.argv[1]], known_arguments["channel"][sys.argv[2]])
    if validate_commit_hash(chromium_commit):
        v8_commit, tools_commit = get_v8_and_tools_commits(chromium_commit)
        if validate_commit_hash(v8_commit) and validate_commit_hash(tools_commit):
            print(json.dumps({"status": "ok", "v8_commit": v8_commit, "tools_commit": tools_commit}))
            return None
        print(json.dumps({"status": "error", "method": f'{main=}'.partition('=')[0], "message": "Commit hash invalid"}))

if __name__ == "__main__":
    main()
