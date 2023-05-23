import sys
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import argparse
import os

# Process a set of fio _bw_ log files
# Summarise, Add disks together to provide "total bandwidth" across all disks
# Generate a png plot with each disk and the total bandwidth

def main():
    #pddict={}
    pdsum_read=pd.DataFrame()
    pdsum_write=pd.DataFrame()
    pdsum=pd.DataFrame()

    imgname='pandas-pandas.png'
    parser=argparse.ArgumentParser()
    parser.add_argument("-m","--metric",action="store",dest="metric",help="Type of metric")
    parser.add_argument("--dpi",action="store",help="DPI of output",type=int)
    parser.add_argument("-s","--summary",action="store_true",help="Sum up the log files and show the aggregate value")
    parser.add_argument("-d","--debug",action="store_true",help="Debug")
    parser.add_argument("--table",action="store_true",help="show summary text table")
    parser.add_argument("--dark",action="store_true",help="Use dark theme")

    args,filenames=parser.parse_known_args()
    metric=args.metric
    debug=args.debug
    dpi=args.dpi
    arglen=len(filenames)
    for filename in filenames:
        # pandas seems to treat "-" as a separator, so replace with "_" for now so that the dataframe
        # is named after the file.  We create one df per file.
        pdname=filename.replace("-","_")
        # read in the file into a temporary dataframe.  This format has changed over fime
        # specify this at the CLI for now, but try to figure it out dynamically
        pdtmp=pd.read_csv(filename)
        # Grab the column count
        field_count=pdtmp.shape[1]
        if field_count==4:
            pdtmp.columns=["time","value","direction","priority"]
        if field_count==5:
            #Not sure if/what's happening here the format does not match the docs. 
            pdtmp.columns=["time","value","direction","priority","dummy1"]       
        if debug:
            print("filename is ",filename)
            print(pdtmp)
            exit()
        
        # pdsum is the name of the df that we use to collect data for each file even
        # if we don't actually sum up the results. Insert an entry for every row, regardless of direction.
        # we dont use this for plotting, just loading the data from CSv, then we split into a read-df and a
        # write df.
        pdsum.insert(0,pdname,pdtmp["value"])
        
        #Create a read_iops and write_iops summary
        pdtmp_read=pdtmp[pdtmp.direction==0]
        pdtmp_write=pdtmp[pdtmp.direction==1]

        # setting index for time might not be the best idea because
        # when using multiple devices / log files - the times may not
        # line up exactly between files - e.g. writes to a file on a ms
        # boundary might split across a 1ms timestamp.

        #pdtmp_read=pdtmp_read.set_index("time")
        pdtmp_read=pdtmp_read.reset_index()

        #pdtmp_write=pdtmp_write.set_index("time")
        pdtmp_write=pdtmp_write.reset_index()

        pdsum_read.insert(0,pdname,pdtmp_read["value"])
        pdsum_write.insert(0,pdname,pdtmp_write["value"])
        metric_name="IOPS"

    # By here pdsum, pdsum_read and pdsum_write have been created
    pdsum_read=pdsum_read.assign(read_total=pdsum_read.sum(axis=1))    
    pdsum_write=pdsum_write.assign(write_total=pdsum_write.sum(axis=1))   

    pdsum_rw=pd.DataFrame()
    pdsum_rw.insert(0,"reads",pdsum_read["read_total"])
    pdsum_rw.insert(0,"writes",pdsum_write["write_total"])
    pdsum_rw=pdsum_rw.assign(aggregate=pdsum_rw.sum(axis=1))

 

    if (args.summary):
        # Here we sum the entry for each file and create an aggregate/sum
        # if we ask for it on the command line.
        print("reads")
        print(pdsum_read[:5])
        print("writes")
        print(pdsum_write[:5])
 

    ax=pdsum.plot()
    ax.set_xlabel("Time")
    ax.set_ylabel(metric_name)
    ax.figure.savefig(imgname)


    #Use darkmode
    if (args.dark):
        plt.style.use('dark_background')

    #  for read only test
    ax=pdsum_read.plot()
    metric_name="read IOPS"
    ax.legend(bbox_to_anchor = (1, 1))
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.set_size_inches(6,3)
    ax.figure.savefig("read_tmp.png",dpi=dpi,bbox_inches='tight')

    #  for write only 
    ax=pdsum_write.plot()
    metric_name="write IOPS"
    ax.legend(bbox_to_anchor = (1, 1))
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.set_size_inches(6,3)
    ax.figure.savefig("write_tmp.png",dpi=dpi,bbox_inches='tight')

    #  for aggregate  
    ax=pdsum_rw.plot()
    ax.legend(bbox_to_anchor = (1, 1))
    metric_name="read/write IOPS"
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.set_size_inches(6,3)
    ax.figure.savefig("aggregate_tmp.png",dpi=dpi,bbox_inches='tight')

    #Special case for iterm2 imgcat
    if (not pdsum_read.empty):
        subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'read_tmp.png;true'])
    if (not pdsum_write.empty):
        subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'write_tmp.png;true'])
    #Always show aggregate?    
    subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'aggregate_tmp.png;true'])
    
    #Maybe print a summary table
    if (args.table):
        if (not pdsum_read.empty):
            print("Read Table:")        
            print(pdsum_read[:5])
        if (not pdsum_write.empty):
            print("Write Table:")
            print(pdsum_write[:5])
        #Presumably we have something... unless only trims...
        print("R/W Summary table:")
        print(pdsum_rw[:5])

if __name__ == "__main__":
    main()