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
from stem import Signal              # To get a new TOR connection
from stem.control import Controller  # To get a new TOR connection
import cloudscraper                  # To manage requests

import pandas as pd
from bs4 import BeautifulSoup
import json

import time                          # To wait bitween two new TOR connection requests
import random as rdm                 # To randomize user agents

from .conf import USERAGENTS
from .conf import VPN

# =============================================================================
# Hybrid methods
# =============================================================================


class hybridmethod:
    """Allow to declare a class and instance version of the same method."""

    def __init__(self, fclass, finstance=None, doc=None):
        self.fclass = fclass
        self.finstance = finstance
        self.__doc__ = doc or fclass.__doc__
        # support use on abstract base classes
        self.__isabstractmethod__ = bool(
            getattr(fclass, '__isabstractmethod__', False)
        )

    def classmethod(self, fclass):
        """Class method version of the function."""
        return type(self)(fclass, self.finstance, None)

    def instancemethod(self, finstance):
        """Instance method version of the function."""
        return type(self)(self.fclass, finstance, self.__doc__)

    def __get__(self, instance, cls):
        """Retreive the right version."""
        if instance is None or self.finstance is None:
            # either bound to the class, or no instance method available
            return self.fclass.__get__(cls, None)
        return self.finstance.__get__(instance, cls)

# =====================================================================================================================
# Module de gestion de connection
# =====================================================================================================================


class ConnectionManager:
    """Connection manager.

    Attributes
    ----------
    str_ip: str
        The current IP address. Useful when using TOR.
    str_ip_old: str
        The previous IP address to check if the new TOR connection requested took effect.
    lst_useragents: list
        List of user agents to use.
    user_agent: dict
        The user agent currently in use.
    vpn_status: list
        Arguments to check the vpn status.
    vpn_connect: list
        Arguments to ask a new connection from the vpn.
    str_tor_pwd: str
        TOR password.
    proxies: dict
        Proxy used by TOR.
    """

    dict_proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }

