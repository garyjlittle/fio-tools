import subprocess
import os
import argparse
import matplotlib.pyplot as plt
import pandas as pd

# Process a set of fio log files either iops or bandwidth
# spit into three dataframes; read, write and combined, then plot
# as a line chart and save png to disk.  By default we will print
# everything to show the user everything, then have the user reduce
# the output as needed.

def main():
    df_read=pd.DataFrame()
    df_write=pd.DataFrame()
    df_rw=pd.DataFrame()

    parser=argparse.ArgumentParser(
        description="Use this to plot the output of fio log files.  Just pass a list of files on the command line"
    )
    parser.add_argument("-m","--metric",action="store",dest="metric",
                        help="Type of metric e.g. iops,bandwidth",
                        choices=["iops","bandwidth"],default="iops")
    parser.add_argument("--dpi",action="store",
                        help="DPI of output 100 is the default.  Larger DPI makes bigger plots",type=int)
    parser.add_argument("--nototals",action="store_true",
                        dest="skiptotals",default=False,
                        help="Don't show a total for all files/devices.  Useful if the chart is compressed too much")
    parser.add_argument("--noagg",action="store_false",
                        dest="showaggr",default=True,
                        help="Skip the aggregate view of read+writes.  Saves screen real-estate")
    parser.add_argument("--noreads",action="store_true",
                        help="Skip the read chart")
    parser.add_argument("--nowrites",action="store_true",
                        help="Skip the writes chart")    
    parser.add_argument("-d","--debug",action="store_true",
                        help="Debug")
    parser.add_argument("--table",action="store_true",
                        help="show summary text table")
    parser.add_argument("--theme",action="store",
                        choices=["light","dark"],
                        default="dark",
                        help="Use theme default is dark theme")

    #Use parse_known_args because we may have any number of args as filenames
    args,filenames=parser.parse_known_args()
    
    metric=args.metric
    debug=args.debug
    dpi=args.dpi

    #bail out if no filenames are passed in
    if(len(filenames))<1:
        print("No filenames supplied")
        exit()

    #for each filename given
    for filename in filenames:
        # The "-" char is a special char for pandas so, replace
        # with "_" when converting filename to a column
        col_from_filename=filename.replace("-","_")
        
        # read in the file into a temporary dataframe.  
        if os.path.exists(filename):
            fiolog_tmp_df=pd.read_csv(filename)
            # Bandwidth is reported by fio in KB/s we
            # want MB/s at a minimum if the metric is bandwidth
            if (metric == "bandwidth"):
                #value is always column 1
                fiolog_tmp_df.iloc[:,1]=fiolog_tmp_df.iloc[:,1]/1000
        else:
            print("File does not exist :",filename)
            exit()            
        
        # Grab the column count from the file.  
        # fio versions may change the number of columns
        field_count=fiolog_tmp_df.shape[1]

        # Name the columns based on the field count
        if field_count==4:
            fiolog_tmp_df.columns=["time","value","direction","priority"]
        elif field_count==5:
            #Not sure if/what's happening here the format does not match the docs.
            fiolog_tmp_df.columns=["time","value","direction","priority","dummy1"]  
        else:
            print("Unknown field count ",field_count)
            exit()      

        if debug:
            print("filename is ",filename)
            print(fiolog_tmp_df)
            exit()
        
        #Separate the read_iops and write_iops as they are on separate
        #lines in the log file.  We add them together later to get a
        #total IO rate for read+write. 
        fiolog_tmp_df_read=fiolog_tmp_df[fiolog_tmp_df.direction==0]
        fiolog_tmp_df_write=fiolog_tmp_df[fiolog_tmp_df.direction==1]
        #We need to reset the index from the time offset to 
        #straight count because there is slight drift
        #in time that the io's are timestamped across files.        
        fiolog_tmp_df_read=fiolog_tmp_df_read.reset_index()
        fiolog_tmp_df_write=fiolog_tmp_df_write.reset_index()

        # Insert a new column into the read and write accumulating
        # dataframes
        df_read.insert(0,col_from_filename,fiolog_tmp_df_read["value"])
        df_write.insert(0,col_from_filename,fiolog_tmp_df_write["value"])

    # Once we have read all the files in the above loop
    # we sum up all the columns and create a new column
    # for the aggregate value
    df_read=df_read.assign(read_total=df_read.sum(axis=1))    
    df_write=df_write.assign(write_total=df_write.sum(axis=1))

    # Insert columns into the read+write aggregate table
    # and then create a column for reads+writes
    df_rw.insert(0,"reads",df_read["read_total"])
    df_rw.insert(0,"writes",df_write["write_total"])
    df_rw=df_rw.assign(rw_total=df_rw.sum(axis=1))


    #
    # Now we plot out the data to png files
    #

    #Use darkmode
    if (args.theme=="dark"):
        plt.style.use('dark_background')
    elif (args.theme=="light"):
        plt.style.use('Solarize_Light2')        

    #  for read results
    if (args.skiptotals):
        df_read=df_read.drop(columns="read_total")
    ax=df_read.plot()

    if (metric=='bandwidth'):
        metric_name="Read MB/s"
    else:        
        metric_name="read IOPS"
    ax.legend(bbox_to_anchor = (1, 1))
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.set_size_inches(6,3)
    ax.figure.savefig("read_tmp.png",dpi=dpi,bbox_inches='tight')

    #  for write reults 
    if (args.skiptotals):
        df_write=df_write.drop(columns="write_total")    
    ax=df_write.plot()
    if (metric=='bandwidth'):
        metric_name="Write MB/s"
    else:        
        metric_name="write IOPS"
    ax.legend(bbox_to_anchor = (1, 1))
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)
    ax.figure.set_size_inches(6,3)
    ax.figure.savefig("write_tmp.png",dpi=dpi,bbox_inches='tight')

    #  for the aggregate results
    if (args.skiptotals):
        df_rw=df_rw.drop(columns="rw_total")    
    ax=df_rw.plot()
    ax.legend(bbox_to_anchor = (1, 1))
    if (metric=='bandwidth'):
        metric_name="Read/Write MB/s"
    else:
        metric_name="read/write IOPS"
    ax.set_xlabel("Index")
    ax.set_ylabel(metric_name)

    #Make the figure wider than it is higher and use the "tight"
    #directive to allow a legend outside the main plot.
    ax.figure.set_size_inches(6,3)
    ax.figure.savefig("aggregate_tmp.png",dpi=dpi,bbox_inches='tight')

    #Special case for iterm2 imgcat - for some reason when we call subprocess.run
    #with /bin/bash, we need to use ;true to avoid leaving the subshell in a `stopped` 
    #state.  For macs - maybe disable image retina display because the charts are hard
    #to read on a retina laptop display.
    if (not df_read.empty and not args.noreads):
        subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'read_tmp.png;true'])
    if (not df_write.empty and not args.nowrites):
        subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'write_tmp.png;true'])
    #Always show aggregate?    
    if (args.showaggr):
        subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'aggregate_tmp.png;true'])
    
    #Maybe print a summary table - useful if imgcat is not available
    if (args.table):
        if (not df_read.empty):
            print("Read Table:")        
            print(df_read[:5])
        if (not df_write.empty):
            print("\nWrite Table:")
            print(df_write[:5])
        #Presumably we have something... unless only trims...
        print("\nR/W Summary table:")
        print(df_rw[:5])

if __name__ == "__main__":
    main()
