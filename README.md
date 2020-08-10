# Coman

## How to install

First download the whole thing and unzip it. Then navigate to the package directory. Typically :

`$ cd ~/Downloads/Coman`

You can use the installer :

`$ ./install`

Or you can paste the "coman" directory in the site-package of your python installation. The ./install file take care of that and install the package in your current python environment while also install all the dependencies.

## Test that everything is working

The "test_coman.py" is here to check that everything is in order. You can use it with `$ python test_coman.py` and check that the tests ran successfully. If you are using a VPN and or TOR you can use :

```shell
$ python test_coman.py vpn=<your_vpn_name> tor=<your_tor_password>
```

If you are not using TOR or a VPN, testing isn't really important. The VPN part is totally optional, even if your are using a VPN, the package can absolutely function without knowing it. Coman has a few VPN commands but they more for convenience than usefulness.

## Install and set up TOR and/or a VPN

The main idea is to allow anonymous scraping using TOR. So if you don't have TOR already set up, here is how you can do that. First, simply install tor as a service :

`$ sudo apt-get install tor`

then you can launch tor with the command :

`$ sudo service tor start`

You can start tor on boot with :

`$ systemctl enable tor`

Now you can use TOR as a service, but in order to request a new identity you need to configure the TOR controller. In the file `/etc/tor/torrc` use the parameters :

`ControlPort 9051
CookieAuthentication 1`

Now you need to choose a password for TOR, and run the command `tor --hash-password <your_password>` which will give you a hash for your password that your place in the `/etc/tor/torrc` file :

`
HashedControlPassword 16:E06D936E26108CCA604AA31B0A24277D188F1B7BCC1ABE504AFE5EA02F`

If you consider using TOR with python, you might want to also get a VPN to run TOR over VPN, it's my advice anyway. VPNs are widely available on line, but are mostly paid services.

## How to use coman

For instruction on how to use `coman` report to the demo.py file.