import os
from platformio.platforms.base import BasePlatform


class Lattice_ice40Platform(BasePlatform):
    """
    The iCE40 family of ultra-low power, non-volatile FPGAs has five devices
    with densities ranging from 384 to 7680 Look-Up Tables (LUTs). In addition
    to LUT-based,low-cost programmable logic, these devices feature Embedded
    Block RAM (EBR), Non-volatile Configuration Memory (NVCM) and Phase Locked
    Loops (PLLs). These features allow the devices to be used in low-cost,
    high-volume consumer and system applications.

    http://www.latticesemi.com/Products/FPGAandCPLD/iCE40.aspx
    """

    PACKAGES = {

        "toolchain-icestorm": {

            # alias is used for quick access to package.
            "alias": "toolchain",

            # Flag which allows PlatformIO to install this package by
            # default via `> platformio install test` command
            "default": True
        },
    }

    def get_build_script(self):
            """ Returns a path to build script """

            # You can return static path
            # return "/path/to/test-builder.py"

            # or detect dynamically if `test-builder.py` is located in the same
            # folder with `test.py`
            return os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "lattice_ice40-builder.py"
            )
