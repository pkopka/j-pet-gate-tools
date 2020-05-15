'''
Created on 26 Feb 2020

@author: pkopka
'''
import ROOT
import numpy as np
import os
import argparse
from array import array

parser = argparse.ArgumentParser(
    description='Program that smear ROOT file.')
parser.add_argument('input', metavar='root_file', type=str, nargs='+',
                    help='Input Root files with Coincidences')
parser.add_argument("-c", "--crt", required=False,
                  action="store", dest="crt", type=float,
                  help="CRT in ps unit")
parser.add_argument("-z", "--FWHM_z",
                  action="store", dest="fwhm_z", type=float, required=False,
                  help="smear in Z pos FWHM[cm]")
parser.add_argument("-l", "--length",
                  action="store", dest="scanner_length", type=float, required=False,
                  help="Lenght of scanner detecot in (Z axis)")
parser.add_argument("-n", "--nov",  required=False,
                  action="store", dest="number_of_volume", type=int,
                  help="Number of volume in splitted detector")


TOF_FLAG = False
POS_FLAG = False

def smear(x, sig_thit):
    return x + sig_thit*np.random.normal()

def set_crystal_id(pos_z, scanner_length, number_of_volume):
    if abs(pos_z) > scanner_length/2.0:
        if pos_z < 0:
            pos_z = -scanner_length/2.0
        else: 
            pos_z  = scanner_length/2.0
    return int(((pos_z + scanner_length/2.0)/(scanner_length/float(number_of_volume)))%number_of_volume)



def smear_root(root_file_path, sig_thit_time=None, sig_thit_pos=None, scanner_length= None, number_of_volume= None):
    f = ROOT.TFile.Open(root_file_path)
    print("Processed file: {0}\n".format(root_file_path))
    tree = f.Get("Coincidences")
    entries = tree.GetEntries()		
    print('Number of coincidences: {0:.3f} M'.format(entries/1E6))

    root_coincidences_file = root_file_path.split('/')[-1].split('.')[0] + '_smear.root'
    outfile = ROOT.TFile(root_coincidences_file, 'recreate')
    new_tree = tree.CloneTree(0)

    if TOF_FLAG:
        time1 = array('d',[0])
        tree.SetBranchAddress('time1', time1)
        time2 = array('d',[0])
        tree.SetBranchAddress('time2', time2)
    if POS_FLAG:
        globalPosZ1 = array('f',[0])
        tree.SetBranchAddress('globalPosZ1', globalPosZ1)
        globalPosZ2 = array('f',[0])
        tree.SetBranchAddress('globalPosZ2', globalPosZ2)
        layerID1 = array('i',[0])
        tree.SetBranchAddress('crystalID1', layerID1)
        layerID2 = array('i',[0])
        tree.SetBranchAddress('crystalID2', layerID2)

    for i, en in enumerate(tree):
        if i%1E6==0 and i != 0:
            print('{0:.2f} M events processed.'.format(i/1E6))
        if TOF_FLAG:
            time1[0] = smear(en.time1, sig_thit_time)
            time2[0] = smear(en.time2, sig_thit_time)
        if POS_FLAG:
            globalPosZ1[0] = smear(en.globalPosZ1, sig_thit_pos)
            globalPosZ2[0] = smear(en.globalPosZ2, sig_thit_pos)
            layerID1[0] = set_crystal_id(globalPosZ1[0],scanner_length, number_of_volume)
            layerID2[0] = set_crystal_id(globalPosZ2[0],scanner_length, number_of_volume)

        new_tree.Fill()

    outfile.cd()
    new_tree.Write()
    outfile.Close()

                


if __name__ == '__main__':

    args = parser.parse_args()
    if args.crt:
        print("Smear TOF CRT = %d ps" % args.crt)
        TOF_FLAG = True
        sig_thit_time = (args.crt/3.33)* 1e-12 # ps -> s
    if args.fwhm_z and args.scanner_length and args.number_of_volume:
        print("Smear position in Z FWHM = %d cm" % args.fwhm_z)
        print("SCANNER LENGTH = %d cm" % args.scanner_length)
        print("NUMER OF VOLUME = %d" % args.number_of_volume)
        POS_FLAG = True
        sig_thit_pos = (args.fwhm_z/2.35)*10.0 # cm -> mm
    
    if TOF_FLAG and POS_FLAG:
        for file_name in args.input:
            smear_root(file_name,
            sig_thit_time=sig_thit_time,
            sig_thit_pos=sig_thit_pos,
            scanner_length=args.scanner_length *10,
                number_of_volume=args.number_of_volume)
    elif TOF_FLAG:
        for file_name in args.input:
            smear_root(file_name, sig_thit_time=sig_thit_time)
    elif POS_FLAG:
        for file_name in args.input:
                smear_root(file_name, sig_thit_pos=sig_thit_pos, 
                scanner_length=args.scanner_length *10,
                number_of_volume=args.number_of_volume)
    else:
        print("use -h, --help  option for show this help message and exit")

