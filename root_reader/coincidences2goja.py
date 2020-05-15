'''
@author: pkopka
'''

import ROOT
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from multiprocessing import Pool
import glob
import struct
import argparse

parser = argparse.ArgumentParser(
    description='Program that convert ROOT tree to LM QETIR format.')
parser.add_argument('input', metavar='F', type=str, nargs='+',
                    help='Input ROOT files')
args = parser.parse_args()

lm_path = args.input[-1]

# resulting file will be produced within the location from where the script was called
goja_coincidences_file = lm_path.split('/')[-1].split('.')[0] + '.txt'

## position in mm
## time difference in ps
s2ps_factor = 1E12
def type_con(en):
	if en.eventID1 != en.eventID2:
		return 4
	elif en.comptonCrystal1!=1 and en.comptonCrystal2!=1:
		return 3
	elif en.comptonPhantom1!=0 and en.comptonPhantom1!=0:
		return 2
	return 1

if __name__ == '__main__':

	f = ROOT.TFile.Open(lm_path)
	print "Processed file: {0}\n".format(lm_path)
 	
	tree = f.Get("Coincidences")
	entries = tree.GetEntries()
		
	print 'Number of coincidences: {0:.3f} M'.format(entries/1E6)

	with open(goja_coincidences_file,'w+b') as output:

		for i, en in enumerate(tree):
			if i%1E6==0 and i != 0:
				print '{0:.2f} M events processed.'.format(i/1E6)
			event = [en.globalPosX1/10, en.globalPosY1/10, en.globalPosZ1/10, en.time1*s2ps_factor,
			        en.globalPosX2/10, en.globalPosY2/10, en.globalPosZ2/10, en.time2*s2ps_factor,
					en.rsectorID1, en.rsectorID2, en.energy1, en.energy2, type_con(en),
					en.sourcePosX1/10, en.sourcePosY1/10, en.sourcePosZ1/10,
					en.sourcePosX2/10, en.sourcePosY2/10, en.sourcePosZ2/10, ]
			event = [str(np.round(x,2)) for x in event]
			output.write("\t".join(event) + "\n")

	f.Close()
