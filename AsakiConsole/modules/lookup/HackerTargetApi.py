from lib.decorators import with_argparser, use_for

import requests
import argparse
import re

class HackerTargetApi(object):
    def _bind_api(self, endpoint: str, query: str) -> requests.Response:
        response = requests.get(
            "https://api.hackertarget.com/%s?q=%s" % (endpoint, query))
        self.poutput(re.sub(r"<.+?>", "", response.text))

    QueryParser = argparse.ArgumentParser()
    QueryParser.add_argument("query", help="Query string")

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_traceroute(self, param):
        """using mtr an advanced traceroute tool trace the path of an Internet connection"""
        self._bind_api("mtr", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_ping(self, param):
        """testing connectivity to a host, perform a ping from our server"""
        self._bind_api("nping", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_dnslookup(self, param):
        """Find DNS records for a domain, results are determined using the dig DNS tool"""
        self._bind_api("dnslookup", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_hostsearch(self, param):
        """Find forward DNS (A) records for a domain"""
        self._bind_api("hostsearch", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_reversedns(self, param):
        """Find Reverse DNS records for an IP address or a range of IP addresses"""
        self._bind_api("reversedns", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_findshareddns(self, param):
        """Find hosts sharing DNS servers"""
        self._bind_api("findshareddns", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_zonetransfer(self, param):
        """Online Test of a zone transfer that will attempt to get all DNS records for a target domain"""
        self._bind_api("zonetransfer", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_whois(self, param):
        """Determine the registered owner of a domain or IP address block with the whois tool."""
        self._bind_api("whois", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_geoip(self, param):
        """Find the location of an IP address using the GeoIP lookup location tool."""
        self._bind_api("geoip", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_reverse_ip(self, param):
        """Discover web hosts sharing an IP address with a reverse IP lookup."""
        self._bind_api("reverseiolookup", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_tcp_port(self, param):
        """Determine the status of an Internet facing service or firewall"""
        self._bind_api("nmap", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_udp_port(self, param):
        """Online UDP port scan available for common UDP services"""
        self._bind_api("nmap", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_subnet(self, param):
        """Determine the properties of a network subnet"""
        self._bind_api("subnetcalc", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_http_headers(self, param):
        """View HTTP Headers of a web site. The HTTP Headers reveal system and web application details."""
        self._bind_api("httpheaders", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_pagelinks(self, param):
        """Dump all the links from a web page."""
        self._bind_api("pagelinks", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_aslookup(self, param):
        """Get Autonomous System Number or ASN details from an AS or an IP address."""
        self._bind_api("aslookup", param.query)

    @use_for("lookup")
    @with_argparser(QueryParser)
    def do_bannerlookup(self, param):
        """Discover network services by querying the service port."""
        self._bind_api("bannerlookup", param.query)
