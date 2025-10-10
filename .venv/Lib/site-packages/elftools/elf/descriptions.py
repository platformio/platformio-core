#-------------------------------------------------------------------------------
# elftools: elf/descriptions.py
#
# Textual descriptions of the various enums and flags of ELF
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from .enums import (
    ENUM_D_TAG, ENUM_E_VERSION, ENUM_P_TYPE_BASE, ENUM_SH_TYPE_BASE,
    ENUM_RELOC_TYPE_i386, ENUM_RELOC_TYPE_x64,
    ENUM_RELOC_TYPE_ARM, ENUM_RELOC_TYPE_AARCH64, ENUM_RELOC_TYPE_PPC64,
    ENUM_RELOC_TYPE_MIPS, ENUM_ATTR_TAG_ARM, ENUM_ATTR_TAG_RISCV,
    ENUM_RELOC_TYPE_S390X, ENUM_RELOC_TYPE_LOONGARCH, ENUM_DT_FLAGS,
    ENUM_DT_FLAGS_1, ENUM_RELOC_TYPE_PPC)
from .constants import (
    P_FLAGS, RH_FLAGS, SH_FLAGS, SUNW_SYMINFO_FLAGS, VER_FLAGS)
from ..common.utils import bytes2hex


def describe_ei_class(x):
    return _DESCR_EI_CLASS.get(x, _unknown)


def describe_ei_data(x):
    return _DESCR_EI_DATA.get(x, _unknown)


def describe_ei_version(x):
    s = '%d' % ENUM_E_VERSION[x]
    if x == 'EV_CURRENT':
        s += ' (current)'
    return s


def describe_ei_osabi(x):
    return _DESCR_EI_OSABI.get(x, _unknown)


def describe_e_type(x, elffile=None):
    if elffile is not None and x == 'ET_DYN':
        # Detect whether this is a normal SO or a PIE executable
        dynamic = elffile.get_section_by_name('.dynamic')
        for t in dynamic.iter_tags('DT_FLAGS_1'):
            if t.entry.d_val & ENUM_DT_FLAGS_1['DF_1_PIE']:
                return 'DYN (Position-Independent Executable file)'
    return _DESCR_E_TYPE.get(x, _unknown)


def describe_e_machine(x):
    return _DESCR_E_MACHINE.get(x, _unknown)


def describe_e_version_numeric(x):
    return '0x%x' % ENUM_E_VERSION[x]


def describe_p_type(x):
    if x in _DESCR_P_TYPE:
        return _DESCR_P_TYPE.get(x)
    elif x >= ENUM_P_TYPE_BASE['PT_LOOS'] and x <= ENUM_P_TYPE_BASE['PT_HIOS']:
        return 'LOOS+%lx' % (x - ENUM_P_TYPE_BASE['PT_LOOS'])
    else:
        return _unknown


def describe_p_flags(x):
    s = ''
    for flag in (P_FLAGS.PF_R, P_FLAGS.PF_W, P_FLAGS.PF_X):
        s += _DESCR_P_FLAGS[flag] if (x & flag) else ' '
    return s


def describe_rh_flags(x):
    return ' '.join(
        _DESCR_RH_FLAGS[flag]
        for flag in (RH_FLAGS.RHF_NONE, RH_FLAGS.RHF_QUICKSTART,
                     RH_FLAGS.RHF_NOTPOT, RH_FLAGS.RHF_NO_LIBRARY_REPLACEMENT,
                     RH_FLAGS.RHF_NO_MOVE, RH_FLAGS.RHF_SGI_ONLY,
                     RH_FLAGS.RHF_GUARANTEE_INIT,
                     RH_FLAGS.RHF_DELTA_C_PLUS_PLUS,
                     RH_FLAGS.RHF_GUARANTEE_START_INIT, RH_FLAGS.RHF_PIXIE,
                     RH_FLAGS.RHF_DEFAULT_DELAY_LOAD,
                     RH_FLAGS.RHF_REQUICKSTART, RH_FLAGS.RHF_REQUICKSTARTED,
                     RH_FLAGS.RHF_CORD, RH_FLAGS.RHF_NO_UNRES_UNDEF,
                     RH_FLAGS.RHF_RLD_ORDER_SAFE)
        if x & flag)


def describe_sh_type(x):
    if x in _DESCR_SH_TYPE:
        return _DESCR_SH_TYPE.get(x)
    elif (x >= ENUM_SH_TYPE_BASE['SHT_LOOS'] and
          x < ENUM_SH_TYPE_BASE['SHT_GNU_versym']):
        return 'loos+0x%lx' % (x - ENUM_SH_TYPE_BASE['SHT_LOOS'])
    else:
        return _unknown


def describe_sh_flags(x):
    s = ''
    for flag in (
            SH_FLAGS.SHF_WRITE, SH_FLAGS.SHF_ALLOC, SH_FLAGS.SHF_EXECINSTR,
            SH_FLAGS.SHF_MERGE, SH_FLAGS.SHF_STRINGS, SH_FLAGS.SHF_INFO_LINK,
            SH_FLAGS.SHF_LINK_ORDER, SH_FLAGS.SHF_OS_NONCONFORMING,
            SH_FLAGS.SHF_GROUP, SH_FLAGS.SHF_TLS, SH_FLAGS.SHF_MASKOS,
            SH_FLAGS.SHF_EXCLUDE):
        s += _DESCR_SH_FLAGS[flag] if (x & flag) else ''
    if not x & SH_FLAGS.SHF_EXCLUDE:
        if x & SH_FLAGS.SHF_MASKPROC:
            s += 'p'
    return s


def describe_symbol_type(x):
    return _DESCR_ST_INFO_TYPE.get(x, _unknown)


def describe_symbol_bind(x):
    return _DESCR_ST_INFO_BIND.get(x, _unknown)


def describe_symbol_visibility(x):
    return _DESCR_ST_VISIBILITY.get(x, _unknown)


