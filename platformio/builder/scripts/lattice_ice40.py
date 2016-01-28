"""
    Build script for lattice ice40 FPGAs
    latticeice40-builder.py
"""

from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment, Glob

env = DefaultEnvironment()
env.Replace(PROGNAME="firmware")

# -- Get all the source files
src_dir = env.subst('$PROJECTSRC_DIR')
total = join(src_dir, '*.v')
src_files = Glob(total)

PCFs = join(src_dir, '*.pcf')
PCF = Glob(PCFs)
print("PCF: {}".format(PCF[0]))

bin_dir = join('$PIOPACKAGES_DIR', 'toolchain-icestorm', 'bin')

# -- Builder 1 (.v --> .blif)
synth = Builder(action=join(bin_dir, 'yosys') + ' -p \"synth_ice40 -blif $TARGET\" $SOURCES',
                suffix='.blif',
                src_suffix='.v')

# -- Builder 2 (.blif --> .asc)
pnr = Builder(action=join(bin_dir, 'arachne-pnr') + ' -d 1k -o $TARGET -p {} $SOURCE'.format(PCF[0]),
              suffix='.asc',
              src_suffix='.blif')

bitstream = Builder(action=join(bin_dir, 'icepack') + ' $SOURCE $TARGET',
                    suffix='.bin',
                    src_suffix='.asc')

env.Append(BUILDERS={'Synth': synth, 'PnR': pnr, 'Bin': bitstream})

blif = env.Synth(src_files)
asc = env.PnR([blif, PCF[0]])
binf = env.Bin(asc)

upload = env.Alias('upload', binf, join(bin_dir, 'iceprog') + ' $SOURCE')
AlwaysBuild(upload)
