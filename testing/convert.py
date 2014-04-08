import sys
import os
import pdb
import numpy as np
import argparse

import intermol.Driver as Driver
import evaluate

def parse_args():
    # to do:
    #   move -h/--help flag to the bottom of the help message or into group_misc
    #   add --version flag

    parser = argparse.ArgumentParser(description = 'Perform a file conversion')

    # input arguments 
    #   (FYI not using argparse's mutually exclusive group since it doesn't support the description argument => ugly -h output)
    group_in = parser.add_argument_group('Choose input conversion format')
    group_in.add_argument('--des_in', nargs=1, metavar='file', help='.cms file for conversion from DESMOND file format')
    group_in.add_argument('--gro_in', nargs=2, metavar='file', help='.gro and .top file for conversion from GROMACS file format')
    group_in.add_argument('--lmp_in', nargs=1, metavar='file', help='.lmp file for conversion from LAMMPS file format')

    # output arguments
    group_out = parser.add_argument_group('Choose output conversion format(s)')
    group_out.add_argument('--desmond', action='store_true', help='convert to DESMOND')
    group_out.add_argument('--gromacs', action='store_true', help='convert to GROMACS')
    group_out.add_argument('--lammps', action='store_true', help='convert to LAMMPS')

    # other
    group_misc = parser.add_argument_group('Other optional arguments')
    group_misc.add_argument('--odir', metavar='directory', default='.', help='specification of output directory (default: ./)')
    group_misc.add_argument('--oname', metavar='prefix', default='', help='specification of prefix for output filenames (default: inputprefix_converted)')
    group_misc.add_argument('-e', '--energy', dest='energy', action='store_true', help='evaluate energy of input and output files for comparison')
    group_misc.add_argument('--efile', default='', help='optional run file for energy evaluation (e.g. .cfg, .mdp, .input)')
    group_misc.add_argument('-d', '--despath', dest='despath', metavar='path', default='', help='path for DESMOND binary, needed for energy evaluation')
    group_misc.add_argument('-g', '--gropath', dest='gropath', metavar='path', default='', help='path for GROMACS binary, needed for energy evaluation')
    group_misc.add_argument('-l', '--lmppath', dest='lmppath', metavar='path', default='', help='path for LAMMPS binary, needed for energy evaluation')
    group_misc.add_argument('-f', '--force', action='store_true', help='ignore warnings')
    
    return parser.parse_args()

def main():
    args = parse_args()

    print 'Performing InterMol conversion...'

    # check if inputs files exist; NOT checking extension type to allow flexibility in naming
    if args.des_in:
        if not os.path.isfile(args.des_in[0]):
            raise Exception('File not found: {0}'.format(args.des_in[0]))
        files = args.des_in
        prefix = args.des_in[0][args.des_in[0].rfind('/')+1:-4] # get prefix of file w/o full path
    elif args.gro_in:
        for f in args.gro_in: # 2 arguments for top and gro file
            if not os.path.isfile(f):
                raise Exception('File not found: {0}'.format(f))
        files = args.gro_in
        prefix = args.gro_in[0][args.gro_in[0].rfind('/')+1:-4]
    elif args.lmp_in:
        if not os.path.isfile(args.lmp_in[0]):
            raise Exception('File not found: {0}'.format(args.lmp_in[0]))
        files = args.lmp_in
        prefix = args.lmp_in[0][args.lmp_in[0].rfind('/')+1:-4]
    else:
        print 'No input file'
        sys.exit(1)

    # check to make sure output directory exists before doing anything
    if not os.path.exists(args.odir):
        raise Exception('Output directory not found: {0}'.format(args.odir))

    # check to make sure a conversion type is selected before doing anything
    if not args.desmond and not args.gromacs and not args.lammps:
        print 'WARNING: no conversion type selected'
        print '         use -f to override'
        if not args.force:
            sys.exit(1)

    # initialize driver
    Driver.initSystem(prefix) # what does this name do?

    # load files -- Driver should know which type based on extension... change this eventually?
    Driver.load(*files)

    # output
    oname = args.oname
    if not args.oname:
        oname = '%s_converted' % prefix
    if args.desmond:
        outfile = '%s/%s.cms' % ( args.odir, oname)
        print 'Converting to Desmond...writing %s...' % outfile
        Driver.write(outfile)
    if args.gromacs:
        print 'Converting to Gromacs...writing %s/%s.gro, %s/%s.top...' % (args.odir, oname, args.odir, oname)
        Driver.write('%s/%s.gro' % (args.odir, oname))
        Driver.write('%s/%s.top' % (args.odir, oname))
    if args.lammps:
        print 'Converting to Lammps...writing %s/%s.lmp...' % (args.odir, oname)
        Driver.write('%s/%s.lmp' % (args.odir, oname))
    
    # calc input energies -- only desmond for now
    if args.energy:
        e_in, e_infile = evaluate.desmond_energies(args.des_in[0], 'Inputs/Desmond/onepoint.cfg')
        print 'Total energy from %s:' % e_infile
        print e_in
        e_out, e_outfile = evaluate.desmond_energies(outfile, 'Inputs/Desmond/onepoint.cfg')    
        print 'Total energy from %s:' % e_outfile
        print e_out

if __name__ == '__main__':
    main()
