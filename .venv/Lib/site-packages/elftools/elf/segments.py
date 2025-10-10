#-------------------------------------------------------------------------------
# elftools: elf/segments.py
#
# ELF segments
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from ..construct import CString
from ..common.utils import struct_parse
from .constants import SH_FLAGS
from .notes import iter_notes


class Segment(object):
    def __init__(self, header, stream):
        self.header = header
        self.stream = stream

    def data(self):
        """ The segment data from the file.
        """
        self.stream.seek(self['p_offset'])
        return self.stream.read(self['p_filesz'])

    def __getitem__(self, name):
        """ Implement dict-like access to header entries
        """
        return self.header[name]

    def section_in_segment(self, section):
        """ Is the given section contained in this segment?

            Note: this tries to reproduce the intricate rules of the
            ELF_SECTION_IN_SEGMENT_STRICT macro of the header
            elf/include/internal.h in the source of binutils.
        """
        # Only the 'strict' checks from ELF_SECTION_IN_SEGMENT_1 are included
        segtype = self['p_type']
        sectype = section['sh_type']
        secflags = section['sh_flags']

        # Only PT_LOAD, PT_GNU_RELRO and PT_TLS segments can contain SHF_TLS
        # sections
        if (    secflags & SH_FLAGS.SHF_TLS and
                segtype in ('PT_TLS', 'PT_GNU_RELRO', 'PT_LOAD')):
            pass
        # PT_TLS segment contains only SHF_TLS sections, PT_PHDR no sections
        # at all
        elif (  (secflags & SH_FLAGS.SHF_TLS) == 0 and
                segtype not in ('PT_TLS', 'PT_PHDR')):
            pass
        else:
            return False

        # PT_LOAD and similar segments only have SHF_ALLOC sections.
        if (    (secflags & SH_FLAGS.SHF_ALLOC) == 0 and
                segtype in ('PT_LOAD', 'PT_DYNAMIC', 'PT_GNU_EH_FRAME',
                            'PT_GNU_RELRO', 'PT_GNU_STACK')):
            return False

        # In ELF_SECTION_IN_SEGMENT_STRICT the flag check_vma is on, so if
        # this is an alloc section, check whether its VMA is in bounds.
        if secflags & SH_FLAGS.SHF_ALLOC:
            secaddr = section['sh_addr']
            vaddr = self['p_vaddr']

            # This checks that the section is wholly contained in the segment.
            # The third condition is the 'strict' one - an empty section will
            # not match at the very end of the segment (unless the segment is
            # also zero size, which is handled by the second condition).

            # Seva 2024-07-12: a zero length section at a zero offset
            # in a zero length segment should match - in GNU readelf, p_memsz
            # is unsigned, on a zero length segment p_memsz-1 wraps around
            # and the third condition matches.
            if not (secaddr >= vaddr and
                    secaddr - vaddr + section['sh_size'] <= self['p_memsz'] and
                    (self['p_memsz'] == 0 or secaddr - vaddr <= self['p_memsz'] - 1)):
                return False

        # If we've come this far and it's a NOBITS section, it's in the segment
        if sectype == 'SHT_NOBITS':
            return True

        secoffset = section['sh_offset']
        poffset = self['p_offset']

        # Same logic as with secaddr vs. vaddr checks above, just on offsets in
        # the file
        # Seva 2024-07-12: similar discrepancy with readelf from unsignedness of p_filesz
        return (secoffset >= poffset and
                secoffset - poffset + section['sh_size'] <= self['p_filesz'] and
                (self['p_filesz'] == 0 or secoffset - poffset <= self['p_filesz'] - 1))


class InterpSegment(Segment):
    """ INTERP segment. Knows how to obtain the path to the interpreter used
        for this ELF file.
    """
    def __init__(self, header, stream):
        super(InterpSegment, self).__init__(header, stream)

    def get_interp_name(self):
        """ Obtain the interpreter path used for this ELF file.
        """
        path_offset = self['p_offset']
        return struct_parse(
            CString('', encoding='utf-8'),
            self.stream,
            stream_pos=path_offset)


class NoteSegment(Segment):
    """ NOTE segment. Knows how to parse notes.
    """
    def __init__(self, header, stream, elffile):
        super(NoteSegment, self).__init__(header, stream)
        self.elffile = elffile

    def iter_notes(self):

        """ Yield all the notes in the segment.  Each result is a dictionary-
            like object with "n_name", "n_type", and "n_desc" fields, amongst
            others.
        """
        return iter_notes(self.elffile, self['p_offset'], self['p_filesz'])
