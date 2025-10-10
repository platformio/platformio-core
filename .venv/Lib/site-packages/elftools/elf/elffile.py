#-------------------------------------------------------------------------------
# elftools: elf/elffile.py
#
# ELFFile - main class for accessing ELF files
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import io
from io import BytesIO
import os
import struct
import zlib

from ..common.exceptions import ELFError, ELFParseError
from ..common.utils import struct_parse, elf_assert
from .structs import ELFStructs
from .sections import (
        Section, StringTableSection, SymbolTableSection,
        SymbolTableIndexSection, SUNWSyminfoTableSection, NullSection,
        NoteSection, StabSection, ARMAttributesSection, RISCVAttributesSection)
from .dynamic import DynamicSection, DynamicSegment
from .relocation import (RelocationSection, RelocationHandler,
        RelrRelocationSection)
from .gnuversions import (
        GNUVerNeedSection, GNUVerDefSection,
        GNUVerSymSection)
from .segments import Segment, InterpSegment, NoteSegment
from ..dwarf.dwarfinfo import DWARFInfo, DebugSectionDescriptor, DwarfConfig
from ..ehabi.ehabiinfo import EHABIInfo
from .hash import ELFHashSection, GNUHashSection
from .constants import SHN_INDICES
from ..dwarf.dwarf_util import _file_crc32

