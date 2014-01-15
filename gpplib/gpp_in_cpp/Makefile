# Author: Arvind Pereira
# Makefile for Arvind's Tools Library.
# Modify the includes, sources, headers, executable and
# other flags accordingly!
INCLUDES = -I ./ -I/usr/local/include -I/usr/include
LIBS = -L/usr/lib/ -L/usr/local/lib -lm -pthread -lpthread
BOOST_MPI_LIBS = -L/usr/local/lib -lboost_mpi -lboost_serialization
BOOST_THREAD_LIBS = -L/usr/local/lib -lboost_thread -lboost_system -lboost_exception
JSON_SPIRIT_LIBS = -L/usr/local/lib -ljson_spirit

CXX_MPI = mpic++
CC = g++
DEBUG = -g
LFLAGS = -Wall $(DEBUG)
CFLAGS = -Wall -c 
PTHREAD_FLAGS = -D_POSIX_PTHREAD_SEMANTICS
SHARED_FLAGS = -fPIC -shared


FAST_MDP_SRCS = FastValueIterate.cpp 
FAST_MDP_HDRS = DiGraph.h
FAST_MDP_OBJS = $(FAST_MDP_SRCS:.cpp=.o)

FAST_MDP = fast_solve_mdp

TOPLEVEL_FOLDER = gpp_in_cpp

all: $(FAST_MDP)
	@echo "-------------------------Done------------------------------"
	@echo "Type: 'make docs' for documentation"
	@echo "Type: 'make tar'  for a code snapshot to be saved to tar.gz"

$(FAST_MDP): $(FAST_MDP_OBJS) $(FAST_MDP_HDRS)
	$(CC) -o $(FAST_MDP) $(FAST_MDP_OBJS)

.cpp.o: $(INCLUDES)
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

tar:
	make clean; cd ..; tar -czf $(TAR_FILE_NAME) $(TOPLEVEL_FOLDER)
	cd ..; mv *$(TOPLEVEL_FOLDER).tar.gz $(TOPLEVEL_FOLDER)/

clean:
	rm -f $(OBJ)
	rm -f $(EXE)
	rm -rf docs

install:
	cp $(FAST_MDP) $(LIB_INSTALL_DESTINATION)
	
LIB_INSTALL_DESTINATION = /usr/local/lib/
INC_INSTALL_DESTINATION = /usr/local/include/
	
TAR_FILE_NAME = `date +'%Y%m%d_%H%M%S_'`$(TOPLEVEL_FOLDER).tar.gz

OBJ = $(FAST_MDP_OBJS)
EXE = $(FAST_MDP)

SOURCES = $(FAST_MDP_SRCS)
HEADERS = $(FAST_MDP_HDRS)

docs: $(SOURCES) $(HEADERS)
	if command -v doxygen; then doxygen Doxyfile; \
	else echo "Doxygen not found. Not making documentation."; fi

