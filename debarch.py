"""architecture matching

@copyright: 2014, Ansgar Burchardt <ansgar@debian.org>
@copyright: 2014, Johannes Schauer <j.schauer@email.de>
@license: GPL-2+
"""

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

_cached_arch2triplet = None
_cached_triplet2arch = None
_cached_cputable = None

def _load_table(path):
    table = []
    with open(path, "r") as f:
        for line in f:
            if not line or line.startswith('#'):
                continue
            table.append(line.split())
    return table

def _read_cputable():
    global _cached_cputable
    if _cached_cputable is None:
        _cached_cputable = _load_table('/usr/share/dpkg/cputable')
    return _cached_cputable

def _read_triplettable():
    global _cached_arch2triplet, _cached_triplet2arch
    if _cached_arch2triplet is None or _cached_triplet2arch is None:
        table = _load_table('/usr/share/dpkg/triplettable')
        arch2triplet = dict()
        triplet2arch = dict()
        for row in table:
            debtriplet = row[0]
            debarch = row[1]
            if '<cpu>' in debtriplet:
                for r in _read_cputable():
                    cpu = r[0]
                    dt = debtriplet.replace('<cpu>', cpu)
                    da = debarch.replace('<cpu>', cpu)
                    arch2triplet[da] = dt
                    triplet2arch[dt] = da
            else:
                arch2triplet[debarch] = debtriplet
                triplet2arch[debtriplet] = debarch
        _cached_arch2triplet = arch2triplet
        _cached_triplet2arch = triplet2arch
    return _cached_triplet2arch, _cached_arch2triplet

def debwildcard_to_debtriplet(arch):
    arch_tuple = arch.split('-', 2)

    if 'any' in arch_tuple:
        if len(arch_tuple) == 3:
            return arch_tuple
        elif len(arch_tuple) == 2:
            return ('any', arch_tuple[0], arch_tuple[1])
        else:
            return ('any', 'any', 'any')
    else:
        return debarch_to_debtriplet(arch)

def debarch_to_debtriplet(arch):
    if (arch.startswith("linux-")):
        arch = arch[6:]

    triplet = _read_triplettable()[1].get(arch)

    if triplet is None:
        return
    return triplet.split('-', 2)

def match_architecture(real, alias):
    if alias == real or alias == "any":
        return True

    real = debarch_to_debtriplet(real)
    alias = debwildcard_to_debtriplet(alias)

    if real is None or len(real) != 3 or alias is None or len(alias) != 3:
        return False

    for i in range(0,3):
        if (alias[i] != real[i] and alias[i] != "any"):
            return False
    return True
