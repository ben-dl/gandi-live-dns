#!venv/bin/python
# encoding: utf-8
'''
Gandi v5 LiveDNS - DynDNS Update via REST API and requests

@author: cave, ported
License GPLv3
https://www.gnu.org/licenses/gpl-3.0.html

Created on 13 Aug 2017, updated for multiple accounts and YAML configs on 13 May 2020 by ported
http://doc.livedns.gandi.net/
http://doc.livedns.gandi.net/#api-endpoint -> https://dns.gandi.net/api/v5/
'''

import requests
import argparse
import confuse


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force', help="force an update/create", action="store_true")
config = confuse.Configuration('gandi-live-dns', __name__)


def get_dynip(iplookup_provider):
    ''' find out own IPv4 at home <-- this is the dynamic IP which changes more or less frequently
    similar to curl ifconfig.me/ip, see example.config.py for details to ifconfig providers
    '''
    r = requests.get(iplookup_provider)
    print(f"Checking dynamic IP: {r.text.strip()}")
    return r.text.strip()


def get_uuid(api_secret, zone):
    '''
    find out ZONE UUID from domain
    Info on domain "DOMAIN"
    GET /domains/<DOMAIN>:
    '''
    url = config["api_endpoint"].get() + '/domains/' + zone
    r = requests.get(url, headers={"X-Api-Key": api_secret})
    json_object = r.json()
    if r.status_code == 200:
        return json_object['zone_uuid']
    else:
        raise Exception(
            f"Error: HTTP Status Code {r.status_code} when trying to get Zone UUID"
            f" for {zone}. Error: {json_object['message']}"
        )


def get_dnsip(api_secret, zone_uuid, subdomain):
    ''' find out IP from first Subdomain DNS-Record
    List all records with name "NAME" and type "TYPE" in the zone UUID
    GET /zones/<UUID>/records/<NAME>/<TYPE>:

    The first subdomain from "subdomains" will be used to get the actual DNS Record IP
    '''

    url = config["api_endpoint"].get() + '/zones/' + zone_uuid + '/records/' + subdomain + '/A'
    headers = {"X-Api-Key": api_secret}
    r = requests.get(url, headers=headers)
    json_object = r.json()
    if r.status_code == 200:
        print(f"Checking IP for DNS Record {zone_uuid}/{subdomain}: {json_object['rrset_values'][0]}")
        return json_object['rrset_values'][0]
    else:
        raise Exception(
            f"Error: HTTP Status Code {r.status_code} when trying to get IP for"
            f" {zone_uuid}/{subdomain}. Error: {json_object['message']}"
        )


def update_records(api_secret, zone_uuid, dyn_ip, subdomain):
    ''' update DNS Records for Subdomains
        Change the "NAME"/"TYPE" record from the zone UUID
        PUT /zones/<UUID>/records/<NAME>/<TYPE>:
        curl -X PUT -H "Content-Type: application/json" \
                    -H 'X-Api-Key: XXX' \
                    -d '{"rrset_ttl": 10800,
                         "rrset_values": ["<VALUE>"]}' \
                    https://dns.gandi.net/api/v5/zones/<UUID>/records/<NAME>/<TYPE>
    '''
    url = config["api_endpoint"].get() + '/zones/' + zone_uuid + '/records/' + subdomain + '/A'
    payload = {"rrset_ttl": config["ttl"].get(), "rrset_values": [dyn_ip]}
    headers = {"X-Api-Key": api_secret}
    r = requests.put(url, json=payload, headers=headers)
    json_object = r.json()
    if r.status_code == 201:
        print(f"Status Code: {r.status_code}/{json_object['message']}, IP updated for {zone_uuid}/{subdomain}")
        return True
    else:
        raise Exception(
            f"Error: HTTP Status Code {r.status_code} when trying to update IP for"
            f" {zone_uuid}/{subdomain}. Error: {json_object['message']}"
        )


args = parser.parse_args()

dyn_ip = get_dynip(config["iplookup"].get())

for account in config['accounts'].get():
    for zone, subdomains in account["zones"].items():
        zone_uuid = get_uuid(account["api_secret"], zone)
        for subdomain in subdomains:
            if not args.force:
                dns_ip = get_dnsip(account["api_secret"], zone_uuid, subdomain)
                if dns_ip == dyn_ip:
                    continue
            update_records(account["api_secret"], zone_uuid, dyn_ip, subdomain)
