import subprocess

print("ls here")
subprocess.run("/bin/ls")
print("ls /tmp")
subprocess.run(["/bin/bash","-c","-l","/bin/ls "+" /tmp"])
print("running imgcat 1")
subprocess.run(['/bin/bash','-i','-c','-l', 'imgcat '+'read_tmp.png ; true '])
print("running imgcat 2")
subprocess.run(['/bin/bash','-i', '-c','-l', 'imgcat '+'aggregate_tmp.png ; true'])