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
import copy

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

    return (initialization,initializationE,execution,executionE,finalization,finalizationE,time_tracker)

# Function to calculate the x-coordinate for the first dataset (Huerta benchmark)
def huerta_1(x, y):
    xf = []
    yf = []
    yerr = []

    for i in range(len(x)):
        xf = np.append(xf, 1e12 / (x[i] * 2.1e8 + 1e-3 * 1.4e6))
        yf = np.append(yf, y[i] - 0.460526) # H2 at 0 scav
        yerr = np.append(yerr, y[i]*0.05) # 5% experimental uncertainty

    return xf, yf, yerr

# Function to calculate the x-coordinate for the second dataset (Huerta benchmark)
# def huerta_2(x, y):
#     xf = []
#     yf = []
#     yerr = []

#     for i in range(len(x)):
#         xf = np.append(xf, 1e12/x[i])
#         yf = np.append(yf, y[i] - 0.460526) # H2 at 0 scav
#         yerr = np.append(yerr, y[i]*0.05) # 5% experimental uncertainty?

#     return xf, yf, yerr

####################################################
### Define Plot Function

def plot_results(sut_dir, ref_dir, args):
    HCO2m_concentrations = ["1e-2", "1e-1", "300e-3", "1e-0"]
    NO3m_concentrations = ["1e-3"]

    sut_T = average_results_time(sut_dir + '/*/log.out')
    ref_T = average_results_time(ref_dir + '/*/log.out')

    # H2 G-values for baseline case of {H_2}^0 (without formate) as defined in Huerta Parajon 2008
    sut_SG_H20 = {}
    sut_SG_H20_err = {}
    ref_SG_H20   = {}
    ref_SG_H20_err = {}

    # H2 G-values for 1mM Nitrate
    sut_SG_H2_1mM = {}
    ref_SG_H2_1mM = {}
    
    sut_GT = average_results(sut_dir + '/*/Br_1e-3_M_NO3m_1e-3_M.phsp')
    ref_GT = average_results(ref_dir + '/*/Br_1e-3_M_NO3m_1e-3_M.phsp')

    V1 = np.copy(sut_GT['H_2^0'][99]) # taking 1e+9 [99] instead of 1e+6 [66], since H2 not stabilised at 1us
    V2 = np.copy(ref_GT['H_2^0'][99])

    # Getting escape yield of H2, which represents {H_2}^0 in Huerta Parajon 2008. Multiplied to match number of concentrations
    sut_SG_H20['H_2^0'] = [V1[1]]*len(HCO2m_concentrations)
    sut_SG_H20_err['H_2^0'] = [V1[2]]*len(HCO2m_concentrations)

    ref_SG_H20['H_2^0'] = [V2[1]]*len(HCO2m_concentrations)
    ref_SG_H20_err['H_2^0'] = [V2[2]]*len(HCO2m_concentrations)

    kobsHCO2m = 2.1e8
    kobsNO3m = 1.0e7

    # Now getting H2 for different concentrations of Nitrate
    for N in NO3m_concentrations: 
        for T in HCO2m_concentrations:
            sut_GT   = average_results(sut_dir + '/*/HCO2m_%s_M_Br_1e-3_M_NO3m_%s_M.phsp'%(T,N))
            ref_GT   = average_results(ref_dir + '/*/HCO2m_%s_M_Br_1e-3_M_NO3m_%s_M.phsp'%(T,N))

            for i in sut_GT.keys():
                V1 = np.copy(sut_GT[i][99]) # taking 1e+9 [99] instead of 1e+6 [66], since H2 not stabilised at 1us
                V2 = np.copy(ref_GT[i][99])
                V1[0] = 1e12 / (float(T)*kobsHCO2m + 1e-3*kobsNO3m)
                V2[0] = 1e12 / (float(T)*kobsHCO2m + 1e-3*kobsNO3m)
                
                if i in sut_SG_H2_1mM:
                    sut_SG_H2_1mM[i].append(V1)
                    ref_SG_H2_1mM[i].append(V2)

                else:
                    sut_SG_H2_1mM[i]   = [V1]
                    ref_SG_H2_1mM[i]   = [V2]

    ##### Subtraction to obtain H yields #####
              
    # Topas under test
    time_sut_1mM = {}
    value_sut_1mM = {}
    error_sut_1mM = {}

    for key in sut_SG_H20: # only interested in H2
        for i in range(len(sut_SG_H2_1mM[key])):
            if i == 0:
                time_sut_1mM[key] = [sut_SG_H2_1mM[key][i][0]]
                value_sut_1mM[key] = [sut_SG_H2_1mM[key][i][1] - sut_SG_H20[key][i]]
                error_sut_1mM[key] = [sut_SG_H2_1mM[key][i][2] + sut_SG_H20_err[key][i]]

            else:
                time_sut_1mM[key].append(sut_SG_H2_1mM[key][i][0])
                value_sut_1mM[key].append(sut_SG_H2_1mM[key][i][1] - sut_SG_H20[key][i])
                error_sut_1mM[key].append(sut_SG_H2_1mM[key][i][2] + sut_SG_H20_err[key][i])


    # print('Time, 1mM: ', time_sut_1mM['H_2^0'])
    # print('G-value, 1mM: ', value_sut_1mM['H_2^0'])
    # print('Error, 1mM: ', error_sut_1mM['H_2^0'],'\n')

    # Topas reference
    time_ref_1mM = {}
    value_ref_1mM = {}
    error_ref_1mM = {}

    for key in ref_SG_H20: # only interested in H2
        for i in range(len(ref_SG_H2_1mM[key])):
            if i == 0:
                time_ref_1mM[key] = [ref_SG_H2_1mM[key][i][0]]
                value_ref_1mM[key] = [ref_SG_H2_1mM[key][i][1] - ref_SG_H20[key][i]]
                error_ref_1mM[key] = [ref_SG_H2_1mM[key][i][2] + ref_SG_H20_err[key][i]]

            else:
                time_ref_1mM[key].append(ref_SG_H2_1mM[key][i][0])
                value_ref_1mM[key].append(ref_SG_H2_1mM[key][i][1] - ref_SG_H20[key][i])
                error_ref_1mM[key].append(ref_SG_H2_1mM[key][i][2] + ref_SG_H20_err[key][i])


    # Huerta data
    #bench1 = np.genfromtxt('analysis/benchmark/HuertaParajon.csv')
    bench1 = np.loadtxt("./analysis/benchmark/HuertaParajon_cleaned.csv")
    tr = list(zip(*bench1))
    x1 = np.array(tr[0][1:5])
    y1 = np.array(tr[1][1:5])
    xf1, yf1, yerr1 = huerta_1(x1,y1)

    # RM 2021 data
    rm_x = [4761.87301608,  15872.66314717,   47615.8732275,   475873.22737223]
    rm_y = [0.7642553191489361, 0.6604255319148935, 0.5872340425531914, 0.5072340425531915]

    # x2 = np.array(tr[0][5:9])
    # y2 = np.array(tr[1][5:9])
    # xf2, yf2, yerr2 = huerta_2(x2,y2)

    fig = plt.figure(figsize=(8,8))
    ax1 = plt.subplot2grid((2,1),(0,0))
    ax2 = plt.subplot2grid((2,1),(1,0))

    matplotlib.rcParams['font.family']     = "sans-serif"
    matplotlib.rcParams['font.sans-serif'] = "Helvetica"
    matplotlib.rcParams['figure.dpi']      = 200

    ax1.set_title("H", fontsize=24)

    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.tick_params(axis='both', which='minor', labelsize=20)

    # print(final_sut["H_2^0"])
    ax1.errorbar(time_sut_1mM["H_2^0"],  value_sut_1mM["H_2^0"], yerr=error_sut_1mM["H_2^0"],  color="r", marker='o', markersize=10, linewidth=0, label='{}'.format(args.sut_label))
    ax1.errorbar(time_ref_1mM["H_2^0"],  value_ref_1mM["H_2^0"], yerr=error_ref_1mM["H_2^0"],  color="blue", marker='x', markersize=10, linewidth=0, label='{}'.format(args.ref_label))

    ax1.errorbar(xf1, yf1, yerr=yerr1, linestyle='', marker='*', markersize=10, markerfacecolor='k', capsize=2, elinewidth=1, zorder=1, color='k', label='Huerta Parajon et al., 2008')
    ax1.plot(rm_x, rm_y, color='k', mfc='white', markeredgecolor='k',zorder=1, marker='^', ms=10, ls = '--', label='Ramos-Méndez et al., 2021')


    #ax1.scatter(1e12/bench1[:,0], bench1[:,1], label='Pastina(1999)')
    #ax1.scatter(bench2[:,0], bench3[:,1], label='Ramos-Mendez(2021)')

    ax1.legend(loc=0)

    ax1.set_xlim(3e3,1E6)
#   ax1.set_ylim([2,4.5])

    ax1.set_xscale('log')

    ax1.set_xlabel("Time [ps]",fontsize=20)

    ax1.set_ylabel("G value [{} / 100 eV]".format(r'$H^{\bullet}$'),fontsize=20)

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
