#!/usr/bin/env python

####################################################
### Import Libraries

import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import os, subprocess
from os.path import isdir, join, split
from glob import glob
from functools import reduce
from pylab import rcParams
import matplotlib

####################################################
### Define Read Functions

def ReadGValues(File):
    GValues = {}

    f = open(File,"r")
    for z in f.readlines():
        A = z.split()
        if len(A) < 4:
            continue

        GVal = float(A[0])
        GErr = float(A[1])
        Time = float(A[2])
        Name = A[3]
        
        # to account for differences in nBio-v4.0 and nBio-v3.0
        if Name == 'O^0' or Name == 'O3P^0':
            continue

        if Name in GValues:
            GValues[Name].append([Time,GVal,GErr])

        else:
            GValues[Name] = [[Time,GVal,GErr]]


    for i in GValues.keys():
        GValues[i] = np.array(GValues[i])

    return GValues


def Glob(match_path):
    os.system('ls ' + match_path + ' > list')
    listFiles = open('list','r')
    fnames = []
    for name in listFiles:
        name = name.split()[0] 
        fnames.append(name)
    os.system('rm list')
    return fnames

def average_results(match_path):
    fnames = Glob(match_path)
    if len(fnames) == 0:
        return None

    Result = {}
    n = 0.0
    for f in fnames:
        data = ReadGValues(f)
        if n == 0.0:
            Results = data
        else:
            for Mol in data.keys():
                Time1 = data[Mol][:,0]
                Data1 = data[Mol][:,1]
                Stdv1 = data[Mol][:,2]

                Results[Mol][:,1] += Data1
                Results[Mol][:,2] += Stdv1**2
        n += 1

    for i in Results.keys():
        Results[i] = np.array(Results[i])
        Results[i][:,1] /= n
        Results[i][:,2] = 1./n * np.sqrt(Results[i][:,2])

    return Results


def average_results_time(match_path):
    fnames = glob(match_path)
    if len(fnames) == 0:
        return None
    
    execution, executionE = 0.0, 0.0
    initialization, initializationE = 0.0, 0.0
    finalization, finalizationE = 0.0, 0.0
    
    N = 0.0

    time_tracker = {}

    for f in fnames:
        Times = float(subprocess.check_output("grep Execution " + f + " | awk '{print $2}' | sed 's/User=//g' | sed 's/s//g' | awk '{sum+=$1}END{print sum/NR}'", shell=True))
        time_tracker[int(N+1)] = Times
        execution += Times
        executionE += Times*Times

        Times = float(subprocess.check_output("grep Initialization " + f + " | awk '{print $2}' | sed 's/User=//g' | sed 's/s//g' | awk '{sum+=$1}END{print sum/NR}'", shell=True))
        initialization  += Times
        initializationE += Times*Times

        Times = float(subprocess.check_output("grep Finalization " + f + " | awk '{print $2}' | sed 's/User=//g' | sed 's/s//g' | awk '{sum+=$1}END{print sum/NR}'", shell=True))
        finalization  += Times
        finalizationE  += Times*Times

        N += 1

    execution /= N
    initialization /= N
    finalization  /= N

    if N > 1:
        executionE = np.sqrt(N/(N-1) * (np.abs(executionE/N - execution**2)))
        initializationE = np.sqrt(N/(N-1) * (np.abs(initializationE/N - initialization**2)))
        finalizationE  = np.sqrt(N/(N-1) * (np.abs(finalizationE/N  - finalization**2)))
    else:
        executionE, initializationE, finalizationE = 0, 0, 0

    return (initialization,initializationE,execution,executionE,finalization,finalizationE, time_tracker)

####################################################
### Define Plot Function

