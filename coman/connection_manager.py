#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 13:58:25 2018.

@author: Tristan Muscat
"""

# =====================================================================================================================
# Libraries
# =====================================================================================================================

import subprocess                    # to use bash commands (check if a service is active, if internet is on, ect.)
from stem import Signal              # To get a new TOR connexion
from stem.control import Controller  # To get a new TOR connexion
import requests                      # To manage requests

import time                          # To wait bitween two new TOR connexion requests
import random as rdm                 # To randomize user agents

from .conf import USERAGENTS
from .conf import VPN

# =====================================================================================================================
# Module de gestion de connexion
# =====================================================================================================================


class ConnectionManager:
    """Connexion manager.

    Attributes
    ----------
    str_ip: str
        The current IP address. Useful when using TOR.
    str_ip_old: str
        The previous IP address to check if the new TOR connexion requested took effect.
    lst_useragents: list
        List of user agents to use.
    user_agent: dict
        The user agent currently in use.
    vpn_status: list
        Arguments to check the vpn status.
    vpn_connect: list
        Arguments to ask a new connexion from the vpn.
    str_tor_pwd: str
        TOR password.
    proxies: dict
        Proxy used by TOR.
    """

# =====================================================================================================================
# Initialisation
# =====================================================================================================================

    def __init__(self, str_useragent=None, str_vpn=None, str_tor_pwd=None):
        """Initialize the connexion manager.

        Parameters
        ----------
        str_useragent : str, optional
            Used to choose a specifi user agent, if None then it is randomized. The default is None.
        str_vpn : str, optional
            The name of the VPN used. Useful to check is the VPN is running before placing a request.
            The default is None.
        str_tor_pwd : str, optional
            TOR password, can be empty. If None then TOR is not used. The default is None.
        """
        # Initialisation du connexion manager, les IP sont à 0.0.0.0 et sont changés plus tard
        self.str_ip = '0.0.0.0'
        self.str_ip_old = '0.0.0.0'
        self._set_useragents(str_useragent)
        self._set_vpn(str_vpn)
        self._set_tor(str_tor_pwd)

    def _set_useragents(self, str_useragent=None):
        """Set the user agents list or use the single user agent provided."""
        # If no user agent is given, then it is randomized for every request.
        if str_useragent is None:
            # Loading the useragents list and picking one randomly.
            self.lst_useragents = USERAGENTS.lst_useragents
            self.user_agent = {'User-Agent': self.lst_useragents[rdm.randint(0, len(self.lst_useragents) - 1)]}
        # If a useragent is given then it is used every time.
        else:
            # Tht useragents list if set to None so requestes can check if they have to change it.
            self.lst_useragents = None
            self.user_agent = str_useragent

    def _set_vpn(self, str_vpn):
        """Set everything needed for the vpn, although it is completely optional and doesn't is really useful."""
        # The VPN name is passed as a varaible to get the right commands to use.
        if str_vpn is not None:
            dict_vpn = VPN.dict_vpn
            self.vpn_status = dict_vpn['vpn_is_on'][str_vpn]
            self.vpn_connect = dict_vpn['vpn_new_connexion'][str_vpn]
        else:
            self.vpn_status = None
            self.vpn_connect = None

    def _set_tor(self, str_tor_pwd):
        """Set the variables used for tor."""
        self.str_tor_pwd = str_tor_pwd
        # If a password is provided, then tor has to be set up.
        if self.str_tor_pwd is not None:
            self.proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }
        else:
            self.proxies = None

# =====================================================================================================================
# Connexions
# =====================================================================================================================

    def request(self, url, bl_clear=False):
        """Use whatever setup we are using to make a http request.

        Parameters
        ----------
        url: str
            The URL.
        bl_clear: bool
            Used when TOR is set up to use the regular network to make a request.

        Returns
        -------
            The result of the request.
        """
        # If the useragent needs to be randomized, we choose one here.
        if self.lst_useragents is not None:
            self.user_agent = {'User-Agent': self.lst_useragents[rdm.randint(0, len(self.lst_useragents) - 1)]}

        # Request through TOR or not.
        if not bl_clear and self.proxies is not None:
            request = requests.get(url, proxies=self.proxies).text
        else:
            request = requests.get(url).text

        return request

    def new_identity(self):
        """Change the identity (IP and such)."""
        # The old IP is used to know if the change took effect.
        self.str_ip_old = self.str_ip

        int_retry = 0
        # If we get the same IP twice we wait and ask again
        while self.str_ip_old == self.str_ip and int_retry < 5:
            time.sleep(2)
            int_retry += 1
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=self.str_tor_pwd)
                controller.signal(Signal.NEWNYM)
            self.str_ip = self.request('https://ifconfig.me')

        # We try 5 times to get a new IP and if it doesn't work the program juste continues. I don't want it to crash
        # just for that. Also it has never happend.

    def vpn_new_connexion(self, *args):
        """Asks a new connexion from the VPN. Honestly should not be used, but I left it there."""
        int_status = subprocess.Popen(self.vpn_connect + list(args),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

        return int_status == 0

# =====================================================================================================================
# Outils
# =====================================================================================================================

    def is_vpn_on(self):
        """Check if the VPN is running."""
        int_status = subprocess.Popen(self.vpn_status,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

        return int_status == 0

    @staticmethod
    def internet_on():
        """Methode qui verifie si une connexion a internet existe ou non."""
        int_status = subprocess.Popen(['wget', '-q', '--spider', 'http://google.com'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

        return int_status == 0

    @staticmethod
    def is_service_running(str_service):
        """Check if a service is running or not."""
        int_status = subprocess.Popen(['/usr/sbin/service', str_service, 'status'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

        return int_status == 0