def describe_symbol_local(x):
    return '[<localentry>: ' + str(1 << x) + ']'


def describe_symbol_other(x):
    vis = describe_symbol_visibility(x['visibility'])
    if x['local'] > 1 and x['local'] < 7:
        return vis + ' ' + describe_symbol_local(x['local'])
    return vis


def describe_symbol_shndx(x):
    return _DESCR_ST_SHNDX.get(x, '%3s' % x)


def describe_reloc_type(x, elffile):
    arch = elffile.get_machine_arch()
    if arch == 'x86':
        return _DESCR_RELOC_TYPE_i386.get(x, _unknown)
    elif arch == 'x64':
        return _DESCR_RELOC_TYPE_x64.get(x, _unknown)
    elif arch == 'ARM':
        return _DESCR_RELOC_TYPE_ARM.get(x, _unknown)
    elif arch == 'AArch64':
        return _DESCR_RELOC_TYPE_AARCH64.get(x, _unknown)
    elif arch == '64-bit PowerPC':
        return _DESCR_RELOC_TYPE_PPC64.get(x, _unknown)
    elif arch == 'PowerPC':
        return _DESCR_RELOC_TYPE_PPC.get(x, _unknown)
    elif arch == 'IBM S/390':
        return _DESCR_RELOC_TYPE_S390X.get(x, _unknown)
    elif arch == 'MIPS':
        return _DESCR_RELOC_TYPE_MIPS.get(x, _unknown)
    elif arch == 'LoongArch':
        return _DESCR_RELOC_TYPE_LOONGARCH.get(x, _unknown)
    else:
        return 'unrecognized: %-7x' % (x & 0xFFFFFFFF)


def describe_dyn_tag(x):
    return _DESCR_D_TAG.get(x, _unknown)


def describe_dt_flags(x):
    return ' '.join(key[3:] for key, val in
        sorted(ENUM_DT_FLAGS.items(), key=lambda t: t[1]) if x & val)


def describe_dt_flags_1(x):
    return ' '.join(key[5:] for key, val in
        sorted(ENUM_DT_FLAGS_1.items(), key=lambda t: t[1]) if x & val)


def describe_syminfo_flags(x):
    return ''.join(_DESCR_SYMINFO_FLAGS[flag] for flag in (
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_CAP,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_DIRECT,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_FILTER,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_AUXILIARY,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_DIRECTBIND,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_COPY,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_LAZYLOAD,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_NOEXTDIRECT,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_INTERPOSE,
        SUNW_SYMINFO_FLAGS.SYMINFO_FLG_DEFERRED) if x & flag)


def describe_symbol_boundto(x):
    return _DESCR_SYMINFO_BOUNDTO.get(x, '%3s' % x)


def describe_ver_flags(x):
    return ' | '.join(_DESCR_VER_FLAGS[flag] for flag in (
        VER_FLAGS.VER_FLG_WEAK,
        VER_FLAGS.VER_FLG_BASE,
        VER_FLAGS.VER_FLG_INFO) if x & flag)


def describe_note(x, machine):
    n_desc = x['n_desc']
    desc = ''
    if x['n_type'] == 'NT_GNU_ABI_TAG':
        if x['n_name'] == 'GNU':
            desc = '\n    OS: %s, ABI: %d.%d.%d' % (
                _DESCR_NOTE_ABI_TAG_OS.get(n_desc['abi_os'], _unknown),
                n_desc['abi_major'], n_desc['abi_minor'], n_desc['abi_tiny'])
        else:
            desc = '\n   description data: %s ' % bytes2hex(x['n_descdata'])
    elif x['n_type'] == 'NT_GNU_BUILD_ID':
        desc = '\n    Build ID: %s' % (n_desc)
    elif x['n_type'] == 'NT_GNU_GOLD_VERSION':
        desc = '\n    Version: %s' % (n_desc)
    elif x['n_type'] == 'NT_GNU_PROPERTY_TYPE_0':
        if x['n_name'] == 'GNU':
            desc = '\n      Properties: ' + describe_note_gnu_properties(x['n_desc'], machine)
        else:
            desc = '\n   description data: %s ' % bytes2hex(x['n_descdata'])
    else:
        desc = '\n      description data: {}'.format(bytes2hex(n_desc))

    if x['n_type'] == 'NT_GNU_ABI_TAG' and x['n_name'] == 'Android':
        note_type = 'NT_VERSION'
        note_type_desc = 'version'
    else:
        note_type = (x['n_type'] if isinstance(x['n_type'], str)
                    else 'Unknown note type:')
        note_type_desc = ('0x%.8x' % x['n_type']
                        if isinstance(x['n_type'], int) else
                        _DESCR_NOTE_N_TYPE.get(x['n_type'], _unknown))
    return '%s (%s)%s' % (note_type, note_type_desc, desc)


def describe_attr_tag_arm(tag, val, extra):
    idx = ENUM_ATTR_TAG_ARM[tag] - 1
    d_entry = _DESCR_ATTR_VAL_ARM[idx]

    if d_entry is None:
        if tag == 'TAG_COMPATIBILITY':
            return (_DESCR_ATTR_TAG_ARM[tag]
                    + 'flag = %d, vendor = %s' % (val, extra))

        elif tag == 'TAG_ALSO_COMPATIBLE_WITH':
            if val.tag == 'TAG_CPU_ARCH':
                return _DESCR_ATTR_TAG_ARM[tag] + d_entry[val]

            else:
                return _DESCR_ATTR_TAG_ARM[tag] + '??? (%d)' % val.tag

        elif tag == 'TAG_NODEFAULTS':
            return _DESCR_ATTR_TAG_ARM[tag] + 'True'

        s = _DESCR_ATTR_TAG_ARM[tag]
        s += '"%s"' % val if val else ''
        return s

    else:
        return _DESCR_ATTR_TAG_ARM[tag] + d_entry[val]

