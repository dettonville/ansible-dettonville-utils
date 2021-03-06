# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.dettonville.utils.plugins.filter import ini

import pytest

import collections
OrderedDict = getattr(collections, 'OrderedDict', dict)

dict_data = OrderedDict([
    ('DEFAULT', OrderedDict([('remove_unused_original_minimum_age_seconds', '16000')])),
    ('libvirt', OrderedDict([('cpu_mode', 'host-model'), ('disk_cachemodes', 'file=directsync,block=none')])),
    ('database', OrderedDict([('idle_timeout', '900'), ('max_pool_size', '30')]))
])

ini_data = '''[DEFAULT]
remove_unused_original_minimum_age_seconds = 16000

[libvirt]
cpu_mode = host-model
disk_cachemodes = file=directsync,block=none

[database]
idle_timeout = 900
max_pool_size = 30'''

ini_no_default = '''[libvirt]
cpu_mode = host-model
disk_cachemodes = file=directsync,block=none

[database]
idle_timeout = 900
max_pool_size = 30'''


@pytest.mark.skipif(OrderedDict is dict, reason="requires python2.7 or higher")
def test_to_ini():
    assert ini.to_ini(dict_data) == ini_data


def test_from_ini():
    assert ini.from_ini(ini_data) == dict_data
    assert 'DEFAULT' not in ini.from_ini(ini_no_default)
