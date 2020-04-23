# Pi-UpTime2.0 and PiZ-UpTime 2.0
*Last Update April 22, 2020.*

To monitor the battery and shutdown the pi automatically every time the Pi reboots, follow the steps below.

1) Save the python scripts you have downloaded in a folder called uptime (or any other name). We will use 
   uptime for this example. Note the path using the "pwd" command. We will assume the path for the folder is
   /home/pi/uptime and all the files are in that folder. Use the file **uptime-2.0-rc.local.py**
   * Please edit the lines in the file which measures termperature. The code for temperature measurement is different
     for PiZ-UpTime and Pi-UpTime. 
2) Edit the file /etc/rc.local - we assume you have your favorite editor (nano, vi, emacs etc.) Make sure
   you use sudo to edit the file. For example, using nano, the command will be "sudo nano /etc/rc.local"
3) Add the following 2 lines just before the last line in /etc/rc.local - the last line in the file is exit 0 

      \# Next line is for the operation of Pi-UpTime or PiZ-UpTime \
      sudo python /home/pi/uptime/uptime-2.0-rc-local.py &

     _exit 0      #  <-- Note this is the last line in the file /etc/rc.local _
     
4) Save the edited file /etc/rc.local and reboot

After reboot, the script is running in the background. No log messages are printed or stored.

To monitor the operating conditions at any *given instant* run the script in the file **uptime-2.0.py** using command "python uptime2.0.py"
Best to run this script with Python 2. Should also work with Python 3.
The polling frequency can be changed by changing the value of the variable ```tiempo``` in the script.

At any time you can hit Control C to terminate the program. 
**_Please make sure you have commented / uncommented the line which measures the temperature, depending on whether you
 are using Pi-UpTime or PiZ-UpTime._**
 
 Contact support via https://alchemy-power.com/contact-us/ should you have any issues.
