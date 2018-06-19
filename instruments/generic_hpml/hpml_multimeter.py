"""
Provides support for HPML multimeters
"""
import enum
import quantities


from instruments.util_fns import assume_units, enum_property, int_property
from instruments.abstract_instruments import Multimeter


class HpmlMultimeter(Multimeter):

    """
    Base class for all instruments compatible with HP Multimeter Language.
    Inherits from `~instruments.Instrument`.

    Example usage:

    >>> import instruments as ik
    >>> inst = ik.generic_scpi.SCPIInstrument.open_visa('GPIB0::23::INSTR')
    >>> print(inst.name)
    """

    class Mode(enum.Enum):

        """
        Enum of valid measurement modes for HP Multimeter Language
        """
        current_ac = 7
        current_dc = 6
        current_acdc = 8

        voltage_ac = 2
        voltage_dc = 1
        voltage_acdc = 3

        frequency = 9
        period = 10

        fourpt_resistance = 5
        resistance = 4

        direct_sampling_ac = 11
        direct_sampling_dc = 12

        sub_sampling_ac = 13
        sub_sampling_dc = 14


    class Format(enum.Enum):
        """

        """

        #  ASCII-15 bytes per reading (see 1st and 2nd Remarks below)
        ascii = 1

        # Single Integer-16 bits 2's complement (2 bytes per reading)
        sint = 2

        # Double Integer-32 bits 2's complement (4 bytes per reading)
        dint = 3

        # Single Real-(IEEE-754) 32 bits, (4 bytes per reading)
        sreal = 4

        # Double Real-(IEEE-754) 64 bits, (8 bytes per reading)
        dreal = 5


    class ToggableMode(enum.Enum):
        """
        Toggable modes (ON/OFF)
        """
        off = 0
        on = 1


    class TriggerMode(enum.Enum):
        """
        Valid trigger sources for HPML Multimeters.

        """
        # Used with: TARM, TRIG, NRDGS
        ## Occurs automatically (whenever required)
        auto = 1

        # Occurs on negative edge transition on the multimeter's external trigger input
        external = 2

        # Occurs when the multimeter's output buffer is empty, reading memory is off or empty,
        # and the controller requests data
        syn = 5

        # Used with: TARM, TRIG
        # Occurs once (upon receipt of TARM SGL or TRIG SGL command, then becomes HOLD)
        single = 3

        # Suspends measurements
        hold = 4

        # Used with: TRIG, NRDGS
        ## Occurs when the power line voltage crosses zero volts
        level = 7

        ## Occurs when the specified voltage is reached on the specified slope of the input signa
        line = 8


    class InputRange(enum.Enum):

        """
        Valid device range parameters outside of directly specifying the range.
        """
        minimum = "MIN"
        maximum = "MAX"
        default = "DEF"
        automatic = "AUTO"

    # PROPERTIES #
    mode = enum_property(
        command="FUNC",
        enum=Mode,
        input_decoration=lambda x: HpmlMultimeter._mode_parse(x),
        doc="""
            Gets/sets the current measurement mode for the multimeter.

            Example usage:

            >>> dmm.mode = dmm.Mode.voltage_dc

            :type: `~HpmlMultimeter.Mode`
            """)

    oformat = enum_property(
        command="OFORMAT",
        enum=Format,
        input_decoration=lambda x: int(x),
        doc="""
            Gets/sets the output format for the multimeter.
            Designates the GPIB output format for readings sent directly to the 
            controller or transferred from reading memory to the controller.
            
            Example usage:

            >>> dmm.oformat = dmm.Format.dreal

            :type: `~HpmlMultimeter.Format`
            """)

    mformat = enum_property(
        command="MFORMAT",
        enum=Format,
        input_decoration=lambda x: int(x),
        doc="""
                Gets/sets the memory format for the multimeter.
                Clears reading memory and designates the storage format for new readings.

                Example usage:

                >>> dmm.mformat = dmm.Format.dreal

                :type: `~HpmlMultimeter.Format`
                """)

    tarm_mode = enum_property(
        command="TARM",
        enum=TriggerMode,
        input_decoration=lambda x: int(x),
        doc="""
                Defines the event that enables (arms) the trigger event (TRIG command). 
                You can also use this command to perform multiple measurement cycles.

                Example usage:

                >>> dmm.tarm_mode = dmm.TriggerMode.syn

                :type: `~HpmlMultimeter.TriggerMode`
                """)

    trigger_mode = enum_property(
        command="TRIG",
        enum=TriggerMode,
        input_decoration=lambda x: int(x),
        doc="""
                Gets/sets the Multimeter trigger mode.

                Example usage:

                >>> dmm.trigger_mode = dmm.TriggerMode.external

                :type: `~HpmlMultimeter.TriggerMode`
            """)

    azero = enum_property(
        command="AZERO",
        enum=ToggableMode,
        input_decoration=lambda x: int(x),
        doc="""
                Enables or disables the autozero function. The autozero function
                applies only to DC voltage, DC current, and resistance measurements.

                Example usage:

                >>> dmm.azero = dmm.ToggableMode.off

                :type: `~HpmlMultimeter.ToggableMode`
            """)

    display = enum_property(
        command="DISP",
        enum=ToggableMode,
        input_decoration=lambda x: int(x),
        doc="""
                Turns the display ON/OFF

                Example usage:

                >>> dmm.display = dmm.ToggableMode.off

                :type: `~HpmlMultimeter.ToggableMode`
            """)

    @property
    def input_range(self):
        """
        Gets/sets the device input range for the device range for the currently
        set multimeter mode.

        Example usages:

        >>> dmm.input_range = dmm.InputRange.automatic
        >>> dmm.input_range = 1 * pq.millivolt

        :units: As appropriate for the current mode setting.
        :type: `~quantities.Quantity`, or `~HpmlMultimeter.InputRange`
        """
        raise NotImplementedError

    @input_range.setter
    def input_range(self, newval):
        raise NotImplementedError

    @property
    def relative(self):
        raise NotImplementedError

    @relative.setter
    def relative(self, newval):
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        The name of the connected instrument.

        :rtype: `str`
        """
        return self.query('ID?')

    @property
    def self_test_ok(self):
        """
        Gets the results of the instrument's self test. Causes the multi

        :rtype: `bool`
        """
        result = self.write('INPUT BUF; TEST')
        # Should sleep here?
        return result


    # BASIC COMMANDS ##

    def reset(self):
        """
        Sets the multimeter to the power-on state without cycling power.
        """
        self.sendcmd('RESET')


    def clear(self):
        """
        Clear instrument. Consult manual for specifics related to that
        instrument.
        """
        self.sendcmd('CLEAR')

    def trigger(self):
        """
        Send a software trigger event to the instrument. On most instruments
        this will cause some sort of hardware event to start. For example, a
        multimeter might take a measurement.

        This software trigger usually performs the same action as a hardware
        trigger to your instrument.

        The Trigger (TRG) command triggers the device if BUS is the selected
        trigger source, otherwise, *TRG is ignored
        """
        self.sendcmd('TRIG 1')

    def measure(self, mode=None):
        """
        Instruct the multimeter to perform a one time measurement. The
        instrument will use default parameters for the requested measurement.
        The measurement will immediately take place, and the results are
        directly sent to the instrument's output buffer.

        Method returns a Python quantity consisting of a numpy array with the
        instrument value and appropriate units. If no appropriate units exist,
        (for example, continuity), then return type is `float`.

        :param mode: Desired measurement mode. If set to `None`, will default
            to the current mode.
        :type mode: `~HpmlMultimeter.Mode`
        """
        if mode is None:
            mode = self.mode
        else:
            self.mode = mode.value
        if not isinstance(mode, HpmlMultimeter.Mode):
            raise TypeError("Mode must be specified as a SCPIMultimeter.Mode "
                            "value, got {} instead.".format(type(mode)))
        # pylint: disable=no-member

        # Should enable trigger function
        self.trigger()

        value = self.read(size=8, encoding='IEEE-754/64')

        return value * UNITS[mode]

    def read(self, size=-1, encoding='utf-8'):
        return super().read(size, encoding)

    @staticmethod
    def _mode_parse(val):
        """
        When given a string of the form

        '6, 1.0E-4'

        this function will return just the first component representing the mode
        the multimeter is currently in.

        :param str val: Input string to be parsed.

        :rtype: `str`
        """
        return int(val.split(',')[0])

UNITS = {
    HpmlMultimeter.Mode.voltage_dc:  quantities.volt,
    HpmlMultimeter.Mode.voltage_ac:  quantities.volt,
    HpmlMultimeter.Mode.current_ac:  quantities.amp,
    HpmlMultimeter.Mode.current_dc:  quantities.amp,
    HpmlMultimeter.Mode.resistance:  quantities.ohm,
    HpmlMultimeter.Mode.fourpt_resistance: quantities.ohm,
    HpmlMultimeter.Mode.frequency:   quantities.hertz,
    HpmlMultimeter.Mode.period:      quantities.second,
}

