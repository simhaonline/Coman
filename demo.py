#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 20:11:45 2020.

@author: Tristan Muscat
"""

from coman import ConnectionManager
from bs4 import BeautifulSoup

# Using class methods

# Getting our public IP.
request = ConnectionManager.request(url='https://ifconfig.me')
soup = BeautifulSoup(request, 'lxml')
ip = soup.find('strong', {'id': 'ip_address'}).text

# Getting our TOR exit node IP.
request = ConnectionManager.request(url='https://ifconfig.me', str_tor_pwd='1234')
soup = BeautifulSoup(request, 'lxml')
ip = soup.find('strong', {'id': 'ip_address'}).text
# Adding the 'str_tor_pwd' parameter is what indicate that we want our request to be sent via TOR.

# Requesting a new TOR connection.
ConnectionManager.new_identity(str_tor_pwd='1234')

# Getting our new TOR exit node IP.
request = ConnectionManager.request(url='https://ifconfig.me', str_tor_pwd='1234')
soup = BeautifulSoup(request, 'lxml')
ip = soup.find('strong', {'id': 'ip_address'}).text


# Using a connection manager object.
# It does essentially the samething, but using an instance helps keep track
# of useragents and set your preferences once.

# To create a connection manager.
cm = ConnectionManager(str_vpn='nordvpn', str_tor_pwd='1234')

# Bascis usage.
ip = cm.request('https://api.ipify.org')
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
