#!/usr/bin/python3
#
# Copyright (C) 2014 Johannes Schauer <j.schauer@email.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software. 

import subprocess
import yaml
import daklib_arch
import debarch

os_list = []

os_list = set([row[0].split('-')[1] for row in debarch._load_table('/usr/share/dpkg/ostable')])

cpu_list = set([row[0] for row in debarch._load_table('/usr/share/dpkg/cputable')])

wildcard_list = [ o + "-" + c for o in os_list for c in cpu_list]

deb_list = subprocess.check_output(["dpkg-architecture", "-L"]).decode().split()

def dpkg_arch_matches(arch, wildcard):
    # environment must be empty or otherwise the DEB_HOST_ARCH environment
    # variable will influence the result
    return subprocess.call(
        ['dpkg-architecture', '-i%s' % wildcard, '-a%s' % arch],
        env={}) == 0

def dose_arch_matches(arch, wildcard):
    with open("/tmp/sources", "w") as f:
        f.write("""
Package: foo
Architecture: %s
Version: 0.invalid.0
"""%(wildcard))
    with open("/tmp/packages", "w") as f:
        f.write("""
Package: build-essential
Architecture: %s
Version: 0.invalid.0
"""%(arch))
    data = subprocess.check_output(['dose-builddebcheck', '--deb-native-arch=%s'%arch,
        '--successes', '/tmp/packages', '/tmp/sources'])
    data = yaml.load(data, Loader=yaml.CBaseLoader)
    return len(data['report']) == 1

check_pairs = [ (d,w) for d in deb_list for w in wildcard_list ]
len_check_pairs = len(check_pairs)

print("checking %d testcases"%len_check_pairs)

for i,(d,w) in enumerate(check_pairs):
    print("\r%f"%((i*100)/len_check_pairs), end="")
    dose_res = dose_arch_matches(d, w)
    dpkg_res = dpkg_arch_matches(d, w)
    try:
        dak_res = daklib_arch.match_architecture(d, w)
    except daklib_arch.InvalidArchitecture:
        dak_res = False
    deb_res = debarch.match_architecture(d,w)
    if dose_res != dpkg_res or dose_res != dak_res \
            or dose_res != deb_res:
        print("difference!")
        print("dose: %s matches %s: %s"%(w,d,dose_res))
        print("dpkg: %s matches %s: %s"%(w,d,dpkg_res))
        print("deb:  %s matches %s: %s"%(w,d,deb_res))
        print("dak:  %s matches %s: %s"%(w,d,dak_res))
