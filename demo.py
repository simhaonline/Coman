#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 20:11:45 2020.

@author: tristan
"""

from coman import ConnectionManager
from bs4 import BeautifulSoup

# To create a connexion manager.
cm = ConnectionManager(str_vpn='nordvpn', str_tor_pwd='1234')

# Bascis usage.
ip = cm.request('https://ifconfig.me')
print(f"The IP a the exit node is : {ip}")

# Requesting new identity.
cm.new_identity()
ip = cm.request('https://api.ipify.org')
print(f"The IP of the new exit node is : {ip}")

# Making a requests without TOR.
ip = cm.request('https://api.ipify.org', bl_clear=True)
print(f"The public IP is : {ip}")

# Example.

# URL to scrap.
str_url = 'http://quotes.toscrape.com/'

# Scraping to URL using TOR and a random user agent.
soup = BeautifulSoup(cm.request(str_url), 'lxml')
quotes = soup.findAll('div', {'class': 'quote'})
quote = quotes[0].find('span', {'class': 'text'}).text
author = quotes[0].find('small', {'class': 'author'}).text

print(f'{quote}\n\t\t\t\t\t-{author}')
