import sys
import matplotlib.pyplot as plt
import pandas as pd

# Process a set of fio _bw_ log files
# Summarise, Add disks together to provide "total bandwidth" across all disks
# Generate a png plot with each disk and the total bandwidth

arglen=len(sys.argv)
resdict={}

for i in range(1,arglen):
    filename=sys.argv[i]
    resdict[filename]=[]
    with open(filename) as f:
        linecount=0
        max_bw_read_kb=0
        for line in f:
            (time_ms,bw_read_kb,bw_write_kb,bw_trim_kb)=line.split(",")
            linecount=linecount+1
            resdict[filename].append(int(bw_read_kb))
            if int(bw_read_kb) > max_bw_read_kb:
                max_bw_read_kb=int(bw_read_kb)
                max_bw_line_number=linecount

    print("Filename = {} Total Lines = {:4d}".format(filename,linecount))
    print("KB Read Max =",max_bw_read_kb,"at line",max_bw_line_number,"\n")

# by now we have our results in a dictionary
# we want to process the results a little before
# writing them out

# row[] = row by row processign across each bandwidth log file
# we need to do this so we can aggregate the individual bw
# for each disk and create a total BW across all disks.
row=[]

# result[] = array of arrays - one array for each bw file and
# an array for the sum of bw used for the "total" plot
result=[]
for element in range(0,linecount):
    for resfile in resdict.keys():
        #convert KB/s to MB/s
        row.append(resdict[resfile][element]/1000)
    row.append(sum(row))
    result.append(row)
    row=[]

#numpy version
#csvarray=np.asarray(result)
#np.savetxt("array.txt",csvarray,delimiter=",",fmt="%d")

#fig,ax=plt.subplots()
#ax.set_xlabel("time")
#ax.set_ylabel("bandwidth (MB/s)")
#ax.plot(result)
#fig.savefig("matplotlib.png")


## pandas version
pdres=pd.DataFrame(result)
## Use the filenames for columnnames, skip argv[0] which is the name of the script.
mycolumns=(sys.argv[1:])
mycolumns.append("Total")
pdres.columns=(mycolumns)

#pandas will handle the formatting of long and/or wide dataframes.
print(pdres)

ax=pdres.plot()
ax.set_xlabel("Time")
ax.set_ylabel("Bandwidth (MB/s)")
ax.figure.savefig("pandas.png")
