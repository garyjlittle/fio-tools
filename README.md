# fio-tools

tools for use with fio and fio output

## fio-log-summary
Use this to plot output of an fio log file (e.g. using a directive like `write_iops_log=sdb`)
```
usage: fio-log-summary.py [-h] [-m {iops,bandwidth}] [--dpi DPI] [--nototals] [--noagg] [--noreads] [--nowrites] [-d] [--table] [--theme {light,dark}]

Use this to plot the output of fio log files. Just pass a list of files on the command line

optional arguments:
  -h, --help            show this help message and exit
  -m {iops,bandwidth}, --metric {iops,bandwidth}
                        Type of metric e.g. iops,bandwidth
  --dpi DPI             DPI of output 100 is the default. Larger DPI makes bigger plots
  --nototals            Don't show a total for all files/devices. Useful if the chart is compressed too much
  --noagg               Skip the aggregate view of read+writes. Saves screen real-estate
  --noreads             Skip the read chart
  --nowrites            Skip the writes chart
  -d, --debug           Debug
  --table               show summary text table
  --theme {light,dark}  Use theme default is dark theme
  ```
  ### fio-log-summay Usage
  e.g. ` python3 ./fio-log-summary.py fio-iop-logs/random-rw-4-jobs.*.log --theme light`
  ### fio-logh-summary Output
  ##### Read IOPS
  ![Reads](https://github.com/garyjlittle/fio-tools/blob/91bd51ba681e3002de971c0ddc0c5de5866e4da9/example-output/read_tmp.png)
  ##### Write IOPS
  ![Writes](https://github.com/garyjlittle/fio-tools/blob/91bd51ba681e3002de971c0ddc0c5de5866e4da9/example-output/write_tmp.png)
  ##### Aggregate IOPS
  ![Aggregate](https://github.com/garyjlittle/fio-tools/blob/91bd51ba681e3002de971c0ddc0c5de5866e4da9/example-output/aggregate_tmp.png)
