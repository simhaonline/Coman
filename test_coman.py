#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 11:29:27 2020.

@author: Tristan Muscat
"""

from coman import ConnectionManager  # The package to test
import unittest                      # For unit testing
import sys                           # For the arguments
import re                            # For parsing arguments


class TestComan(unittest.TestCase):
    VPN = None
    TOR = None

    def test_coman(self):
        """Test the basic connexion manager."""
        # Create a connexion manage.
        cm = ConnectionManager(str_vpn=self.VPN, str_tor_pwd=self.TOR)

        # Check if the connexion manager is able to make requests
        ip_local = cm.request('https://ifconfig.me', bl_clear=True)
        self.assertNotEqual(ip_local, '0.0.0.0')

    def test_tor(self):
        """Test that TOR is working properly."""
        # If tor is not to be tested, then nothing is done.
        if self.TOR is not None:
            # Create a connexion manager.
            cm = ConnectionManager(str_vpn=self.VPN, str_tor_pwd=self.TOR)

            # Get the router public IP (might be from the VPN).
            ip_public = cm.request('https://api.ipify.org', bl_clear=True)
            # Get the IP at the TOR exit node. Requests a new identity and ask for the new IP.
            ip_tor_1 = cm.request('https://api.ipify.org')
            cm.new_identity()
            ip_tor_2 = cm.request('https://api.ipify.org')

            # Comapring each IPs. they should all be different.
            self.assertNotEqual(ip_public, ip_tor_1)
            self.assertNotEqual(ip_public, ip_tor_2)
            self.assertNotEqual(ip_tor_1, ip_tor_2)

    def test_vpn(self):
        """Check that the VPN is running, nothing more."""
        if self.VPN is not None:
            # Create a connexion manager.
            cm = ConnectionManager(str_vpn=self.VPN, str_tor_pwd=self.TOR)
            # Check that the vpn is running properly.
            self.assertTrue(cm.is_vpn_on())


if __name__ == "__main__":
    # Parsing the args
    if len(sys.argv) > 1:
        # Getting the VPN name and the TOR password.
        try:
            TestComan.VPN = sys.argv.pop([i for i, x in enumerate(sys.argv) if re.match(r'vpn=', x)][0]).split('=')[1]
        except IndexError:
            pass
        try:
            TestComan.TOR = sys.argv.pop([i for i, x in enumerate(sys.argv) if re.match(r'tor=', x)][0]).split('=')[1]
        except IndexError:
            pass
    unittest.main()
