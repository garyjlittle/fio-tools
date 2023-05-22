import sys
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import argparse

# Process a set of fio _bw_ log files
# Summarise, Add disks together to provide "total bandwidth" across all disks
# Generate a png plot with each disk and the total bandwidth

def main():
    #pddict={}
    pdsum=pd.DataFrame()
    

    #PNG output filename
    imgname='pandas-pandas.png'
    parser=argparse.ArgumentParser()
    parser.add_argument("-m","--metric",action="store",dest="metric",help="Type of metric")
    parser.add_argument("--fields",action="store",dest="field_count",help="Format of the fio file (number of fields)",type=int,default=4)
    parser.add_argument("-s","--summary",action="store_true",help="Sum up the log files and show the aggregate value")
    parser.add_argument("-d","--debug",action="store_true",help="Debug")
    parser.add_argument("--table",action="store_true",help="show summary text table")
    args,filenames=parser.parse_known_args()
    metric=args.metric
    debug=args.debug
    field_count=args.field_count
    arglen=len(filenames)
    i=0
    for filename in filenames:
        # pandas seems to treat "-" as a separator, so replace with "_" for now so that the dataframe
        # is named after the file.  We create one df per file.
        pdname=filename.replace("-","_")
        # read in the file into a temporary dataframe.  This format has changed over fime
        # specify this at the CLI for now, but try to figure it out dynamically
        if field_count==4:
            pdtmp=pd.read_csv(filename,names=["time","value","direction","priority"])
        if field_count==5:
            #Not sure if/what's happening here the format does not match the docs. 
            pdtmp=pd.read_csv(filename,names=["time","value","direction","priority","dummy1"])        
        if debug:
            print("filename is ",filename)
            print(pdtmp)
            exit()
        # pdsum is the name of the df that we use to collect data for each file even
        # if we don't actually sum up the results.
        if metric == "bandwidth":
            # fio reports in kb/s but probably we want to show MB/s
            pdsum.insert(0,pdname,pdtmp["value"]/1000)
            metric_name="Bandwidth (MB/s)"
        else:
            pdsum.insert(0,pdname,pdtmp["value"])
            metric_name="IOPS"
    
        i+=1

    if (args.summary):
        # Here we sum the entry for each file and create an aggregate/sum
        # if we ask for it on the command line.
        pdsum=pdsum.assign(total=pdsum.sum(axis=1))
    if (args.table):
        print(pdsum)

    ax=pdsum.plot()
    ax.set_xlabel("Time")
    ax.set_ylabel(metric_name)
    ax.figure.savefig(imgname)

    #Special case for iterm2 imgcat
    subprocess.call(['/bin/bash','-i', '-c','-l', 'imgcat '+imgname])



if __name__ == "__main__":
    main()