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
    parser.add_argument("-a","--anything",action="store")
    parser.add_argument("-m","--metric",action="store",dest="metric",help="Type of metric")
    args,extras=parser.parse_known_args()
    print("args are ",args)
    print("metric is ",args.metric)
    metric=args.metric
    print("switch is ",args.anything)
    arglen=len(extras)
    i=0
    for filename in extras:
        # pandas seems to tread "-" as a separator, so replace with "_" for now
        pdname=filename.replace("-","_")
        #we dont need the full dict for the simple case - leave it here for reference
        #pddict[pdname]=pd.read_csv(filename,names=["time","value","direction","priority"])
        pdtmp=pd.read_csv(filename,names=["time","value","direction","priority"])
        #i-1 because i starts at 1.  Divide by 1000 to get MB/s
        if metric == "bandwidth":
            pdsum.insert(0,pdname,pdtmp["value"]/1000)
            metric_name="Bandwidth (MB/s)"
        else:
            pdsum.insert(0,pdname,pdtmp["value"])
            metric_name="IOPS"
    
        i+=1

    pdsum=pdsum.assign(total=pdsum.sum(axis=1))
    print(pdsum)

    ax=pdsum.plot()
    ax.set_xlabel("Time")
    ax.set_ylabel(metric_name)
    ax.figure.savefig(imgname)

    #Special case for iterm2 imgcat
    subprocess.call(['/bin/bash', '-i', '-c','-l', 'imgcat '+imgname])



if __name__ == "__main__":
    main()