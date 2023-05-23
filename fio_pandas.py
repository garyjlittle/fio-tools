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
    pdsum_read=pd.DataFrame()
    pdsum_write=pd.DataFrame()
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
        i+=1

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

    #  for read only test
    ax=pdsum_read.plot()
    metric_name="read IOPS"
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.savefig("read_tmp.png")

    #  for write only 
    ax=pdsum_write.plot()
    metric_name="write IOPS"
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.savefig("write_tmp.png")

    #  for aggregate  
    ax=pdsum_rw.plot()
    metric_name="read/write IOPS"
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.savefig("aggregate_tmp.png")

    #Special case for iterm2 imgcat
    # subprocess.call(['/bin/bash','-i', '-c','-l', 'imgcat '+imgname])
    #subprocess.call(['/bin/bash','-i', '-c','-l', 'imgcat '+'read_tmp.png'])


if __name__ == "__main__":
    main()