def describe_attr_tag_riscv(tag, val, extra):
    idx = ENUM_ATTR_TAG_RISCV[tag] - 1
    d_entry = _DESCR_ATTR_VAL_RISCV[idx]

    if d_entry is None:
        s = _DESCR_ATTR_TAG_RISCV[tag]
        s += '"%s"' % val if val else ''
        return s

    else:
        return _DESCR_ATTR_TAG_RISCV[tag] + d_entry[val]

def describe_note_gnu_property_bitmap_and(values, prefix, value):
    descs = []
    for mask, desc in values:
        if value & mask:
            descs.append(desc)
    return '%s: %s' % (prefix, ', '.join(descs))

def describe_note_gnu_properties(properties, machine):
    descriptions = []
    for prop in properties:
        t, d, sz = prop.pr_type, prop.pr_data, prop.pr_datasz
        if t == 'GNU_PROPERTY_STACK_SIZE':
            if type(d) is int:
                prop_desc = 'stack size: 0x%x' % d
            else:
                prop_desc = 'stack size: <corrupt length: 0x%x>' % sz
        elif t == 'GNU_PROPERTY_NO_COPY_ON_PROTECTED':
            if sz != 0:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = 'no copy on protected'
        elif t == 'GNU_PROPERTY_X86_FEATURE_1_AND':
            if sz != 4:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = describe_note_gnu_property_bitmap_and(_DESCR_NOTE_GNU_PROPERTY_X86_FEATURE_1_FLAGS, 'x86 feature', d)
        elif t == 'GNU_PROPERTY_X86_FEATURE_2_USED':
            if sz != 4:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = describe_note_gnu_property_bitmap_and(_DESCR_NOTE_GNU_PROPERTY_X86_FEATURE_2_FLAGS, 'x86 feature used', d)                
        elif t == 'GNU_PROPERTY_X86_ISA_1_NEEDED':
            if sz != 4:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = describe_note_gnu_property_bitmap_and(_DESCR_NOTE_GNU_PROPERTY_X86_ISA_1_FLAGS, 'x86 ISA needed', d)
        elif t == 'GNU_PROPERTY_X86_ISA_1_USED':
            if sz != 4:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = describe_note_gnu_property_bitmap_and(_DESCR_NOTE_GNU_PROPERTY_X86_ISA_1_FLAGS, 'x86 ISA used', d)
        elif t == 'GNU_PROPERTY_AARCH64_FEATURE_1_AND' and machine == 'EM_AARCH64':
            if sz != 4:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = describe_note_gnu_property_bitmap_and(_DESCR_NOTE_GNU_PROPERTY_AARCH64_FEATURE_1_AND, 'aarch64 feature', d)
        elif t == 'GNU_PROPERTY_AARCH64_FEATURE_1_AND' and machine == 'EM_RISCV':
            # RISC-V shares the same bit-mask with AArch64
            if sz != 4:
                prop_desc = ' <corrupt length: 0x%x>' % sz
            else:
                prop_desc = describe_note_gnu_property_bitmap_and(_DESCR_NOTE_GNU_PROPERTY_RISCV_FEATURE_1_AND, 'RISC-V AND feature', d)
        elif _DESCR_NOTE_GNU_PROPERTY_TYPE_LOPROC <= t <= _DESCR_NOTE_GNU_PROPERTY_TYPE_HIPROC:
            prop_desc = '<processor-specific type 0x%x data: %s >' % (t, bytes2hex(d, sep=' '))
        elif _DESCR_NOTE_GNU_PROPERTY_TYPE_LOUSER <= t <= _DESCR_NOTE_GNU_PROPERTY_TYPE_HIUSER:
            prop_desc = '<application-specific type 0x%x data: %s >' % (t, bytes2hex(d, sep=' '))
        else:
            prop_desc = '<unknown type 0x%x data: %s >' % (t, bytes2hex(d, sep=' '))
        descriptions.append(prop_desc)
    return '\n        '.join(descriptions)

#-------------------------------------------------------------------------------
_unknown = '<unknown>'


_DESCR_EI_CLASS = dict(
    ELFCLASSNONE='none',
    ELFCLASS32='ELF32',
    ELFCLASS64='ELF64',
)


_DESCR_EI_DATA = dict(
    ELFDATANONE='none',
    ELFDATA2LSB="2's complement, little endian",
    ELFDATA2MSB="2's complement, big endian",
)


_DESCR_EI_OSABI = dict(
    ELFOSABI_SYSV='UNIX - System V',
    ELFOSABI_HPUX='UNIX - HP-UX',
    ELFOSABI_NETBSD='UNIX - NetBSD',
    ELFOSABI_LINUX='UNIX - Linux',
    ELFOSABI_HURD='UNIX - GNU/Hurd',
    ELFOSABI_SOLARIS='UNIX - Solaris',
    ELFOSABI_AIX='UNIX - AIX',
    ELFOSABI_IRIX='UNIX - IRIX',
    ELFOSABI_FREEBSD='UNIX - FreeBSD',
    ELFOSABI_TRU64='UNIX - TRU64',
    ELFOSABI_MODESTO='Novell - Modesto',
    ELFOSABI_OPENBSD='UNIX - OpenBSD',
    ELFOSABI_OPENVMS='VMS - OpenVMS',
    ELFOSABI_NSK='HP - Non-Stop Kernel',
    ELFOSABI_AROS='AROS',
    ELFOSABI_FENIXOS='Fenix OS',
    ELFOSABI_CLOUD='Nuxi - CloudABI',
    ELFOSABI_SORTIX='Sortix',
    ELFOSABI_ARM_AEABI='ARM - EABI',
    ELFOSABI_ARM='ARM - ABI',
    ELFOSABI_CELL_LV2='CellOS Lv-2',
    ELFOSABI_STANDALONE='Standalone App',
)


_DESCR_E_TYPE = dict(
    ET_NONE='NONE (None)',
    ET_REL='REL (Relocatable file)',
    ET_EXEC='EXEC (Executable file)',
    ET_DYN='DYN (Shared object file)',
    ET_CORE='CORE (Core file)',
    PROC_SPECIFIC='Processor Specific',
)


