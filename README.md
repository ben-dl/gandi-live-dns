gandi-live-dns
----

This is a simple dynamic DNS updater for the [Gandi](https://www.gandi.net) registrar. It uses their [LiveDNS REST API](http://doc.livedns.gandi.net/) to update the zone file for a subdomain of a domain to point at the external IPv4 address of the computer it has been run from.

With the new v5 Website, Gandi has also launched a new REST API which makes it easier to communicate via bash/curl or python/requests.

### Goal

You want your homeserver to be always available at `dynamic_subdomain.mydomain.tld`.

#### Download
Download the Script from here as [zip](https://github.com/ben-dl/gandi-live-dns/archive/master.zip)/[tar.gz](https://github.com/ben-dl/gandi-live-dns/archive/master.tar.gz) and extract it.  

or clone from git

`git clone https://github.com/ben-dl/gandi-live-dns.git` 

#### Create venv & install requirements
`python3 -m venv venv`
`source venv/bin/activate` (or similar for other OSs/shells)
`pip install -r requirements.txt`

#### Script Configuration
Copy `example-config.yaml` to `~/.config/gandi-live-dns/config.yaml` and edit the file to fit your needs.

##### api_endpoint
Gandiv5 LiveDNS API Location
http://doc.livedns.gandi.net/#api-endpoint

```
api_endpoint = 'https://dns.api.gandi.net/api/v5'
```

##### accounts
List of accounts to update onto

For each account:

###### api_secret
Retrieve your API Key from the "Security" section in new [Gandi Account admin panel](https://account.gandi.net/) to be able to make authenticated requests to the API.

###### zones
Map of domain name (zone) to the subdomains that need to be updated. Use `@` for the root domain.

#### Run the script
And run the script:

```
user@server:~$ source venv/bin/activate
user@server:~$ python gandi-live-dns.py --force
```

If your IP has changed, it will be detected and the update will be triggered. The force option given above is explained in the next section.

#### Command Line Arguments

```
root@dyndns:~/gandi-live-dns-master/src# ./gandi-live-dns.py -h
usage: gandi-live-dns.py [-h] [-f]

optional arguments:
  -h, --help     show this help message and exit
  -f, --force    force an update/create

```

The force option runs the script even when no IP change has been detected. 
It will update all records and even create them if they are missing in the 
zone. This can be used if additional/new subdomains get appended to the config file.  

### Cron the script

Run the script every five minutes. 
```
*/5 * * * * /path/to/script/venv/bin/python /path/to/script/gandi-live-dns.py >/dev/null 2>&1 
```
