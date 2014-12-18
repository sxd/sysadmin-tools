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

import sys
import os
import re
import subprocess

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

regex_pid = re.compile("\d+")
regex_name = re.compile("^Name: .*")

proc_files = os.listdir("/proc/")
proc_pid = {}
proc_name = {}

for proc_dir in proc_files:
    if re.match(regex_pid, proc_dir) is not None:

        try: 
            if sys.version_info >= (2, 7):
                cont = subprocess.check_output("grep Name /proc/"+proc_dir+"/status",shell=True,stderr=None)

                pid_name = cont.split()[1]

                pid_sum = int(subprocess.check_output("grep 'Swap' /proc/"+proc_dir+"/smaps | awk 'BEGIN{sum=0}{sum+=$2}END{print sum}'",shell=True))
            else:
                pipe = subprocess.Popen("grep Name /proc/"+proc_dir+"/status",shell=True,stderr=None,stdout=subprocess.PIPE).stdout
                line = pipe.readline()
                
                pid_name = line.split()[1]

                pipe = subprocess.Popen("grep 'Swap' /proc/"+proc_dir+"/smaps | awk 'BEGIN{sum=0}{sum+=$2}END{print sum}'",shell=True,stderr=None,stdout=subprocess.PIPE).stdout
                line = pipe.readline()
                pid_sum = int(line)

        except Exception as ex:
            continue

        if pid_sum > 0 :
            proc_pid[proc_dir] = {}
            proc_pid[proc_dir]["name"] = pid_name
            proc_pid[proc_dir]["swap_used"] = pid_sum
            proc_pid[proc_dir]["swap_hr"] = size_suffix(pid_sum*1024)
            
            if proc_name.has_key(pid_name):
                proc_name[pid_name]["swap"] += pid_sum
            else:
                proc_name[pid_name] = {}
                proc_name[pid_name]["swap"] = pid_sum

            proc_name[pid_name]["swap_hr"] = size_suffix(proc_name[pid_name]["swap"]*1024)
            

for proc in proc_name:
    print "%s %s" % (proc, proc_name[proc]["swap_hr"])

#for proc in proc_pid:
#    print "%s %s %s" % (proc_pid[proc]["name"], proc, proc_pid[proc]["swap_hr"])

