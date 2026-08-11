#!/usr/bin/env zsh

ngspice -b twoport.kron.rad.cir && python plot.polar.py -o polarpattern.eps