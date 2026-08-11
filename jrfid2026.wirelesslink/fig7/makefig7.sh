#!/usr/bin/env zsh

ngspice -b complete.cir  && python plot.complete.py -o complete.eps