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

    Results = {}
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
                Results[Mol][:,2] += Stdv1
        n += 1

    for i in Results.keys():
        Results[i] = np.array(Results[i])
        Results[i][:,1] /= n
        Results[i][:,2] /= n

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
    Temps = np.arange(9)*10 + 10

    sut_T = average_results_time(sut_dir + '/*/log.out')
    ref_T = average_results_time(ref_dir + '/*/log.out')

    sut_G   = []
    ref_G   = []
    bench_G = []

    sut_SG   = {}
    ref_SG   = {}
    bench_SG = {}

    # Experimental data used in R.M. 2022: https://doi.org/10.1088/1361-6560/ac79f9

    #--- OH

    # Spinks and Woods, 1990
    SPINKSx = [24.897119341563787]
    SPINKSy = [2.7240437158469946]

    # Elliot et al., 1993
    ELL1x = [23.868312757201647, 17.695473251028808]
    ELL1y = [2.66120218579235, 2.7540983606557377]

    ELL2x = [21.810699588477366, 79.83539094650206]
    ELL2y = [2.9371584699453552, 3.349726775956284]

    ELL3x = [28.395061728395063, 17.79835390946502, 30.967078189300413]
    ELL3y = [2.959016393442623, 2.8688524590163933, 3.021857923497268]

    ELL4x = [30.246913580246915, 17.79835390946502, 33.02469135802469, 72.7366255144033]
    ELL4y = [2.907103825136612, 2.7568306010928962, 3.0437158469945356, 3.4508196721311473]

    ELL5x = [19.958847736625515, 28.80658436213992]
    ELL5y = [2.4672131147540983, 2.6038251366120218]

    #--- e_aq

    # Elliot et al., 1993
    ELL6x = [25]
    ELL6y = [2.644]

    # Schmidt et al., 1992
    SCHMIDTx = [25.401606425702813, 47.69076305220884, 68.77510040160642, 86.84738955823293]
    SCHMIDTy = [2.664, 2.658, 2.66, 2.824]

    # Kent and Sims (in Elliot et al., 2009)
    KENT1x = [20.983935742971887, 15.763052208835342, 17.269076305220885]
    KENT1y = [2.3820000000000006, 2.6, 2.602]
    
    # Jha et al., 1972
    JHAx = [22.79116465863454]
    JHAy = [2.696]

    # Janik et al., 2007
    JAN1x = [21.88755020080321]
    JAN1y = [2.73]

    JAN2x = [22.08835341365462]
    JAN2y = [2.9279999999999995]

    #--- H2O2

    # Elliot et al., 1993
    ELL7x = [25.2, 70.30000000000001]
    ELL7y = [0.6879518072289156, 0.608433734939759]

    # Elliot, 1998
    ELL8x = [70.2, 25]
    ELL8y = [0.6704819277108434, 0.7198795180722891]

    # Kent and Sims (in Elliot et al., 2009)
    KENT2x = [20, 20, 20, 20, 20]
    KENT2y = [0.6795180722891566, 0.708433734939759, 0.75, 0.8012048192771084, 0.7879518072289156]

    # Stefanic and LaVerne, 2002
    STEFx = [60, 25, 80]
    STEFy = [0.6620481927710843, 0.7078313253012047, 0.5975903614457831]
        
    #--- H2

    # Elliot et al., 1990
    ELL9x = [25, 100]
    ELL9y = [0.42, 0.46]

    for T in Temps:
        sut_GT   = average_results(sut_dir + '/*/electron_Gvalue_Corrected_%s.phsp'%(T))
        ref_GT   = average_results(ref_dir + '/*/electron_Gvalue_Corrected_%s.phsp'%(T))
        bench_GT = ReadGValues("./analysis/benchmark/electron_Gvalue_ByHand_%s.phsp"%(T))

        sut_G.append(sut_GT)
        ref_G.append(ref_GT)
        bench_G.append(bench_GT)

        for i in sut_GT.keys():
            V1 = np.copy(sut_GT[i][-1])
            V2 = np.copy(ref_GT[i][-1])
            V3 = np.copy(bench_GT[i][-1])
            V1[0] = T
            V2[0] = T
            V3[0] = T
            if i in sut_SG:
                sut_SG[i].append(V1)
                ref_SG[i].append(V2)
                bench_SG[i].append(V3)

            else:
                sut_SG[i]   = [V1]
                ref_SG[i]   = [V2]
                bench_SG[i] = [V3]

    for i in sut_SG.keys():
        sut_SG[i]   = np.array(sut_SG[i])
        ref_SG[i]   = np.array(ref_SG[i])
        bench_SG[i] = np.array(bench_SG[i])

    fig = plt.figure(figsize=(20,18))
    ax1 = plt.subplot2grid((3,3),(0,0))
    ax2 = plt.subplot2grid((3,3),(0,1))
    ax3 = plt.subplot2grid((3,3),(0,2))
    ax4 = plt.subplot2grid((3,3),(1,0))
    ax5 = plt.subplot2grid((3,3),(1,1))
    ax6 = plt.subplot2grid((3,3),(1,2))
    ax7 = plt.subplot2grid((3,3),(2,0))
    ax8 = plt.subplot2grid((3,3),(2,1),colspan=2)
    #ax9 = plt.subplot2grid((3,3),(2,2))

    matplotlib.rcParams['font.family']     = "sans-serif"
    matplotlib.rcParams['font.sans-serif'] = "Helvetica"
    matplotlib.rcParams['figure.dpi']      = 200

    ax1.set_title(r"$e_{aq}^{-}$", fontsize=24)
    ax2.set_title(r"$OH$",         fontsize=24)
    ax3.set_title(r"$H$",          fontsize=24)
    ax4.set_title(r"$H_{2}$",      fontsize=24)
    ax5.set_title(r"$H_{2}O_{2}$", fontsize=24)
    ax6.set_title(r"$H^{+}$",      fontsize=24)
    ax7.set_title(r"$OH^{-}$",     fontsize=24)

    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.tick_params(axis='both', which='minor', labelsize=20)

    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.tick_params(axis='both', which='minor', labelsize=20)

    ax3.tick_params(axis='both', which='major', labelsize=20)
    ax3.tick_params(axis='both', which='minor', labelsize=20)

    ax4.tick_params(axis='both', which='major', labelsize=20)
    ax4.tick_params(axis='both', which='minor', labelsize=20)

    ax5.tick_params(axis='both', which='major', labelsize=20)
    ax5.tick_params(axis='both', which='minor', labelsize=20)

    ax6.tick_params(axis='both', which='major', labelsize=20)
    ax6.tick_params(axis='both', which='minor', labelsize=20)

    ax7.tick_params(axis='both', which='major', labelsize=20)
    ax7.tick_params(axis='both', which='minor', labelsize=20)

    ax1.errorbar(bench_G[0]["e_aq^-1"][:,0][::10],bench_G[0]["e_aq^-1"][:,1][::10],yerr=bench_G[0]["e_aq^-1"][:,2][::10], color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax2.errorbar(bench_G[0]["OH^0"][:,0][::10],   bench_G[0]["OH^0"][:,1][::10],   yerr=bench_G[0]["OH^0"][:,2][::10],    color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax3.errorbar(bench_G[0]["H^0"][:,0][::10],    bench_G[0]["H^0"][:,1][::10],    yerr=bench_G[0]["H^0"][:,2][::10],     color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax4.errorbar(bench_G[0]["H_2^0"][:,0][::10],  bench_G[0]["H_2^0"][:,1][::10],  yerr=bench_G[0]["H_2^0"][:,2][::10],   color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax5.errorbar(bench_G[0]["H2O2^0"][:,0][::10], bench_G[0]["H2O2^0"][:,1][::10], yerr=bench_G[0]["H2O2^0"][:,2][::10],  color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax6.errorbar(bench_G[0]["H3O^1"][:,0][::10],  bench_G[0]["H3O^1"][:,1][::10],  yerr=bench_G[0]["H3O^1"][:,2][::10],   color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax7.errorbar(bench_G[0]["OH^-1"][:,0][::10],  bench_G[0]["OH^-1"][:,1][::10],  yerr=bench_G[0]["OH^-1"][:,2][::10],   color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)

    ax1.errorbar(bench_G[-1]["e_aq^-1"][:,0][::10],bench_G[-1]["e_aq^-1"][:,1][::10],yerr=bench_G[-1]["e_aq^-1"][:,2][::10], color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax2.errorbar(bench_G[-1]["OH^0"][:,0][::10],   bench_G[-1]["OH^0"][:,1][::10],   yerr=bench_G[-1]["OH^0"][:,2][::10],    color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax3.errorbar(bench_G[-1]["H^0"][:,0][::10],    bench_G[-1]["H^0"][:,1][::10],    yerr=bench_G[-1]["H^0"][:,2][::10],     color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax4.errorbar(bench_G[-1]["H_2^0"][:,0][::10],  bench_G[-1]["H_2^0"][:,1][::10],  yerr=bench_G[-1]["H_2^0"][:,2][::10],   color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax5.errorbar(bench_G[-1]["H2O2^0"][:,0][::10], bench_G[-1]["H2O2^0"][:,1][::10], yerr=bench_G[-1]["H2O2^0"][:,2][::10],  color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax6.errorbar(bench_G[-1]["H3O^1"][:,0][::10],  bench_G[-1]["H3O^1"][:,1][::10],  yerr=bench_G[-1]["H3O^1"][:,2][::10],   color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10)
    ax7.errorbar(bench_G[-1]["OH^-1"][:,0][::10],  bench_G[-1]["OH^-1"][:,1][::10],  yerr=bench_G[-1]["OH^-1"][:,2][::10],   color="k", marker="^", ls = 'none', markerfacecolor="white", markersize=10, label='Ramos-Méndez et al., 2022')

    ax1.errorbar(sut_G[0]["e_aq^-1"][:,0],sut_G[0]["e_aq^-1"][:,1],yerr=sut_G[0]["e_aq^-1"][:,2], color="r", linewidth=2)
    ax2.errorbar(sut_G[0]["OH^0"][:,0],   sut_G[0]["OH^0"][:,1],   yerr=sut_G[0]["OH^0"][:,2],    color="r", linewidth=2)
    ax3.errorbar(sut_G[0]["H^0"][:,0],    sut_G[0]["H^0"][:,1],    yerr=sut_G[0]["H^0"][:,2],     color="r", linewidth=2)
    ax4.errorbar(sut_G[0]["H_2^0"][:,0],  sut_G[0]["H_2^0"][:,1],  yerr=sut_G[0]["H_2^0"][:,2],   color="r", linewidth=2)
    ax5.errorbar(sut_G[0]["H2O2^0"][:,0], sut_G[0]["H2O2^0"][:,1], yerr=sut_G[0]["H2O2^0"][:,2],  color="r", linewidth=2)
    ax6.errorbar(sut_G[0]["H3O^1"][:,0],  sut_G[0]["H3O^1"][:,1],  yerr=sut_G[0]["H3O^1"][:,2],   color="r", linewidth=2)
    ax7.errorbar(sut_G[0]["OH^-1"][:,0],  sut_G[0]["OH^-1"][:,1],  yerr=sut_G[0]["OH^-1"][:,2],   color="r", linewidth=2, label=r'{} 10$\degree$C'.format(args.sut_label))

    ax1.errorbar(sut_G[-1]["e_aq^-1"][:,0],sut_G[-1]["e_aq^-1"][:,1],yerr=sut_G[-1]["e_aq^-1"][:,2], color="orange", linewidth=2, linestyle='--')
    ax2.errorbar(sut_G[-1]["OH^0"][:,0],   sut_G[-1]["OH^0"][:,1],   yerr=sut_G[-1]["OH^0"][:,2],    color="orange", linewidth=2, linestyle='--')
    ax3.errorbar(sut_G[-1]["H^0"][:,0],    sut_G[-1]["H^0"][:,1],    yerr=sut_G[-1]["H^0"][:,2],     color="orange", linewidth=2, linestyle='--')
    ax4.errorbar(sut_G[-1]["H_2^0"][:,0],  sut_G[-1]["H_2^0"][:,1],  yerr=sut_G[-1]["H_2^0"][:,2],   color="orange", linewidth=2, linestyle='--')
    ax5.errorbar(sut_G[-1]["H2O2^0"][:,0], sut_G[-1]["H2O2^0"][:,1], yerr=sut_G[-1]["H2O2^0"][:,2],  color="orange", linewidth=2, linestyle='--')
    ax6.errorbar(sut_G[-1]["H3O^1"][:,0],  sut_G[-1]["H3O^1"][:,1],  yerr=sut_G[-1]["H3O^1"][:,2],   color="orange", linewidth=2, linestyle='--')
    ax7.errorbar(sut_G[-1]["OH^-1"][:,0],  sut_G[-1]["OH^-1"][:,1],  yerr=sut_G[-1]["OH^-1"][:,2],   color="orange", linewidth=2, linestyle='--', label=r'{} 90$\degree$C'.format(args.sut_label))

    ax1.errorbar(ref_G[0]["e_aq^-1"][:,0],ref_G[0]["e_aq^-1"][:,1],yerr=ref_G[0]["e_aq^-1"][:,2], color="b", linewidth=2)
    ax2.errorbar(ref_G[0]["OH^0"][:,0],   ref_G[0]["OH^0"][:,1],   yerr=ref_G[0]["OH^0"][:,2],    color="b", linewidth=2)
    ax3.errorbar(ref_G[0]["H^0"][:,0],    ref_G[0]["H^0"][:,1],    yerr=ref_G[0]["H^0"][:,2],     color="b", linewidth=2)
    ax4.errorbar(ref_G[0]["H_2^0"][:,0],  ref_G[0]["H_2^0"][:,1],  yerr=ref_G[0]["H_2^0"][:,2],   color="b", linewidth=2)
    ax5.errorbar(ref_G[0]["H2O2^0"][:,0], ref_G[0]["H2O2^0"][:,1], yerr=ref_G[0]["H2O2^0"][:,2],  color="b", linewidth=2)
    ax6.errorbar(ref_G[0]["H3O^1"][:,0],  ref_G[0]["H3O^1"][:,1],  yerr=ref_G[0]["H3O^1"][:,2],   color="b", linewidth=2)
    ax7.errorbar(ref_G[0]["OH^-1"][:,0],  ref_G[0]["OH^-1"][:,1],  yerr=ref_G[0]["OH^-1"][:,2],   color="b", linewidth=2, label=r'{} 10$\degree$C'.format(args.ref_label))

    ax1.errorbar(ref_G[-1]["e_aq^-1"][:,0],ref_G[-1]["e_aq^-1"][:,1],yerr=ref_G[-1]["e_aq^-1"][:,2], color="k", linewidth=2, linestyle='--')
    ax2.errorbar(ref_G[-1]["OH^0"][:,0],   ref_G[-1]["OH^0"][:,1],   yerr=ref_G[-1]["OH^0"][:,2],    color="k", linewidth=2, linestyle='--')
    ax3.errorbar(ref_G[-1]["H^0"][:,0],    ref_G[-1]["H^0"][:,1],    yerr=ref_G[-1]["H^0"][:,2],     color="k", linewidth=2, linestyle='--')
    ax4.errorbar(ref_G[-1]["H_2^0"][:,0],  ref_G[-1]["H_2^0"][:,1],  yerr=ref_G[-1]["H_2^0"][:,2],   color="k", linewidth=2, linestyle='--')
    ax5.errorbar(ref_G[-1]["H2O2^0"][:,0], ref_G[-1]["H2O2^0"][:,1], yerr=ref_G[-1]["H2O2^0"][:,2],  color="k", linewidth=2, linestyle='--')
    ax6.errorbar(ref_G[-1]["H3O^1"][:,0],  ref_G[-1]["H3O^1"][:,1],  yerr=ref_G[-1]["H3O^1"][:,2],   color="k", linewidth=2, linestyle='--')
    ax7.errorbar(ref_G[-1]["OH^-1"][:,0],  ref_G[-1]["OH^-1"][:,1],  yerr=ref_G[-1]["OH^-1"][:,2],   color="k", linewidth=2, linestyle='--', label=r'{} 90$\degree$C'.format(args.ref_label))

    ax1.set_xlim([1,1E7])
    ax2.set_xlim([1,1E7])
    ax3.set_xlim([1,1E7])
    ax4.set_xlim([1,1E7])
    ax5.set_xlim([1,1E7])
    ax6.set_xlim([1,1E7])
    ax7.set_xlim([1,1E7])

    ax1.set_ylim([2,4.5])
    ax2.set_ylim([2,5.5])
    ax3.set_ylim([0.45,0.7])
    ax4.set_ylim([0.2,0.6])
    ax5.set_ylim([0,0.8])
    ax6.set_ylim([2.5,4.5])
    ax7.set_ylim([0,0.7])

    ax1.set_xscale("log")
    ax2.set_xscale("log")
    ax3.set_xscale("log")
    ax4.set_xscale("log")
    ax5.set_xscale("log")
    ax6.set_xscale("log")
    ax7.set_xscale("log")

    ax1.set_xlabel("Time (ps)",fontsize=20)
    ax2.set_xlabel("Time (ps)",fontsize=20)
    ax3.set_xlabel("Time (ps)",fontsize=20)
    ax4.set_xlabel("Time (ps)",fontsize=20)
    ax5.set_xlabel("Time (ps)",fontsize=20)
    ax6.set_xlabel("Time (ps)",fontsize=20)
    ax7.set_xlabel("Time (ps)",fontsize=20)

    ax1.set_ylabel("GValue",fontsize=20)
    ax2.set_ylabel("GValue",fontsize=20)
    ax3.set_ylabel("GValue",fontsize=20)
    ax4.set_ylabel("GValue",fontsize=20)
    ax5.set_ylabel("GValue",fontsize=20)
    ax6.set_ylabel("GValue",fontsize=20)
    ax7.set_ylabel("GValue",fontsize=20)

    ax7.legend(loc=2)

    ax1.grid(True,dashes=[5,5])
    ax2.grid(True,dashes=[5,5])
    ax3.grid(True,dashes=[5,5])
    ax4.grid(True,dashes=[5,5])
    ax5.grid(True,dashes=[5,5])
    ax6.grid(True,dashes=[5,5])
    ax7.grid(True,dashes=[5,5])

    ax8.set_axis_off()
    Table = ax8.table(cellText=[['%1.3f +/- %1.3f' % (sut_T[2],sut_T[3]), '%1.3f +/- %1.3f' % (ref_T[2],ref_T[3])]],\
                      rowLabels=['Exec.'],\
                      colLabels=(args.sut_label+' (s)',args.ref_label+' (s)'),\
                      loc='center'\
                      )

    Table.set_fontsize(20)
    Table.scale(1,3)

    #ax9.set_axis_off()

    fig.tight_layout()
    fig.savefig(join(args.outdir,'TimeEvolution.pdf'))

    plt.clf()
    plt.cla()
    plt.close()

    fig = plt.figure(figsize=(20,18))
    ax1 = plt.subplot2grid((3,3),(0,0))
    ax2 = plt.subplot2grid((3,3),(0,1))
    ax3 = plt.subplot2grid((3,3),(0,2))
    ax4 = plt.subplot2grid((3,3),(1,0))
    ax5 = plt.subplot2grid((3,3),(1,1))
    ax6 = plt.subplot2grid((3,3),(1,2))
    ax7 = plt.subplot2grid((3,3),(2,0))
    ax8 = plt.subplot2grid((3,3),(2,1),colspan=2)
    #ax9 = plt.subplot2grid((3,3),(2,2))

    matplotlib.rcParams['font.family']     = "sans-serif"
    matplotlib.rcParams['font.sans-serif'] = "Helvetica"
    matplotlib.rcParams['figure.dpi']      = 200

    ax1.set_title(r"$e_{aq}^{-}$", fontsize=24)
    ax2.set_title(r"$OH$",         fontsize=24)
    ax3.set_title(r"$H$",          fontsize=24)
    ax4.set_title(r"$H_{2}$",      fontsize=24)
    ax5.set_title(r"$H_{2}O_{2}$", fontsize=24)
    ax6.set_title(r"$H^{+}$",      fontsize=24)
    ax7.set_title(r"$OH^{-}$",     fontsize=24)

    ax1.tick_params(axis='both', which='major', labelsize=20)
    ax1.tick_params(axis='both', which='minor', labelsize=20)

    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.tick_params(axis='both', which='minor', labelsize=20)

    ax3.tick_params(axis='both', which='major', labelsize=20)
    ax3.tick_params(axis='both', which='minor', labelsize=20)

    ax4.tick_params(axis='both', which='major', labelsize=20)
    ax4.tick_params(axis='both', which='minor', labelsize=20)

    ax5.tick_params(axis='both', which='major', labelsize=20)
    ax5.tick_params(axis='both', which='minor', labelsize=20)

    ax6.tick_params(axis='both', which='major', labelsize=20)
    ax6.tick_params(axis='both', which='minor', labelsize=20)

    ax7.tick_params(axis='both', which='major', labelsize=20)
    ax7.tick_params(axis='both', which='minor', labelsize=20)

    ax1.scatter(ELL6x, ELL6y, marker ='o', s=70, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax1.scatter(SCHMIDTx, SCHMIDTy, marker ='v', s=70, zorder=2, color='k',label = 'Schmidt et al., 1992')
    ax1.scatter(KENT1x, KENT1y, marker ='s', s=70, zorder=2, color='k',label = 'Kent and Sims (in Elliot et al., 2009)')
    ax1.scatter(JHAx, JHAy, marker ='*', s=90, zorder=2, color='k',label = 'Jha et al., 1972')
    ax1.scatter(JAN1x, JAN1y, marker ='x', s=70, zorder=2, color='k',label = 'Janik et al., 2007')
    ax1.scatter(JAN2x, JAN2y, marker ='D', s=70, zorder=2, color='k',label = 'Janik et al., 2007')
    ax1.legend()

    ax2.scatter(SPINKSx, SPINKSy, marker ='o', s=70, zorder=2, color='k',label = 'Spinks and Woods, 1990')
    ax2.scatter(ELL1x, ELL1y, marker ='v', s=70, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax2.scatter(ELL2x, ELL2y, marker ='s', s=70, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax2.scatter(ELL3x, ELL3y, marker ='*', s=90, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax2.scatter(ELL4x, ELL4y, marker ='x', s=70, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax2.scatter(ELL5x, ELL5y, marker ='D', s=70, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax2.legend()

    ax4.scatter(ELL9x, ELL9y, marker ='o', s=70, zorder=2, color='k',label = 'Elliot et al., 1990')
    ax4.legend()

    ax5.scatter(ELL7x, ELL7y, marker ='o', s=70, zorder=2, color='k',label = 'Elliot et al., 1993')
    ax5.scatter(ELL8x, ELL8y, marker ='v', s=70, zorder=2, color='k',label = 'Elliot, 1998')
    ax5.scatter(KENT2x, KENT2y, marker ='s', s=70, zorder=2, color='k',label = 'Kent and Sims (in Elliot et al., 2009)')
    ax5.scatter(STEFx, STEFy, marker ='*', s=90, zorder=2, color='k',label = 'Stefanic and LaVerne, 2002')
    ax5.legend()

    ax1.errorbar(bench_SG["e_aq^-1"][:,0], bench_SG["e_aq^-1"][:,1],yerr=bench_SG["e_aq^-1"][:,2], color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10)
    ax2.errorbar(bench_SG["OH^0"][:,0],    bench_SG["OH^0"][:,1],   yerr=bench_SG["OH^0"][:,2],    color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10)
    ax3.errorbar(bench_SG["H^0"][:,0],     bench_SG["H^0"][:,1],    yerr=bench_SG["H^0"][:,2],     color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10)
    ax4.errorbar(bench_SG["H_2^0"][:,0],   bench_SG["H_2^0"][:,1],  yerr=bench_SG["H_2^0"][:,2],   color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10)
    ax5.errorbar(bench_SG["H2O2^0"][:,0],  bench_SG["H2O2^0"][:,1], yerr=bench_SG["H2O2^0"][:,2],  color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10)
    ax6.errorbar(bench_SG["H3O^1"][:,0],   bench_SG["H3O^1"][:,1],  yerr=bench_SG["H3O^1"][:,2],   color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10)
    ax7.errorbar(bench_SG["OH^-1"][:,0],   bench_SG["OH^-1"][:,1],  yerr=bench_SG["OH^-1"][:,2],   color="k", ls = 'none', marker="^", markerfacecolor="white", markersize=10, label='Ramos-Méndez et al., 2022')

    ax1.errorbar(sut_SG["e_aq^-1"][:,0], sut_SG["e_aq^-1"][:,1],yerr=sut_SG["e_aq^-1"][:,2], color="r", linewidth=2)
    ax2.errorbar(sut_SG["OH^0"][:,0],    sut_SG["OH^0"][:,1],   yerr=sut_SG["OH^0"][:,2],    color="r", linewidth=2)
    ax3.errorbar(sut_SG["H^0"][:,0],     sut_SG["H^0"][:,1],    yerr=sut_SG["H^0"][:,2],     color="r", linewidth=2)
    ax4.errorbar(sut_SG["H_2^0"][:,0],   sut_SG["H_2^0"][:,1],  yerr=sut_SG["H_2^0"][:,2],   color="r", linewidth=2)
    ax5.errorbar(sut_SG["H2O2^0"][:,0],  sut_SG["H2O2^0"][:,1], yerr=sut_SG["H2O2^0"][:,2],  color="r", linewidth=2)
    ax6.errorbar(sut_SG["H3O^1"][:,0],   sut_SG["H3O^1"][:,1],  yerr=sut_SG["H3O^1"][:,2],   color="r", linewidth=2)
    ax7.errorbar(sut_SG["OH^-1"][:,0],   sut_SG["OH^-1"][:,1],  yerr=sut_SG["OH^-1"][:,2],   color="r", linewidth=2, label=args.sut_label)

    ax1.errorbar(ref_SG["e_aq^-1"][:,0], ref_SG["e_aq^-1"][:,1],yerr=ref_SG["e_aq^-1"][:,2], color="b", dashes=[8,5], linewidth=2)
    ax2.errorbar(ref_SG["OH^0"][:,0],    ref_SG["OH^0"][:,1],   yerr=ref_SG["OH^0"][:,2],    color="b", dashes=[8,5], linewidth=2)
    ax3.errorbar(ref_SG["H^0"][:,0],     ref_SG["H^0"][:,1],    yerr=ref_SG["H^0"][:,2],     color="b", dashes=[8,5], linewidth=2)
    ax4.errorbar(ref_SG["H_2^0"][:,0],   ref_SG["H_2^0"][:,1],  yerr=ref_SG["H_2^0"][:,2],   color="b", dashes=[8,5], linewidth=2)
    ax5.errorbar(ref_SG["H2O2^0"][:,0],  ref_SG["H2O2^0"][:,1], yerr=ref_SG["H2O2^0"][:,2],  color="b", dashes=[8,5], linewidth=2)
    ax6.errorbar(ref_SG["H3O^1"][:,0],   ref_SG["H3O^1"][:,1],  yerr=ref_SG["H3O^1"][:,2],   color="b", dashes=[8,5], linewidth=2)
    ax7.errorbar(ref_SG["OH^-1"][:,0],   ref_SG["OH^-1"][:,1],  yerr=ref_SG["OH^-1"][:,2],   color="b", dashes=[8,5], linewidth=2, label=args.ref_label)

    # print('nBio-v4.0: ', sut_SG["H_2^0"][:,1], sut_SG["H_2^0"][:,2])
    # print('nBio-v3.0: ', ref_SG["H_2^0"][:,1], sut_SG["H_2^0"][:,2])

    ax1.set_xlim([0,100])
    ax2.set_xlim([0,100])
    ax3.set_xlim([0,100])
    ax4.set_xlim([0,105])
    ax5.set_xlim([0,100])
    ax6.set_xlim([0,100])
    ax7.set_xlim([0,100])

    ax1.set_ylim([2,4.5])
    ax2.set_ylim([2,5.5])
    ax3.set_ylim([0.45,0.7])
    ax4.set_ylim([0.2,0.6])
    ax5.set_ylim([0,0.9])
    ax6.set_ylim([2.5,4.5])
    ax7.set_ylim([0,0.7])

    ax1.set_xlabel("Temperature (C)",fontsize=20)
    ax2.set_xlabel("Temperature (C)",fontsize=20)
    ax3.set_xlabel("Temperature (C)",fontsize=20)
    ax4.set_xlabel("Temperature (C)",fontsize=20)
    ax5.set_xlabel("Temperature (C)",fontsize=20)
    ax6.set_xlabel("Temperature (C)",fontsize=20)
    ax7.set_xlabel("Temperature (C)",fontsize=20)

    ax1.set_ylabel("GValue",fontsize=20)
    ax2.set_ylabel("GValue",fontsize=20)
    ax3.set_ylabel("GValue",fontsize=20)
    ax4.set_ylabel("GValue",fontsize=20)
    ax5.set_ylabel("GValue",fontsize=20)
    ax6.set_ylabel("GValue",fontsize=20)
    ax7.set_ylabel("GValue",fontsize=20)

    ax7.legend(loc=0)

    ax1.grid(True,dashes=[5,5])
    ax2.grid(True,dashes=[5,5])
    ax3.grid(True,dashes=[5,5])
    ax4.grid(True,dashes=[5,5])
    ax5.grid(True,dashes=[5,5])
    ax6.grid(True,dashes=[5,5])
    ax7.grid(True,dashes=[5,5])

    ax8.set_axis_off()
    Table = ax8.table(cellText=[['%1.3f +/- %1.3f' % (sut_T[2],sut_T[3]), '%1.3f +/- %1.3f' % (ref_T[2],ref_T[3])]],\
                      rowLabels=['Exec.'],\
                      colLabels=(args.sut_label+' (s)',args.ref_label+' (s)'),\
                      loc='center'\
                      )

    Table.set_fontsize(20)
    Table.scale(1,3)
    
    #ax9.set_axis_off()

    fig.tight_layout()
    fig.savefig(join(args.outdir,'TemperatureEvolution.pdf'))

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
