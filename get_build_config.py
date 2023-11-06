#!/usr/bin/env python3

import json
import sys

gn_sln = [
    { "name"        : "v8",
        "url"         : "https://chromium.googlesource.com/v8/v8.git",
        "deps_file"   : "DEPS",
        "managed"     : False,
        "custom_deps" : {
            # These deps are unnecessary for building.
            "v8/testing/gmock"                      : None,
            "v8/test/wasm-js"                       : None,
            "v8/third_party/android_tools"          : None,
            "v8/third_party/catapult"               : None,
            "v8/third_party/colorama/src"           : None,
            "v8/tools/gyp"                          : None,
            "v8/tools/luci-go"                      : None,
        },
        "custom_vars": {
            "build_for_node" : True,
        },
    },
]

gn_args = """
is_debug=false
is_clang=true
target_cpu="%s"
v8_target_cpu="%s"
clang_use_chrome_plugins=false
use_custom_libcxx=false
symbol_level=0
strip_debug_info=true
is_component_build=false
v8_monolithic=true
v8_use_external_startup_data=false
treat_warnings_as_errors=false
v8_enable_gdbjit=false
v8_enable_i18n_support=true
icu_use_data_file=false
v8_enable_test_features=false
exclude_unwind_tables=true
"""

def main():
	print(json.dumps({"status": "ok", "spec": "solutions = %s" % gn_sln, "args": (gn_args % (sys.argv[1], sys.argv[1])).replace('\n', ' ').strip()}))

if __name__ == "__main__":
    main()