def plot_results(sut_dir, ref_dir, args):
    concentrations = ["1e-3", "1e-2", "1e-1", "1e-0", "1e+1"]

    sut_T = average_results_time(sut_dir + '/*/log.out')
    ref_T = average_results_time(ref_dir + '/*/log.out')

    sut_G   = []
    ref_G   = []

    sut_SG   = {}
    ref_SG   = {}
    kobs = 9.7e8

    for T in concentrations: 
        sut_GT   = average_results(sut_dir + '/*/Methanol_%s_M_Nitrate_25e-3_M.phsp'%(T))
        ref_GT   = average_results(ref_dir + '/*/Methanol_%s_M_Nitrate_25e-3_M.phsp'%(T))

        sut_G.append(sut_GT)
        ref_G.append(ref_GT)

        for i in sut_GT.keys():
            V1 = np.copy(sut_GT[i][66])
            V2 = np.copy(ref_GT[i][66])
            V1[0] = 1e12 / (float(T)*kobs)
            V2[0] = 1e12 / (float(T)*kobs)
            
            if i in sut_SG:
                sut_SG[i].append(V1)
                ref_SG[i].append(V2)

            else:
                sut_SG[i]   = [V1]
                ref_SG[i]   = [V2]

    for i in sut_SG.keys():
        sut_SG[i]   = np.array(sut_SG[i])
        ref_SG[i]   = np.array(ref_SG[i])

    bench1 = np.genfromtxt('analysis/benchmark/Pastina1999.csv')
    
    bench2 = np.genfromtxt('analysis/benchmark/Hiroki2002.csv')

    bench3 = np.genfromtxt("analysis/benchmark/Ramos-Mendez2021.csv")

    fig = plt.figure(figsize=(8,8))
    ax1 = plt.subplot2grid((2,1),(0,0))
    ax2 = plt.subplot2grid((2,1),(1,0))

    matplotlib.rcParams['font.family']     = "sans-serif"
    matplotlib.rcParams['font.sans-serif'] = "Helvetica"
    matplotlib.rcParams['figure.dpi']      = 200

    ax1.set_title(r"$H_{2}O_{2}$", fontsize=24)

    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.tick_params(axis='both', which='minor', labelsize=20)

    ax1.errorbar(sut_SG["H2O2^0"][:,0],  sut_SG["H2O2^0"][:,1], yerr=sut_SG["H2O2^0"][:,2],  color="r", marker='o', markersize=10, linewidth=0, label=args.sut_label)
    ax1.errorbar(ref_SG["H2O2^0"][:,0],  ref_SG["H2O2^0"][:,1], yerr=ref_SG["H2O2^0"][:,2],  color="b", marker='x', markersize=10, linewidth=0, label=args.ref_label)
    ax1.scatter(1e12/bench1[:,0], bench1[:,1], marker='*', s=90, color='k', label='Pastina et al., 1999')
    ax1.scatter(1e12/(bench2[:,0]*kobs), bench2[:,1], marker='v', s=90, color='k', label='Hiroki et al., 2002')

    # RM 2021 data
    rm_x = [1.03092784e+06, 1.03092784e+05, 1.03092784e+04, 1.03092784e+03, 1.03092784e+02]
    rm_y = [0.7808383233532934, 0.7329341317365269, 0.6287425149700598, 0.4047904191616767, 0.08502994011976056]
    ax1.plot(rm_x, rm_y, color='k', mfc='white', markeredgecolor='k',zorder=1, marker='^', ms=10, ls = '--', label='Ramos-Méndez et al., 2021')

    ax1.legend(loc=0)

    ax1.set_xlim(5e1,2E6)
#    ax1.set_ylim([2,4.5])

    ax1.set_xscale('log')

    ax1.set_xlabel("Time (ps)",fontsize=20)

    ax1.set_ylabel("G value [{} / 100 eV]".format(r'$H_{2}O_{2}$'),fontsize=20)

    ax2.set_axis_off()
    Table = ax2.table(cellText=[['%1.3f +/- %1.3f' % (sut_T[2],sut_T[3]), '%1.3f +/- %1.3f' % (ref_T[2],ref_T[3])]],\
                      rowLabels=['Exec.'],\
                      colLabels=(args.sut_label+' (s)',args.ref_label+' (s)'),\
                      loc='center'\
                      )

    Table.set_fontsize(20)
    Table.scale(1,3)

    fig.tight_layout()
    fig.savefig(join(args.outdir,'TimeEvolution.pdf'))

    plt.clf()
    plt.cla()
    plt.close()

####################################################
### Define Main

def Main():
    parser = ArgumentParser()
    parser.add_argument('sut_dir', help='Result directory for MC under test')
    parser.add_argument('ref_dir', help='Result directory for benchmark')
    parser.add_argument('-o', '--outdir', default=None, help='Output directory')
    parser.add_argument('--sut_label', default='TOPAS under test')
    parser.add_argument('--ref_label', default='TOPAS benchmark')
    args = parser.parse_args()
    
    if not isdir(args.sut_dir):
        print('Could not find %s' % args.sut_dir)
        exit(1)

    if not isdir(args.ref_dir):
        print('Could not find %s' % args.ref_dir)
        exit(1)

    if not args.outdir:
        args.outdir = join('results', split(args.sut_dir.rstrip(os.sep))[-1])
    if not isdir(args.outdir):
        os.makedirs(args.outdir)

    plot_results(args.sut_dir, args.ref_dir, args)

####################################################
### Run Main

if __name__=="__main__":
    Main()

####################################################
