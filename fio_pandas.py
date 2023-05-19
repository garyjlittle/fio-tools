import sys
import matplotlib.pyplot as plt
import pandas as pd

# Process a set of fio _bw_ log files
# Summarise, Add disks together to provide "total bandwidth" across all disks
# Generate a png plot with each disk and the total bandwidth

arglen=len(sys.argv)
#pddict={}
pdsum=pd.DataFrame()

for i in range(1,arglen):
    # pandas seems to tread "-" as a separator, so replace with "_" for now
    filename=sys.argv[i]
    pdname=sys.argv[i].replace("-","_")
    #we dont need the full dict for the simple case - leave it here for reference
    #pddict[pdname]=pd.read_csv(filename,names=["time","value","direction","priority"])
    pdtmp=pd.read_csv(filename,names=["time","value","direction","priority"])
    #i-1 because i starts at 1.  Divide by 1000 to get MB/s
    pdsum.insert(i-1,pdname,pdtmp["value"]/1000)

pdsum=pdsum.assign(total=pdsum.sum(axis=1))
print(pdsum)

ax=pdsum.plot()
ax.set_xlabel("Time")
ax.set_ylabel("Bandwidth (MB/sec)")
ax.figure.savefig("pandas-pandas.png")

#Special case for iterm2 imgcat
imgname='pandas.png'
subprocess.call(['/bin/bash', '-i', '-c','-l', 'imgcat '+imgname])
