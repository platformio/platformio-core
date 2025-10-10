#-------------------------------------------------------------------------------
# elftools: dwarf/datatype_cpp.py
#
# First draft at restoring the source level name a C/C++ datatype
# from DWARF data. Aiming at compatibility with llvm-dwarfdump v15.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from ..common.utils import bytes2str

cpp_symbols = dict(
    pointer   = "*",
    reference = "&",
    const     = "const",
    volatile  = "volatile")

def describe_cpp_datatype(var_die):
    return str(parse_cpp_datatype(var_die))

def parse_cpp_datatype(var_die):
    """Given a DIE that describes a variable, a parameter, or a member
    with DW_AT_type in it, tries to return the C++ datatype as a string

    Returns a TypeDesc.

    Does not follow typedefs, doesn't  resolve array element types
    or struct members. Not good for a debugger.
    """
    t = TypeDesc()

    if not 'DW_AT_type' in var_die.attributes:
        t.tag = ''
        return t

    type_die = var_die.get_DIE_from_attribute('DW_AT_type')

    mods = []
    # Unlike readelf, dwarfdump doesn't chase typedefs
    while type_die.tag in ('DW_TAG_const_type', 'DW_TAG_volatile_type', 'DW_TAG_pointer_type', 'DW_TAG_reference_type'):
        modifier = _strip_type_tag(type_die) # const/volatile/reference/pointer
        mods.insert(0, modifier)
        if not 'DW_AT_type' in type_die.attributes: # void* is encoded as a pointer to nothing
            t.name = t.tag = "void"
            t.modifiers = tuple(mods)
            return t
        type_die = type_die.get_DIE_from_attribute('DW_AT_type')

    # From this point on, type_die doesn't change
    t.tag = _strip_type_tag(type_die)
    t.modifiers = tuple(mods)

    if t.tag in ('ptr_to_member', 'subroutine'):
        if t.tag == 'ptr_to_member':
            ptr_prefix = DIE_name(type_die.get_DIE_from_attribute('DW_AT_containing_type')) + "::"
            type_die = type_die.get_DIE_from_attribute('DW_AT_type')
        elif "DW_AT_object_pointer" in type_die.attributes: # Older compiler... Subroutine, but with an object pointer
            ptr_prefix = DIE_name(DIE_type(DIE_type(type_die.get_DIE_from_attribute('DW_AT_object_pointer')))) + "::"
        else: # Not a pointer to member
            ptr_prefix = ''

        if t.tag == 'subroutine':
            params = tuple(format_function_param(p, p) for p in type_die.iter_children() if p.tag in ("DW_TAG_formal_parameter", "DW_TAG_unspecified_parameters") and 'DW_AT_artificial' not in p.attributes)
            params = ", ".join(params)
            if 'DW_AT_type' in type_die.attributes:
                retval_type = parse_cpp_datatype(type_die)
                is_pointer = retval_type.modifiers and retval_type.modifiers[-1] == 'pointer'
                retval_type = str(retval_type)
                if not is_pointer:
                    retval_type += " "
            else:
                retval_type = "void "

            if len(mods) and mods[-1] == 'pointer':
                mods.pop()
                t.modifiers = tuple(mods)
                t.name = "%s(%s*)(%s)" % (retval_type, ptr_prefix, params)
            else:
                t.name = "%s(%s)" % (retval_type, params)
            return t
    elif DIE_is_ptr_to_member_struct(type_die):
        dt =  parse_cpp_datatype(next(type_die.iter_children())) # The first element is pfn, a function pointer with a this
        dt.modifiers = tuple(dt.modifiers[:-1]) # Pop the extra pointer
        dt.tag = "ptr_to_member_type" # Not a function pointer per se
        return dt
    elif t.tag == 'array':
        t.dimensions = (_array_subtype_size(sub)
            for sub
            in type_die.iter_children()
            if sub.tag == 'DW_TAG_subrange_type')
        t.name = describe_cpp_datatype(type_die)
        return t

    # Now the nonfunction types
    # Blank name is sometimes legal (unnamed unions, etc)

    t.name = safe_DIE_name(type_die, t.tag + " ")

    # Check the nesting - important for parameters
    parent = type_die.get_parent()
    scopes = list()
    while parent.tag in ('DW_TAG_class_type', 'DW_TAG_structure_type', 'DW_TAG_union_type', 'DW_TAG_namespace'):
        scopes.insert(0, safe_DIE_name(parent, _strip_type_tag(parent) + " "))
        # If unnamed scope, fall back to scope type - like "structure "
        parent = parent.get_parent()
    t.scopes = tuple(scopes)

    return t

