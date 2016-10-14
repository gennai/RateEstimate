# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../")
import os  
import csv
import math
from datasetCrossSections.datasetCrossSectionsHLTPhysics import *
from triggersGroupMap.Menu_online_v3p1_V4 import *

Method = 1 #0: rate = count ; 1:HLT, rate = psNorm*count / LS*nLS ; 2:Zerobias, rate = 11245Hz * target nBunchs * nCount/total Event
LS = 23.31
PsNorm = 107*7.
nLS = 246-43+1
ps_const = 11245.0*2200.0
for dataset in datasetList:
    xsection = xsectionDatasets[dataset]


def my_print(datasetList):
    for dataset in datasetList:
        print dataset
    print len(datasetList)

def mergeRates(input_dir,output_dir,output_name,keyWord,writeMatrix,type_in='dataset',elementlist=[],writeMatrixRoot=False):
    wdir = input_dir
    
    ########## Merging the individual path rates
#    if L1write:
#        h1 = open(output_name[:-4]+'_L1.tsv', "w")
    rateList = []
    for i in range(2*len(datasetList)+5):
        rateList.append([]) #0 Prescale
    
    rateDataset = {}
    TotalEventsPerDataset = {}
    datasetListFromFile = []
    total_ps = 0
    ## fill datasetList properly
    for dataset in datasetList:
        datasetListFromFile.append(dataset)
        TotalEventsPerDataset[dataset] = 0

    
    Nlines = 0
    Nfiles = 0
    
    ### Looping over the individual .tsv files
    for rate_file in os.listdir(wdir):
        print rate_file
        if (keyWord in rate_file) :
#        if ("pu23to27rates_MC_v4p4_V1__frozen_2015_25ns14e33_v4p4_HLT_V1_2e33_PUfilterGen_matrixEvents.tsv" in rate_file) and not ("group" in rate_file):
            with open(wdir+rate_file) as tsvfile:
                print wdir+rate_file
                tsvreader = csv.reader(tsvfile, delimiter="\t")
                Nfiles += 1
                i = 0
                ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
                for line in tsvreader: 
    		    if "TotalEvents" in line[0]:
       			for k in xrange(0,len(datasetList)): 
                            print line[k+1]
                            TotalEventsPerDataset[datasetListFromFile[k]] += float(line[k+1])
                        print TotalEventsPerDataset
                        print line
                        print "*"*30
                        print len(line)
                        print "*"*30
                        continue
                    groupCheck = True
                    if (line[0]!='Path') and (line[0] not in rateList[0]):
                        if (groupCheck ): 
                            rateList[0].append(line[0])
                            for ii in range(0,len(datasetList)):
                                rateList[2*ii+3].append(float(line[3*ii+1]))
                                rateList[2*ii+4].append(float(line[3*ii+3])**2)
                            tmp_count=0.0
                            tmp_error_sq=0.0
                            i += 1
                    elif (line[0]!='Path'):
                        if (groupCheck ):
                            for ii in range(0,len(datasetList)):
                                rateList[2*ii+3][i] += float(line[3*ii+1])
                                rateList[2*ii+4][i] += float(line[3*ii+3])**2
                            i += 1
                if (Nlines==0): Nlines = i
    
    print "Nfiles = ",Nfiles
    print "Nlines = ",Nlines
   
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
     
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
     
        return False
    
    TotalRateList = []
    TotalErrorList = []
   
    if Method==1:
        total_LS = 0
        for dataset in datasetList:
            rateDataset [dataset] = PsNorm/(nLS*LS)
            total_LS += nLS
        rateDataset_total = PsNorm/(total_LS*LS)
    elif Method==2:
        rateDataset_total = 0
        for dataset in datasetList:
            rateDataset [dataset] = (ps_const/TotalEventsPerDataset[dataset])# [1b = 1E-24 cm^2, 1b = 1E12pb ]
            rateDataset_total += TotalEventsPerDataset[dataset]
            print rateDataset [dataset]
        rateDataset_total = ps_const/rateDataset_total

    elif Method==0:
        for dataset in datasetList:
            rateDataset[dataset]=1
            rateDataset_total = 1
    else:
        for dataset in datasetList:
            rateDataset[dataset]=0
            rateDataset_total = 0

    
    for j in xrange (0,Nlines):
        TotalRateList.append(0)
        TotalErrorList.append(0)
        for i in xrange(0,len(datasetList)):
                TotalRateList[j] += rateList[2*i+3][j]
                TotalErrorList[j] += rateList[2*i+4][j]
        TotalRateList[j] += total_ps
        TotalErrorList[j] = math.sqrt(math.fabs(TotalErrorList[j]))
    
    ### Filling up the new .tsv file with the content of the python list
    if not writeMatrix:
        h = open(output_dir+'/'+output_name, "w")
        text_rate = 'Path\t\tTotal\t\t\t'
        for i in range(len(datasetList)):
            text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
        text_rate += '\n'
    
        text_rate += "TotalEvents\t\t\t\t"
        for dataset in datasetList:
            text_rate += str(TotalEventsPerDataset[dataset])
            text_rate += "\t\t\t"
        text_rate = text_rate[:-1]+"\n"
        h.write(text_rate)
        for j in xrange (0,Nlines):
            text_rate = ""
            text_rate += str(rateList[0][j])
            text_rate += "\t"
    
            text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF)
            text_rate += "\t+/-\t"
            text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF)
            text_rate += "\t"
            for i in xrange(0,len(datasetList)):
                if rateList[2*i+3][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[2*i+3][j]*rateDataset[datasetListFromFile[i]]*File_Factor*lumiSF
                    error = math.sqrt(rateList[2*i+4][j])*rateDataset[datasetListFromFile[i]]*File_Factor*lumiSF
                text_rate += str(rate)
                text_rate += "\t+/-\t"
                text_rate += str(error)
                text_rate += "\t"
        
            text_rate = text_rate[:-1]+"\n"
            h.write(text_rate)
        h.close()
    else:
        h = open(output_dir+'/'+output_name, "w")
        text_rate_title = '\t'
        #print elementlist
        for elem in elementlist:
            text_rate_title += elem + "\t"
        text_rate_title += '\n'
        h.write(text_rate_title)
        #text_rate = ''
        for elem_1 in elementlist:
            text_rate=elem_1+"\t"
            for elem_2 in elementlist:
                tmp_list = rateList[0]
                j=rateList[0].index(str((elem_1,elem_2)))
                text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF)
