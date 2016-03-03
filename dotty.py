#!/usr/bin/env python

# Copyright (C) 2015 Vibhav Pant <vibhavp@gmail.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import print_function
import json
import os
import shutil
from sys import stderr, version_info
import argparse
try:
    import yaml
    YAML_IMPORTED = True
except ImportError:
    YAML_IMPORTED = False

if version_info[0] == 2:
    input = raw_input


def ask_user(prompt):
    valid = {"yes":True, 'y':True, '':True, "no":False, 'n':False}
    while True:
        print(prompt+" ",end="")
        choice = input().lower()
        if choice in valid:
            return valid[choice]
        else:
            print("Enter a correct choice.", file=stderr)


def create_directory(path):
    exp = os.path.expanduser(path)
    if (not os.path.isdir(exp)):
        print(exp+" doesnt exist, creating.")
        os.makedirs(exp)


def _create_symlink(src, dest, replace):
    dest = os.path.expanduser(dest)
    src = os.path.abspath(src)
    if os.path.exists(dest):
        if os.path.islink(dest) and os.readlink(dest) == src:
            print("Skipping existing {0} -> {1}".format(dest, src))
            return
        elif replace or ask_user(dest+" exists, delete it? [Y/n]"):
            if os.path.isfile(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        else:
            return
    print("Linking {0} -> {1}".format(dest, src))
    os.symlink(src, dest)


def create_symlink(src, dest, replace):
    if isinstance(dest, list):
        for item in dest:
            _create_symlink(src, item, replace)
    else:
        _create_symlink(src, dest, replace)


def copy_path(src, dest):
    dest = os.path.expanduser(dest)
    src = os.path.abspath(src)
    if os.path.exists(dest):
        if ask_user(dest+ " exists, delete it? [Y/n]"):
            if os.path.isfile(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        else:
            return
    print("Copying {0} -> {1}".format(src, dest))
    shutil.copy(src, dest)


def run_command(command):
    os.system(command)


def load_config(config_file):
    with open(config_file) as f:
        _, ext = os.path.splitext(config_file)
        if ext in [".js"]:
            return json.load(f)
        elif YAML_IMPORTED and ext in [".yml", ".yaml"]:
            return yaml.load(f)
        raise ValueError("Unknown config format")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="the JSON file you want to use")
    parser.add_argument("-r", "--replace", action="store_true",
                        help="replace files/folders if they already exist")
    args = parser.parse_args()
    js = load_config(args.config)
    os.chdir(os.path.expanduser(os.path.abspath(os.path.dirname(args.config))))

    directories = js.get("directories")
    links = js.get("link")
    copy = js.get("copy")
    commands = js.get("commands")
    pacman = js.get("pacman")
    apt = js.get("apt")

    # if directories: [create_directory(path) for path in directories]

    if links: [create_symlink(src, links[src], args.replace) for src in links]

    # if copy: [copy_path(src, copy[src]) for src in copy]

    # if commands: [run_command(command) for command in commands]

    # if pacman:
    #     packages = " ".join(pacman)
    #     run_command("sudo pacman -S "+packages)

    # if apt:
    #     packages = " ".join(apt)
    #     run_command("sudo apt-get install "+packages)

    print("Done!")

if __name__ == "__main__":
    main()
