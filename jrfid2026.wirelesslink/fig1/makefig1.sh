#!/usr/bin/env zsh

ngspice -b twoport.kron.cir && python comparemaxwell.py
