#
# Regular cron jobs for the slimbookamdcontroller package
#
0 4	* * *	root	[ -x /usr/bin/slimbookamdcontroller_maintenance ] && /usr/bin/slimbookamdcontroller_maintenance
s