_DESCR_E_MACHINE = dict(
    EM_NONE='None',
    EM_M32='WE32100',
    EM_SPARC='Sparc',
    EM_386='Intel 80386',
    EM_68K='MC68000',
    EM_88K='MC88000',
    EM_860='Intel 80860',
    EM_MIPS='MIPS R3000',
    EM_S370='IBM System/370',
    EM_S390='IBM S/390',
    EM_MIPS_RS4_BE='MIPS 4000 big-endian',
    EM_IA_64='Intel IA-64',
    EM_X86_64='Advanced Micro Devices X86-64',
    EM_AVR='Atmel AVR 8-bit microcontroller',
    EM_ARM='ARM',
    EM_AARCH64='AArch64',
    EM_BLACKFIN='Analog Devices Blackfin',
    EM_PPC='PowerPC',
    EM_PPC64='PowerPC64',
    EM_RISCV='RISC-V',
    EM_LOONGARCH='LoongArch',
    RESERVED='RESERVED',
)


_DESCR_P_TYPE = dict(
    PT_NULL='NULL',
    PT_LOAD='LOAD',
    PT_DYNAMIC='DYNAMIC',
    PT_INTERP='INTERP',
    PT_NOTE='NOTE',
    PT_SHLIB='SHLIB',
    PT_PHDR='PHDR',
    PT_GNU_EH_FRAME='GNU_EH_FRAME',
    PT_GNU_STACK='GNU_STACK',
    PT_GNU_RELRO='GNU_RELRO',
    PT_GNU_PROPERTY='GNU_PROPERTY',
    PT_ARM_ARCHEXT='ARM_ARCHEXT',
    PT_ARM_EXIDX='EXIDX',  # binutils calls this EXIDX, not ARM_EXIDX
    PT_AARCH64_ARCHEXT='AARCH64_ARCHEXT',
    PT_AARCH64_UNWIND='AARCH64_UNWIND',
    PT_TLS='TLS',
    PT_MIPS_ABIFLAGS='ABIFLAGS',
    PT_RISCV_ATTRIBUTES='RISCV_ATTRIBUT',
)


_DESCR_P_FLAGS = {
    P_FLAGS.PF_X: 'E',
    P_FLAGS.PF_R: 'R',
    P_FLAGS.PF_W: 'W',
}


_DESCR_SH_TYPE = dict(
    SHT_NULL='NULL',
    SHT_PROGBITS='PROGBITS',
    SHT_SYMTAB='SYMTAB',
    SHT_STRTAB='STRTAB',
    SHT_RELA='RELA',
    SHT_HASH='HASH',
    SHT_DYNAMIC='DYNAMIC',
    SHT_NOTE='NOTE',
    SHT_NOBITS='NOBITS',
    SHT_REL='REL',
    SHT_SHLIB='SHLIB',
    SHT_DYNSYM='DYNSYM',
    SHT_INIT_ARRAY='INIT_ARRAY',
    SHT_FINI_ARRAY='FINI_ARRAY',
    SHT_PREINIT_ARRAY='PREINIT_ARRAY',
    SHT_GNU_ATTRIBUTES='GNU_ATTRIBUTES',
    SHT_GNU_HASH='GNU_HASH',
    SHT_GROUP='GROUP',
    SHT_SYMTAB_SHNDX='SYMTAB SECTION INDICIES',
    SHT_RELR='RELR',
    SHT_GNU_verdef='VERDEF',
    SHT_GNU_verneed='VERNEED',
    SHT_GNU_versym='VERSYM',
    SHT_GNU_LIBLIST='GNU_LIBLIST',
    SHT_AMD64_UNWIND='X86_64_UNWIND',
    SHT_ARM_EXIDX='ARM_EXIDX',
    SHT_ARM_PREEMPTMAP='ARM_PREEMPTMAP',
    SHT_ARM_ATTRIBUTES='ARM_ATTRIBUTES',
    SHT_ARM_DEBUGOVERLAY='ARM_DEBUGOVERLAY',
    SHT_AARCH64_ATTRIBUTES='AARCH64_ATTRIBUTES',
    SHT_RISCV_ATTRIBUTES='RISCV_ATTRIBUTES',
    SHT_MIPS_LIBLIST='MIPS_LIBLIST',
    SHT_MIPS_DEBUG='MIPS_DEBUG',
    SHT_MIPS_REGINFO='MIPS_REGINFO',
    SHT_MIPS_PACKAGE='MIPS_PACKAGE',
    SHT_MIPS_PACKSYM='MIPS_PACKSYM',
    SHT_MIPS_RELD='MIPS_RELD',
    SHT_MIPS_IFACE='MIPS_IFACE',
    SHT_MIPS_CONTENT='MIPS_CONTENT',
    SHT_MIPS_OPTIONS='MIPS_OPTIONS',
    SHT_MIPS_SHDR='MIPS_SHDR',
    SHT_MIPS_FDESC='MIPS_FDESC',
    SHT_MIPS_EXTSYM='MIPS_EXTSYM',
    SHT_MIPS_DENSE='MIPS_DENSE',
    SHT_MIPS_PDESC='MIPS_PDESC',
    SHT_MIPS_LOCSYM='MIPS_LOCSYM',
    SHT_MIPS_AUXSYM='MIPS_AUXSYM',
    SHT_MIPS_OPTSYM='MIPS_OPTSYM',
    SHT_MIPS_LOCSTR='MIPS_LOCSTR',
    SHT_MIPS_LINE='MIPS_LINE',
    SHT_MIPS_RFDESC='MIPS_RFDESC',
    SHT_MIPS_DELTASYM='MIPS_DELTASYM',
    SHT_MIPS_DELTAINST='MIPS_DELTAINST',
    SHT_MIPS_DELTACLASS='MIPS_DELTACLASS',
    SHT_MIPS_DWARF='MIPS_DWARF',
    SHT_MIPS_DELTADECL='MIPS_DELTADECL',
    SHT_MIPS_SYMBOL_LIB='MIPS_SYMBOL_LIB',
    SHT_MIPS_EVENTS='MIPS_EVENTS',
    SHT_MIPS_TRANSLATE='MIPS_TRANSLATE',
    SHT_MIPS_PIXIE='MIPS_PIXIE',
    SHT_MIPS_XLATE='MIPS_XLATE',
    SHT_MIPS_XLATE_DEBUG='MIPS_XLATE_DEBUG',
    SHT_MIPS_WHIRL='MIPS_WHIRL',
    SHT_MIPS_EH_REGION='MIPS_EH_REGION',
    SHT_MIPS_XLATE_OLD='MIPS_XLATE_OLD',
    SHT_MIPS_PDR_EXCEPTION='MIPS_PDR_EXCEPTION',
    SHT_MIPS_ABIFLAGS='MIPS_ABIFLAGS',
)


