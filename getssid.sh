#!/bin/bash

iw dev wlp2s0 link | grep -Po 'SSID: \K.*'
