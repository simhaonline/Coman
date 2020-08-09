#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 20:11:45 2020.

@author: tristan
"""

from coman import ConnectionManager
from requests import get

ip = get('https://api.ipify.org').text
print(f"L'adresse IP courante est : {ip}")

cm = ConnectionManager(str_vpn='nordvpn', str_tor_pwd='1234')

ip = cm.request('https://ifconfig.me')
print(f"L'adresse IP de la requete en utilisant tor est : {ip}")

cm.new_identity()
ip = cm.request('https://api.ipify.org')
print(f"L'adresse IP après demande de nouvelle identité est : {ip}")

ip = cm.request('https://api.ipify.org', bl_clear=True)
print(f"L'adresse IP courante est : {ip}")

cm.is_vpn_on()

cm.vpn_new_connexion()