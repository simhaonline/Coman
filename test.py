from coman import ConnectionManager

cm = ConnectionManager(str_vpn='nordvpn', str_tor_pwd='1234')

ip = cm.request('https://ifconfig.me')
print(f"L'adresse IP de la requete en utilisant tor est : {ip}")

cm.new_identity()
ip = cm.request('https://api.ipify.org')
print(f"L'adresse IP après demande de nouvelle identité est : {ip}")

ip = cm.request('https://api.ipify.org', bl_clear=True)
print(f"L'adresse IP courante est : {ip}")

test = cm.is_vpn_on()
print(test)