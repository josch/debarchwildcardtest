Execute `run.py` to compare the implementations of architecture wildcard
matching as done by dose3, dpkg and dak. It tests by feeding each
implementation about 150k possible combinations of architecture wildcards and
real Debian architectures. The number varies with the os, cpu and debian
architectures listed in the files in `/usr/share/dpkg/`.