class ELFFile(object):
    """ Creation: the constructor accepts a stream (file-like object) with the
        contents of an ELF file.

        Optionally, a stream_loader function can be passed as the second
        argument. This stream_loader function takes a relative file path to
        load a supplementary object file, and returns a stream suitable for
        creating a new ELFFile. Currently, the only such relative file path is
        obtained from the supplementary object files.

        Accessible attributes:

            stream:
                The stream holding the data of the file - must be a binary
                stream (bytes, not string).

            elfclass:
                32 or 64 - specifies the word size of the target machine

            little_endian:
                boolean - specifies the target machine's endianness

            elftype:
                string or int, either known value of E_TYPE enum defining ELF
                type (e.g. executable, dynamic library or core dump) or integral
                unparsed value

            header:
                the complete ELF file header

            e_ident_raw:
                the raw e_ident field of the header
    """
    def __init__(self, stream, stream_loader=None):
        self.stream = stream
        self.stream.seek(0, io.SEEK_END)
        self.stream_len = self.stream.tell()

        self._identify_file()
        self.structs = ELFStructs(
            little_endian=self.little_endian,
            elfclass=self.elfclass)

        self.structs.create_basic_structs()
        self.header = self._parse_elf_header()
        self.structs.create_advanced_structs(
                self['e_type'],
                self['e_machine'],
                self['e_ident']['EI_OSABI'])
        self.stream.seek(0)
        self.e_ident_raw = self.stream.read(16)

        self._section_header_stringtable = \
            self._get_section_header_stringtable()
        self._section_name_map = None
        self.stream_loader = stream_loader

    @classmethod
    def load_from_path(cls, path):
        """Takes a path to a file on the local filesystem, and returns an
        ELFFile from it, setting up a correct stream_loader relative to the
        original file.
        """
        stream = open(path, 'rb')
        return ELFFile(stream, ELFFile.make_relative_loader(path))
    
    @staticmethod
    def make_relative_loader(base_path):
        """ Return a function that takes a potentially relative path,
            resolves it against base_path (bytes or str), and opens a file at that.

            ELFFile uses functions like that for resolving DWARF links.
        """
        if isinstance(base_path, str):
            base_path = base_path.encode('UTF-8') # resolver takes a bytes path
        base_directory = os.path.dirname(base_path)
        def loader(rel_path):
            if not os.path.isabs(rel_path):
                rel_path = os.path.join(base_directory, rel_path)
            return open(rel_path, 'rb')
        return loader

    def num_sections(self):
        """ Number of sections in the file
        """
        if self['e_shoff'] == 0:
            return 0
        # From the ELF ABI documentation at
        # https://refspecs.linuxfoundation.org/elf/gabi4+/ch4.sheader.html:
        # "e_shnum normally tells how many entries the section header table
        # contains. [...] If the number of sections is greater than or equal to
        # SHN_LORESERVE (0xff00), e_shnum has the value SHN_UNDEF (0) and the
        # actual number of section header table entries is contained in the
        # sh_size field of the section header at index 0 (otherwise, the sh_size
        # member of the initial entry contains 0)."
        if self['e_shnum'] == 0:
            return self._get_section_header(0)['sh_size']
        return self['e_shnum']

    def get_section(self, n, type=None):
        """ Get the section at index #n from the file (Section object or a
            subclass)
        """
        section_header = self._get_section_header(n)
        if type and section_header.sh_type not in type:
            raise ELFError("Unexpected section type %s, expected %s" % (section_header['sh_type'], type))
        return self._make_section(section_header)
    
    def _get_linked_symtab_section(self, n):
        """ Get the section at index #n from the file, throws
            if it's not a SYMTAB/DYNTAB.
            Used for resolving section links with target type validation.
        """
        section_header = self._get_section_header(n)
        if section_header['sh_type'] not in ('SHT_SYMTAB', 'SHT_DYNSYM'):
            raise ELFError("Section points at section %d of type %s, expected SHT_SYMTAB/SHT_DYNSYM" % (n, section_header['sh_type']))
        return self._make_section(section_header)
    
    def _get_linked_strtab_section(self, n):
        """ Get the section at index #n from the file, throws
            if it's not a STRTAB.
            Used for resolving section links with target type validation.
        """
        section_header = self._get_section_header(n)
        if section_header['sh_type'] != 'SHT_STRTAB':
            raise ELFError("SHT_SYMTAB section points at section %d of type %s, expected SHT_STRTAB" % (n, section_header['sh_type']))
        return self._make_section(section_header)    

    def get_section_by_name(self, name):
        """ Get a section from the file, by name. Return None if no such
            section exists.
        """
        # The first time this method is called, construct a name to number
        # mapping
        #
        if self._section_name_map is None:
            self._make_section_name_map()
        secnum = self._section_name_map.get(name, None)
        return None if secnum is None else self.get_section(secnum)

    def get_section_index(self, section_name):
        """ Gets the index of the section by name. Return None if no such
            section name exists.
        """
        # The first time this method is called, construct a name to number
        # mapping
        #
        if self._section_name_map is None:
            self._make_section_name_map()
        return self._section_name_map.get(section_name, None)
    
    def has_section(self, section_name):
        """ Section existence check by name, without the overhead of parsing if found.
        """
        if self._section_name_map is None:
            self._make_section_name_map()
        return section_name in self._section_name_map

    def iter_sections(self, type=None):
        """ Yield all the sections in the file. If the optional |type|
            parameter is passed, this method will only yield sections of the
            given type. The parameter value must be a string containing the
            name of the type as defined in the ELF specification, e.g.
            'SHT_SYMTAB'.
        """
        for i in range(self.num_sections()):
            section = self.get_section(i)
            if type is None or section['sh_type'] == type:
                yield section

    def num_segments(self):
        """ Number of segments in the file
        """
        # From: https://github.com/hjl-tools/x86-psABI/wiki/X86-psABI
        # Section: 4.1.2 Number of Program Headers
        # If the number of program headers is greater than or equal to
        # PN_XNUM (0xffff), this member has the value PN_XNUM
        # (0xffff). The actual number of program header table entries
        # is contained in the sh_info field of the section header at
        # index 0.
        if self['e_phnum'] < 0xffff:
            return self['e_phnum']
        else:
            return self.get_section(0)['sh_info']

    def get_segment(self, n):
        """ Get the segment at index #n from the file (Segment object)
        """
        segment_header = self._get_segment_header(n)
        return self._make_segment(segment_header)

    def iter_segments(self, type=None):
        """ Yield all the segments in the file. If the optional |type|
            parameter is passed, this method will only yield segments of the
            given type. The parameter value must be a string containing the
            name of the type as defined in the ELF specification, e.g.
            'PT_LOAD'.
        """
        for i in range(self.num_segments()):
            segment = self.get_segment(i)
            if type is None or segment['p_type'] == type:
                yield segment

    def address_offsets(self, start, size=1):
        """ Yield a file offset for each ELF segment containing a memory region.

            A memory region is defined by the range [start...start+size). The
            offset of the region is yielded.
        """
        end = start + size
        # consider LOAD only to prevent same address being yielded twice
        for seg in self.iter_segments(type='PT_LOAD'):
            if (start >= seg['p_vaddr'] and
                end <= seg['p_vaddr'] + seg['p_filesz']):
                yield start - seg['p_vaddr'] + seg['p_offset']

    def has_dwarf_info(self, strict=False):
        """ Check whether this file appears to have debugging information.
            We assume that if it has the .debug_info or .zdebug_info section, it
            has all the other required sections as well.

            Unless you pass strict=True, the presence of .eh_frame section,
            which is DWARF adjacent but hardly DWARF proper, will count as debug info.
            Stripped files contain .eh_frame but none of the .[z]debug_xxx sections.
        """
        return (self.has_section('.debug_info') or
            self.has_section('.zdebug_info') or
            (not strict and self.has_section('.eh_frame')))

    def get_dwarf_info(self, relocate_dwarf_sections=True, follow_links=True):
        """ Return a DWARFInfo object representing the debugging information in
            this file.

            If relocate_dwarf_sections is True, relocations for DWARF sections
            are looked up and applied.

            If follow_links is True, we will try to load the external and/or supplementary
            object file (if any), and use it to resolve references and imports.
        """
        # Expect that has_dwarf_info() was called, so at least .debug_info is
        # present.
        # Sections that aren't found will be passed as None to DWARFInfo.

        # TODO: support linking by build ID
        # https://sourceware.org/gdb/current/onlinedocs/gdb.html/Separate-Debug-Files.html

        # A file may contain a debug link but not be stripped, so check for debug_info just in case
        debuglink_section = self.get_section_by_name('.gnu_debuglink')
        if debuglink_section and not self.has_dwarf_info(True) and follow_links and self.stream_loader:
            debuglink = struct_parse(self.structs.Gnu_debuglink, debuglink_section.stream, debuglink_section.header.sh_offset)
            with self.stream_loader(debuglink.filename) as ext_file:
                # Validate checksum...
                if _file_crc32(ext_file) != debuglink.checksum:
                    raise ELFError('The linked DWARF file does not match the checksum in the link.')
                ext_file.seek(0, os.SEEK_SET)
                ext_elffile = ELFFile(ext_file, self.stream_loader)
                # Inheriting the stream loader like that might be wrong if the supplementary DWARF link in the other file
                # is relative to the other file's directory as opposed to this file's directory.
                return ext_elffile.get_dwarf_info(relocate_dwarf_sections=relocate_dwarf_sections, follow_links=True)
       
        section_names = ('.debug_info', '.debug_aranges', '.debug_abbrev',
                         '.debug_str', '.debug_line', '.debug_frame',
                         '.debug_loc', '.debug_ranges', '.debug_pubtypes',
                         '.debug_pubnames', '.debug_addr',
                         '.debug_str_offsets', '.debug_line_str',
                         '.debug_loclists', '.debug_rnglists',
                         '.debug_sup', '.gnu_debugaltlink', '.debug_types')

        compressed = self.has_section('.zdebug_info')
        if compressed:
            section_names = tuple(map(lambda x: '.z' + x[1:], section_names))

        # As it is loaded in the process image, .eh_frame cannot be compressed
        section_names += ('.eh_frame', )

        (debug_info_sec_name, debug_aranges_sec_name, debug_abbrev_sec_name,
         debug_str_sec_name, debug_line_sec_name, debug_frame_sec_name,
         debug_loc_sec_name, debug_ranges_sec_name, debug_pubtypes_name,
         debug_pubnames_name, debug_addr_name, debug_str_offsets_name,
         debug_line_str_name, debug_loclists_sec_name, debug_rnglists_sec_name,
         debug_sup_name, gnu_debugaltlink_name, debug_types_sec_name,
         eh_frame_sec_name) = section_names

        debug_sections = {}
        for secname in section_names:
            section = self.get_section_by_name(secname)
            if section is None:
                debug_sections[secname] = None
            else:
                dwarf_section = self._read_dwarf_section(
                    section,
                    relocate_dwarf_sections)
                if compressed and secname.startswith('.z'):
                    dwarf_section = self._decompress_dwarf_section(dwarf_section)
                debug_sections[secname] = dwarf_section

        # Lookup if we have any of the .gnu_debugaltlink (GNU proprietary
        # implementation) or .debug_sup sections, referencing a supplementary
        # DWARF file

        dwarfinfo = DWARFInfo(
                config=DwarfConfig(
                    little_endian=self.little_endian,
                    default_address_size=self.elfclass // 8,
                    machine_arch=self.get_machine_arch()),
                debug_info_sec=debug_sections[debug_info_sec_name],
                debug_aranges_sec=debug_sections[debug_aranges_sec_name],
                debug_abbrev_sec=debug_sections[debug_abbrev_sec_name],
                debug_frame_sec=debug_sections[debug_frame_sec_name],
                eh_frame_sec=debug_sections[eh_frame_sec_name],
                debug_str_sec=debug_sections[debug_str_sec_name],
                debug_loc_sec=debug_sections[debug_loc_sec_name],
                debug_ranges_sec=debug_sections[debug_ranges_sec_name],
                debug_line_sec=debug_sections[debug_line_sec_name],
                debug_pubtypes_sec=debug_sections[debug_pubtypes_name],
                debug_pubnames_sec=debug_sections[debug_pubnames_name],
                debug_addr_sec=debug_sections[debug_addr_name],
                debug_str_offsets_sec=debug_sections[debug_str_offsets_name],
                debug_line_str_sec=debug_sections[debug_line_str_name],
                debug_loclists_sec=debug_sections[debug_loclists_sec_name],
                debug_rnglists_sec=debug_sections[debug_rnglists_sec_name],
                debug_sup_sec=debug_sections[debug_sup_name],
                gnu_debugaltlink_sec=debug_sections[gnu_debugaltlink_name],
                debug_types_sec=debug_sections[debug_types_sec_name]
                )
        if follow_links:
            dwarfinfo.supplementary_dwarfinfo = self.get_supplementary_dwarfinfo(dwarfinfo)
        return dwarfinfo
    
    def has_dwarf_link(self):
        """ Whether the binary's debug info is in an
            external file. Use get_dwarf_link to retrieve the path to it.
        """
        return self.has_section('.gnu_debuglink')
    
    def get_dwarf_link(self):
        """ Read the .gnu_debuglink section, return an object with filename (as bytes) and checksum (as number) in it.
        """
        section = self.get_section_by_name('.gnu_debuglink')
        return struct_parse(self.structs.Gnu_debuglink, section.stream, section.header.sh_offset) if section else None

    def get_supplementary_dwarfinfo(self, dwarfinfo):
        """
        Read supplementary dwarfinfo, from either the standared .debug_sup
        section, the GNU proprietary .gnu_debugaltlink, or .gnu_debuglink.
        """
        supfilepath = dwarfinfo.parse_debugsupinfo()
        if supfilepath is not None and self.stream_loader is not None:
            stream = self.stream_loader(supfilepath)
            supelffile = ELFFile(stream)
            dwarf_info = supelffile.get_dwarf_info()
            stream.close()
            return dwarf_info
        return None


    def has_ehabi_info(self):
        """ Check whether this file appears to have arm exception handler index table.
        """
        return any(self.iter_sections(type='SHT_ARM_EXIDX'))

    def get_ehabi_infos(self):
        """ Generally, shared library and executable contain 1 .ARM.exidx section.
            Object file contains many .ARM.exidx sections.
            So we must traverse every section and filter sections whose type is SHT_ARM_EXIDX.
        """
        _ret = []
        if self['e_type'] == 'ET_REL':
            # TODO: support relocatable file
            assert False, "Current version of pyelftools doesn't support relocatable file."
        for section in self.iter_sections(type='SHT_ARM_EXIDX'):
            _ret.append(EHABIInfo(section, self.little_endian))
        return _ret if len(_ret) > 0 else None

    def get_machine_arch(self):
        """ Return the machine architecture, as detected from the ELF header.
        """
        architectures = {
            'EM_M32'           : 'AT&T WE 32100',
            'EM_SPARC'         : 'SPARC',
            'EM_386'           : 'x86',
            'EM_68K'           : 'Motorola 68000',
            'EM_88K'           : 'Motorola 88000',
            'EM_IAMCU'         : 'Intel MCU',
            'EM_860'           : 'Intel 80860',
            'EM_MIPS'          : 'MIPS',
            'EM_S370'          : 'IBM System/370',
            'EM_MIPS_RS3_LE'   : 'MIPS RS3000 Little-endian',
            'EM_PARISC'        : 'Hewlett-Packard PA-RISC',
            'EM_VPP500'        : 'Fujitsu VPP500',
            'EM_SPARC32PLUS'   : 'Enhanced SPARC',
            'EM_960'           : 'Intel 80960',
            'EM_PPC'           : 'PowerPC',
            'EM_PPC64'         : '64-bit PowerPC',
            'EM_S390'          : 'IBM S/390',
            'EM_SPU'           : 'IBM SPU/SPC',
            'EM_V800'          : 'NEC V800',
            'EM_FR20'          : 'Fujitsu FR20',
            'EM_RH32'          : 'TRW RH-32',
            'EM_RCE'           : 'Motorola RCE',
            'EM_ARM'           : 'ARM',
            'EM_ALPHA'         : 'Digital Alpha',
            'EM_SH'            : 'Hitachi SH',
            'EM_SPARCV9'       : 'SPARC Version 9',
            'EM_TRICORE'       : 'Siemens TriCore embedded processor',
            'EM_ARC'           : 'Argonaut RISC Core, Argonaut Technologies Inc.',
            'EM_H8_300'        : 'Hitachi H8/300',
            'EM_H8_300H'       : 'Hitachi H8/300H',
            'EM_H8S'           : 'Hitachi H8S',
            'EM_H8_500'        : 'Hitachi H8/500',
            'EM_IA_64'         : 'Intel IA-64',
            'EM_MIPS_X'        : 'MIPS-X',
            'EM_COLDFIRE'      : 'Motorola ColdFire',
            'EM_68HC12'        : 'Motorola M68HC12',
            'EM_MMA'           : 'Fujitsu MMA',
            'EM_PCP'           : 'Siemens PCP',
            'EM_NCPU'          : 'Sony nCPU',
            'EM_NDR1'          : 'Denso NDR1',
            'EM_STARCORE'      : 'Motorola Star*Core',
            'EM_ME16'          : 'Toyota ME16',
            'EM_ST100'         : 'STMicroelectronics ST100',
            'EM_TINYJ'         : 'Advanced Logic TinyJ',
            'EM_X86_64'        : 'x64',
            'EM_PDSP'          : 'Sony DSP',
            'EM_PDP10'         : 'Digital Equipment PDP-10',
            'EM_PDP11'         : 'Digital Equipment PDP-11',
            'EM_FX66'          : 'Siemens FX66',
            'EM_ST9PLUS'       : 'STMicroelectronics ST9+ 8/16 bit',
            'EM_ST7'           : 'STMicroelectronics ST7 8-bit',
            'EM_68HC16'        : 'Motorola MC68HC16',
            'EM_68HC11'        : 'Motorola MC68HC11',
            'EM_68HC08'        : 'Motorola MC68HC08',
            'EM_68HC05'        : 'Motorola MC68HC05',
            'EM_SVX'           : 'Silicon Graphics SVx',
            'EM_ST19'          : 'STMicroelectronics ST19 8-bit',
            'EM_VAX'           : 'Digital VAX',
            'EM_CRIS'          : 'Axis Communications 32-bit',
            'EM_JAVELIN'       : 'Infineon Technologies 32-bit',
            'EM_FIREPATH'      : 'Element 14 64-bit DSP',
            'EM_ZSP'           : 'LSI Logic 16-bit DSP',
            'EM_MMIX'          : 'Donald Knuth\'s educational 64-bit',
            'EM_HUANY'         : 'Harvard University machine-independent object files',
            'EM_PRISM'         : 'SiTera Prism',
            'EM_AVR'           : 'Atmel AVR 8-bit',
            'EM_FR30'          : 'Fujitsu FR30',
            'EM_D10V'          : 'Mitsubishi D10V',
            'EM_D30V'          : 'Mitsubishi D30V',
            'EM_V850'          : 'NEC v850',
            'EM_M32R'          : 'Mitsubishi M32R',
            'EM_MN10300'       : 'Matsushita MN10300',
            'EM_MN10200'       : 'Matsushita MN10200',
            'EM_PJ'            : 'picoJava',
            'EM_OPENRISC'      : 'OpenRISC 32-bit',
            'EM_ARC_COMPACT'   : 'ARC International ARCompact',
            'EM_XTENSA'        : 'Tensilica Xtensa',
            'EM_VIDEOCORE'     : 'Alphamosaic VideoCore',
            'EM_TMM_GPP'       : 'Thompson Multimedia',
            'EM_NS32K'         : 'National Semiconductor 32000 series',
            'EM_TPC'           : 'Tenor Network TPC',
            'EM_SNP1K'         : 'Trebia SNP 1000',
            'EM_ST200'         : 'STMicroelectronics ST200',
            'EM_IP2K'          : 'Ubicom IP2xxx',
            'EM_MAX'           : 'MAX',
            'EM_CR'            : 'National Semiconductor CompactRISC',
            'EM_F2MC16'        : 'Fujitsu F2MC16',
            'EM_MSP430'        : 'Texas Instruments msp430',
            'EM_BLACKFIN'      : 'Analog Devices Blackfin',
            'EM_SE_C33'        : 'Seiko Epson S1C33',
            'EM_SEP'           : 'Sharp',
            'EM_ARCA'          : 'Arca RISC',
            'EM_UNICORE'       : 'PKU-Unity MPRC',
            'EM_EXCESS'        : 'eXcess',
            'EM_DXP'           : 'Icera Semiconductor Deep Execution Processor',
            'EM_ALTERA_NIOS2'  : 'Altera Nios II',
            'EM_CRX'           : 'National Semiconductor CompactRISC CRX',
            'EM_XGATE'         : 'Motorola XGATE',
            'EM_C166'          : 'Infineon C16x/XC16x',
            'EM_M16C'          : 'Renesas M16C',
            'EM_DSPIC30F'      : 'Microchip Technology dsPIC30F',
            'EM_CE'            : 'Freescale Communication Engine RISC core',
            'EM_M32C'          : 'Renesas M32C',
            'EM_TSK3000'       : 'Altium TSK3000',
            'EM_RS08'          : 'Freescale RS08',
            'EM_SHARC'         : 'Analog Devices SHARC',
            'EM_ECOG2'         : 'Cyan Technology eCOG2',
            'EM_SCORE7'        : 'Sunplus S+core7 RISC',
            'EM_DSP24'         : 'New Japan Radio (NJR) 24-bit DSP',
            'EM_VIDEOCORE3'    : 'Broadcom VideoCore III',
            'EM_LATTICEMICO32' : 'Lattice FPGA RISC',
            'EM_SE_C17'        : 'Seiko Epson C17',
            'EM_TI_C6000'      : 'TI TMS320C6000',
            'EM_TI_C2000'      : 'TI TMS320C2000',
            'EM_TI_C5500'      : 'TI TMS320C55x',
            'EM_TI_ARP32'      : 'TI Application Specific RISC, 32bit',
            'EM_TI_PRU'        : 'TI Programmable Realtime Unit',
            'EM_MMDSP_PLUS'    : 'STMicroelectronics 64bit VLIW',
            'EM_CYPRESS_M8C'   : 'Cypress M8C',
            'EM_R32C'          : 'Renesas R32C',
            'EM_TRIMEDIA'      : 'NXP Semiconductors TriMedia',
            'EM_QDSP6'         : 'QUALCOMM DSP6',
            'EM_8051'          : 'Intel 8051',
            'EM_STXP7X'        : 'STMicroelectronics STxP7x',
            'EM_NDS32'         : 'Andes Technology RISC',
            'EM_ECOG1'         : 'Cyan Technology eCOG1X',
            'EM_ECOG1X'        : 'Cyan Technology eCOG1X',
            'EM_MAXQ30'        : 'Dallas Semiconductor MAXQ30',
            'EM_XIMO16'        : 'New Japan Radio (NJR) 16-bit',
            'EM_MANIK'         : 'M2000 Reconfigurable RISC',
            'EM_CRAYNV2'       : 'Cray Inc. NV2',
            'EM_RX'            : 'Renesas RX',
            'EM_METAG'         : 'Imagination Technologies META',
            'EM_MCST_ELBRUS'   : 'MCST Elbrus',
            'EM_ECOG16'        : 'Cyan Technology eCOG16',
            'EM_CR16'          : 'National Semiconductor CompactRISC CR16 16-bit',
            'EM_ETPU'          : 'Freescale',
            'EM_SLE9X'         : 'Infineon Technologies SLE9X',
            'EM_L10M'          : 'Intel L10M',
            'EM_K10M'          : 'Intel K10M',
            'EM_AARCH64'       : 'AArch64',
            'EM_AVR32'         : 'Atmel 32-bit',
            'EM_STM8'          : 'STMicroeletronics STM8 8-bit',
            'EM_TILE64'        : 'Tilera TILE64',
            'EM_TILEPRO'       : 'Tilera TILEPro',
            'EM_MICROBLAZE'    : 'Xilinx MicroBlaze 32-bit RISC',
            'EM_CUDA'          : 'NVIDIA CUDA',
            'EM_TILEGX'        : 'Tilera TILE-Gx',
            'EM_CLOUDSHIELD'   : 'CloudShield',
            'EM_COREA_1ST'     : 'KIPO-KAIST Core-A 1st generation',
            'EM_COREA_2ND'     : 'KIPO-KAIST Core-A 2nd generation',
            'EM_ARC_COMPACT2'  : 'Synopsys ARCompact V2',
            'EM_OPEN8'         : 'Open8 8-bit RISC',
            'EM_RL78'          : 'Renesas RL78',
            'EM_VIDEOCORE5'    : 'Broadcom VideoCore V',
            'EM_78KOR'         : 'Renesas 78KOR',
            'EM_56800EX'       : 'Freescale 56800EX',
            'EM_BA1'           : 'Beyond BA1',
            'EM_BA2'           : 'Beyond BA2',
            'EM_XCORE'         : 'XMOS xCORE',
            'EM_MCHP_PIC'      : 'Microchip 8-bit PIC',
            'EM_INTEL205'      : 'Reserved by Intel',
            'EM_INTEL206'      : 'Reserved by Intel',
            'EM_INTEL207'      : 'Reserved by Intel',
            'EM_INTEL208'      : 'Reserved by Intel',
            'EM_INTEL209'      : 'Reserved by Intel',
            'EM_KM32'          : 'KM211 KM32 32-bit',
            'EM_KMX32'         : 'KM211 KMX32 32-bit',
            'EM_KMX16'         : 'KM211 KMX16 16-bit',
            'EM_KMX8'          : 'KM211 KMX8 8-bit',
            'EM_KVARC'         : 'KM211 KVARC',
            'EM_CDP'           : 'Paneve CDP',
            'EM_COGE'          : 'Cognitive',
            'EM_COOL'          : 'Bluechip Systems CoolEngine',
            'EM_NORC'          : 'Nanoradio Optimized RISC',
            'EM_CSR_KALIMBA'   : 'CSR Kalimba',
            'EM_Z80'           : 'Zilog Z80',
            'EM_VISIUM'        : 'VISIUMcore',
            'EM_FT32'          : 'FTDI Chip FT32 32-bit RISC',
            'EM_MOXIE'         : 'Moxie',
            'EM_AMDGPU'        : 'AMD GPU',
            'EM_RISCV'         : 'RISC-V',
            'EM_BPF'           : 'Linux BPF - in-kernel virtual machine',
            'EM_CSKY'          : 'C-SKY',
            'EM_LOONGARCH'     : 'LoongArch',
            'EM_FRV'           : 'Fujitsu FR-V'
        }

        return architectures.get(self['e_machine'], '<unknown>')

    def get_shstrndx(self):
        """ Find the string table section index for the section header table
        """
        # From https://refspecs.linuxfoundation.org/elf/gabi4+/ch4.eheader.html:
        # If the section name string table section index is greater than or
        # equal to SHN_LORESERVE (0xff00), this member has the value SHN_XINDEX
        # (0xffff) and the actual index of the section name string table section
        # is contained in the sh_link field of the section header at index 0.
        if self['e_shstrndx'] != SHN_INDICES.SHN_XINDEX:
            return self['e_shstrndx']
        else:
            return self._get_section_header(0)['sh_link']

    #-------------------------------- PRIVATE --------------------------------#

    def __getitem__(self, name):
        """ Implement dict-like access to header entries
        """
        return self.header[name]

    def _identify_file(self):
        """ Verify the ELF file and identify its class and endianness.
        """
        # Note: this code reads the stream directly, without using ELFStructs,
        # since we don't yet know its exact format. ELF was designed to be
        # read like this - its e_ident field is word-size and endian agnostic.
        self.stream.seek(0)
        magic = self.stream.read(4)
        elf_assert(magic == b'\x7fELF', 'Magic number does not match')

        ei_class = self.stream.read(1)
        if ei_class == b'\x01':
            self.elfclass = 32
        elif ei_class == b'\x02':
            self.elfclass = 64
        else:
            raise ELFError('Invalid EI_CLASS %s' % repr(ei_class))

        ei_data = self.stream.read(1)
        if ei_data == b'\x01':
            self.little_endian = True
        elif ei_data == b'\x02':
            self.little_endian = False
        else:
            raise ELFError('Invalid EI_DATA %s' % repr(ei_data))

    def _section_offset(self, n):
        """ Compute the offset of section #n in the file
        """
        shentsize = self['e_shentsize']
        if self['e_shoff'] > 0 and shentsize < self.structs.Elf_Shdr.sizeof():
            raise ELFError('Too small e_shentsize: %s' % shentsize)
        return self['e_shoff'] + n * shentsize

    def _segment_offset(self, n):
        """ Compute the offset of segment #n in the file
        """
        phentsize = self['e_phentsize']
        if self['e_phoff'] > 0 and phentsize < self.structs.Elf_Phdr.sizeof():
            raise ELFError('Too small e_phentsize: %s' % phentsize)
        return self['e_phoff'] + n * phentsize

    def _make_segment(self, segment_header):
        """ Create a Segment object of the appropriate type
        """
        segtype = segment_header['p_type']
        if segtype == 'PT_INTERP':
            return InterpSegment(segment_header, self.stream)
        elif segtype == 'PT_DYNAMIC':
            return DynamicSegment(segment_header, self.stream, self)
        elif segtype == 'PT_NOTE':
            return NoteSegment(segment_header, self.stream, self)
        else:
            return Segment(segment_header, self.stream)

    def _get_section_header(self, n):
        """ Find the header of section #n, parse it and return the struct
        """

        stream_pos = self._section_offset(n)
        if stream_pos > self.stream_len:
            return None

        return struct_parse(
            self.structs.Elf_Shdr,
            self.stream,
            stream_pos=stream_pos)

    def _get_section_name(self, section_header):
        """ Given a section header, find this section's name in the file's
            string table
        """
        if self._section_header_stringtable is None:
            raise ELFParseError("String Table not found")

        name_offset = section_header['sh_name']
        return self._section_header_stringtable.get_string(name_offset)

    def _make_section(self, section_header):
        """ Create a section object of the appropriate type
        """
        name = self._get_section_name(section_header)
        sectype = section_header['sh_type']

        if sectype == 'SHT_STRTAB':
            return StringTableSection(section_header, name, self)
        elif sectype == 'SHT_NULL':
            return NullSection(section_header, name, self)
        elif sectype in ('SHT_SYMTAB', 'SHT_DYNSYM', 'SHT_SUNW_LDYNSYM'):
            return self._make_symbol_table_section(section_header, name)
        elif sectype == 'SHT_SYMTAB_SHNDX':
            return self._make_symbol_table_index_section(section_header, name)
        elif sectype == 'SHT_SUNW_syminfo':
            return self._make_sunwsyminfo_table_section(section_header, name)
        elif sectype == 'SHT_GNU_verneed':
            return self._make_gnu_verneed_section(section_header, name)
        elif sectype == 'SHT_GNU_verdef':
            return self._make_gnu_verdef_section(section_header, name)
        elif sectype == 'SHT_GNU_versym':
            return self._make_gnu_versym_section(section_header, name)
        elif sectype in ('SHT_REL', 'SHT_RELA'):
            return RelocationSection(section_header, name, self)
        elif sectype == 'SHT_DYNAMIC':
            return DynamicSection(section_header, name, self)
        elif sectype == 'SHT_NOTE':
            return NoteSection(section_header, name, self)
        elif sectype == 'SHT_PROGBITS' and name == '.stab':
            return StabSection(section_header, name, self)
        elif sectype == 'SHT_ARM_ATTRIBUTES':
            return ARMAttributesSection(section_header, name, self)
        elif sectype == 'SHT_RISCV_ATTRIBUTES':
            return RISCVAttributesSection(section_header, name, self)
        elif sectype == 'SHT_HASH':
            return self._make_elf_hash_section(section_header, name)
        elif sectype == 'SHT_GNU_HASH':
            return self._make_gnu_hash_section(section_header, name)
        elif sectype == 'SHT_RELR':
            return RelrRelocationSection(section_header, name, self)
        else:
            return Section(section_header, name, self)

    def _make_section_name_map(self):
        self._section_name_map = {}
        for i, sec in enumerate(self.iter_sections()):
            self._section_name_map[sec.name] = i

    def _make_symbol_table_section(self, section_header, name):
        """ Create a SymbolTableSection
        """
        linked_strtab_index = section_header['sh_link']
        strtab_section = self._get_linked_strtab_section(linked_strtab_index)
        return SymbolTableSection(
            section_header, name,
            elffile=self,
            stringtable=strtab_section)

    def _make_symbol_table_index_section(self, section_header, name):
        """ Create a SymbolTableIndexSection object
        """
        linked_symtab_index = section_header['sh_link']
        return SymbolTableIndexSection(
            section_header, name, elffile=self,
            symboltable=linked_symtab_index)

    def _make_sunwsyminfo_table_section(self, section_header, name):
        """ Create a SUNWSyminfoTableSection
        """
        linked_strtab_index = section_header['sh_link']
        strtab_section = self._get_linked_symtab_section(linked_strtab_index)
        return SUNWSyminfoTableSection(
            section_header, name,
            elffile=self,
            symboltable=strtab_section)

    def _make_gnu_verneed_section(self, section_header, name):
        """ Create a GNUVerNeedSection
        """
        linked_strtab_index = section_header['sh_link']
        strtab_section = self._get_linked_strtab_section(linked_strtab_index)
        return GNUVerNeedSection(
            section_header, name,
            elffile=self,
            stringtable=strtab_section)

    def _make_gnu_verdef_section(self, section_header, name):
        """ Create a GNUVerDefSection
        """
        linked_strtab_index = section_header['sh_link']
        strtab_section = self._get_linked_strtab_section(linked_strtab_index)
        return GNUVerDefSection(
            section_header, name,
            elffile=self,
            stringtable=strtab_section)

    def _make_gnu_versym_section(self, section_header, name):
        """ Create a GNUVerSymSection
        """
        linked_strtab_index = section_header['sh_link']
        strtab_section = self.get_section(linked_strtab_index)
        return GNUVerSymSection(
            section_header, name,
            elffile=self,
            symboltable=strtab_section)

    def _make_elf_hash_section(self, section_header, name):
        linked_symtab_index = section_header['sh_link']
        symtab_section = self._get_linked_symtab_section(linked_symtab_index)
        return ELFHashSection(
            section_header, name, self, symtab_section
        )

    def _make_gnu_hash_section(self, section_header, name):
        linked_symtab_index = section_header['sh_link']
        symtab_section = self._get_linked_symtab_section(linked_symtab_index)
        return GNUHashSection(
            section_header, name, self, symtab_section
        )

    def _get_segment_header(self, n):
        """ Find the header of segment #n, parse it and return the struct
        """
        return struct_parse(
            self.structs.Elf_Phdr,
            self.stream,
            stream_pos=self._segment_offset(n))

    def _get_section_header_stringtable(self):
        """ Get the string table section corresponding to the section header
            table.
        """
        stringtable_section_num = self.get_shstrndx()

        stringtable_section_header = self._get_section_header(stringtable_section_num)
        if stringtable_section_header is None:
            return None

        return StringTableSection(
                header=stringtable_section_header,
                name='',
                elffile=self)

    def _parse_elf_header(self):
        """ Parses the ELF file header and assigns the result to attributes
            of this object.
        """
        return struct_parse(self.structs.Elf_Ehdr, self.stream, stream_pos=0)

    def _read_dwarf_section(self, section, relocate_dwarf_sections):
        """ Read the contents of a DWARF section from the stream and return a
            DebugSectionDescriptor. Apply relocations if asked to.
        """
        phantom_bytes = self.has_phantom_bytes()
        # The section data is read into a new stream, for processing
        section_stream = BytesIO()
        section_data = section.data()
        section_stream.write(section_data[::2] if phantom_bytes else section_data)

        if relocate_dwarf_sections:
            reloc_handler = RelocationHandler(self)
            reloc_section = reloc_handler.find_relocations_for_section(section)
            if reloc_section is not None:
                if phantom_bytes:
                    # No guidance how should the relocation work - before or after the odd byte skip
                    raise ELFParseError("This binary has relocations in the DWARF sections, currently not supported.")
                else:
                    reloc_handler.apply_section_relocations(
                            section_stream, reloc_section)

        return DebugSectionDescriptor(
                stream=section_stream,
                name=section.name,
                global_offset=section['sh_offset'],
                size=section.data_size//2 if phantom_bytes else section.data_size,
                address=section['sh_addr'])

    @staticmethod
    def _decompress_dwarf_section(section):
        """ Returns the uncompressed contents of the provided DWARF section.
        """
        # TODO: support other compression formats from readelf.c
        assert section.size > 12, 'Unsupported compression format.'

        section.stream.seek(0)
        # According to readelf.c the content should contain "ZLIB"
        # followed by the uncompressed section size - 8 bytes in
        # big-endian order
        compression_type = section.stream.read(4)
        assert compression_type == b'ZLIB', \
            'Invalid compression type: %r' % (compression_type)

        uncompressed_size = struct.unpack('>Q', section.stream.read(8))[0]

        decompressor = zlib.decompressobj()
        uncompressed_stream = BytesIO()
        while True:
            chunk = section.stream.read(4096)
            if not chunk:
                break
            uncompressed_stream.write(decompressor.decompress(chunk))
        uncompressed_stream.write(decompressor.flush())

        uncompressed_stream.seek(0, io.SEEK_END)
        size = uncompressed_stream.tell()
        assert uncompressed_size == size, \
                'Wrong uncompressed size: expected %r, but got %r' % (
                    uncompressed_size, size,
                )

        return section._replace(stream=uncompressed_stream, size=size)

    def close(self):
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def has_phantom_bytes(self):
        """The XC16 compiler for the PIC microcontrollers emits DWARF where all odd bytes in all DWARF sections
           are to be discarded ("phantom").

            We don't know where does the phantom byte discarding fit into the usual chain of section content transforms.
            There are no XC16/PIC binaries in the corpus with relocations against DWARF, and the DWARF section compression
            seems to be unsupported by XC16.
        """
        # Vendor flag EF_PIC30_NO_PHANTOM_BYTE=0x80000000: clear means phantom bytes are present
        return self['e_machine'] == 'EM_DSPIC30F' and (self['e_flags'] & 0x80000000) == 0
