import sys
import matplotlib.pyplot as plt
import pandas as pd

# Process a set of fio _bw_ log files
# Summarise, Add disks together to provide "total bandwidth" across all disks
# Generate a png plot with each disk and the total bandwidth

arglen=len(sys.argv)
resdict={}

# For each fio bandwidth file passed in, create a dictionary with the 
# content of the file (read) an array attached to the dictionary item.
for i in range(1,arglen):
    filename=sys.argv[i]
    # Name the dictonary item the filename of the fio log currently being processed
    # and create an empty array
    resdict[filename]=[]
    with open(filename) as f:
        linecount=0
        max_bw_read_kb=0
        for line in f:
            (time_ms,bw_read_kb,bw_write_kb,bw_trim_kb)=line.split(",")
            linecount=linecount+1
            #add the lines of the file to the array. Currently only
            #the read bw is used.
            resdict[filename].append(int(bw_read_kb))
            if int(bw_read_kb) > max_bw_read_kb:
                max_bw_read_kb=int(bw_read_kb)
                max_bw_line_number=linecount
    #Print a summary of each fio bandwidth file processed
    print("Filename = {} Total Lines = {:4d}".format(filename,linecount))
    print("KB Read Max =",max_bw_read_kb,"at line",max_bw_line_number,"\n")

# by now we have our results in a dictionary and we want to process the results 
# a little for example converting to MB/s and creating an additional column for
# the total bandwidth.

# row[] = row by row processign across each bandwidth log file
# we need to do this so we can aggregate the individual bw
# for each disk and create a total BW across all disks.
row=[]

# result[] = array of arrays - one array for each bw file and
# an array for the sum of bw used for the "total" plot
result=[]

# We do this for every row across all the files so the outer loop
# is the rows, and the inner loop the columns in each row.

#for every row
for element in range(0,linecount):
    #for every column per row
    for resfile in resdict.keys():
        #convert KB/s to MB/s
        row.append(resdict[resfile][element]/1000)
    row.append(sum(row))
    result.append(row)
    # clear the current row  and fetch the next row.
    row=[]

#numpy version
#csvarray=np.asarray(result)
#np.savetxt("array.txt",csvarray,delimiter=",",fmt="%d")

#fig,ax=plt.subplots()
#ax.set_xlabel("time")
#ax.set_ylabel("bandwidth (MB/s)")
#ax.plot(result)
#fig.savefig("matplotlib.png")


# pandas dataframe is the ideal construct for this job.  The "result" 2D array
# is almost there, but lacks columns and also converting the array to a dataframe
# gives us the ability to pass that into matplotlib and to the plotting for us with
# no further work on our part.

#Convert the 2D array into a dataframe here.
pdres=pd.DataFrame(result)

# Use the filenames for columnnames, skip argv[0] which is the name of the script.
mycolumns=(sys.argv[1:])
# Add a column name for the new calculated column we added
mycolumns.append("Total")
# Set the dataframe columns to the array we just created.
pdres.columns=(mycolumns)

# !!!! TODO Import the First column from one of the logs here

#pandas will handle the formatting of long and/or wide dataframes.
#it gives us a summarised view which is nice.
print(pdres)

# Create the graphical plot and write out to a .png file
ax=pdres.plot()
ax.set_xlabel("Time")
ax.set_ylabel("Bandwidth (MB/s)")
ax.figure.savefig("pandas.png")
