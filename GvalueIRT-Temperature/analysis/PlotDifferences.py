###############################
### Import Libraries

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

###############################
### Define Read Functions

def ReadGValues(File):
	GValues = {}

	f = open(File,"r")
	for z in f.readlines():
		A = z.split()
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


def PlotTimeEvolution(Ref,Test):
	Temp = [0,-1]
	fig = plt.figure(figsize=(20,18))
	ax1 = plt.subplot2grid((3,3),(0,0))
	ax2 = plt.subplot2grid((3,3),(0,1))
	ax3 = plt.subplot2grid((3,3),(0,2))
	ax4 = plt.subplot2grid((3,3),(1,0))
	ax5 = plt.subplot2grid((3,3),(1,1))
	ax6 = plt.subplot2grid((3,3),(1,2))
	ax7 = plt.subplot2grid((3,3),(2,0))

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

	for j in range(len(Temp)):
		i = Temp[j]
		ax1.errorbar(Ref[i]["e_aq^-1"][:,0][::10],Ref[i]["e_aq^-1"][:,1][::10],yerr=Ref[i]["e_aq^-1"][:,2][::10], color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
		ax2.errorbar(Ref[i]["OH^0"][:,0][::10],   Ref[i]["OH^0"][:,1][::10],   yerr=Ref[i]["OH^0"][:,2][::10],    color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
		ax3.errorbar(Ref[i]["H^0"][:,0][::10],    Ref[i]["H^0"][:,1][::10],    yerr=Ref[i]["H^0"][:,2][::10],     color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
		ax4.errorbar(Ref[i]["H_2^0"][:,0][::10],  Ref[i]["H_2^0"][:,1][::10],  yerr=Ref[i]["H_2^0"][:,2][::10],   color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
		ax5.errorbar(Ref[i]["H2O2^0"][:,0][::10], Ref[i]["H2O2^0"][:,1][::10], yerr=Ref[i]["H2O2^0"][:,2][::10],  color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
		ax6.errorbar(Ref[i]["H3O^1"][:,0][::10],  Ref[i]["H3O^1"][:,1][::10],  yerr=Ref[i]["H3O^1"][:,2][::10],   color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
		ax7.errorbar(Ref[i]["OH^-1"][:,0][::10],  Ref[i]["OH^-1"][:,1][::10],  yerr=Ref[i]["OH^-1"][:,2][::10],   color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)

		ax1.errorbar(Test[i]["e_aq^-1"][:,0],Test[i]["e_aq^-1"][:,1],yerr=Test[i]["e_aq^-1"][:,2], color="r", linewidth=2)
		ax2.errorbar(Test[i]["OH^0"][:,0],   Test[i]["OH^0"][:,1],   yerr=Test[i]["OH^0"][:,2],    color="r", linewidth=2)
		ax3.errorbar(Test[i]["H^0"][:,0],    Test[i]["H^0"][:,1],    yerr=Test[i]["H^0"][:,2],     color="r", linewidth=2)
		ax4.errorbar(Test[i]["H_2^0"][:,0],  Test[i]["H_2^0"][:,1],  yerr=Test[i]["H_2^0"][:,2],   color="r", linewidth=2)
		ax5.errorbar(Test[i]["H2O2^0"][:,0], Test[i]["H2O2^0"][:,1], yerr=Test[i]["H2O2^0"][:,2],  color="r", linewidth=2)
		ax6.errorbar(Test[i]["H3O^1"][:,0],  Test[i]["H3O^1"][:,1],  yerr=Test[i]["H3O^1"][:,2],   color="r", linewidth=2)
		ax7.errorbar(Test[i]["OH^-1"][:,0],  Test[i]["OH^-1"][:,1],  yerr=Test[i]["OH^-1"][:,2],   color="r", linewidth=2)


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

	ax1.grid(True,dashes=[5,5])
	ax2.grid(True,dashes=[5,5])
	ax3.grid(True,dashes=[5,5])
	ax4.grid(True,dashes=[5,5])
	ax5.grid(True,dashes=[5,5])
	ax6.grid(True,dashes=[5,5])
	ax7.grid(True,dashes=[5,5])

	fig.tight_layout()
	fig.savefig("TimeEvolution")

	plt.clf()
	plt.cla()
	plt.close()

def PlotTempEvolution(RefS,TestS, RefF, TestF,Temp):
	fig = plt.figure(figsize=(20,18))
	ax1 = plt.subplot2grid((3,3),(0,0))
	ax2 = plt.subplot2grid((3,3),(0,1))
	ax3 = plt.subplot2grid((3,3),(0,2))
	ax4 = plt.subplot2grid((3,3),(1,0))
	ax5 = plt.subplot2grid((3,3),(1,1))
	ax6 = plt.subplot2grid((3,3),(1,2))
	ax7 = plt.subplot2grid((3,3),(2,0))

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

	ax1.errorbar(Temp, RefS["e_aq^-1"][:,1],yerr=RefS["e_aq^-1"][:,2], color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax2.errorbar(Temp, RefS["OH^0"][:,1],   yerr=RefS["OH^0"][:,2],    color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax3.errorbar(Temp, RefS["H^0"][:,1],    yerr=RefS["H^0"][:,2],     color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax4.errorbar(Temp, RefS["H_2^0"][:,1],  yerr=RefS["H_2^0"][:,2],   color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax5.errorbar(Temp, RefS["H2O2^0"][:,1], yerr=RefS["H2O2^0"][:,2],  color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax6.errorbar(Temp, RefS["H3O^1"][:,1],  yerr=RefS["H3O^1"][:,2],   color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax7.errorbar(Temp, RefS["OH^-1"][:,1],  yerr=RefS["OH^-1"][:,2],   color="b", marker="o", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)

	ax1.errorbar(Temp, TestS["e_aq^-1"][:,1],yerr=TestS["e_aq^-1"][:,2], color="r", linewidth=2)
	ax2.errorbar(Temp, TestS["OH^0"][:,1],   yerr=TestS["OH^0"][:,2],    color="r", linewidth=2)
	ax3.errorbar(Temp, TestS["H^0"][:,1],    yerr=TestS["H^0"][:,2],     color="r", linewidth=2)
	ax4.errorbar(Temp, TestS["H_2^0"][:,1],  yerr=TestS["H_2^0"][:,2],   color="r", linewidth=2)
	ax5.errorbar(Temp, TestS["H2O2^0"][:,1], yerr=TestS["H2O2^0"][:,2],  color="r", linewidth=2)
	ax6.errorbar(Temp, TestS["H3O^1"][:,1],  yerr=TestS["H3O^1"][:,2],   color="r", linewidth=2)
	ax7.errorbar(Temp, TestS["OH^-1"][:,1],  yerr=TestS["OH^-1"][:,2],   color="r", linewidth=2)

	ax1.errorbar(Temp, RefF["e_aq^-1"][:,1],yerr=RefF["e_aq^-1"][:,2], color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax2.errorbar(Temp, RefF["OH^0"][:,1],   yerr=RefF["OH^0"][:,2],    color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax3.errorbar(Temp, RefF["H^0"][:,1],    yerr=RefF["H^0"][:,2],     color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax4.errorbar(Temp, RefF["H_2^0"][:,1],  yerr=RefF["H_2^0"][:,2],   color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax5.errorbar(Temp, RefF["H2O2^0"][:,1], yerr=RefF["H2O2^0"][:,2],  color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax6.errorbar(Temp, RefF["H3O^1"][:,1],  yerr=RefF["H3O^1"][:,2],   color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)
	ax7.errorbar(Temp, RefF["OH^-1"][:,1],  yerr=RefF["OH^-1"][:,2],   color="b", marker="d", dashes=[0,1], markerfacecolor="none", markersize=15, linewidth=2)

	ax1.errorbar(Temp, TestF["e_aq^-1"][:,1],yerr=TestF["e_aq^-1"][:,2], color="r", dashes=[8,5], linewidth=2)
	ax2.errorbar(Temp, TestF["OH^0"][:,1],   yerr=TestF["OH^0"][:,2],    color="r", dashes=[8,5], linewidth=2)
	ax3.errorbar(Temp, TestF["H^0"][:,1],    yerr=TestF["H^0"][:,2],     color="r", dashes=[8,5], linewidth=2)
	ax4.errorbar(Temp, TestF["H_2^0"][:,1],  yerr=TestF["H_2^0"][:,2],   color="r", dashes=[8,5], linewidth=2)
	ax5.errorbar(Temp, TestF["H2O2^0"][:,1], yerr=TestF["H2O2^0"][:,2],  color="r", dashes=[8,5], linewidth=2)
	ax6.errorbar(Temp, TestF["H3O^1"][:,1],  yerr=TestF["H3O^1"][:,2],   color="r", dashes=[8,5], linewidth=2)
	ax7.errorbar(Temp, TestF["OH^-1"][:,1],  yerr=TestF["OH^-1"][:,2],   color="r", dashes=[8,5], linewidth=2)

	ax1.set_xlim([0,100])
	ax2.set_xlim([0,100])
	ax3.set_xlim([0,100])
	ax4.set_xlim([0,100])
	ax5.set_xlim([0,100])
	ax6.set_xlim([0,100])
	ax7.set_xlim([0,100])

	ax1.set_ylim([2,4.5])
	ax2.set_ylim([2,5.5])
	ax3.set_ylim([0.45,0.7])
	ax4.set_ylim([0.2,0.6])
	ax5.set_ylim([0,0.8])
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

	ax1.grid(True,dashes=[5,5])
	ax2.grid(True,dashes=[5,5])
	ax3.grid(True,dashes=[5,5])
	ax4.grid(True,dashes=[5,5])
	ax5.grid(True,dashes=[5,5])
	ax6.grid(True,dashes=[5,5])
	ax7.grid(True,dashes=[5,5])

	fig.tight_layout()
	fig.savefig("TemperatureEvolution")

	plt.clf()
	plt.cla()
	plt.close()

###############################
### Define Main

def Main():
	Ref_FileFormat = "./Manual/electron_Gvalue_ByHand_%s.phsp"
	Tes_FileFormat = "./Automatic/electron_Gvalue_Corrected_%s.phsp"

	Temperatures = [10,20,30,40,50,60,70,80,90]

	Ref_Data = []
	Tes_Data = []

	Ref_DataS_T = {}
	Tes_DataS_T = {}

	Ref_DataF_T = {}
	Tes_DataF_T = {}

	for i in Temperatures:
		Ref_GValues = ReadGValues(Ref_FileFormat%(i))
		Tes_GValues = ReadGValues(Tes_FileFormat%(i))
		Ref_Data.append(Ref_GValues)
		Tes_Data.append(Tes_GValues)

		for k in Ref_GValues.keys():
			if k in Ref_DataS_T:
				Ref_DataS_T[k].append(Ref_GValues[k][0])
				Tes_DataS_T[k].append(Tes_GValues[k][0])

				Ref_DataF_T[k].append(Ref_GValues[k][-1])
				Tes_DataF_T[k].append(Tes_GValues[k][-1])

			else:
				Ref_DataS_T[k] = [Ref_GValues[k][0]]
				Tes_DataS_T[k] = [Tes_GValues[k][0]]

				Ref_DataF_T[k] = [Ref_GValues[k][-1]]
				Tes_DataF_T[k] = [Tes_GValues[k][-1]]


	for i in Ref_DataS_T.keys():
		Ref_DataS_T[i] = np.array(Ref_DataS_T[i])
		Tes_DataS_T[i] = np.array(Tes_DataS_T[i])

		Ref_DataF_T[i] = np.array(Ref_DataF_T[i])
		Tes_DataF_T[i] = np.array(Tes_DataF_T[i])

	PlotTimeEvolution(Ref_Data,Tes_Data)
	PlotTempEvolution(Ref_DataS_T,Tes_DataS_T,Ref_DataF_T,Tes_DataF_T, Temperatures)

###############################
### Run Main

if __name__=="__main__":
	Main()

###############################