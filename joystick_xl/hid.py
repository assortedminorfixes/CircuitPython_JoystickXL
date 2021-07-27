"""
Initial USB configuration tools for use in ``boot.py`` setup.

This module provides the necessary functions to create a CircuitPython USB HID device
with a descriptor that includes the configured type and quantity of inputs.
"""

import usb_hid  # type: ignore (this is a CircuitPython built-in)

from joystick_xl import __version__


def create_joystick(axes: int = 4, buttons: int = 24, hats: int = 0) -> usb_hid.Device:
    """
    Create the ``usb_hid.Device`` required by ``usb_hid.enable()`` in ``boot.py``.

    :param axes: The number of axes to support, from 0 to 8.  (Default is 4)
    :type axes: int, optional
    :param buttons: The number of buttons to support, from 0 to 128.  (Default is 24)
    :type buttons: int, optional
    :param hats: The number of hat switches to support, from 0 to 4.  (Default is 0)
    :type hats: int, optional
    :return: A ``usb_hid.Device`` object with a descriptor identifying it as a joystick
        with the specified number of buttons, axes and hat switches.
    :rtype: ``usb_hid.Device``
    """
    _num_axes = axes
    _num_buttons = buttons
    _num_hats = hats

    # Validate the number of configured axes, buttons and hats.
    if _num_axes < 0 or _num_axes > 8:
        raise ValueError("Axis count must be from 0-8.")

    if _num_buttons < 0 or _num_buttons > 128 or _num_buttons % 8 != 0:
        raise ValueError("Button count must be from 0-128 and divisible by 8.")

    if _num_hats < 0 or _num_hats > 4 or _num_hats % 2 != 0:
        raise ValueError("Hat count must be from 0-4 and divisible by 2.")

    _report_length = 0

    # Formatting is disabled below to allow the USB descriptor elements to be
    # grouped and annotated such that the descriptor is readable and maintainable.

    # fmt: off
    _descriptor = bytearray((
        0x05, 0x01,                         # : USAGE_PAGE (Generic Desktop)
        0x09, 0x04,                         # : USAGE (Joystick)
        0xA1, 0x01,                         # : COLLECTION (Application)
        0x85, 0xFF,                         # :   REPORT_ID (Set at runtime, index=7)
    ))

    if _num_axes > 0:
        for i in range(_num_axes):
            _descriptor.extend(bytes((
                0x09, min(0x30 + i, 0x36)   # :     USAGE (X,Y,Z,Rx,Ry,Rz,S0,S1)
            )))

        _descriptor.extend(bytes((
            0x15, 0x81,                     # :     LOGICAL_MINIMUM (-127)
            0x25, 0x7F,                     # :     LOGICAL_MAXIMUM (127)
            0x75, 0x08,                     # :     REPORT_SIZE (8)
            0x95, _num_axes,                # :     REPORT_COUNT (num_axes)
            0x81, 0x02,                     # :     INPUT (Data,Var,Abs)
        )))

        _report_length = _num_axes

    if _num_hats > 0:
        for i in range(_num_hats):
            _descriptor.extend(bytes((
                0x09, 0x39,                 # :     USAGE (Hat switch)
            )))

        _descriptor.extend(bytes((
            0x15, 0x00,                     # :     LOGICAL_MINIMUM (0)
            0x25, 0x07,                     # :     LOGICAL_MAXIMUM (7)
            0x35, 0x00,                     # :     PHYSICAL_MINIMUM (0)
            0x46, 0x3B, 0x01,               # :     PHYSICAL_MAXIMUM (315)
            0x65, 0x14,                     # :     UNIT (Eng Rot:Angular Pos)
            0x75, 0x04,                     # :     REPORT_SIZE (4)
            0x95, _num_hats,                # :     REPORT_COUNT (num_hats)
            0x81, 0x42,                     # :     INPUT (Data,Var,Abs,Null)
        )))

        _report_length += int(_num_hats / 2)

    # *** padding bits may need to be inserted here ***

    if _num_buttons > 0:
        _descriptor.extend(bytes((
            0x05, 0x09,                     # :     USAGE_PAGE (Button)
            0x19, 0x01,                     # :     USAGE_MINIMUM (Button 1)
            0x29, _num_buttons,             # :     USAGE_MAXIMUM (num_buttons)
            0x15, 0x00,                     # :     LOGICAL_MINIMUM (0)
            0x25, 0x01,                     # :     LOGICAL_MAXIMUM (1)
            0x95, _num_buttons,             # :     REPORT_COUNT (num_buttons)
            0x75, 0x01,                     # :     REPORT_SIZE (1)
            0x81, 0x02,                     # :     INPUT (Data,Var,Abs)
        )))

        _report_length += int(_num_buttons / 8)

    # *** padding bits may need to be inserted here ***

    _descriptor.extend(bytes((
        0xC0,                               # : END_COLLECTION
    )))
    # fmt: on

    # write configuration data to boot.out using 'print'
    print(
        "JoystickXL",
        __version__,
        "(",
        _num_axes,
        "axes,",
        _num_buttons,
        "buttons,",
        _num_hats,
        "hats,",
        _report_length,
        "report bytes )",
    )

    return usb_hid.Device(
        report_descriptor=bytes(_descriptor),
        usage_page=0x01,  # same as USAGE_PAGE from descriptor above
        usage=0x04,  # same as USAGE from descriptor above
        in_report_length=_report_length,  # length (in bytes) of reports to host
        out_report_length=0,  # length (in bytes) of reports from host
        report_id_index=7,  # 0-based byte position of report id index in descriptor
    )
