#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# hp3458a.py: Driver for the HP3458a Digital Voltmeter.
#
# © 2018 Nuno Mendes (nuno.laurentino.mendes@cern.ch).
#
# This file is a part of the InstrumentKit project.
# Licensed under the AGPL version 3.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Driver for the HP3458a Digital Voltmeter

Originally contributed and copyright held by Nuno Mendes (nuno.laurentino.mendes@cern.ch)

An unrestricted license has been provided to the maintainers of the Instrument
Kit project.
"""



from __future__ import absolute_import
import time

import quantities as pq
import instruments.generic_hpml.hpml_multimeter

from instruments.abstract_instruments import Multimeter
from instruments.util_fns import assume_units, bool_property, enum_property

# CLASSES #####################################################################


class HP3458a(instruments.generic_hpml.hpml_multimeter.HpmlMultimeter):
    """The `HP3458a` is a 8.5 digit bench multimeter.

    It supports DCV, ACV, ACV + DCV, 2 wire Ohms, 4 wire Ohms, DCV/DCV Ratio,
    ACV/DCV Ratio, Offset compensated 2 wire Ohms and Offset compensated 4 wire
    Ohms measurements.
    The 3458A is a pre-SCPI instrument.

    """

    def __init__(self, filelike):
        super().__init__(filelike)
        self.terminator = "\r"
        #self.write('OFORMAT DREAL')




if __name__ == '__main__':
    multimeter = HP3458a.open_visa('GPIB0::23::INSTR')

    # print(multimeter.mode)

    # This does not work yet because the getter is not prepared to
    #multimeter.mode = multimeter.Mode.current_dc

    print(multimeter.measure(multimeter.Mode.current_dc))
