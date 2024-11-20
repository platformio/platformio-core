#
# Copyright (c) 2013-2015 Grigori Goronzy <greg@chown.ath.cx>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import serial
import sys
import os
import time
import struct
import re
import errno
from stcgal.models import MCUModelDatabase
from stcgal.utils import Utils
from stcgal.options import Stc89Option
from stcgal.options import Stc12Option
from stcgal.options import Stc12AOption
from stcgal.options import Stc15Option
from stcgal.options import Stc15AOption
from stcgal.options import Stc8Option
from abc import ABC
from abc import abstractmethod
import functools
import tqdm

try:
    import usb.core
    import usb.util
    _usb_available = True
except ImportError:
    _usb_available = False


class StcFramingException(Exception):
    """Something wrong with packet framing or checksum"""
    pass


class StcProtocolException(Exception):
    """High-level protocol issue, like wrong packet type"""
    pass


class StcBaseProtocol(ABC):
    """Basic functionality for STC BSL protocols"""

    PACKET_START = bytes([0x46, 0xb9])
    """magic word that starts a packet"""

    PACKET_END = bytes([0x16])
    """magic byte that ends a packet"""

    PACKET_MCU = bytes([0x68])
    """magic byte for packets received from MCU"""

    PACKET_HOST = bytes([0x6a])
    """magic byte for packets sent by host"""

    PARITY = serial.PARITY_NONE
    """parity configuration for serial communication"""

    def __init__(self, port, baud_handshake, baud_transfer):
        self.port = port
        self.baud_handshake = baud_handshake
        self.baud_transfer = baud_transfer

        self.mcu_magic = 0
        self.mcu_clock_hz = 0.0
        self.mcu_bsl_version = ""
        self.options = None
        self.model = None
        self.split_eeprom = None
        self.split_code = None
        self.uid = None
        self.debug = False
        self.status_packet = None
        self.protocol_name = None
        self.progress = None
        self.progress_cb = self.progress_bar_cb
        self.linearBaseAddress = 0

    def progress_text_cb(self, current, written, maximum):
        print(current, written, maximum)

    def progress_bar_cb(self, current, written, maximum):
        if not self.progress:
            self.progress = tqdm.tqdm(
                total=maximum,
                unit="Bytes",
                desc="Writing flash",
                dynamic_ncols=True,
                ascii=True  # Use ASCII-only output for better compatibility
            )
        self.progress.n = current  # Set the current progress
        self.progress.refresh()  # Force the progress bar to refresh
        if current == maximum:
            self.progress.close()


    def dump_packet(self, data, receive=True):
        if self.debug:
            print("%s Packet data: %s" % (("<-" if receive else "->"),
                  Utils.hexstr(data, " ")), file=sys.stderr)

    def read_bytes_safe(self, num):
        """Read data from serial port with timeout handling

        Read timeouts should raise an exception, that is the Python way."""

        data = self.ser.read(num)
        if len(data) != num:
            raise serial.SerialTimeoutException("read timeout")

        return data

    def extract_payload(self, packet):
        """Extract the payload of a packet"""

        if packet[-1] != self.PACKET_END[0]:
            self.dump_packet(packet)
            raise StcFramingException("incorrect frame end")

        return packet[5:-1]

    @abstractmethod
    def write_packet(self, packet_data, epilogue_len = 0):
        pass

    def read_packet(self):
        """Read and check packet from MCU.

        Reads a packet of data from the MCU and and do
        validity and checksum checks on it.

        Returns packet payload or None in case of an error.
        """

        # read and check frame start magic
        packet = bytes()
        packet += self.read_bytes_safe(1)
        # Some (?) BSL versions don't send a frame start with the status
        # packet. Let's be liberal and accept that always, just in case.
        if packet[0] == self.PACKET_MCU[0]:
            packet = self.PACKET_START + self.PACKET_MCU
        else:
            if packet[0] != self.PACKET_START[0]:
                self.dump_packet(packet)
                raise StcFramingException("incorrect frame start")
            packet += self.read_bytes_safe(1)
            if packet[1] != self.PACKET_START[1]:
                self.dump_packet(packet)
                raise StcFramingException("incorrect frame start")

            # read direction
            packet += self.read_bytes_safe(1)
            if packet[2] != self.PACKET_MCU[0]:
                self.dump_packet(packet)
                raise StcFramingException("incorrect packet direction magic")

        # read length
        packet += self.read_bytes_safe(2)

        # read packet data
        packet_len, = struct.unpack(">H", packet[3:5])
        packet += self.read_bytes_safe(packet_len - 3)

        # verify checksum and extract payload
        payload = self.extract_payload(packet)

        self.dump_packet(packet, receive=True)

        # payload only is returned
        return payload

    def print_mcu_info(self):
        """Print MCU status information"""

        MCUModelDatabase.print_model_info(self.model)
        print("Target frequency: %.3f MHz" % (self.mcu_clock_hz / 1E6))
        print("Target BSL version: %s" % self.mcu_bsl_version)

    def pulse(self, character=b"\x7f", timeout=0):
        """Send a sequence of bytes for synchronization with MCU"""

        duration = 0
        while True:
            if timeout > 0 and duration > timeout:
                raise serial.SerialTimeoutException("pulse timeout")
            self.ser.write(character)
            self.ser.flush()
            time.sleep(0.030)
            duration += 0.030
            if self.ser.inWaiting() > 0: break

    def initialize_model(self):
        """Initialize model-specific information"""

        self.mcu_magic, = struct.unpack(">H", self.status_packet[20:22])
        try:
            self.model = MCUModelDatabase.find_model(self.mcu_magic)
        except NameError:
            msg = ("WARNING: Unknown model %02X%02X!" %
                (self.mcu_magic >> 8, self.mcu_magic & 0xff))
            print(msg, file=sys.stderr)
            self.model = MCUModelDatabase.MCUModel(name="UNKNOWN",
                magic=self.mcu_magic, total=63488, code=63488, eeprom=0)
        except ValueError as ex:
            raise StcProtocolException(ex)

        # special case for duplicated mcu magic,
        #   0xf294 (STC15F104W, STC15F104E)
        #   0xf2d4 (STC15L104W, STC15L104E)
        # duplicated mcu magic can be found using command,
        #   grep -o 'magic=[^,]*' models.py | sort | uniq -d
        if self.mcu_magic in (0xF294, 0xF2D4):
            mcu_name = self.model.name[:-1]
            mcu_name += "E" if self.status_packet[17] < 0x70 else "W"
            self.model = self.model._replace(name = mcu_name)

    def get_status_packet(self):
        """Read and decode status packet"""

        packet = self.read_packet()
        if packet[0] == 0x80:
            # need to re-ack
            self.ser.parity = serial.PARITY_EVEN
            packet = (self.PACKET_START
                      + self.PACKET_HOST
                      + bytes([0x00, 0x07, 0x80, 0x00, 0xF1])
                      + self.PACKET_END)
            self.dump_packet(packet, receive=False)
            self.ser.write(packet)
            self.ser.flush()
            self.pulse()
            packet = self.read_packet()
        return packet

    def get_iap_delay(self, clock_hz):
        """IAP wait states for STC12A+ (according to datasheet(s))"""

        iap_wait = 0x80
        if clock_hz < 1E6: iap_wait = 0x87
        elif clock_hz < 2E6: iap_wait = 0x86
        elif clock_hz < 3E6: iap_wait = 0x85
        elif clock_hz < 6E6: iap_wait = 0x84
        elif clock_hz < 12E6: iap_wait = 0x83
        elif clock_hz < 20E6: iap_wait = 0x82
        elif clock_hz < 24E6: iap_wait = 0x81

        return iap_wait

    def set_option(self, name, value):
        self.options.set_option(name, value)

    def reset_device(self, resetcmd=False, resetpin=False, invertreset=False):
        if not resetcmd:
            print("Cycling power: ", end="")
            sys.stdout.flush()
            
            if resetpin == "rts":
                self.ser.setRTS(True)
            elif resetpin == "dtr":
                self.ser.setDTR(True)
            elif resetpin == "rts_inverted":
                self.ser.setRTS(False)
            else: # dtr_inverted
                self.ser.setDTR(False)
				
            time.sleep(0.25)
            
            if resetpin == "rts":
                self.ser.setRTS(False)
            elif resetpin == "dtr":
                self.ser.setDTR(False)
            elif resetpin == "rts_inverted":
                self.ser.setRTS(True)
            else: # dtr_inverted
                self.ser.setDTR(True)
				
            time.sleep(0.030)
            print("done")
        else:
            print("Cycling power via shell cmd: " + resetcmd)
            os.system(resetcmd)

        print("Waiting for MCU: ", end="")
        sys.stdout.flush()

    def connect(self, autoreset=False, resetcmd=False, resetpin=False):
        """Connect to MCU and initialize communication.

        Set up serial port, send sync sequence and get part info.
        """

        self.ser = serial.Serial(port=self.port, parity=self.PARITY)
        # set baudrate separately to work around a bug with the CH340 driver
        # on older Linux kernels
        self.ser.baudrate = self.baud_handshake

        # fast timeout values to deal with detection errors
        self.ser.timeout = 0.5
        self.ser.interCharTimeout = 0.5

        # avoid glitches if there is something in the input buffer
        self.ser.flushInput()

        if autoreset:
            self.reset_device(resetcmd, resetpin)
        else:
            print("Waiting for MCU, please cycle power: ", end="")
            sys.stdout.flush()

        # send sync, and wait for MCU response
        # ignore errors until we see a valid response
        self.status_packet = None
        while not self.status_packet:
            try:
                self.pulse()
                self.status_packet = self.get_status_packet()
                if len(self.status_packet) < 23:
                    raise StcProtocolException("status packet too short")
            except (StcFramingException, serial.SerialTimeoutException): pass
        print("done")

        # conservative timeout values
        self.ser.timeout = 15.0
        self.ser.interCharTimeout = 1.0

        self.initialize_model()

    @abstractmethod
    def initialize_status(self, status_packet):
        """Initialize internal state from status packet"""
        pass

    @abstractmethod
    def initialize_options(self, status_packet):
        """Initialize options from status packet"""
        pass

    def initialize(self, base_protocol=None):
        """
        Initialize from another instance. This is an alternative for calling
        connect() and is used by protocol autodetection.
        """
        if base_protocol:
            self.ser = base_protocol.ser
            self.ser.parity = self.PARITY
            packet = base_protocol.status_packet
            packet = (self.PACKET_START
                      + self.PACKET_MCU
                      + struct.pack(">H", len(packet) + 4)
                      + packet
                      + self.PACKET_END)
            self.status_packet = self.extract_payload(packet)
            self.mcu_magic = base_protocol.mcu_magic
            self.model = base_protocol.model

        self.initialize_status(self.status_packet)
        self.print_mcu_info()
        self.initialize_options(self.status_packet)

    def disconnect(self):
        """Disconnect from MCU"""

        # reset mcu
        packet = bytes([0x82])
        self.write_packet(packet)
        self.ser.close()
        print("Disconnected!")