_DESCR_SH_FLAGS = {
    SH_FLAGS.SHF_WRITE: 'W',
    SH_FLAGS.SHF_ALLOC: 'A',
    SH_FLAGS.SHF_EXECINSTR: 'X',
    SH_FLAGS.SHF_MERGE: 'M',
    SH_FLAGS.SHF_STRINGS: 'S',
    SH_FLAGS.SHF_INFO_LINK: 'I',
    SH_FLAGS.SHF_LINK_ORDER: 'L',
    SH_FLAGS.SHF_OS_NONCONFORMING: 'O',
    SH_FLAGS.SHF_GROUP: 'G',
    SH_FLAGS.SHF_TLS: 'T',
    SH_FLAGS.SHF_MASKOS: 'o',
    SH_FLAGS.SHF_EXCLUDE: 'E',
}


_DESCR_RH_FLAGS = {
    RH_FLAGS.RHF_NONE: 'NONE',
    RH_FLAGS.RHF_QUICKSTART: 'QUICKSTART',
    RH_FLAGS.RHF_NOTPOT: 'NOTPOT',
    RH_FLAGS.RHF_NO_LIBRARY_REPLACEMENT: 'NO_LIBRARY_REPLACEMENT',
    RH_FLAGS.RHF_NO_MOVE: 'NO_MOVE',
    RH_FLAGS.RHF_SGI_ONLY: 'SGI_ONLY',
    RH_FLAGS.RHF_GUARANTEE_INIT: 'GUARANTEE_INIT',
    RH_FLAGS.RHF_DELTA_C_PLUS_PLUS: 'DELTA_C_PLUS_PLUS',
    RH_FLAGS.RHF_GUARANTEE_START_INIT: 'GUARANTEE_START_INIT',
    RH_FLAGS.RHF_PIXIE: 'PIXIE',
    RH_FLAGS.RHF_DEFAULT_DELAY_LOAD: 'DEFAULT_DELAY_LOAD',
    RH_FLAGS.RHF_REQUICKSTART: 'REQUICKSTART',
    RH_FLAGS.RHF_REQUICKSTARTED: 'REQUICKSTARTED',
    RH_FLAGS.RHF_CORD: 'CORD',
    RH_FLAGS.RHF_NO_UNRES_UNDEF: 'NO_UNRES_UNDEF',
    RH_FLAGS.RHF_RLD_ORDER_SAFE: 'RLD_ORDER_SAFE',
}


_DESCR_ST_INFO_TYPE = dict(
    STT_NOTYPE='NOTYPE',
    STT_OBJECT='OBJECT',
    STT_FUNC='FUNC',
    STT_SECTION='SECTION',
    STT_FILE='FILE',
    STT_COMMON='COMMON',
    STT_TLS='TLS',
    STT_NUM='NUM',
    STT_RELC='RELC',
    STT_SRELC='SRELC',
)


_DESCR_ST_INFO_BIND = dict(
    STB_LOCAL='LOCAL',
    STB_GLOBAL='GLOBAL',
    STB_WEAK='WEAK',
)


_DESCR_ST_VISIBILITY = dict(
    STV_DEFAULT='DEFAULT',
    STV_INTERNAL='INTERNAL',
    STV_HIDDEN='HIDDEN',
    STV_PROTECTED='PROTECTED',
    STV_EXPORTED='EXPORTED',
    STV_SINGLETON='SINGLETON',
    STV_ELIMINATE='ELIMINATE',
)


_DESCR_ST_SHNDX = dict(
    SHN_UNDEF='UND',
    SHN_ABS='ABS',
    SHN_COMMON='COM',
)


_DESCR_SYMINFO_FLAGS = {
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_DIRECT: 'D',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_DIRECTBIND: 'B',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_COPY: 'C',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_LAZYLOAD: 'L',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_NOEXTDIRECT: 'N',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_AUXILIARY: 'A',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_FILTER: 'F',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_INTERPOSE: 'I',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_CAP: 'S',
    SUNW_SYMINFO_FLAGS.SYMINFO_FLG_DEFERRED: 'P',
}


_DESCR_SYMINFO_BOUNDTO = dict(
    SYMINFO_BT_SELF='<self>',
    SYMINFO_BT_PARENT='<parent>',
    SYMINFO_BT_NONE='',
    SYMINFO_BT_EXTERN='<extern>',
)


_DESCR_VER_FLAGS = {
    0: '',
    VER_FLAGS.VER_FLG_BASE: 'BASE',
    VER_FLAGS.VER_FLG_WEAK: 'WEAK',
    VER_FLAGS.VER_FLG_INFO: 'INFO',
}


# PT_NOTE section types
_DESCR_NOTE_N_TYPE = dict(
    NT_GNU_ABI_TAG='ABI version tag',
    NT_GNU_HWCAP='DSO-supplied software HWCAP info',
    NT_GNU_BUILD_ID='unique build ID bitstring',
    NT_GNU_GOLD_VERSION='gold version',
    NT_GNU_PROPERTY_TYPE_0='program properties'
)