#--------------------------------------------------

class TypeDesc(object):
    """ Encapsulates a description of a datatype, as parsed from DWARF DIEs.
        Not enough to display the variable in the debugger, but enough
        to produce a type description string similar to those of llvm-dwarfdump.

        name - name for primitive datatypes, element name for arrays, the
            whole name for functions and function pouinters

        modifiers - a collection of "const"/"pointer"/"reference", from the
            chain of DIEs preceeding the real type DIE

        scopes - a collection of struct/class/namespace names, parents of the
            real type DIE

        tag - the tag of the real type DIE, stripped of initial DW_TAG_ and
            final _type

        dimensions - the collection of array dimensions, if the type is an
            array. -1 means an array of unknown dimension.

    """
    def __init__(self):
        self.name = None
        self.modifiers = () # Reads left to right
        self.scopes = () # Reads left to right
        self.tag = None
        self.dimensions = None

    def __str__(self):
        # Some reference points from dwarfdump:
        # const->pointer->const->char = const char *const
        # const->reference->const->int = const const int &
        # const->reference->int = const int &
        name = str(self.name)
        mods = self.modifiers

        parts = []
        # Initial const/volatile applies to the var ifself, other consts apply to the pointee
        if len(mods) and mods[0] in ('const', 'volatile'):
            parts.append(mods[0])
            mods = mods[1:]

        # ref->const in the end, const goes in front
        if mods[-2:] == ("reference", "const"):
            parts.append("const")
            mods = mods[0:-1]

        if self.scopes:
            name = '::'.join(self.scopes)+'::' + name
        parts.append(name)

        if len(mods):
            parts.append("".join(cpp_symbols[mod] for mod in mods))

        if self.dimensions:
            dims = "".join('[%s]' % (str(dim) if dim > 0 else '',)
                for dim in self.dimensions)
        else:
            dims = ''

        return " ".join(parts)+dims

def DIE_name(die):
    return bytes2str(die.attributes['DW_AT_name'].value)

def safe_DIE_name(die, default = ''):
    return bytes2str(die.attributes['DW_AT_name'].value) if 'DW_AT_name' in die.attributes else default

def DIE_type(die):
    return die.get_DIE_from_attribute("DW_AT_type")

class ClassDesc(object):
    def __init__(self):
        self.scopes = ()
        self.const_member = False

def get_class_spec_if_member(func_spec, the_func):
    if 'DW_AT_object_pointer' in the_func.attributes:
        this_param = the_func.get_DIE_from_attribute('DW_AT_object_pointer')
        this_type = parse_cpp_datatype(this_param)
        class_spec = ClassDesc()
        class_spec.scopes = this_type.scopes + (this_type.name,)
        class_spec.const_member = any(("const", "pointer") == this_type.modifiers[i:i+2]
            for i in range(len(this_type.modifiers))) # const -> pointer -> const for this arg of const
        return class_spec

    # Check the parent element chain - could be a class
    parent = func_spec.get_parent()

    scopes = []
    while parent.tag in ("DW_TAG_class_type", "DW_TAG_structure_type", "DW_TAG_namespace"):
        scopes.insert(0, DIE_name(parent))
        parent = parent.get_parent()
    if scopes:
        cs = ClassDesc()
        cs.scopes = tuple(scopes)
        return cs

    return None

def format_function_param(param_spec, param):
    if param_spec.tag == 'DW_TAG_formal_parameter':
        if 'DW_AT_name' in param.attributes:
            name = DIE_name(param)
        elif 'DW_AT_name' in param_spec.attributes:
            name = DIE_name(param_spec)
        else:
            name = None
        type = parse_cpp_datatype(param_spec)
        return  str(type)
    else: # unspecified_parameters AKA variadic
        return "..."

def DIE_is_ptr_to_member_struct(type_die):
    if type_die.tag == 'DW_TAG_structure_type':
        members = tuple(die for die in type_die.iter_children() if die.tag == "DW_TAG_member")
        return len(members) == 2 and safe_DIE_name(members[0]) == "__pfn" and safe_DIE_name(members[1]) == "__delta"
    return False

def _strip_type_tag(die):
    """Given a DIE with DW_TAG_foo_type, returns foo"""
    if isinstance(die.tag, int): # User-defined tag 
        return ""
    return die.tag[7:-5]

def _array_subtype_size(sub):
    if 'DW_AT_upper_bound' in sub.attributes:
        return sub.attributes['DW_AT_upper_bound'].value + 1
    if 'DW_AT_count' in sub.attributes:
        return sub.attributes['DW_AT_count'].value
    else:
        return -1