class StcAutoProtocol(StcBaseProtocol):
    """
    Protocol handler for autodetection of protocols. Does not implement full
    functionality for any device class.
    """

    def initialize_model(self):
        super().initialize_model()

        protocol_database = [("stc89", r"STC(89|90)(C|LE)\d"),
                             ("stc12a", r"STC12(C|LE)\d052"),
                             ("stc12b", r"STC12(C|LE)(52|56)"),
                             ("stc12", r"(STC|IAP)(10|11|12)\D"),
                             ("stc15a", r"(STC|IAP)15[FL][012]0\d(E|EA|)$"),
                             ("stc15", r"(STC|IAP|IRC)15\D"),
                             ("stc8g", r"STC8H1K\d\d$"),
                             ("stc8g", r"STC8G"),
                             ("stc8d", r"STC8H"),
                             ("stc8d", r"STC32"),
                             ("stc8d", r"STC8A8K\d\dD\d"),
                             ("stc8", r"STC8\D")]

        for protocol_name, pattern in protocol_database:
            if re.match(pattern, self.model.name):
                self.protocol_name = protocol_name
                break
        else:
            self.protocol_name = None

    def initialize_options(self, status_packet):
        raise NotImplementedError

    def initialize_status(self, status_packet):
        raise NotImplementedError

    def write_packet(self, packet_data, epilogue_len = 0):
        raise NotImplementedError