# Values in GNU .note.ABI-tag notes (n_type=='NT_GNU_ABI_TAG')
_DESCR_NOTE_ABI_TAG_OS = dict(
    ELF_NOTE_OS_LINUX='Linux',
    ELF_NOTE_OS_GNU='GNU',
    ELF_NOTE_OS_SOLARIS2='Solaris 2',
    ELF_NOTE_OS_FREEBSD='FreeBSD',
    ELF_NOTE_OS_NETBSD='NetBSD',
    ELF_NOTE_OS_SYLLABLE='Syllable',
)


# Values in GNU .note.gnu.property notes (n_type=='NT_GNU_PROPERTY_TYPE_0') have
# different formats which need to be parsed/described differently
_DESCR_NOTE_GNU_PROPERTY_TYPE_LOPROC=0xc0000000
_DESCR_NOTE_GNU_PROPERTY_TYPE_HIPROC=0xdfffffff
_DESCR_NOTE_GNU_PROPERTY_TYPE_LOUSER=0xe0000000
_DESCR_NOTE_GNU_PROPERTY_TYPE_HIUSER=0xffffffff


# Bit masks for GNU_PROPERTY_X86_FEATURE_1_xxx flags in the form
# (mask, flag_description) in the desired output order
_DESCR_NOTE_GNU_PROPERTY_X86_FEATURE_1_FLAGS = (
    (1, 'IBT'),
    (2, 'SHSTK'),
    (4, 'LAM_U48'),
    (8, 'LAM_U57'),
)

# Bit masks for GNU_PROPERTY_X86_FEATURE_2_xxx flags in the form
# (mask, flag_description) in the desired output order
_DESCR_NOTE_GNU_PROPERTY_X86_FEATURE_2_FLAGS = (
    (1, 'x86'),
    (2, 'x87'),
    (4, 'MMX'),
    (8, 'XMM'),
    (16, 'YMM'),
    (32, 'ZMM'),
)

# Same for GNU_PROPERTY_X86_SET_1_xxx
_DESCR_NOTE_GNU_PROPERTY_X86_ISA_1_FLAGS = (
    (1, 'x86-64-baseline'),
    # TODO; there is a long list
)

# Same for GNU_PROPERTY_AARCH64_FEATURE_1_AND
_DESCR_NOTE_GNU_PROPERTY_AARCH64_FEATURE_1_AND = (
    (1, 'bti'),
    (2, 'pac'),
)

_DESCR_NOTE_GNU_PROPERTY_RISCV_FEATURE_1_AND = (
    (1, 'ZICFILP'),
    (2, 'ZICFISS'),
)

def _reverse_dict(d, low_priority=()):
    """
    This is a tiny helper function to "reverse" the keys/values of a dictionary
    provided in the first argument, i.e. {k: v} becomes {v: k}.

    The second argument (optional) provides primitive control over what to do in
    the case of conflicting values - if a value is present in this list, it will
    not override any other entries of the same value.
    """
    out = {}
    for k, v in d.items():
        if v in out and k in low_priority:
            continue
        out[v] = k
    return out

_DESCR_RELOC_TYPE_i386 = _reverse_dict(ENUM_RELOC_TYPE_i386)
_DESCR_RELOC_TYPE_x64 = _reverse_dict(ENUM_RELOC_TYPE_x64)
_DESCR_RELOC_TYPE_ARM = _reverse_dict(ENUM_RELOC_TYPE_ARM)
_DESCR_RELOC_TYPE_AARCH64 = _reverse_dict(ENUM_RELOC_TYPE_AARCH64)
_DESCR_RELOC_TYPE_PPC64 = _reverse_dict(ENUM_RELOC_TYPE_PPC64)
_DESCR_RELOC_TYPE_PPC = _reverse_dict(ENUM_RELOC_TYPE_PPC)
_DESCR_RELOC_TYPE_S390X = _reverse_dict(ENUM_RELOC_TYPE_S390X)
_DESCR_RELOC_TYPE_MIPS = _reverse_dict(ENUM_RELOC_TYPE_MIPS)
_DESCR_RELOC_TYPE_LOONGARCH = _reverse_dict(ENUM_RELOC_TYPE_LOONGARCH)

_low_priority_D_TAG = (
    # these are 'meta-tags' marking semantics of numeric ranges of the enum
    # they should not override other tags with the same numbers
    # see https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-42444.html
    'DT_LOOS',
    'DT_HIOS',
    'DT_LOPROC',
    'DT_HIPROC',
    'DT_ENCODING',
)
_DESCR_D_TAG = _reverse_dict(ENUM_D_TAG, low_priority=_low_priority_D_TAG)