# =====================================================================================================================
# Initialisation
# =====================================================================================================================

    def __init__(self, str_useragent=None, str_vpn=None, str_tor_pwd=None):
        """Initialize the connection manager.

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
        # Initialisation du connection manager, les IP sont à 0.0.0.0 et sont changés plus tard
        self.str_ip = '0.0.0.0'
        self.str_ip_old = '0.0.0.0'
        self.str_tor_pwd = str_tor_pwd
        self.scraper = cloudscraper.create_scraper()
        self._set_useragents(str_useragent)
        self._set_vpn(str_vpn)

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
            self.vpn_connect = dict_vpn['vpn_new_connection'][str_vpn]

            request = ConnectionManager.request(url='https://nordvpn.com/api/server')
            soup = BeautifulSoup(request, 'lxml')
            lst_servers = json.loads(soup.text)

            servers = pd.DataFrame({'Country': [serv['country'] for serv in lst_servers],
                                    'Domain': [serv['domain'] for serv in lst_servers]})

            servers['Flag'] = servers['Domain'].astype(str).str.extract(r'^([a-z]{2})\d{2,4}.nordvpn.com$')
            servers['ID'] = servers['Domain'].astype(str).str.extract(r'^[a-z]{2}(\d{2,4}).nordvpn.com$')

            self.servers = servers
        else:
            self.vpn_status = None
            self.vpn_connect = None

# =====================================================================================================================
# Connections
# =====================================================================================================================

    @hybridmethod
    def request(cls, url, str_tor_pwd=None, dict_user_agent=None):
        """Get the HTTP code of a webpage."""
        if dict_user_agent is None:
            dict_user_agent = {'User-Agent':
                               USERAGENTS.lst_useragents[rdm.randint(0, len(USERAGENTS.lst_useragents) - 1)]}
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        # Request through TOR or not.
        if str_tor_pwd is not None:
            request = scraper.get(url, proxies=ConnectionManager.dict_proxies, headers=dict_user_agent).text
        else:
            request = scraper.get(url, headers=dict_user_agent).text

        return request

    @hybridmethod
    def new_identity(cls, str_tor_pwd):
        """Change the identity (IP and such)."""
        # The old IP is used to know if the change took effect.
        str_ip_old = ConnectionManager.request('https://api.ipify.org', str_tor_pwd=str_tor_pwd)
        str_ip = str_ip_old

        int_retry = 0
        # If we get the same IP twice we wait and ask again
        while str_ip_old == str_ip and int_retry < 5:
            time.sleep(2)
            int_retry += 1
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=str_tor_pwd)
                controller.signal(Signal.NEWNYM)
            str_ip = ConnectionManager.request('https://api.ipify.org', str_tor_pwd=str_tor_pwd)

    @hybridmethod
    def vpn_new_connection(cls, str_vpn, lst_countries=None):
        """Asks a new connection from the VPN. Honestly should not be used, but I left it there."""
        request = ConnectionManager.request(url='https://nordvpn.com/api/server')
        soup = BeautifulSoup(request, 'lxml')
        lst_servers = json.loads(soup.text)

        servers = pd.DataFrame({'Country': [serv['country'] for serv in lst_servers],
                                'Domain': [serv['domain'] for serv in lst_servers]})

        servers['Flag'] = servers['Domain'].astype(str).str.extract(r'^([a-z]{2})\d{2,4}.nordvpn.com$')
        servers['ID'] = servers['Domain'].astype(str).str.extract(r'^[a-z]{2}(\d{2,4}).nordvpn.com$')

        if lst_countries is not None:
            int_serv = rdm.choice(servers.loc[servers['Flag'].isin(lst_countries)].index)
        else:
            int_serv = rdm.randint(0, servers.shape[0] - 1)

        new_server = VPN.dict_vpn['vpn_new_connection'][str_vpn] + list(servers.loc[int_serv, ['Flag', 'ID']])
        int_status = subprocess.Popen(new_server, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

        return int_status == 0

    @request.instancemethod
    def request(self, url, bl_clear=False, dict_user_agent=None):
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
        if (self.lst_useragents is not None) and (dict_user_agent is None):
            self.user_agent = {'User-Agent': self.lst_useragents[rdm.randint(0, len(self.lst_useragents) - 1)]}
        elif self.lst_useragents is not None:
            self.user_agent = dict_user_agent

        # Request through TOR or not.
        if not bl_clear and self.str_tor_pwd is not None:
            request = self.scraper.get(url, proxies=ConnectionManager.dict_proxies, headers=self.user_agent).text
        else:
            request = self.scraper.get(url, headers=self.user_agent).text

        return request

    @new_identity.instancemethod
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
            self.str_ip = self.request('https://api.ipify.org')

        # We try 5 times to get a new IP and if it doesn't work the program juste continues. I don't want it to crash
        # just for that. Also it has never happend.

    @vpn_new_connection.instancemethod
    def vpn_new_connection(self, lst_countries=None, *args):
        """Asks a new connection from the VPN. Honestly should not be used, but I left it there."""
        if lst_countries is not None:
            int_serv = rdm.choice(self.servers.loc[self.servers['Flag'].isin(lst_countries)].index)
        else:
            int_serv = rdm.randint(0, self.servers.shape[0] - 1)
        new_server = self.vpn_connect + list(self.servers.loc[int_serv, ['Flag', 'ID']])

        int_status = subprocess.Popen(new_server, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

        return int_status == 0

# =====================================================================================================================
# Tools
# =====================================================================================================================

    def is_vpn_on(self):
        """Check if the VPN is running."""
        int_status = subprocess.Popen(self.vpn_status,
                                      stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

        return int_status == 0

    @staticmethod
    def internet_on():
        """Methode qui verifie si une connection a internet existe ou non."""
        int_status = subprocess.Popen(['wget', '-q', '--spider', 'http://google.com'],
                                      stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

        return int_status == 0

    @staticmethod
    def is_service_running(str_service):
        """Check if a service is running or not."""
        int_status = subprocess.Popen(['/usr/sbin/service', str_service, 'status'],
                                      stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

        return int_status == 0
