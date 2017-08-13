#!/usr/bin/python3

import os
import time
import subprocess

# for getting ip address
import socket
import fcntl
import struct


def get_ip_address(ifname):
    """Updated from http://stackoverflow.com/a/24196955 for Python 3"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode())
    )[20:24])


def wait_ip_address(ifname):
    wait_delay = 0.3  # seconds
    start = time.time()
    while ((time.time() - start) < 10):
        try:
            return get_ip_address(ifname)
        except IOError:
            time.sleep(wait_delay)  # wait for the interface to rise
    return None


def main():
    vpn_iface_name = "tun0"
    vpnroot = os.path.expanduser("~/Scripts/openvpn")
    vpn_already_on = False

    try:
        vpn_ip = get_ip_address(vpn_iface_name)
        vpn_already_on = True

    except:
        start_fpath = os.path.join(vpnroot, "start.sh")
        config_fpath = os.path.join(vpnroot, "east.conf")
        subprocess.run([start_fpath, config_fpath])

        vpn_ip = wait_ip_address(vpn_iface_name)

    subprocess.run(["rtorrent", "-b", vpn_ip])

    if not vpn_already_on:
        stop_fpath = os.path.join(vpnroot, "stop.sh")
        subprocess.run(["sudo", stop_fpath])


if __name__ == '__main__':
    main()