_DESCR_ATTR_TAG_ARM = dict(
    TAG_FILE='File Attributes',
    TAG_SECTION='Section Attributes:',
    TAG_SYMBOL='Symbol Attributes:',
    TAG_CPU_RAW_NAME='Tag_CPU_raw_name: ',
    TAG_CPU_NAME='Tag_CPU_name: ',
    TAG_CPU_ARCH='Tag_CPU_arch: ',
    TAG_CPU_ARCH_PROFILE='Tag_CPU_arch_profile: ',
    TAG_ARM_ISA_USE='Tag_ARM_ISA_use: ',
    TAG_THUMB_ISA_USE='Tag_Thumb_ISA_use: ',
    TAG_FP_ARCH='Tag_FP_arch: ',
    TAG_WMMX_ARCH='Tag_WMMX_arch: ',
    TAG_ADVANCED_SIMD_ARCH='Tag_Advanced_SIMD_arch: ',
    TAG_PCS_CONFIG='Tag_PCS_config: ',
    TAG_ABI_PCS_R9_USE='Tag_ABI_PCS_R9_use: ',
    TAG_ABI_PCS_RW_DATA='Tag_ABI_PCS_RW_use: ',
    TAG_ABI_PCS_RO_DATA='Tag_ABI_PCS_RO_use: ',
    TAG_ABI_PCS_GOT_USE='Tag_ABI_PCS_GOT_use: ',
    TAG_ABI_PCS_WCHAR_T='Tag_ABI_PCS_wchar_t: ',
    TAG_ABI_FP_ROUNDING='Tag_ABI_FP_rounding: ',
    TAG_ABI_FP_DENORMAL='Tag_ABI_FP_denormal: ',
    TAG_ABI_FP_EXCEPTIONS='Tag_ABI_FP_exceptions: ',
    TAG_ABI_FP_USER_EXCEPTIONS='Tag_ABI_FP_user_exceptions: ',
    TAG_ABI_FP_NUMBER_MODEL='Tag_ABI_FP_number_model: ',
    TAG_ABI_ALIGN_NEEDED='Tag_ABI_align_needed: ',
    TAG_ABI_ALIGN_PRESERVED='Tag_ABI_align_preserved: ',
    TAG_ABI_ENUM_SIZE='Tag_ABI_enum_size: ',
    TAG_ABI_HARDFP_USE='Tag_ABI_HardFP_use: ',
    TAG_ABI_VFP_ARGS='Tag_ABI_VFP_args: ',
    TAG_ABI_WMMX_ARGS='Tag_ABI_WMMX_args: ',
    TAG_ABI_OPTIMIZATION_GOALS='Tag_ABI_optimization_goals: ',
    TAG_ABI_FP_OPTIMIZATION_GOALS='Tag_ABI_FP_optimization_goals: ',
    TAG_COMPATIBILITY='Tag_compatibility: ',
    TAG_CPU_UNALIGNED_ACCESS='Tag_CPU_unaligned_access: ',
    TAG_FP_HP_EXTENSION='Tag_FP_HP_extension: ',
    TAG_ABI_FP_16BIT_FORMAT='Tag_ABI_FP_16bit_format: ',
    TAG_MPEXTENSION_USE='Tag_MPextension_use: ',
    TAG_DIV_USE='Tag_DIV_use: ',
    TAG_NODEFAULTS='Tag_nodefaults: ',
    TAG_ALSO_COMPATIBLE_WITH='Tag_also_compatible_with: ',
    TAG_T2EE_USE='Tag_T2EE_use: ',
    TAG_CONFORMANCE='Tag_conformance: ',
    TAG_VIRTUALIZATION_USE='Tag_Virtualization_use: ',
    TAG_MPEXTENSION_USE_OLD='Tag_MPextension_use_old: ',
)

