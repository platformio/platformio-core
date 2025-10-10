#-------------------------------------------------------------------------------
# elftools: elf/notes.py
#
# ELF notes
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from ..common.utils import struct_parse, bytes2hex, roundup, bytes2str
from ..construct import CString


def iter_notes(elffile, offset, size):
    """ Yield all the notes in a section or segment.
    """
    end = offset + size
    nhdr_size = elffile.structs.Elf_Nhdr.sizeof()
    # Note: a note's name and data are 4-byte aligned, but it's possible there's
    # additional padding at the end to satisfy the alignment requirement of the segment.
    while offset + nhdr_size < end:
        note = struct_parse(
            elffile.structs.Elf_Nhdr,
            elffile.stream,
            stream_pos=offset)
        note['n_offset'] = offset
        offset += nhdr_size
        elffile.stream.seek(offset)
        if note['n_namesz']:
            # n_namesz is 4-byte aligned.
            disk_namesz = roundup(note['n_namesz'], 2)
            note['n_name'] = bytes2str(
                CString('').parse(elffile.stream.read(disk_namesz)))
            offset += disk_namesz
        else:
            note['n_name'] = None

        desc_data = elffile.stream.read(note['n_descsz'])
        note['n_descdata'] = desc_data
        if note['n_type'] == 'NT_GNU_ABI_TAG' and note['n_name'] == 'GNU':
            note['n_desc'] = struct_parse(elffile.structs.Elf_abi,
                                          elffile.stream,
                                          offset)
        elif note['n_type'] == 'NT_GNU_BUILD_ID' and note['n_name'] == 'GNU':
            note['n_desc'] = bytes2hex(desc_data)
        elif note['n_type'] == 'NT_GNU_GOLD_VERSION' and note['n_name'] == 'GNU':
            note['n_desc'] = bytes2str(desc_data)
        elif note['n_type'] == 'NT_PRPSINFO':
            note['n_desc'] = struct_parse(elffile.structs.Elf_Prpsinfo,
                                          elffile.stream,
                                          offset)
        elif note['n_type'] == 'NT_FILE':
            note['n_desc'] = struct_parse(elffile.structs.Elf_Nt_File,
                                          elffile.stream,
                                          offset)
        elif note['n_type'] == 'NT_GNU_PROPERTY_TYPE_0' and note['n_name'] == 'GNU':
            off = offset
            props = []
            # n_descsz contains the size of the note "descriptor" (the data payload),
            # excluding padding. See "Note Section" in https://refspecs.linuxfoundation.org/elf/elf.pdf
            current_note_end = offset + note['n_descsz']
            while off < current_note_end:
                p = struct_parse(elffile.structs.Elf_Prop, elffile.stream, off)
                off += roundup(p.pr_datasz + 8, 2 if elffile.elfclass == 32 else 3)
                props.append(p)
            note['n_desc'] = props
        else:
            note['n_desc'] = desc_data
        offset += roundup(note['n_descsz'], 2)
        note['n_size'] = offset - note['n_offset']
        yield note
