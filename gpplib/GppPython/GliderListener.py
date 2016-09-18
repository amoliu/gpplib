import dockserverTalk.dockserverTalk as DT
from dockserverTalk.dialogues import Buffer
import time

# Modify these three variables to suit your situation:
dockserver="10.1.1.20"
glider="sim_039"
port=6564
# A sender ID must consist of "name;number" otherwise the dockserver 
# doesn't answer apparently.
senderID="arvind-pereira;0xabcde0123"
senderID="test-dt;0xb1gb00b5"
# If debugging is True, then raw packets sent to and received from the 
# dockserver can be inspected.
debugging=False


class MyBuffer(Buffer):
    def __init__(self,dockserverComm):
        Buffer.__init__(self,dockserverComm)
        # when we put data on the queue, and someone
        # is reading out the queue, we use the name
        # of the glider as identifier.
        self.glider=dockserverComm.gliderName
        self.MPQueue=dockserverComm.MPQueue

    # override the add method.
    def add(self,mesg):
        self+=mesg # note that self is a list.
        while True:
            # getCompleteLine is a method of Buffer and subclassed.
            # this method returns a complete line (incl. CR) or an
            # empty string
            mesg=self.getCompleteLine()
            if mesg=='':
                break
            # We have something to write. Let's put it into the dockserver's
            # Message Passing Queue
            self.MPQueue.put((self.glider,mesg))


# Create a threaded dockserver Comm instance
t=DT.ThreadedDockserverComm(dockserver,glider,port,
                            senderID=senderID,debug=debugging)
# connect our MyBuffer class to the buffer handler:
t.connect_bufferHandler(MyBuffer)
# start the thread
t.start()
# Of course, if you have two gliders, or more, you can fire up as many threads.
# Each thread will communicate through the same Queue.

if not t.isAlive():
    raise IOError,"DockserverComm instance didn't start up."
else:
    print "Ok so far. Going to listen to 20 lines of dialogue."
    print "Make sure that the glider produces a dialogue, otherwise"
    print "we'll get stuck..."
ln=0
while 1:
    if not DT.ThreadedDockserverComm.MPQueue.empty():
        while not DT.ThreadedDockserverComm.MPQueue.empty():
            x=DT.ThreadedDockserverComm.MPQueue.get_nowait()
            gliderName,mesg=x
            print gliderName,"says:",mesg.rstrip() 
            ln+=1
    else:
        # if there is nothing in the queue, then
        # sleep briefly not to keep the CPU busy all the time...
        time.sleep(0.1)
    if ln>=20:
        break

#t.terminate()
#t.join()
#print "We're Done."
