#!/bin/bash

apt-get upgrade
apt-get update

mkdir ~/.ssh
chmod 700 ~/.ssh

echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6jTV+2PEoMk5SlvuJC1fj9DmtcUV7KM7DWDsI3GW2cYj0Xo8fmE87d7qQvpZEHBHzgQiljT7mtZvxivkEqjQQAJuXjFrBSMHpDue+lnZWTi8PtAyQ7lI2/mKi+kezJBiBI5wANZkrw5CAl5mtRGVNY9g3MsEAqiEzT/7+YiHa+abznFQdEOoAPP9t4zmu3CwEece+aLL48Gz83Ow030f5mtF10cjhaXLfITED0jErFey4mbzjlyFq+RKv5ITCPNlesQomKxrPMm/IPPwM5vUvCVKRWYeOJE++Gv2zSDTxI3QbCWOYm4W5EH226YZjVrTaZBb/N1dI40Mo28demzON Home@Erics-MBP-4.home
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD1vbj1E6GgfAT7NYWQkV6ltIHcbek4vahChPWDQclLsq2VtSHn6+vBT5893Wdfm9Sm1eWRXwYSuloGizVxN6kxuDClAJSXoaiopxgpiI2YFe+fwBrVJgZi4Z5eUf5D+gtttxxrdOJNVl0Hp1vnkbEPWx6PA/xGZM+twUBpqCGIvUw1NwSuakLXMzBvr3sSHO4uptpkTLCX4USNDdi9NnOKvbsFQKmEkKInwz8TdNRRH1cjX+vW9ISwuzrDWfNsuUq47U5ge4NQONBx64HhjHOVn4UipeEXiq6A5ZWz+s2PYvS9g/H2PyOx2pccNuLkO3m1mCVox5I0azMacHABIw0H
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPsypvuXjEiE59dFCb02gfDB4s8LKGqM1lpu/grstrf37NsU+oIGugfIi0UoBjwxDZqx1Kn1oFXtXyrCmhqcmCjeL19G6JGCcIJh3qnmQEjNCfzEWrSsTrbxcyv8mhoJiIFnF1egt0ItHcsrV+aWMloaNjghR4iiCve8vMUd2kLU+iGdwJ5qrT9rWVFxj/GGjwMJG6sXTQH8iUT2G1xDxu5OCYJsn4Ek6X8AJ9/CFaDkFkk3oDirS0Y47pZoMdNqYwoWmHYN47zE2TFtCn03bt1enZAbmSJ5VPb3Ufpt7H7UBsMnRXW9G+QdAyiYy0Pf/3i19GzyLoABTlEWO/NuWV eday@Erics-MacBook-Pro.local
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDBNSAkGNJ7An9x9TywWYnUenmlH1aY0FmEfZJs5ecP7sq9AmMjniWQiq8YKBHo2rFrgWA3n+QW6p21KKBqufnqJJ2I9xncnuny6MIACX0LZy27clXBxhvtG2pU2/8UUzIgmoBZP/Cd6uxcqzCOGV0ndWkl/MI7+aW5231ftMkqoWKoQKSTpzNwR7gf2KLlAsluYDo9K6ziVJ1YaxbW9lp4LMghzs4iDdN0u6fYefwwAzfUwnNdUthEa+2Lgx5tB2itLSBFpYQclH1gQowGtfQDNyVsi6PZoEsscHAjqJZKIB/EI+AIkOX4TjN6fLtwpmNmTH6+bKPKF8S4B9d9Z9iT root@CalFreshMaster" > ~/.ssh/authorized_keys

chmod 600 ~/.ssh/authorized_keys

ufw allow OpenSSH
ufw enable

cd /etc
git clone https://github.com/eday1632/calfresh.git

mkdir /etc/calfresh/logs

git config --global user.email "eric.day87@gmail.com"
git confid --global user.name "Eric Day"
