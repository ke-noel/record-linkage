#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Dominic Parent <dominic.parent@canada.ca>
#
# Distributed under terms of the  license.

"""
Command line interface for package.
Taking inspiration from Python Cookbook by Beazley and Jones.
"""
import argparse
import funcs
from linkage1 import Linkage1

parser = argparse.ArgumentParser(description="test argument parser, if you see this emssage you shouldn't be using this")

parser.add_argument('-r', '--record',
                    dest='record',
                    action='store',
                    required=False,
                    type=str,
                    help='Records to read.')
parser.add_argument('-t', '--tag',
                    dest='tag',
                    action='store',
                    required=False,
                    help='Tag for job.')
parser.add_argument('-c', '--cutoff',
                    dest='cutoff',
                    action='store',
                    type=int,
                    required=False,
                    help='Cut off score.')
parser.add_argument('-b', '--block',
                    dest='block',
                    action='store',
                    nargs='+',
                    required=False,
                    help='List of blocking variables.')
parser.add_argument('-e', '--exact',
                    dest="exact",
                    action='store',
                    nargs='+',
                    required=False,
                    help='List of exact variables.')
parser.add_argument('-s', '--string',
                    dest='string',
                    action='store',
                    nargs='+',
                    required=False,
                    help='List of string variables.')
parser.add_argument('-m', '--method',
                    dest='method',
                    action='store',
                    required=False,
                    help='Comparison method.')

arguments = parser.parse_args()

print(arguments.record)
print(arguments.tag)
print(arguments.cutoff)
print(arguments.block)
print(arguments.exact)
print(arguments.string)
print(arguments.method)

data = funcs.read_data(arguments.record)
link = Linkage1(arguments.tag, data, arguments.cutoff, block_on=arguments.block,
        comp_exact=arguments.exact,
        comp_string=arguments.string)
link.get_pairs()
link.get_features()
link.get_matches()
link.get_counts()
link.make_hist(link.pairs_dist, 'Block_pairs_hist.json')
link.make_hist(link.real_dup_dist, 'Real_dups_hist.json')
link.make_hist(link.dup_dist, 'Dups_hist.json')
link.remove_dup()