class Stc89Protocol(StcBaseProtocol):
    """Protocol handler for STC 89/90 series"""

    PARITY = serial.PARITY_NONE
    """Parity configuration - these don't use any parity"""

    PROGRAM_BLOCKSIZE = 128
    """block size for programming flash"""

    def __init__(self, port, baud_handshake, baud_transfer):
        StcBaseProtocol.__init__(self, port, baud_handshake, baud_transfer)

        self.cpu_6t = None

    def extract_payload(self, packet):
        """Verify the checksum of packet and return its payload"""

        packet_csum = packet[-2]
        calc_csum = sum(packet[2:-2]) & 0xff
        if packet_csum != calc_csum:
            self.dump_packet(packet)
            raise StcFramingException("packet checksum mismatch")

        payload = StcBaseProtocol.extract_payload(self, packet)
        return payload[:-1]

    def write_packet(self, packet_data, epilogue_len = 0):
        """Send packet to MCU.

        Constructs a packet with supplied payload and sends it to the MCU.
        """

        # frame start and direction magic
        packet = bytes()
        packet += self.PACKET_START
        packet += self.PACKET_HOST

        # packet length and payload
        packet += struct.pack(">H", len(packet_data) + 5)
        packet += packet_data

        # checksum and end code
        packet += bytes([sum(packet[2:]) & 0xff])
        packet += self.PACKET_END

        self.dump_packet(packet, receive=False)
        self.ser.write(packet)
        self.ser.flush()

    def get_status_packet(self):
        """Read and decode status packet"""

        status_packet = self.read_packet()
        if status_packet[0] != 0x00:
            raise StcProtocolException("incorrect magic in status packet")
        return status_packet

    def initialize_options(self, status_packet):
        """Initialize options"""

        if len(status_packet) < 20:
            raise StcProtocolException("invalid options in status packet")

        self.options = Stc89Option(status_packet[19])
        self.options.print()

    def calculate_baud(self):
        """Calculate MCU baudrate setting.

        Calculate appropriate baudrate settings for the MCU's UART,
        according to clock frequency and requested baud rate.
        """

        # timing is different in 6T mode
        sample_rate = 16 if self.cpu_6t else 32
        # baudrate is directly controlled by programming the MCU's BRT register
        brt = 65536 - round((self.mcu_clock_hz) / (self.baud_transfer * sample_rate))
        brt_csum = (2 * (256 - brt)) & 0xff
        baud_actual = (self.mcu_clock_hz) / (sample_rate * (65536 - brt))
        baud_error = (abs(self.baud_transfer - baud_actual) * 100.0) / self.baud_transfer
        if baud_error > 5.0:
            print("WARNING: baudrate error is %.2f%%. You may need to set a slower rate." %
                  baud_error, file=sys.stderr)

        # IAP wait states (according to datasheet(s))
        iap_wait = 0x80
        if self.mcu_clock_hz < 5E6: iap_wait = 0x83
        elif self.mcu_clock_hz < 10E6: iap_wait = 0x82
        elif self.mcu_clock_hz < 20E6: iap_wait = 0x81

        # MCU delay after switching baud rates
        delay = 0xa0

        return brt, brt_csum, iap_wait, delay

    def initialize_status(self, status_packet):
        """Decode status packet and store basic MCU info"""

        self.cpu_6t = not bool(status_packet[19] & 1)

        cpu_t = 6.0 if self.cpu_6t else 12.0
        freq_counter = 0
        for i in range(8):
            freq_counter += struct.unpack(">H", status_packet[1+2*i:3+2*i])[0]
        freq_counter /= 8.0
        self.mcu_clock_hz = (self.baud_handshake * freq_counter * cpu_t) / 7.0

        bl_version, bl_stepping = struct.unpack("BB", status_packet[17:19])
        self.mcu_bsl_version = "%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                            chr(bl_stepping))

    def handshake(self):
        """Switch to transfer baudrate

        Switches to transfer baudrate and verifies that the setting works with
        a ping-pong exchange of packets."""

        # check new baudrate
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        brt, brt_csum, iap, delay = self.calculate_baud()
        print("checking ", end="")
        sys.stdout.flush()
        packet = bytes([0x8f])
        packet += struct.pack(">H", brt)
        packet += bytes([0xff - (brt >> 8), brt_csum, delay, iap])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        self.ser.baudrate = self.baud_handshake
        if response[0] != 0x8f:
            raise StcProtocolException("incorrect magic in handshake packet")

        # switch to baudrate
        print("setting ", end="")
        sys.stdout.flush()
        packet = bytes([0x8e])
        packet += struct.pack(">H", brt)
        packet += bytes([0xff - (brt >> 8), brt_csum, delay])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        if response[0] != 0x8e:
            raise StcProtocolException("incorrect magic in handshake packet")

        # ping-pong test
        print("testing ", end="")
        sys.stdout.flush()
        packet = bytes([0x80, 0x00, 0x00, 0x36, 0x01])
        packet += struct.pack(">H", self.mcu_magic)
        for _ in range(4):
            self.write_packet(packet)
            response = self.read_packet()
            if response[0] != 0x80:
                raise StcProtocolException("incorrect magic in handshake packet")

        print("done")

    def erase_flash(self, erase_size, _):
        """Erase the MCU's flash memory.

        Erase the flash memory with a block-erase command.
        flash_size is ignored; not used on STC 89 series.
        """

        blks = ((erase_size + 511) // 512) * 2
        print("Erasing %d blocks: " % blks, end="")
        sys.stdout.flush()
        packet = bytes([0x84, blks, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x80:
            raise StcProtocolException("incorrect magic in erase packet")
        print("done")

    def program_flash(self, data):
        """Program the MCU's flash memory.

        Write data into flash memory, using the PROGRAM_BLOCKSIZE
        as the block size (depends on MCU's RAM size).
        """

        for i in range(0, len(data), self.PROGRAM_BLOCKSIZE):
            packet = bytes(3)
            packet += struct.pack(">H", i)
            packet += struct.pack(">H", self.PROGRAM_BLOCKSIZE)
            packet += data[i:i+self.PROGRAM_BLOCKSIZE]
            while len(packet) < self.PROGRAM_BLOCKSIZE + 7: packet += b"\x00"
            csum = sum(packet[7:]) & 0xff
            self.write_packet(packet)
            response = self.read_packet()
            if len(response) < 1 or response[0] != 0x80:
                raise StcProtocolException("incorrect magic in write packet")
            elif len(response) < 2 or response[1] != csum:
                raise StcProtocolException("verification checksum mismatch")
            self.progress_cb(i, self.PROGRAM_BLOCKSIZE, len(data))
        self.progress_cb(len(data), self.PROGRAM_BLOCKSIZE, len(data))

    def program_options(self):
        """Program option byte into flash"""

        print("Setting options: ", end="")
        sys.stdout.flush()
        msr = self.options.get_msr()
        packet = bytes([0x8d, msr, 0xff, 0xff, 0xff])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x8d:
            raise StcProtocolException("incorrect magic in option packet")
        print("done")


class Stc89AProtocol(StcBaseProtocol):
    """Protocol handler for STC 89/90 series"""

    PARITY = serial.PARITY_NONE
    """Parity configuration - these don't use any parity"""

    PROGRAM_BLOCKSIZE = 128
    """block size for programming flash"""

    def __init__(self, port, baud_handshake, baud_transfer):
        StcBaseProtocol.__init__(self, port, baud_handshake, baud_transfer)

        self.cpu_6t = None

    def extract_payload(self, packet):
        """Verify the checksum of packet and return its payload"""

        packet_csum = packet[-2] + (packet[-3] << 8)
        calc_csum = sum(packet[2:-3]) & 0xffff
        if packet_csum != calc_csum:
            self.dump_packet(packet)
            raise StcFramingException("packet checksum mismatch")

        payload = StcBaseProtocol.extract_payload(self, packet)
        return payload[:-1]

    def write_packet(self, packet_data):
        """Send packet to MCU.

        Constructs a packet with supplied payload and sends it to the MCU.
        """

        # frame start and direction magic
        packet = bytes()
        packet += self.PACKET_START
        packet += self.PACKET_HOST

        # packet length and payload
        packet += struct.pack(">H", len(packet_data) + 6)
        packet += packet_data

        # checksum and end code
        packet += struct.pack(">H", sum(packet[2:]) & 0xffff)
        packet += self.PACKET_END

        self.dump_packet(packet, receive=False)
        self.ser.write(packet)
        self.ser.flush()

    def get_status_packet(self):
        """Read and decode status packet"""

        status_packet = self.read_packet()
        if status_packet[0] != 0x50:
            raise StcProtocolException("incorrect magic in status packet" + str(status_packet[0]))
        return status_packet

    def initialize_options(self, status_packet):
        """Initialize options"""

        if len(status_packet) < 20:
            raise StcProtocolException("invalid options in status packet")
        self.options = Stc89Option(status_packet[1])
        self.options.print()

        self.ser.parity = "E"

    def calculate_baud(self):
        """Calculate MCU baudrate setting.

        Calculate appropriate baudrate settings for the MCU's UART,
        according to clock frequency and requested baud rate.
        """

        # timing is different in 6T mode
        sample_rate = 32 #if self.cpu_6t else 32
        # baudrate is directly controlled by programming the MCU's BRT register
        brt = 65536 - round((self.mcu_clock_hz) / (self.baud_transfer * sample_rate))
        
        baud_actual = (self.mcu_clock_hz) / (sample_rate * (65536 - brt))
        baud_error = (abs(self.baud_transfer - baud_actual) * 100.0) / self.baud_transfer
        if baud_error > 5.0:
            print("WARNING: baudrate error is %.2f%%. You may need to set a slower rate." %
                  baud_error, file=sys.stderr)

        # IAP wait states (according to datasheet(s))
        iap_wait = 0x80
        if self.mcu_clock_hz < 10E6: iap_wait = 0x83
        elif self.mcu_clock_hz < 30E6: iap_wait = 0x82
        elif self.mcu_clock_hz < 50E6: iap_wait = 0x81

        # MCU delay after switching baud rates
        delay = 0xa0

        return brt, iap_wait

    def initialize_status(self, status_packet):
        """Decode status packet and store basic MCU info"""

        self.cpu_6t = not bool(status_packet[1] & 1)

        freq_counter = struct.unpack(">H", status_packet[13:15])[0]
        self.mcu_clock_hz = (12 * freq_counter * self.baud_handshake)

        bl_version, bl_stepping = struct.unpack("BB", status_packet[17:19])
        bl_minor = status_packet[22] & 0x0f
        self.mcu_bsl_version = "%d.%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                               bl_minor, chr(bl_stepping))

    def handshake(self):
        """Switch to transfer baudrate

        Switches to transfer baudrate and verifies that the setting works with
        a ping-pong exchange of packets."""

        # check new baudrate
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        brt,iap = self.calculate_baud()
        print("checking ", end="")
        sys.stdout.flush()
        packet = bytes([0x01])
        packet += struct.pack(">H", brt)
        packet += bytes([iap])
        self.write_packet(packet)
        time.sleep(0.2)
        print(self.baud_transfer)
        response = self.read_packet()
        
        if response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")

        self.ser.baudrate = self.baud_transfer

        # ping-pong test
        print("testing ", end="")
        sys.stdout.flush()
        packet = bytes([0x05, 0x00, 0x00, 0x46, 0xB9])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x05:
            raise StcProtocolException("incorrect magic in handshake packet")

        print("done")

    def reset_device(self, resetcmd=False):
        if not resetcmd:
            print("Cycling power: ", end="")
            sys.stdout.flush()
            self.ser.setDTR(False)
            time.sleep(0.5)
            self.ser.setDTR(True)
            print("done")
        else:
            print("Cycling power via shell cmd: " + resetcmd)
            os.system(resetcmd)

        print("Waiting for MCU: ", end="")
        sys.stdout.flush()

    def erase_flash(self, erase_size, _):
        """Erase the MCU's flash memory.

        Erase the flash memory with a block-erase command.
        flash_size is ignored; not used on STC 89 series.
        """

        print("Erasing All blocks: ", end="")
        sys.stdout.flush()
        packet = bytes([0x03, 0x00, 0x00, 0x46, 0xB9])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x03:
            raise StcProtocolException("incorrect magic in erase packet")

        print("MCU ID: {:x}{:x}{:x}{:x}{:x}{:x}{:x}".format(response[1],response[2],response[3]
        ,response[4],response[5],response[6],response[7]))

        print("done")

    def program_flash(self, data):
        """Program the MCU's flash memory.

        Write data into flash memory, using the PROGRAM_BLOCKSIZE
        as the block size (depends on MCU's RAM size).
        """
        p = 0

        for i in range(0, len(data), self.PROGRAM_BLOCKSIZE):
            packet = bytes(3)
            if p == 0:
                packet = bytes([0x22,0x00,0x00])
            else:
                packet = bytes([0x02])
                packet += int(128 * p).to_bytes(length=2, byteorder='big', signed=True)

            
            p = p + 1
            packet += bytes([0x46, 0xB9])
            packet += data[i:i+self.PROGRAM_BLOCKSIZE]
            
            self.write_packet(packet)

            response = self.read_packet()
            if len(response) < 1 or response[0] != 0x02:
                raise StcProtocolException("incorrect magic in write packet")

            self.progress_cb(i, self.PROGRAM_BLOCKSIZE, len(data))
        self.progress_cb(len(data), self.PROGRAM_BLOCKSIZE, len(data))

    def program_options(self):
        """Program option byte into flash"""

        print("Setting options: ")
        sys.stdout.flush()
        msr = self.options.get_msr()
        packet = bytes([0x04,0x00,0x00,0x46,0xB9, msr])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x04:
            raise StcProtocolException("incorrect magic in option packet")
        print("done")
    
    def disconnect(self):
        """Disconnect from MCU"""

        # reset mcu
        packet = bytes([0xFF])
        self.write_packet(packet)
        self.ser.close()
        print("Disconnected!")


class Stc12AOptionsMixIn:
    def program_options(self):
        print("Setting options: ", end="")
        sys.stdout.flush()
        msr = self.options.get_msr()
        packet = bytes([0x8d, msr[0], msr[1], msr[2], 0xff, msr[3]])
        packet += struct.pack(">I", int(self.mcu_clock_hz))
        packet += bytes([msr[3]])
        packet += bytes([0xff, msr[0], msr[1], 0xff, 0xff, 0xff, 0xff, msr[2]])
        packet += bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
        packet += struct.pack(">I", int(self.mcu_clock_hz))
        packet += bytes([0xff, 0xff, 0xff])

        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x80:
            raise StcProtocolException("incorrect magic in option packet")

        # XXX: this is done by STC-ISP on newer parts. not sure why, but let's
        # just replicate it, just to be sure.
        if self.bsl_version >= 0x66:
            packet = bytes([0x50])
            self.write_packet(packet)
            response = self.read_packet()
            if response[0] != 0x10:
                raise StcProtocolException("incorrect magic in option packet")

        print("done")


class Stc12AProtocol(Stc12AOptionsMixIn, Stc89Protocol):

    """countdown value for flash erase"""
    ERASE_COUNTDOWN = 0x0d

    def __init__(self, port, baud_handshake, baud_transfer):
        Stc89Protocol.__init__(self, port, baud_handshake, baud_transfer)

    def initialize_status(self, status_packet):
        """Decode status packet and store basic MCU info"""

        freq_counter = 0
        for i in range(8):
            freq_counter += struct.unpack(">H", status_packet[1+2*i:3+2*i])[0]
        freq_counter /= 8.0
        self.mcu_clock_hz = (self.baud_handshake * freq_counter * 12.0) / 7.0

        bl_version, bl_stepping = struct.unpack("BB", status_packet[17:19])
        self.mcu_bsl_version = "%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                            chr(bl_stepping))

        self.bsl_version = bl_version

    def calculate_baud(self):
        """Calculate MCU baudrate setting.

        Calculate appropriate baudrate settings for the MCU's UART,
        according to clock frequency and requested baud rate.
        """

        # baudrate is directly controlled by programming the MCU's BRT register
        brt = 256 - round((self.mcu_clock_hz) / (self.baud_transfer * 16))
        if brt <= 1 or brt > 255:
            raise StcProtocolException("requested baudrate cannot be set")
        brt_csum = (2 * (256 - brt)) & 0xff
        baud_actual = (self.mcu_clock_hz) / (16 * (256 - brt))
        baud_error = (abs(self.baud_transfer - baud_actual) * 100.0) / self.baud_transfer
        if baud_error > 5.0:
            print("WARNING: baudrate error is %.2f%%. You may need to set a slower rate." %
                  baud_error, file=sys.stderr)

        # IAP wait states
        iap_wait = self.get_iap_delay(self.mcu_clock_hz)

        # MCU delay after switching baud rates
        delay = 0x80

        return brt, brt_csum, iap_wait, delay

    def initialize_options(self, status_packet):
        """Initialize options"""

        if len(status_packet) < 31:
            raise StcProtocolException("invalid options in status packet")

        # create option state
        self.options = Stc12AOption(status_packet[23:26] + status_packet[29:30])
        self.options.print()

    def handshake(self):
        """Do baudrate handshake

        Initiate and do the (rather complicated) baudrate handshake.
        """

        # start baudrate handshake
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        brt, brt_csum, iap, delay = self.calculate_baud()
        print("checking ", end="")
        sys.stdout.flush()
        packet = bytes([0x8f, 0xc0, brt, 0x3f, brt_csum, delay, iap])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        self.ser.baudrate = self.baud_handshake
        if response[0] != 0x8f:
            raise StcProtocolException("incorrect magic in handshake packet")

        # switch to the settings
        print("setting ", end="")
        sys.stdout.flush()
        packet = bytes([0x8e, 0xc0, brt, 0x3f, brt_csum, delay])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        if response[0] != 0x8e:
            raise StcProtocolException("incorrect magic in handshake packet")

        # ping-pong test
        print("testing ", end="")
        sys.stdout.flush()
        packet = bytes([0x80, 0x00, 0x00, 0x36, 0x01])
        packet += struct.pack(">H", self.mcu_magic)
        for _ in range(4):
            self.write_packet(packet)
            response = self.read_packet()
            if response[0] != 0x80:
                raise StcProtocolException("incorrect magic in handshake packet")

        print("done")

    def erase_flash(self, erase_size, flash_size):
        """Erase the MCU's flash memory.

        Erase the flash memory with a block-erase command.
        """

        blks = ((erase_size + 511) // 512) * 2
        size = ((flash_size + 511) // 512) * 2
        print("Erasing %d blocks: " % blks, end="")
        sys.stdout.flush()
        packet = bytes([0x84, 0xff, 0x00, blks, 0x00, 0x00, size,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00])
        for i in range(0x80, self.ERASE_COUNTDOWN, -1): packet += bytes([i])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x80:
            raise StcProtocolException("incorrect magic in erase packet")
        print("done")


class Stc12OptionsMixIn:
    def program_options(self):
        print("Setting options: ", end="")
        sys.stdout.flush()
        msr = self.options.get_msr()
        # XXX: it's not 100% clear if the index of msr[3] is consistent
        # between devices, so write it to both indices.
        packet = bytes([0x8d, msr[0], msr[1], msr[2], msr[3],
                        0xff, 0xff, 0xff, 0xff, msr[3], 0xff,
                        0xff, 0xff, 0xff, 0xff, 0xff, 0xff])

        packet += struct.pack(">I", int(self.mcu_clock_hz))
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x50:
            raise StcProtocolException("incorrect magic in option packet")
        print("done")

        # If UID wasn't sent with erase acknowledge, it should be in this packet
        if not self.uid:
            self.uid = response[18:25]

        print("Target UID: %s" % Utils.hexstr(self.uid))


class Stc12BaseProtocol(StcBaseProtocol):
    """Base class for STC 10/11/12 series protocol handlers"""

    PROGRAM_BLOCKSIZE = 128
    """block size for programming flash"""

    ERASE_COUNTDOWN = 0x0d
    """countdown value for flash erase"""

    PARITY = serial.PARITY_EVEN
    """Parity for error correction was introduced with STC12"""

    def __init__(self, port, baud_handshake, baud_transfer):
        StcBaseProtocol.__init__(self, port, baud_handshake, baud_transfer)

    def extract_payload(self, packet):
        """Verify the checksum of packet and return its payload"""

        packet_csum, = struct.unpack(">H", packet[-3:-1])
        calc_csum = sum(packet[2:-3]) & 0xffff
        if packet_csum != calc_csum:
            self.dump_packet(packet)
            raise StcFramingException("packet checksum mismatch")

        payload = StcBaseProtocol.extract_payload(self, packet)
        return payload[:-2]

    def write_packet(self, packet_data, epilogue_len = 0):
        """Send packet to MCU.

        Constructs a packet with supplied payload and sends it to the MCU.
        """

        # frame start and direction magic
        packet = bytes()
        packet += self.PACKET_START
        packet += self.PACKET_HOST

        # packet length and payload
        packet += struct.pack(">H", len(packet_data) + 6)
        packet += packet_data

        # checksum and end code
        packet += struct.pack(">H", sum(packet[2:]) & 0xffff)
        packet += self.PACKET_END
        
        i = 0
        while i < epilogue_len:
            packet += bytes([0x66])
            i += 1

        self.dump_packet(packet, receive=False)
        self.ser.write(packet)
        self.ser.flush()

    def initialize_status(self, status_packet):
        """Decode status packet and store basic MCU info"""

        freq_counter = 0
        for i in range(8):
            freq_counter += struct.unpack(">H", status_packet[1+2*i:3+2*i])[0]
        freq_counter /= 8.0
        self.mcu_clock_hz = (self.baud_handshake * freq_counter * 12.0) / 7.0

        bl_version, bl_stepping = struct.unpack("BB", status_packet[17:19])
        self.mcu_bsl_version = "%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                            chr(bl_stepping))

        self.bsl_version = bl_version

    def calculate_baud(self):
        """Calculate MCU baudrate setting.

        Calculate appropriate baudrate settings for the MCU's UART,
        according to clock frequency and requested baud rate.
        """

        # baudrate is directly controlled by programming the MCU's BRT register
        brt = 256 - round((self.mcu_clock_hz) / (self.baud_transfer * 16))
        if brt <= 1 or brt > 255:
            raise StcProtocolException("requested baudrate cannot be set")
        brt_csum = (2 * (256 - brt)) & 0xff
        baud_actual = (self.mcu_clock_hz) / (16 * (256 - brt))
        baud_error = (abs(self.baud_transfer - baud_actual) * 100.0) / self.baud_transfer
        if baud_error > 5.0:
            print("WARNING: baudrate error is %.2f%%. You may need to set a slower rate." %
                  baud_error, file=sys.stderr)

        # IAP wait states
        iap_wait = self.get_iap_delay(self.mcu_clock_hz)

        # MCU delay after switching baud rates
        delay = 0x80

        return brt, brt_csum, iap_wait, delay

    def initialize_options(self, status_packet):
        """Initialize options"""

        if len(status_packet) < 29:
            raise StcProtocolException("invalid options in status packet")

        # create option state
        self.options = Stc12Option(status_packet[23:26] + status_packet[27:28])
        self.options.print()

    def handshake(self):
        """Do baudrate handshake

        Initate and do the (rather complicated) baudrate handshake.
        """

        # start baudrate handshake
        brt, brt_csum, iap, delay = self.calculate_baud()
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        packet = bytes([0x50, 0x00, 0x00, 0x36, 0x01])
        packet += struct.pack(">H", self.mcu_magic)
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x8f:
            raise StcProtocolException("incorrect magic in handshake packet")

        # test new settings
        print("testing ", end="")
        sys.stdout.flush()
        packet = bytes([0x8f, 0xc0, brt, 0x3f, brt_csum, delay, iap])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        self.ser.baudrate = self.baud_handshake
        if response[0] != 0x8f:
            raise StcProtocolException("incorrect magic in handshake packet")

        # switch to the settings
        print("setting ", end="")
        sys.stdout.flush()
        packet = bytes([0x8e, 0xc0, brt, 0x3f, brt_csum, delay])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        if response[0] != 0x84:
            raise StcProtocolException("incorrect magic in handshake packet")

        print("done")

    def erase_flash(self, erase_size, flash_size):
        """Erase the MCU's flash memory.

        Erase the flash memory with a block-erase command.
        """

        blks = ((erase_size + 511) // 512) * 2
        size = ((flash_size + 511) // 512) * 2
        print("Erasing %d blocks: " % blks, end="")
        sys.stdout.flush()
        packet = bytes([0x84, 0xff, 0x00, blks, 0x00, 0x00, size,
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00, 0x00])
        for i in range(0x80, self.ERASE_COUNTDOWN, -1): packet += bytes([i])
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x00:
            raise StcProtocolException("incorrect magic in erase packet")
        print("done")

        # UID, only sent with this packet by some BSLs
        if len(response) >= 8:
            self.uid = response[1:8]

    def program_flash(self, data):
        """Program the MCU's flash memory.

        Write data into flash memory, using the PROGRAM_BLOCKSIZE
        as the block size (depends on MCU's RAM size).
        """

        for i in range(0, len(data), self.PROGRAM_BLOCKSIZE):
            packet = bytes(3)
            packet += struct.pack(">H", i)
            packet += struct.pack(">H", self.PROGRAM_BLOCKSIZE)
            packet += data[i:i+self.PROGRAM_BLOCKSIZE]
            while len(packet) < self.PROGRAM_BLOCKSIZE + 7: packet += b"\x00"
            self.write_packet(packet)
            response = self.read_packet()
            if response[0] != 0x00:
                raise StcProtocolException("incorrect magic in write packet")
            self.progress_cb(i, self.PROGRAM_BLOCKSIZE, len(data))
        self.progress_cb(len(data), self.PROGRAM_BLOCKSIZE, len(data))

        print("Finishing write: ", end="")
        sys.stdout.flush()
        packet = bytes([0x69, 0x00, 0x00, 0x36, 0x01])
        packet += struct.pack(">H", self.mcu_magic)
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x8d:
            raise StcProtocolException("incorrect magic in finish packet")
        print("done")


class Stc12Protocol(Stc12OptionsMixIn, Stc12BaseProtocol):
    """STC 10/11/12 series protocol handler"""

    def __init__(self, port, handshake, baud):
        Stc12BaseProtocol.__init__(self, port, handshake, baud)


class Stc12BProtocol(Stc12AOptionsMixIn, Stc12BaseProtocol):
    """STC 10/11/12 variant protocol handler"""

    def __init__(self, port, handshake, baud):
        Stc12BaseProtocol.__init__(self, port, handshake, baud)


class Stc15AProtocol(Stc12Protocol):
    """Protocol handler for STC 15 series"""

    ERASE_COUNTDOWN = 0x5e
    PROGRAM_BLOCKSIZE = 64

    def __init__(self, port, handshake, baud, trim):
        Stc12Protocol.__init__(self, port, handshake, baud)

        self.trim_frequency = trim
        self.trim_data = None
        self.frequency_counter = 0

    def initialize_options(self, status_packet):
        """Initialize options"""

        if len(status_packet) < 37:
            raise StcProtocolException("invalid options in status packet")

        # create option state
        self.options = Stc15AOption(status_packet[23:36])
        self.options.print()

    def get_status_packet(self):
        """Read and decode status packet"""

        status_packet = self.read_packet()
        if status_packet[0] == 0x80:
            # need to re-ack
            packet = bytes([0x80])
            self.write_packet(packet)
            self.pulse()
            status_packet = self.read_packet()
        if status_packet[0] != 0x50:
            raise StcProtocolException("incorrect magic in status packet")
        return status_packet

    def initialize_status(self, status_packet):
        """Decode status packet and store basic MCU info"""

        freq_counter = 0
        for i in range(4):
            freq_counter += struct.unpack(">H", status_packet[1+2*i:3+2*i])[0]
        freq_counter /= 4.0
        self.mcu_clock_hz = (self.baud_handshake * freq_counter * 12.0) / 7.0

        bl_version, bl_stepping = struct.unpack("BB", status_packet[17:19])
        self.mcu_bsl_version = "%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                            chr(bl_stepping))

        self.trim_data = status_packet[51:58]
        self.freq_counter = freq_counter

    def get_trim_sequence(self, frequency):
        """Return frequency-specific coarse trim sequence"""

        packet = bytes()
        if frequency < 7.5E6:
            packet += bytes([0x18, 0x00, 0x02, 0x00])
            packet += bytes([0x18, 0x80, 0x02, 0x00])
            packet += bytes([0x18, 0x80, 0x02, 0x00])
            packet += bytes([0x18, 0xff, 0x02, 0x00])
        elif frequency < 10E6:
            packet += bytes([0x18, 0x80, 0x02, 0x00])
            packet += bytes([0x18, 0xff, 0x02, 0x00])
            packet += bytes([0x58, 0x00, 0x02, 0x00])
            packet += bytes([0x58, 0xff, 0x02, 0x00])
        elif frequency < 15E6:
            packet += bytes([0x58, 0x00, 0x02, 0x00])
            packet += bytes([0x58, 0x80, 0x02, 0x00])
            packet += bytes([0x58, 0x80, 0x02, 0x00])
            packet += bytes([0x58, 0xff, 0x02, 0x00])
        elif frequency < 21E6:
            packet += bytes([0x58, 0x80, 0x02, 0x00])
            packet += bytes([0x58, 0xff, 0x02, 0x00])
            packet += bytes([0x98, 0x00, 0x02, 0x00])
            packet += bytes([0x98, 0x80, 0x02, 0x00])
        elif frequency < 31E6:
            packet += bytes([0x98, 0x00, 0x02, 0x00])
            packet += bytes([0x98, 0x80, 0x02, 0x00])
            packet += bytes([0x98, 0x80, 0x02, 0x00])
            packet += bytes([0x98, 0xff, 0x02, 0x00])
        else:
            packet += bytes([0xd8, 0x00, 0x02, 0x00])
            packet += bytes([0xd8, 0x80, 0x02, 0x00])
            packet += bytes([0xd8, 0x80, 0x02, 0x00])
            packet += bytes([0xd8, 0xb4, 0x02, 0x00])

        return packet

    def handshake(self):
        """Initiate and do the frequency adjustment and baudrate
        switch handshake.

        This rather complicated handshake trims the MCU's calibrated RC
        frequency and switches the baud rate at the same time.

        Flash programming uses a fixed frequency and that frequency is
        calibrated along with the frequency specified by the user.
        """

        user_speed = self.trim_frequency
        if user_speed <= 0:
            user_speed = self.mcu_clock_hz
        program_speed = 22118400

        user_count = int(self.freq_counter * (user_speed / self.mcu_clock_hz))
        program_count = int(self.freq_counter * (program_speed / self.mcu_clock_hz))

        # Initiate handshake
        print("Trimming frequency: ", end="")
        sys.stdout.flush()
        packet = bytes([0x50, 0x00, 0x00, 0x36, 0x01])
        packet += struct.pack(">H", self.mcu_magic)
        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x8f:
            raise StcProtocolException("incorrect magic in handshake packet")

        # trim challenge-response, first round
        packet = bytes([0x65])
        packet += self.trim_data
        packet += bytes([0xff, 0xff, 0x06, 0x06])
        # add trim challenges for target frequency
        packet += self.get_trim_sequence(user_speed)
        # add trim challenge for program frequency
        packet += bytes([0x98, 0x00, 0x02, 0x00])
        packet += bytes([0x98, 0x80, 0x02, 0x00])
        self.write_packet(packet)
        self.pulse(timeout=1.0)
        response = self.read_packet()
        if len(response) < 36 or response[0] != 0x65:
            raise StcProtocolException("incorrect magic in handshake packet")

        # determine programming speed trim value
        target_trim_a, target_count_a = struct.unpack(">HH", response[28:32])
        target_trim_b, target_count_b = struct.unpack(">HH", response[32:36])
        if target_count_a == target_count_b:
            raise StcProtocolException("frequency trimming failed")
        m = (target_trim_b - target_trim_a) / (target_count_b - target_count_a)
        n = target_trim_a - m * target_count_a
        program_trim = round(m * program_count + n)
        if program_trim > 65535 or program_trim < 0:
            raise StcProtocolException("frequency trimming failed")

        # determine trim trials for second round
        trim_a, count_a = struct.unpack(">HH", response[12:16])
        trim_b, count_b = struct.unpack(">HH", response[16:20])
        trim_c, count_c = struct.unpack(">HH", response[20:24])
        trim_d, count_d = struct.unpack(">HH", response[24:28])
        # select suitable coarse trim range
        if count_c <= user_count and count_d >= user_count:
            target_trim_a = trim_c
            target_trim_b = trim_d
            target_count_a = count_c
            target_count_b = count_d
        else:
            target_trim_a = trim_a
            target_trim_b = trim_b
            target_count_a = count_a
            target_count_b = count_b
        # linear interpolate to find range to try next
        if target_count_a == target_count_b:
            raise StcProtocolException("frequency trimming failed")
        m = (target_trim_b - target_trim_a) / (target_count_b - target_count_a)
        n = target_trim_a - m * target_count_a
        target_trim = round(m * user_count + n)
        target_trim_start = min(max(target_trim - 5, target_trim_a), target_trim_b)
        if target_trim_start + 11 > 65535 or target_trim_start < 0:
            raise StcProtocolException("frequency trimming failed")

        # trim challenge-response, second round
        packet = bytes([0x65])
        packet += self.trim_data
        packet += bytes([0xff, 0xff, 0x06, 0x0B])
        for i in range(11):
            packet += struct.pack(">H", target_trim_start + i)
            packet += bytes([0x02, 0x00])
        self.write_packet(packet)
        self.pulse(timeout=1.0)
        response = self.read_packet()
        if len(response) < 56 or response[0] != 0x65:
            raise StcProtocolException("incorrect magic in handshake packet")

        # determine best trim value
        best_trim = 0
        best_count = 65535
        for i in range(11):
            trim, count = struct.unpack(">HH", response[12+4*i:16+4*i])
            if abs(count - user_count) < abs(best_count - user_count):
                best_trim = trim
                best_count = count
        final_freq = (best_count / self.freq_counter) * self.mcu_clock_hz
        print("%.03f MHz" % (final_freq / 1E6))
        self.options.set_trim(best_trim)

        # finally, switch baudrate
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        iap_wait = self.get_iap_delay(program_speed)
        packet = bytes([0x8e])
        packet += struct.pack(">H", program_trim)
        packet += struct.pack(">B", 230400 // self.baud_transfer)
        packet += bytes([0xa1, 0x64, 0xb8, 0x00, iap_wait, 0x20, 0xff, 0x00])
        self.write_packet(packet)
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer
        response = self.read_packet()
        if response[0] != 0x84:
            raise StcProtocolException("incorrect magic in handshake packet")
        print("done")

    def program_options(self):
        print("Setting options: ", end="")
        sys.stdout.flush()
        msr = self.options.get_msr()
        packet = bytes([0x8d])
        packet += msr
        packet += bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff])

        self.write_packet(packet)
        response = self.read_packet()
        if response[0] != 0x50:
            raise StcProtocolException("incorrect magic in option packet")
        print("done")

        print("Target UID: %s" % Utils.hexstr(self.uid))


class Stc15Protocol(Stc15AProtocol):
    """Protocol handler for later STC 15 series"""

    def __init__(self, port, handshake, baud, trim):
        Stc15AProtocol.__init__(self, port, handshake, baud, trim)

        self.trim_value = None

    def initialize_options(self, status_packet):
        """Initialize options"""

        if len(status_packet) < 14:
            raise StcProtocolException("invalid options in status packet")

        # create option state
        # XXX: check how option bytes are concatenated here
        self.options = Stc15Option(status_packet[5:8] + status_packet[12:13] + status_packet[37:38])
        self.options.print()

    def initialize_status(self, status_packet):
        """Decode status packet and store basic MCU info"""

        # check bit that control internal vs. external clock source
        # get frequency either stored from calibration or from
        # frequency counter
        self.external_clock = (status_packet[7] & 0x01) == 0
        if self.external_clock:
            count, = struct.unpack(">H", status_packet[13:15])
            self.mcu_clock_hz = self.baud_handshake * count
        else:
            self.mcu_clock_hz, = struct.unpack(">I", status_packet[8:12])
            # all ones means no calibration
            # new chips are shipped without any calibration
            if self.mcu_clock_hz == 0xffffffff: self.mcu_clock_hz = 0

        # pre-calibrated trim adjust for 24 MHz, range 0x40
        self.freq_count_24 = status_packet[4]

        # wakeup timer factory value
        self.wakeup_freq, = struct.unpack(">H", status_packet[1:3])

        bl_version, bl_stepping = struct.unpack("BB", status_packet[17:19])
        bl_minor = status_packet[22] & 0x0f
        self.mcu_bsl_version = "%d.%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                               bl_minor, chr(bl_stepping))
        self.bsl_version = bl_version

    def print_mcu_info(self):
        """Print additional STC15 info"""

        StcBaseProtocol.print_mcu_info(self)
        print("Target wakeup frequency: %.3f KHz" %(self.wakeup_freq / 1000))

    def choose_range(self, packet, response, target_count):
        """Choose appropriate trim value mean for next round from challenge
        responses."""

        calib_data = response[2:]
        challenge_data = packet[2:]
        calib_len = response[1]
        if len(calib_data) < 2 * calib_len:
            raise StcProtocolException("range calibration data missing")

        for i in range(calib_len - 1):
            count_a, count_b = struct.unpack(">HH", calib_data[2*i:2*i+4])
            trim_a, trim_b, trim_range = struct.unpack(">BxBB", challenge_data[2*i:2*i+4])
            if ((count_a <= target_count and count_b >= target_count) or
                    (count_b <= target_count and count_a >= target_count)):
                m = (trim_b - trim_a) / (count_b - count_a)
                n = trim_a - m * count_a
                target_trim = round(m * target_count + n)
                if target_trim > 65536 or target_trim < 0:
                    raise StcProtocolException("frequency trimming failed")
                return (target_trim, trim_range)

        return None

    def choose_trim(self, packet, response, target_count):
        """Choose best trim for given target count from challenge
        responses."""

        calib_data = response[2:]
        challenge_data = packet[2:]
        calib_len = response[1]
        if len(calib_data) < 2 * calib_len:
            raise StcProtocolException("trim calibration data missing")

        best = None
        best_count = sys.maxsize
        for i in range(calib_len):
            count, = struct.unpack(">H", calib_data[2*i:2*i+2])
            trim_adj, trim_range = struct.unpack(">BB", challenge_data[2*i:2*i+2])
            if abs(count - target_count) < best_count:
                best_count = abs(count - target_count)
                best = (trim_adj, trim_range), count

        if not best:
            raise StcProtocolException("frequency trimming failed")

        return best

    def calibrate(self):
        """Calibrate selected user frequency and the high-speed program
        frequency and switch to selected baudrate."""

        # handle uncalibrated chips
        if self.mcu_clock_hz == 0 and self.trim_frequency <= 0:
            raise StcProtocolException("uncalibrated, please provide a trim value")

        # determine target counters
        user_speed = self.trim_frequency
        if user_speed <= 0: user_speed = self.mcu_clock_hz
        program_speed = 22118400
        target_user_count = round(user_speed / (self.baud_handshake/2))
        target_prog_count = round(program_speed / (self.baud_handshake/2))

        # calibration, round 1
        print("Trimming frequency: ", end="")
        sys.stdout.flush()
        packet = bytes([0x00])
        packet += struct.pack(">B", 12)
        packet += bytes([0x00, 0xc0, 0x80, 0xc0, 0xff, 0xc0])
        packet += bytes([0x00, 0x80, 0x80, 0x80, 0xff, 0x80])
        packet += bytes([0x00, 0x40, 0x80, 0x40, 0xff, 0x40])
        packet += bytes([0x00, 0x00, 0x80, 0x00, 0xc0, 0x00])
        self.write_packet(packet)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select ranges and trim values
        user_trim = self.choose_range(packet, response, target_user_count)
        prog_trim = self.choose_range(packet, response, target_prog_count)
        if user_trim is None or prog_trim is None:
            raise StcProtocolException("frequency trimming unsuccessful")

        # calibration, round 2
        packet = bytes([0x00])
        packet += struct.pack(">B", 12)
        for i in range(user_trim[0] - 3, user_trim[0] + 3):
            packet += bytes([i & 0xff, user_trim[1]])
        for i in range(prog_trim[0] - 3, prog_trim[0] + 3):
            packet += bytes([i & 0xff, prog_trim[1]])
        self.write_packet(packet)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select final values
        user_trim, user_count = self.choose_trim(packet, response, target_user_count)
        prog_trim, _ = self.choose_trim(packet, response, target_prog_count)
        self.trim_value = user_trim
        self.trim_frequency = round(user_count * (self.baud_handshake / 2))
        print("%.03f MHz" % (self.trim_frequency / 1E6))

        # switch to programming frequency
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        packet = bytes([0x01])
        packet += bytes(prog_trim)
        # XXX: baud rate calculation is different between MCUs with and without
        # hardware UART. Only one family of models seems to lack a hardware
        # UART, and we can isolate those with a check on the magic.
        # This is a bit of a hack, but it works.
        if (self.mcu_magic >> 8) == 0xf2:
            packet += struct.pack(">H", int(65536 - program_speed / self.baud_transfer))
            packet += struct.pack(">H", int(65536 - program_speed / 2 * 3 / self.baud_transfer))
        else:
            packet += struct.pack(">H", int(65536 - program_speed / (self.baud_transfer * 4)))
            packet += bytes(reversed(user_trim))
        iap_wait = self.get_iap_delay(program_speed)
        packet += bytes([iap_wait])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 1 or response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer

    def switch_baud_ext(self):
        """Switch baudrate using external clock source"""

        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        packet = bytes([0x01])
        packet += bytes([self.freq_count_24, 0x40])
        bauds = int(65536 - self.mcu_clock_hz / self.baud_transfer / 4)
        if bauds >= 65536:
            raise StcProtocolException("baudrate adjustment failed")
        packet += struct.pack(">H", bauds)
        iap_wait = self.get_iap_delay(self.mcu_clock_hz)
        packet += bytes([0x00, 0x00, iap_wait])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 1 or response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")
        time.sleep(0.1)
        self.ser.baudrate = self.baud_transfer

        # for switching back to RC, program factory values
        self.trim_value = (self.freq_count_24, 0x40)
        self.trim_frequency = int(24E6)

    def handshake(self):
        """Do the handshake to calibrate frequencies and switch to
        programming baudrate. Complicated by the fact that programming
        can also use the external clock."""

        # external clock needs special handling
        if self.external_clock:
            self.switch_baud_ext()
        else:
            self.calibrate()

        # test/prepare
        packet = bytes([0x05])
        if self.bsl_version >= 0x72:
            packet += bytes([0x00, 0x00, 0x5a, 0xa5])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) == 1 and response[0] == 0x0f:
            raise StcProtocolException("MCU is locked")
        if len(response) < 1 or response[0] != 0x05:
            raise StcProtocolException("incorrect magic in handshake packet")

        print("done")

    def erase_flash(self, erase_size, flash_size):
        """Erase the MCU's flash memory.

        Erase the flash memory with a block-erase command.
        Note that this protocol always seems to erase everything.
        """

        print("Erasing flash: ", end="")
        sys.stdout.flush()
        packet = bytes([0x03])
        if erase_size <= flash_size:
           # erase flash only
           packet += bytes([0x00])
        else:
           # erase flash and eeprom
           packet += bytes([0x01])
        if self.bsl_version >= 0x72:
            packet += bytes([0x00, 0x5a, 0xa5])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 1 or response[0] != 0x03:
            raise StcProtocolException("incorrect magic in handshake packet")
        print("done")

        if len(response) >= 8:
            self.uid = response[1:8]

        # we should have a UID at this point
        if not self.uid:
            raise StcProtocolException("UID is missing")

    def program_flash(self, data):
        """Program the MCU's flash memory."""

        for i in range(0, len(data), self.PROGRAM_BLOCKSIZE):
            packet = bytes([0x22]) if i == 0 else bytes([0x02])
            packet += struct.pack(">H", i)
            if self.bsl_version >= 0x72:
                packet += bytes([0x5a, 0xa5])
            packet += data[i:i+self.PROGRAM_BLOCKSIZE]
            while len(packet) < self.PROGRAM_BLOCKSIZE + 3: packet += b"\x00"
            self.write_packet(packet)
            response = self.read_packet()
            if len(response) < 2 or response[0] != 0x02 or response[1] != 0x54:
                raise StcProtocolException("incorrect magic in write packet")
            self.progress_cb(i, self.PROGRAM_BLOCKSIZE, len(data))
        self.progress_cb(len(data), self.PROGRAM_BLOCKSIZE, len(data))

        # BSL 7.2+ needs a write finish packet according to dumps
        if self.bsl_version >= 0x72:
            print("Finishing write: ", end="")
            sys.stdout.flush()
            packet = bytes([0x07, 0x00, 0x00, 0x5a, 0xa5])
            self.write_packet(packet)
            response = self.read_packet()
            if len(response) < 2 or response[0] != 0x07 or response[1] != 0x54:
                raise StcProtocolException("incorrect magic in finish packet")
            print("done")

    def build_options(self):
        """Build a 64 byte packet of option data from the current
        configuration."""

        msr = self.options.get_msr()
        packet = bytes([0xff] * 23)
        packet += bytes([(self.trim_frequency >> 24) & 0xff,
                         0xff,
                         (self.trim_frequency >> 16) & 0xff,
                         0xff,
                         (self.trim_frequency >> 8) & 0xff,
                         0xff,
                         (self.trim_frequency >> 0) & 0xff,
                         0xff])
        packet += bytes([msr[3]])
        packet += bytes([0xff] * 23)
        if len(msr) > 4:
            packet += bytes([msr[4]])
        else:
            packet += bytes([0xff])
        packet += bytes([0xff] * 3)
        packet += bytes([self.trim_value[0], self.trim_value[1] + 0x3f])
        packet += msr[0:3]
        return packet

    def program_options(self):
        print("Setting options: ", end="")
        sys.stdout.flush()

        packet = bytes([0x04, 0x00, 0x00])
        if self.bsl_version >= 0x72:
            packet += bytes([0x5a, 0xa5])
        packet += self.build_options()
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x04 or response[1] != 0x54:
            raise StcProtocolException("incorrect magic in option packet")
        print("done")

        print("Target UID: %s" % Utils.hexstr(self.uid))


class StcUsb15Protocol(Stc15Protocol):
    """USB should use large blocks"""
    PROGRAM_BLOCKSIZE = 128

    """VID of STC devices"""
    USB_VID = 0x5354

    """PID of STC devices"""
    USB_PID = 0x4312

    def __init__(self):
        # XXX: this is really ugly!
        Stc15Protocol.__init__(self, "", 0, 0, 0)
        self.dev = None

    def dump_packet(self, data, request=0, value=0, index=0, receive=True):
        if self.debug:
            print("%s bRequest=%02X wValue=%04X wIndex=%04X data: %s" %
                  (("<-" if receive else "->"), request, value, index,
                   Utils.hexstr(data, " ")), file=sys.stderr)

    def read_packet(self):
        """Read a packet from the MCU"""

        dev2host = usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE | usb.util.CTRL_IN
        packet = self.dev.ctrl_transfer(dev2host, 0, 0, 0, 132).tobytes()
        if len(packet) < 5 or packet[0] != 0x46 or packet[1] != 0xb9:
            self.dump_packet(packet)
            raise StcFramingException("incorrect frame start")

        data_len = packet[2]
        if (data_len) > len(packet) + 3:
            self.dump_packet(packet)
            raise StcFramingException("frame length mismatch")

        data = packet[2:-1]
        csum = functools.reduce(lambda x, y: x - y, data, 0) & 0xff
        if csum != packet[-1]:
            self.dump_packet(packet)
            raise StcFramingException("frame checksum mismatch")

        self.dump_packet(packet, receive=True)
        return packet[3:3+data_len]

    def write_packet(self, request, value=0, index=0, data=bytes([0])):
        """Write USB control packet"""

        # Control transfers are maximum of 8 bytes each, and every
        # invidual partial transfer is checksummed individually.
        i = 0
        chunks = bytes()
        while i < len(data):
            c = data[i:i+7]
            csum = functools.reduce(lambda x, y: x - y, c, 0) & 0xff
            chunks += c + bytes([csum])
            i += 7

        self.dump_packet(chunks, request, value, index, receive=False)
        host2dev = usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE | usb.util.CTRL_OUT
        self.dev.ctrl_transfer(host2dev, request, value, index, chunks)

    def connect(self, autoreset=False, resetcmd=False, resetpin=False):
        """Connect to USB device and read info packet"""

        # USB support is optional. Provide an error if pyusb is not available.
        if not _usb_available:
            raise StcProtocolException(
                "USB support not available. " +
                "pyusb is not installed or not working correctly.")

        print("Waiting for MCU, please cycle power: ", end="")
        sys.stdout.flush()

        self.status_packet = None
        while not self.status_packet:
            try:
                self.dev = usb.core.find(idVendor=self.USB_VID, idProduct=self.USB_PID)
                if self.dev:
                    self.dev.set_configuration()
                    self.status_packet = self.read_packet()
                    if len(self.status_packet) < 38:
                        self.status_packet = None
                        raise StcFramingException
                else: raise StcFramingException
            except StcFramingException:
                time.sleep(0.5)
            except usb.core.USBError as err:
                if err.errno == errno.EACCES:
                    raise IOError(err.strerror)

        self.initialize_model()
        print("done")

    def handshake(self):
        print("Initializing: ", end="")
        sys.stdout.flush()

        # handshake
        self.write_packet(0x01, 0, 0, bytes([0x03]))
        response = self.read_packet()
        if response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")

        # enable/unlock MCU
        self.write_packet(0x05, 0xa55a, 0)
        response = self.read_packet()
        if response[0] == 0x0f:
            raise StcProtocolException("MCU is locked")
        if response[0] != 0x05:
            raise StcProtocolException("incorrect magic in handshake packet")

        print("done")

    def erase_flash(self, code, eeprom):
        print("Erasing flash: ", end="")
        sys.stdout.flush()
        self.write_packet(0x03, 0xa55a, 0)
        # XXX: better way to detect MCU has finished
        time.sleep(2)
        packet = self.read_packet()
        if packet[0] != 0x03:
            raise StcProtocolException("incorrect magic in erase packet")
        self.uid = packet[1:8]
        print("done")

    def program_flash(self, data):
        """Program the MCU's flash memory."""

        for i in range(0, len(data), self.PROGRAM_BLOCKSIZE):
            packet = data[i:i+self.PROGRAM_BLOCKSIZE]
            while len(packet) < self.PROGRAM_BLOCKSIZE: packet += b"\x00"
            self.write_packet(0x22 if i == 0 else 0x02, 0xa55a, i, packet)
            # XXX: better way to detect MCU has finished
            time.sleep(0.1)
            response = self.read_packet()
            if response[0] != 0x02 or response[1] != 0x54:
                raise StcProtocolException("incorrect magic in write packet")
            self.progress_cb(i, self.PROGRAM_BLOCKSIZE, len(data))
        self.progress_cb(len(data), self.PROGRAM_BLOCKSIZE, len(data))

    def program_options(self):
        print("Setting options: ", end="")
        sys.stdout.flush()

        # always use 24 MHz pre-tuned value for now
        self.trim_value = (self.freq_count_24, 0x40)
        self.trim_frequency = int(24E6)

        packet = self.build_options()
        self.write_packet(0x04, 0xa55a, 0, packet)
        # XXX: better way to detect MCU has finished
        time.sleep(0.5)
        response = self.read_packet()
        if response[0] != 0x04 or response[1] != 0x54:
            raise StcProtocolException("incorrect magic in option packet")
        print("done")

        print("Target UID: %s" % Utils.hexstr(self.uid))

    def disconnect(self):
        if self.dev:
            self.write_packet(0xff)
            print("Disconnected!")


class Stc8Protocol(Stc15Protocol):
    """Protocol handler for STC8 series"""

    def __init__(self, port, handshake, baud, trim):
        Stc15Protocol.__init__(self, port, handshake, baud, trim)
        self.trim_divider = None
        self.reference_voltage = None
        self.mfg_date = ()

    def initialize_options(self, status_packet):
        """Initialize options"""
        if len(status_packet) < 17:
            raise StcProtocolException("invalid options in status packet")

        # create option state
        self.options = Stc8Option(status_packet[9:12] + status_packet[15:17])
        self.options.print()

    def initialize_status(self, packet):
        """Decode status packet and store basic MCU info"""

        if len(packet) < 39:
            raise StcProtocolException("invalid status packet")

        self.mcu_clock_hz, = struct.unpack(">I", packet[1:5])
        self.external_clock = False
        # all ones means no calibration
        # new chips are shipped without any calibration
        # XXX: somehow check if that still holds
        if self.mcu_clock_hz == 0xffffffff: self.mcu_clock_hz = 0

        # wakeup timer factory value
        self.wakeup_freq, = struct.unpack(">H", packet[23:25])
        self.reference_voltage, = struct.unpack(">H", packet[35:37])
        self.mfg_date = (
            2000 + Utils.decode_packed_bcd(packet[37]),
            Utils.decode_packed_bcd(packet[38]),
            Utils.decode_packed_bcd(packet[39])
        )

        bl_version, bl_stepping = struct.unpack("BB", packet[17:19])
        bl_minor = packet[22] & 0x0f
        self.mcu_bsl_version = "%d.%d.%d%s" % (bl_version >> 4, bl_version & 0x0f,
                                               bl_minor, chr(bl_stepping))
        self.bsl_version = bl_version

    def print_mcu_info(self):
        """Print additional STC8 info"""
        super().print_mcu_info()
        print("Target ref. voltage: %d mV" % self.reference_voltage)
        print("Target mfg. date: %04d-%02d-%02d" % self.mfg_date)

    def set_option(self, name, value):
        super().set_option(name, value)

    def calibrate(self):
        """Calibrate selected user frequency frequency and switch to selected baudrate."""

        # handle uncalibrated chips
        if self.mcu_clock_hz == 0 and self.trim_frequency <= 0:
            raise StcProtocolException("uncalibrated, please provide a trim value")

        # determine target counter
        user_speed = self.trim_frequency
        if user_speed <= 0: user_speed = self.mcu_clock_hz
        target_user_count = round(user_speed / (self.baud_handshake/2))

        # calibration, round 1
        print("Trimming frequency: ", end="")
        sys.stdout.flush()
        packet = bytes([0x00])
        packet += struct.pack(">B", 12)
        packet += bytes([0x00, 0x00, 23*1, 0x00, 23*2, 0x00])
        packet += bytes([23*3, 0x00, 23*4, 0x00, 23*5, 0x00])
        packet += bytes([23*6, 0x00, 23*7, 0x00, 23*8, 0x00])
        packet += bytes([23*9, 0x00, 23*10, 0x00, 255, 0x00])
        self.write_packet(packet)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select ranges and trim values
        for divider in (1, 2, 3, 4, 5):
            user_trim = self.choose_range(packet, response, target_user_count * divider)
            if user_trim is not None:
                self.trim_divider = divider
                break
        if user_trim is None:
            raise StcProtocolException("frequency trimming unsuccessful")

        # calibration, round 2
        packet = bytes([0x00])
        packet += struct.pack(">B", 12)
        for i in range(user_trim[0] - 1, user_trim[0] + 2):
            packet += bytes([i & 0xff, 0x00])
        for i in range(user_trim[0] - 1, user_trim[0] + 2):
            packet += bytes([i & 0xff, 0x01])
        for i in range(user_trim[0] - 1, user_trim[0] + 2):
            packet += bytes([i & 0xff, 0x02])
        for i in range(user_trim[0] - 1, user_trim[0] + 2):
            packet += bytes([i & 0xff, 0x03])
        self.write_packet(packet)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select final values
        user_trim, user_count = self.choose_trim(packet, response, target_user_count)
        self.trim_value = user_trim
        self.trim_frequency = round(user_count * (self.baud_handshake / 2) / self.trim_divider)
        print("%.03f MHz" % (self.trim_frequency / 1E6))

        # switch to programming frequency
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        packet = bytes([0x01, 0x00, 0x00])
        bauds = self.baud_transfer * 4
        packet += struct.pack(">H", round(65536 - 24E6 / bauds))
        packet += bytes([user_trim[1], user_trim[0]])
        iap_wait = self.get_iap_delay(24E6)
        packet += bytes([iap_wait])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 1 or response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")
        self.ser.baudrate = self.baud_transfer

    def build_options(self):
        """Build a packet of option data from the current configuration."""

        msr = self.options.get_msr()
        packet = 40 * bytearray([0xff])
        packet[3] = 0
        packet[6] = 0
        packet[22] = 0
        packet[24:28] = struct.pack(">I", self.trim_frequency)
        packet[28:30] = self.trim_value
        packet[30] = self.trim_divider
        packet[32] = msr[0]
        packet[36:40] = msr[1:5]
        return bytes(packet)

    def disconnect(self):
        """Disconnect from MCU"""

        # reset mcu
        packet = bytes([0xff])
        self.write_packet(packet)
        self.ser.close()
        print("Disconnected!")


class Stc8dProtocol(Stc8Protocol):
    """Protocol handler for STC8A8K64D4 series"""

    def __init__(self, port, handshake, baud, trim):
        Stc8Protocol.__init__(self, port, handshake, baud, trim)

    def set_option(self, name, value):
        super().set_option(name, value)
        if name == 'program_eeprom_split':
            split_point = Utils.to_int(value);

            if self.model.mcs251:
                """Minimum size is 1K in STC-ISP"""
                if split_point == 0 and self.model.iap:
                    split_point = 0x400;

                # CODE starts at 0xFF0000
                self.split_code = 0x10000;
                # EEPROM starts at 0xFE0000
                self.split_eeprom = split_point;
            else:
                if split_point == 0 and self.model.iap:
                    split_point = self.model.code;

                self.split_code = split_point;
                self.split_eeprom = self.model.total - self.split_code;

    def choose_range(self, packet, response, target_count):
        """Choose appropriate trim value mean for next round from challenge
        responses."""


        challenge_data = packet[2:]
        calib_data = response[2:]
        calib_len = response[1]
        if len(calib_data) < 2 * calib_len:
            raise StcProtocolException("range calibration data missing")
        for i in range(calib_len >> 1):
            count_a, count_b = struct.unpack(
                ">HH", calib_data[4 * i: 4 * i + 4])
            trim_a, trim_b, trim_range = struct.unpack(
                ">BxBB", challenge_data[4 * i:4 * i + 4])
            if ((count_a <= target_count and count_b >= target_count)):
                target_trim = round(
                    (target_count - count_a) * (trim_b - trim_a) / (count_b - count_a) + trim_a)
                # target_trim will be set at the center of packet in the 2nd calibration
                if target_trim < 6 or target_trim > 255 - 5:
                    raise StcProtocolException("frequency trimming failed")
                return (target_trim, trim_range)
        return None

    def choose_trim(self, packet, response, target_count):
        """Choose best trim for given target count from challenge
        responses."""
        calib_data = response[2:]
        challenge_data = packet[2:]
        calib_len = response[1]
        if len(calib_data) < 2 * calib_len:
            raise StcProtocolException("trim calibration data missing")
        best = None
        best_count = sys.maxsize
        for i in range(calib_len):
            count, = struct.unpack(">H", calib_data[2 * i: 2 * i + 2])
            trim_adj, trim_range = struct.unpack(
                ">BB", challenge_data[2 * i: 2 * i + 2])
            if abs(count - target_count) < best_count:
                best_count = abs(count - target_count)
                best = (trim_adj, trim_range), count
        if not best:
            raise StcProtocolException("frequency trimming failed")
        return best


    def calibrate(self):
        """Calibrate selected user frequency frequency and switch to selected baudrate."""

        # handle uncalibrated chips
        if self.mcu_clock_hz == 0 and self.trim_frequency <= 0:
            raise StcProtocolException(
                "uncalibrated, please provide a trim value")

        # determine target counter
        user_speed = self.trim_frequency
        if user_speed <= 0:
            user_speed = self.mcu_clock_hz
        target_user_count = round(user_speed / self.baud_handshake)

        # calibration, round 1
        print("Target frequency: ", end="")
        sys.stdout.flush()
        packet = bytes([0x00, 0x08])
        packet += bytes([0x00, 0x00, 0xFF, 0x00])
        packet += bytes([0x00, 0x10, 0xFF, 0x10])
        packet += bytes([0x00, 0x20, 0xFF, 0x20])
        packet += bytes([0x00, 0x30, 0xFF, 0x30])
        self.write_packet(packet)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select ranges and trim values
        for divider in range(1, 6):
            user_trim = self.choose_range(
                packet, response, target_user_count * divider)
            if user_trim is not None:
                self.trim_divider = divider
                break
        if user_trim is None:
            raise StcProtocolException("frequency trimming unsuccessful")

        # calibration, round 2
        packet = bytes([0x00, 0x0C])
        for i in range(-6, 6):
            packet += bytes([user_trim[0] + i, user_trim[1]])
        self.write_packet(packet)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select final values
        user_trim, user_count = self.choose_trim(
            packet, response, target_user_count * self.trim_divider)
        self.trim_value = user_trim
        self.trim_frequency = round(
            user_count * self.baud_handshake/self.trim_divider)
        print("Target %.03f MHz" % (user_speed / 1E6))
        print("Adjusted frequency: %.03f MHz(%.03f%%)" % (
            (self.trim_frequency / 1E6), (self.trim_frequency*100/user_speed-100)))

        # switch to programming frequency
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        packet = bytes([0x01, 0x00, 0x00])
        bauds = self.baud_transfer * 4
        packet += struct.pack(">H", round(65536 - 24E6 / bauds))
        packet += bytes([user_trim[1], user_trim[0]])
        # iap_wait = self.get_iap_delay(24E6)
        iap_wait = 0x98  # iap_wait for "STC8A8K64D4"
        packet += bytes([iap_wait])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 1 or response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")
        self.ser.baudrate = self.baud_transfer

    def build_options(self):
        """Build a packet of option data from the current configuration."""
        msr = self.options.get_msr()
        packet = 40 * bytearray([0xff])
        packet[3] = 0x00
        packet[6] = 0x00
        packet[22] = 0x00
        packet[24:28] = struct.pack(">I", self.trim_frequency)
        packet[28:30] = self.trim_value
        packet[30] = self.trim_divider
        packet[32] = msr[0]
        packet[36:40] = msr[1:5]
        return bytes(packet)


class Stc8gProtocol(Stc8dProtocol):
    """Protocol handler for STC8G series"""

    def __init__(self, port, handshake, baud, trim):
        Stc8dProtocol.__init__(self, port, handshake, baud, trim)

    def calibrate(self):
        """Calibrate selected user frequency frequency and switch to selected baudrate."""

        # handle uncalibrated chips
        if self.mcu_clock_hz == 0 and self.trim_frequency <= 0:
            raise StcProtocolException(
                "uncalibrated, please provide a trim value")

        # determine target counter
        user_speed = self.trim_frequency
        if user_speed <= 0:
            user_speed = self.mcu_clock_hz
        target_user_count = round(user_speed / self.baud_handshake)

        # calibration, round 1
        print("Target frequency: ", end="")
        sys.stdout.flush()
        packet = bytes([0x00, 0x05])
        packet += bytes([0x00, 0x00, 0x80, 0x00])
        packet += bytes([0x00, 0x80, 0x80, 0x80])
        packet += bytes([0xFF, 0x00])
        self.write_packet(packet, 12)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select ranges and trim values
        for divider in range(1, 6):
            user_trim = self.choose_range(
                packet, response, target_user_count * divider)
            if user_trim is not None:
                self.trim_divider = divider
                break
        if user_trim is None:
            raise StcProtocolException("frequency trimming unsuccessful")

        # calibration, round 2
        packet = bytes([0x00, 0x0C])
        for i in range(-6, 6):
            packet += bytes([user_trim[0] + i, user_trim[1]])
        self.write_packet(packet, 19)
        self.pulse(b"\xfe", timeout=1.0)
        response = self.read_packet()
        if len(response) < 2 or response[0] != 0x00:
            raise StcProtocolException("incorrect magic in handshake packet")

        # select final values
        user_trim, user_count = self.choose_trim(
            packet, response, target_user_count * self.trim_divider)
        self.trim_value = user_trim
        self.trim_frequency = round(
            user_count * self.baud_handshake/self.trim_divider)
        print("Target %.03f MHz" % (user_speed / 1E6))
        print("Adjusted frequency: %.03f MHz(%.03f%%)" % (
            (self.trim_frequency / 1E6), (self.trim_frequency*100/user_speed-100)))

        # switch to programming frequency
        print("Switching to %d baud: " % self.baud_transfer, end="")
        sys.stdout.flush()
        packet = bytes([0x01, 0x00, 0x00])
        bauds = self.baud_transfer * 4
        packet += struct.pack(">H", round(65536 - 24E6 / bauds))
        packet += bytes([user_trim[1], user_trim[0]])
        # iap_wait = self.get_iap_delay(24E6)
        iap_wait = 0x98  # iap_wait for "STC8A8K64D4"
        packet += bytes([iap_wait])
        self.write_packet(packet)
        response = self.read_packet()
        if len(response) < 1 or response[0] != 0x01:
            raise StcProtocolException("incorrect magic in handshake packet")
        self.ser.baudrate = self.baud_transfer