#                text_rate += "\t+/-\t"
#                text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF)
                text_rate += "\t"
            text_rate = text_rate[:-1]+"\n"
            h.write(text_rate)
        h.close()
        if writeMatrixRoot:
            import ROOT
            lenth = len(elementlist)
            c1 = ROOT.TCanvas( 'c1', 'A Simple 2D Histogram', 800,640 )
            c1.SetLeftMargin(0.2)
            c1.SetRightMargin(0.1)
            c1.SetBottomMargin(0.2)
            CorelHisto = ROOT.TH2F('DatasetCorrelHisto','Overlapping rates for %s pairs'%(type_in), lenth, 0, lenth, lenth, 0, lenth)
            n=1
            for elem in elementlist:
                CorelHisto.GetXaxis().SetBinLabel(n,elem)
                CorelHisto.GetXaxis().LabelsOption("v")
                CorelHisto.GetYaxis().SetBinLabel(n,elem)
                CorelHisto.GetYaxis().LabelsOption("v")
                n+=1
            i=1
            for elem_1 in elementlist:
                j=1
                for elem_2 in elementlist:
                    k=rateList[0].index(str((elem_1,elem_2)))
                    tmp_value = TotalRateList[k]*rateDataset_total*File_Factor*lumiSF
                    CorelHisto.SetBinContent(i,j,tmp_value)
                    j+=1
                i+=1
        CorelHisto.SetStats(0)
        CorelHisto.Draw("COLZ")
        c1.Print("%s/CorelationRate_%s.png"%(output_dir,type_in))
        #time.sleep(100)
        

File_Factor=1.0
lumiSF=1.0
UnprescaledCount = True

#start~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mergeRates("../ResultsBatch/ResultsBatch_groupEvents/","../Results/","output.group.tsv",'matrixEvents_groups_HLTPhysic',False)
mergeRates("../ResultsBatch/ResultsBatch_Pure_groupEvents/","../Results/","output.puregroup.tsv",'matrixEvents_Pure_groups_',False)
mergeRates("../ResultsBatch/ResultsBatch_primaryDatasetEvents/","../Results/","output.dataset.tsv",'matrixEvents_primaryDataset_HLTPhysic',False)
mergeRates("../ResultsBatch/ResultsBatch_Pure_primaryDatasetEvents/","../Results/","output.puredataset.tsv",'matrixEvents_Pure_primaryDataset_',False)
mergeRates("../ResultsBatch/ResultsBatch_streamEvents/","../Results/","output.stream.tsv",'matrixEvents_stream_HLTPhysic',False)
mergeRates("../ResultsBatch/ResultsBatch_Pure_streamEvents/","../Results/","output.purestream.tsv",'matrixEvents_Pure_Stream_',False)
mergeRates("../ResultsBatch/ResultsBatch_Core_primaryDatasetEvents/","../Results/","output.matrix_coredataset.tsv",'matrixEvents_Core_primaryDataset_',True,"dataset",pure_primaryDatasetList,True)


my_print(datasetList)