_DESCR_ATTR_VAL_ARM = [
    None, #1
    None, #2
    None, #3
    None, #4
    None, #5
    { #6 TAG_CPU_ARCH
        0 : 'Pre-v4',
        1 : 'v4',
        2 : 'v4T',
        3 : 'v5T',
        4 : 'v5TE',
        5 : 'v5TEJ',
        6 : 'v6',
        7 : 'v6KZ',
        8 : 'v6T2',
        9 : 'v6K',
        10: 'v7',
        11: 'v6-M',
        12: 'v6S-M',
        13: 'v7E-M',
        14: 'v8',
        15: 'v8-R',
        16: 'v8-M.baseline',
        17: 'v8-M.mainline',
    },
    { #7 TAG_CPU_ARCH_PROFILE
        0x00: 'None',
        0x41: 'Application',
        0x52: 'Realtime',
        0x4D: 'Microcontroller',
        0x53: 'Application or Realtime',
    },
    { #8 TAG_ARM_ISA
        0: 'No',
        1: 'Yes',
    },
    { #9 TAG_THUMB_ISA
        0: 'No',
        1: 'Thumb-1',
        2: 'Thumb-2',
        3: 'Yes',
    },
    { #10 TAG_FP_ARCH
        0: 'No',
        1: 'VFPv1',
        2: 'VFPv2 ',
        3: 'VFPv3',
        4: 'VFPv3-D16',
        5: 'VFPv4',
        6: 'VFPv4-D16',
        7: 'FP ARM v8',
        8: 'FPv5/FP-D16 for ARMv8',
    },
    { #11 TAG_WMMX_ARCH
        0: 'No',
        1: 'WMMXv1',
        2: 'WMMXv2',
    },
    { #12 TAG_ADVANCED_SIMD_ARCH
        0: 'No',
        1: 'NEONv1',
        2: 'NEONv1 with Fused-MAC',
        3: 'NEON for ARMv8',
        4: 'NEON for ARMv8.1',
    },
    { #13 TAG_PCS_CONFIG
        0: 'None',
        1: 'Bare platform',
        2: 'Linux application',
        3: 'Linux DSO',
        4: 'PalmOS 2004',
        5: 'PalmOS (reserved)',
        6: 'SymbianOS 2004',
        7: 'SymbianOS (reserved)',
    },
    { #14 TAG_ABI_PCS_R9_USE
        0: 'v6',
        1: 'SB',
        2: 'TLS',
        3: 'Unused',
    },
    { #15 TAG_ABI_PCS_RW_DATA
        0: 'Absolute',
        1: 'PC-relative',
        2: 'SB-relative',
        3: 'None',
    },
    { #16 TAG_ABI_PCS_RO_DATA
        0: 'Absolute',
        1: 'PC-relative',
        2: 'None',
    },
    { #17 TAG_ABI_PCS_GOT_USE
        0: 'None',
        1: 'direct',
        2: 'GOT-indirect',
    },
    { #18 TAG_ABI_PCS_WCHAR_T
        0: 'None',
        1: '??? 1',
        2: '2',
        3: '??? 3',
        4: '4',
    },
    { #19 TAG_ABI_FP_ROUNDING
        0: 'Unused',
        1: 'Needed',
    },
    { #20 TAG_ABI_FP_DENORMAL
        0: 'Unused',
        1: 'Needed',
        2: 'Sign only',
    },
    { #21 TAG_ABI_FP_EXCEPTIONS
        0: 'Unused',
        1: 'Needed',
    },
    { #22 TAG_ABI_FP_USER_EXCEPTIONS
        0: 'Unused',
        1: 'Needed',
    },
    { #23 TAG_ABI_FP_NUMBER_MODEL
        0: 'Unused',
        1: 'Finite',
        2: 'RTABI',
        3: 'IEEE 754',
    },
    { #24 TAG_ABI_ALIGN_NEEDED
        0: 'None',
        1: '8-byte',
        2: '4-byte',
        3: '??? 3',
    },
    { #25 TAG_ABI_ALIGN_PRESERVED
        0: 'None',
        1: '8-byte, except leaf SP',
        2: '8-byte',
        3: '??? 3',
    },
    { #26 TAG_ABI_ENUM_SIZE
        0: 'Unused',
        1: 'small',
        2: 'int',
        3: 'forced to int',
    },
    { #27 TAG_ABI_HARDFP_USE
        0: 'As Tag_FP_arch',
        1: 'SP only',
        2: 'Reserved',
        3: 'Deprecated',
    },
    { #28 TAG_ABI_VFP_ARGS
        0: 'AAPCS',
        1: 'VFP registers',
        2: 'custom',
        3: 'compatible',
    },
    { #29 TAG_ABI_WMMX_ARGS
        0: 'AAPCS',
        1: 'WMMX registers',
        2: 'custom',
    },
    { #30 TAG_ABI_OPTIMIZATION_GOALS
        0: 'None',
        1: 'Prefer Speed',
        2: 'Aggressive Speed',
        3: 'Prefer Size',
        4: 'Aggressive Size',
        5: 'Prefer Debug',
        6: 'Aggressive Debug',
    },
    { #31 TAG_ABI_FP_OPTIMIZATION_GOALS
        0: 'None',
        1: 'Prefer Speed',
        2: 'Aggressive Speed',
        3: 'Prefer Size',
        4: 'Aggressive Size',
        5: 'Prefer Accuracy',
        6: 'Aggressive Accuracy',
    },
    { #32 TAG_COMPATIBILITY
        0: 'No',
        1: 'Yes',
    },
    None, #33
    { #34 TAG_CPU_UNALIGNED_ACCESS
        0: 'None',
        1: 'v6',
    },
    None, #35
    { #36 TAG_FP_HP_EXTENSION
        0: 'Not Allowed',
        1: 'Allowed',
    },
    None, #37
    { #38 TAG_ABI_FP_16BIT_FORMAT
        0: 'None',
        1: 'IEEE 754',
        2: 'Alternative Format',
    },
    None, #39
    None, #40
    None, #41
    { #42 TAG_MPEXTENSION_USE
        0: 'Not Allowed',
        1: 'Allowed',
    },
    None, #43
    { #44 TAG_DIV_USE
        0: 'Allowed in Thumb-ISA, v7-R or v7-M',
        1: 'Not allowed',
        2: 'Allowed in v7-A with integer division extension',
    },
    None, #45
    None, #46
    None, #47
    None, #48
    None, #49
    None, #50
    None, #51
    None, #52
    None, #53
    None, #54
    None, #55
    None, #56
    None, #57
    None, #58
    None, #59
    None, #60
    None, #61
    None, #62
    None, #63
    None, #64
    None, #65
    { #66 TAG_FP_HP_EXTENSION
        0: 'Not Allowed',
        1: 'Allowed',
    },
    None, #67
    { #68 TAG_VIRTUALIZATION_USE
        0: 'Not Allowed',
        1: 'TrustZone',
        2: 'Virtualization Extensions',
        3: 'TrustZone and Virtualization Extensions',
    },
    None, #69
    { #70 TAG_MPEXTENSION_USE_OLD
        0: 'Not Allowed',
        1: 'Allowed',
    },
]

_DESCR_ATTR_TAG_RISCV = dict(
    TAG_FILE='File Attributes',
    TAG_SECTION='Section Attributes:',
    TAG_SYMBOL='Symbol Attributes:',
    TAG_STACK_ALIGN='Tag_RISCV_stack_align: ',
    TAG_ARCH='Tag_RISCV_arch: ',
    TAG_UNALIGNED='Tag_RISCV_unaligned_access: ',
    TAG_PRIV_SPEC='Tag_RISCV_priv_spec: ',
    TAG_PRIV_SPEC_MINOR='Tag_RISCV_priv_spec_minor: ',
    TAG_PRIV_SPEC_REVISION='Tag_RISCV_priv_spec_revision: ',
    TAG_ATOMIC_ABI='Tag_RISCV_atomic_abi: ',
    TAG_X3_REG_USAGE='Tag_RISCV_x3_reg_usage: ',
)

_DESCR_ATTR_VAL_RISCV = [
    None, #1
    None, #2
    None, #3
    { #4 TAG_RISCV_stack_align
        4: '4-bytes',
        16: '16-bytes',
    },
    None, #5 TAG_RISCV_arch
    { #6 TAG_RISCV_unaligned_access
        0: 'Not Allowed',
        1: 'Allowed',
    },
    None, #8 TAG_RISCV_priv_spec
    None, #10 TAG_RISCV_priv_spec_minor
    None, #12 TAG_RISCV_priv_spec_revision
    { #14 TAG_RISCV_atomic_abi
        0: 'UNKNOWN: This object uses unknown atomic ABI.',
        1: 'A6C: This object uses the A6 classical atomic ABI.',
        2: 'A6S: This object uses the strengthened A6 ABI.',
        3: 'A7: This object uses the A7 atomic ABI.'
    },
    { #16 TAG_RISCV_x3_reg_usage
        0: 'This object uses x3 as a fixed register with unknown purpose.',
        1: 'This object uses x3 as the global pointer, for relaxation purposes.',
        2: 'This object uses x3 as the shadow stack pointer.',
        3: 'This object uses X3 as a temporary register.',
    },
]
