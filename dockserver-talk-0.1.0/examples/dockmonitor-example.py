import dockserverTalk
from time import sleep

print "Simple program to monitor a dockserver."
dockserver=raw_input("Give the ip address or name of the dockserver :")
port=int(raw_input("And the TCP port where the client connects to (usuall 6564): "))

print "Ok, we're set up now. I will start the dockserver monitor and kill it"
print "again after 1 minute."

# setting up a message passing queue (which is not used here, but alas).

MPQ=dockserverTalk.dockserverTalk.Queue()

dm=dockserverTalk.dockmonitor.DockMonitor(dockserver,port,MPQ,debug=True)

dm.handle_connect()
dm.start()
sleep(60)
print "Time is up!"
dm.terminate()
"Going to kill all threads..."

