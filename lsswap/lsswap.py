#!/usr/bin/python

#    Copyright 2014 Jonathan Gonzalez V <jonathan.abdiel@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import subprocess
import sys
import os
import re
import getopt
import collections
from prettytable import PrettyTable

# Dev utils
# import pprint
# pp = pprint.PrettyPrinter(indent=4)


def usage():
    print """This command must be run as root
Usage:

-h		Print this message
--order-by	It takes one of the values: swap or name
"""


def size_suffix(bytes):
    convertion = [
        (1024 ** 5, 'P'),
        (1024 ** 4, 'T'),
        (1024 ** 3, 'G'),
        (1024 ** 2, 'M'),
        (1024 ** 1, 'K'),
        (1024 ** 0, 'B'),
        ]

    bytes = int(bytes)
    for factor, suffix in convertion:
        if bytes >= factor:
            break

    total = bytes / factor

    return str(total) + suffix


def run_cmd(cmd=""):

    if cmd is "":
        return 1

    if sys.version_info >= (2, 7):
        cont = subprocess.check_output(cmd,
                                       shell=True,
                                       stderr=None)
    else:
        p = subprocess.Popen(cmd,
                             shell=True,
                             stderr=None,
                             stdout=subprocess.PIPE)
        cont = p.stdout.readline()

    return cont


def get_data(by_name=True):
    regex_pid = re.compile("\d+")

    proc_files = os.listdir("/proc/")
    p_pid = {}
    p_name = {}

    for p_dir in proc_files:
        if re.match(regex_pid, p_dir) is None:
            continue

        try:
            cont = run_cmd("grep Name /proc/" +
                           p_dir +
                           "/status")

            proc_name = cont.split()[1]

            p_sum = run_cmd("grep 'Swap' /proc/" +
                            p_dir +
                            "/smaps 2> /dev/null | " +
                            "awk 'BEGIN{s=0}{s+=$2}END{print s}'")
            p_sum = int(p_sum) * 1024

        except Exception as ex:
            print ex
            continue

        if p_sum > 0:
            p_pid[p_dir] = {}
            p_pid[p_dir]["name"] = p_name
            p_pid[p_dir]["swap_used"] = p_sum
            p_pid[p_dir]["swap_hr"] = size_suffix(p_sum)

            if proc_name in p_name:
                p_name[proc_name]["swap"] += p_sum
            else:
                p_name[proc_name] = {}
                p_name[proc_name]["swap"] = p_sum

                p_name[proc_name]["swap_hr"] = size_suffix(
                    p_name[proc_name]["swap"])

    if by_name:
        return p_name
    else:
        return p_pid


def print_simple(procs=None):

    if procs is None:
        return None

    table = PrettyTable(["CMD", "Swap"])
    table.align["CMD"] = "l"
    table.align["Swap"] = "r"

    for proc in procs:
        table.add_row([
            proc,
            procs[proc]["swap_hr"]])

    print table


def order_procs(procs=None, order="s"):
    if procs is None:
        return None

    procs_o = {}
    if order in ("s", "swap"):
        procs_o = collections.OrderedDict(sorted(procs.items(),
                                                 key=lambda t: t[1]['swap']))
    elif order in ("n", "name"):
        procs_o = collections.OrderedDict(sorted(procs.items(),
                                                 key=lambda t: t[0]))

    return procs_o


def lswap_main():

    opts, args = getopt.getopt(sys.argv[1:], "h",
                               ["help",
                                "h",
                                "order-by="])

    by_name = True
    order_by = "s"

    for opt, arg in opts:
        if opt in ("--h", "-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("--order-by"):
            order_by = arg

    procs = get_data(by_name)

    procs_ordered = order_procs(procs, order_by)

    print_simple(procs_ordered)


if __name__ == "__main__":
    lswap_main()
