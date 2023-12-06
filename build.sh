#!/usr/bin/env bash

get_json_field() {
    echo "$(printf "%s" "$(echo $1 | python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj["'$2'"])')")"
}

print_error() {
    IFS=$'\n' read -rd '' -a messages <<< "$4";
    echo "Error: $1"
    echo "Error method: $2 [$3]"
    for index in "${!messages[@]}"; do
        echo "Error message[$index]: ${messages[$index]}"
    done
}

parse_arguments_script="./parse_arguments.py"
get_version_script="./get_latest_v8_version_info.py"
get_build_config_script="./get_build_config.py"

parsed_arguments=$(printf "%s" "$(python3 $parse_arguments_script "$1" "$2" "$3")")
if [ $(get_json_field "$parsed_arguments" "status") == "error" ]; then
    print_error "Can't parse arguments" "$(get_json_field "$parsed_arguments" "method")" "$parse_arguments_script" "$(get_json_field "$parsed_arguments" "message")"
    exit 1
fi

platform=$(get_json_field "$parsed_arguments" "platform")
architecture=$(get_json_field "$parsed_arguments" "architecture")
channel=$(get_json_field "$parsed_arguments" "channel")

version_info=$(printf "%s" "$(python3 $get_version_script $platform $channel)")
if [ $(get_json_field "$version_info" "status") == "error" ]; then
    print_error "Can't get v8 and tools commit" "$(get_json_field "$version_info" "method")" "$get_version_script" "$(get_json_field "$version_info" "message")"
    exit 1
fi

last_v8_commit=$(head -n 1 "${platform}_${architecture}.hash" | xargs)
v8_commit=$(get_json_field "$version_info" "v8_commit")
tools_commit=$(get_json_field "$version_info" "tools_commit")

echo "Last build commit: $last_v8_commit"
echo "Current build commit: $v8_commit"
if [ "$last_v8_commit" == "$v8_commit" ]; then
    echo "true" > ./.skip_build
    exit 0
fi

echo "false" > ./.skip_build
echo $v8_commit > ./.commit_hash

git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
git -C ./depot_tools reset --hard $tools_commit
rm -rf ./depot_tools/.git

export DEPOT_TOOLS_WIN_TOOLCHAIN=0
PATH="$(pwd -P)/depot_tools:$PATH"

git clone https://chromium.googlesource.com/v8/v8.git
git -C ./v8 reset --hard $v8_commit

build_config=$(printf "%s" "$(python3 $get_build_config_script "$architecture")")
if [ $(get_json_field "$build_config" "status") == "error" ]; then
    print_error "Can't get v8 build config" "$(get_json_field "$build_config" "method")" "$get_build_config_script" "$(get_json_field "$build_config" "message")"
    exit 1
fi

gclient config --spec "$(get_json_field "$build_config" "spec")"
gclient sync

if [ "$platform" == "unix" ] && ( [ "$architecture" == "x86" ] || [ "$architecture" == "arm" ] ); then
    use_sysroot="false"
    ./v8/build/install-build-deps.sh --no-syms --lib32 --no-android --arm --no-chromeos-fonts --no-nacl --no-backwards-compatible --no-prompt
else
    use_sysroot="true"
    if [ "$platform" == "unix" ]; then
        python3 ./v8/build/linux/sysroot_scripts/install-sysroot.py --arch=$architecture || true
    fi
fi

if [ "$platform" == "win" ] && ( [ "$architecture" == "x64" ] || [ "$architecture" == "arm64" ] ); then
    patch -p1 < ./windows64_icu.patch
fi

gn gen out/Release --root=./v8 --args="$(get_json_field "$build_config" "args") use_sysroot=${use_sysroot}"
ninja -j 4 -C out/Release v8_monolith
