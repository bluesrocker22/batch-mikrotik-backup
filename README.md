# batch-mikrotik-backup
mikrotik batch backup script with autodetection of RouterOS version (for changing syntax between 6 and 7 versions). 

Now it may use only for config export (not for binary backup). 

It use 'compact' export command and making backups, which contains sensitive data (ppp passwords, for example). 

All you need is one file with the list of ip addresses of your devices (comma-separated or in column).

Filename should be: addresses.txt

Script will use one pair of credentials for getting access to all devices from list.

Just login/password authentication now supported. 

## Known issues
Windows is supported with monkey patch (reason: https://github.com/paramiko/paramiko/pull/2130)

Warning! 
It's don't working with 6.49.7 and possibly on some others, don't know why (disconnect after several output strings in the file) 
Need to check it before use! 

Similar issue here:
https://github.com/ktbyers/netmiko/issues/2880

I think it may be more useful exporting backup to disk and download it after creation