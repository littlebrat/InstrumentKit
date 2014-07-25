#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# hp6652a.py: Python class for the HP 6652a power supply
##
# © 2014 Wil Langford (wil.langford+instrumentkit@gmail.com)
#
# adapted from hp6624a.py by:
# © 2014 Steven Casagrande (scasagrande@galvant.ca).
#
# This file is a part of the InstrumentKit project.
# Licensed under the AGPL version 3.
##
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
##

## FEATURES ####################################################################

from __future__ import division

## IMPORTS #####################################################################

import quantities as pq

from instruments.abstract_instruments import (PowerSupply)
from instruments.util_fns import assume_units

## CLASSES #####################################################################


class HP6652a(PowerSupply):
    """
    The HP6652a is a single output power supply.

    According to the manual, this class MIGHT be usable for any HP power supply
    with a model number HP66XYA, where X is in {4,5,7,8,9} and Y is a digit(?).
    (e.g. HP6652A and HP6671A)

    HOWEVER, it has only been tested by the author with an HP6652A power supply.
    
    Example usage:
    
    >>> import instruments as ik
    >>> psu = ik.hp.HP6652a.open_serial('/dev/ttyUSB0', 57600)
    >>> psu.voltage = 10 # Sets output voltage to 10V.
    """
    
    def __init__(self, filelike):
        super(HP6652a, self).__init__(filelike)

    ## ENUMS ##

    # I don't know of any possible enumerations supported
    # by this instrument.

    ## PROPERTIES ##

    @property
    def voltage(self):
        """
        Gets/sets the output voltage.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~quantities.Quantity`
        """
        return pq.Quantity(
            float(self.query('VOLT?')),
            pq.volt
        )

    @voltage.setter
    def voltage(self, newval):
        self.sendcmd(
            'VOLT {}'.format(
                assume_units(newval, pq.volt).rescale(pq.volt).magnitude
            )
        )

    @property
    def current(self):
        """
        Gets/sets the output current.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A}` otherwise.
        :type: `float` or `~quantities.Quantity`
        """
        return pq.Quantity(
            float(self.query('CURR?')),
            pq.amp
        )

    @current.setter
    def current(self, newval):
        self.sendcmd(
            'CURR {}'.format(
                assume_units(newval, pq.amp).rescale(pq.amp).magnitude
            )
        )

    @property
    def voltage_sense(self):
        """
        Gets the actual voltage as measured by the sense wires for the
        specified channel.

        :units: :math:`\\text{V}` (volts)
        :rtype: `~quantities.Quantity`
        """
        return pq.Quantity(
            float(self.query('MEAS:VOLT?')),
            pq.volt
        )

    @property
    def current_sense(self):
        """
        Gets the actual output current as measured by the instrument for
        the specified channel.

        :units: :math:`\\text{A}` (amps)
        :rtype: `~quantities.Quantity`
        """
        return pq.Quantity(
            float(self.query('MEAS:CURR?')),
            pq.amp
        )

    @property
    def overvoltage(self):
        """
        Gets/sets the overvoltage protection setting for the specified channel.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~quantities.Quantity`
        """
        return pq.Quantity(
            float(self.query('VOLT:PROT?')),
            pq.volt
        )

    @overvoltage.setter
    def overvoltage(self, newval):
        self.sendcmd(
            'VOLT:PROT {}'.format(
                assume_units(newval, pq.volt).rescale(pq.volt).magnitude
            )
        )

    @property
    def overcurrent(self):
        """
        Gets/sets the overcurrent protection setting for the specified channel.

        This is a toggle setting. It is either on or off.

        :type: `bool`
        """
        return (True if self.query('CURR:PROT:STAT?')
                is '1' else False)

    @overcurrent.setter
    def overcurrent(self, newval):
        if newval is True:
            newval = 1
        else:
            newval = 0
        self.sendcmd('CURR:PROT:STAT {}'.format(newval))

    @property
    def output(self):
        """
        Gets/sets the outputting status of the specified channel.

        This is a toggle setting. True will turn on the channel output
        while False will turn it off.

        :type: `bool`
        """
        return (True if self.query('OUTP?')
                is '1' else False)

    @output.setter
    def output(self, newval):
        if newval is True:
            newval = 1
        else:
            newval = 0
        self.sendcmd('OUTP {}'.format(newval))

    @property
    def channel(self):
        return self

    @property
    def display_mode_text(self):
        """
        Gets/sets the display mode.

        This is a toggle setting. True will allow text to be sent to the
        front-panel LCD with the display_text() method.  False returns to
        the normal display mode.

        :type: `bool`
        """
        return (True if self.query('DISP:MODE?')
                is 'TEXT' else False)

    @display_mode_text.setter
    def display_mode_text(self, newval):
        if newval is True:
            newval = 'TEXT'
        else:
            newval = 'NORM'
        self.sendcmd('DISP:MODE {}'.format(newval))

    ## METHODS ##

    def reset(self):
        """
        Reset overvoltage and overcurrent errors to resume operation.
        """
        self.sendcmd('OUTP:PROT:CLE')

    def display_text(self, text_to_display):
        """
        Sends up to 12 arbitrary (uppercase) alphanumerics to be sent to
        the front-panel LCD display.  Some punctuation is allowed, and
        can affect the number of characters allowed.  See the programming
        manual for the HP6652A for more details.

        Because the maximum valid number of possible characters is 15 (counting
        the possible use of punctuation), the text will be truncated to 15
        characters before the command is sent to the instrument.

        If an invalid string is sent, the command will fail silently.  Any
        lowercase letters in the text_to_display will be converted to
        uppercase before the command is sent to the instrument.

        No attempt to validate punctuation is currently made.

        Because the string cannot be read back from the instrument, this
        method returns the actual string value sent.

        :type: 'str'
        """

        if len(text_to_display) > 15:
            text_to_display = text_to_display[:15]
        text_to_display = text_to_display.upper()

        self.sendcmd('DISP:TEXT "{}"'.format(text_to_display))

        return text_to_display
