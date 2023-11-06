#!/usr/bin/env python3

import re

def get_version_info_by_name(version_file_content, name):
    return re.search(f'^#define V8_{name.upper()}.*?(\d+).*?$', version_file_content, re.MULTILINE).groups(1)[0]

def get_version_string(version_file):
    with open(version_file) as f:
        version_file_content = f.read()
    version_array = [];
    for name in ["major_version", "minor_version", "build_number", "patch_level"]:
        version_array.append(get_version_info_by_name(version_file_content, name))
    return ".".join(version_array) + ("" if get_version_info_by_name(version_file_content, "is_candidate_version") == "0" else " (candidate)")

def main():
    print(get_version_string("./v8/include/v8-version.h"))

if __name__ == "__main__":
    main()
