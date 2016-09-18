# Author: Arvind Pereira

# Modify the includes, sources, headers, executable and
# other flags accordingly!
INCLUDES = -I ./ -I/usr/local/include
LIBS = -L/usr/lib/ -lm

CC = g++
DEBUG = -g
LFLAGS = -Wall -pedantic $(DEBUG)
CFLAGS = -Wall -pedantic -c

SOURCES = Test.cpp

HEADERS = DiGraph.h

OBJ = $(SOURCES:.cpp=.o)

EXE = Test

all: Test

$(EXE):	$(OBJ)
	$(CC) -o $(EXE) $(OBJ) $(LFLAGS) $(LIBS)    

.cpp.o: $(HEADERS)
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

tar:
	tar -czf $(EXE).tar.gz $(SOURCES) $(HEADERS) Makefile

clean:
	rm -f $(OBJ)
	rm -f $(EXE)
