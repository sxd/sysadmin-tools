#!/usr/bin/python

#    Copyright 2019 Jonathan Gonzalez V <jonathan.abdiel@gmail.com>
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
import getopt
from prettytable import PrettyTable

from linode_api4 import LinodeClient
from linode_api4.objects import DomainRecord


def usage():
    print("""Update/Create domain within your Linode account
You must create the API token in https://cloud.linode.com/profile/tokens

Usage:

-h		Print this message
--token		API Token from https://cloud.linode.com/profile/tokens
--domain	Domain name you want to update (A register)
""")


def dns_update_auth(token):
    client = LinodeClient(token)

    return client


def dns_get_domains(client):
    domains = client.domains()

    domain_list = dict()

    for domain in domains:
        for s in domain.records:
            domain_list[s.id] = {
                "id": s.id,
                "parent_id": s.domain_id,
                "name": s.name,
                "main_domain": domain.domain,
                "target": s.target,
                "type": s.type,
                "object": s
            }

    return domain_list


def dns_print_domains(domain_list):

    if domain_list is None:
        return None

    table = PrettyTable(["ID", "Domain", "Sub-Domain", "IP"])
    table.align["ID"] = "l"
    table.align["Domain"] = "l"
    table.align["Sub-Domain"] = "l"
    table.align["IP"] = "l"

    for d_id, data in domain_list.items():
        if data["name"] == "" or data["type"] not in ("A"):
            continue
        table.add_row([
            d_id,
            data["main_domain"],
            data["name"],
            data["target"],
        ])

    print(table)


def dns_update_domain_ip(domain, ip):
    domain._set("target", ip)

    rs = domain.save()

    return rs


def dns_update():

    opts, args = getopt.getopt(sys.argv[1:], "hgt:d:",
                               ["help",
                                "domain-id=",
                                "ip=",
                                "token=",
                                "get-domains="])

    token = None
    domain = None
    get_domains = False
    ip = None

    for opt, arg in opts:
        if opt in ("--token", "-t"):
            token = arg
        elif opt in ("--domain-id", "-d"):
            domain = int(arg)
        elif opt in("--get-domains", "-g"):
            get_domains = True
        elif opt in("--ip"):
            ip = arg
        elif opt in ("--help", "-h"):
            usage()
            sys.exit(0)

    if token is None:
        usage()
        sys.exit(0)

    client = dns_update_auth(token)

    domain_list = dns_get_domains(client)
    if get_domains:
        dns_print_domains(domain_list)
        sys.exit(0)

    if domain is not None and ip is not None:
        if domain not in domain_list:
            print("The domain id doesn't exists")
            sys.exit(0)
        rs = dns_update_domain_ip(domain_list[domain]["object"], ip)

        if rs:
            print("Record updated")
            sys.exit(0)
        else:
            print("Record not updated")
            sys.exit(1)


if __name__ == "__main__":
    dns_update()
