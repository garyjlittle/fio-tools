# fio-tools

tools for use with fio and fio output

* `fio_log_summary` - summarise, plot and total per-disk log files from fio output (bandwidth).  requires `matplotlib`,`pandas` 
  * `fio-bw.1.log  fio-bw.2.log  fio-bw.3.log1` - example log files to be used with the above
  * Usage `./fio_log_summary.py *.log ; imgcat pandas.png`. 
   
The script will print a text summary and generate a png image.  If `imgcat` is installed it can be used to view it in the terminal - else start a python webserver and view the image that way.
