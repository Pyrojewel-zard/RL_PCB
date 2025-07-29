CC = g++
AR = ar
ARFLAGS = -rcs	# r - replace existing or replace new file(s) to archive
		# c - do not warn if the library had to be created.
		# s - create an archive index (cf. ranlib)
		
PYTHON_PACKAGE_PATH = ./package/pcb

#DEPENDENCIES
NETLIST_GRAPH_PATH = ./netlist_graph

INCLUDES = -I ./include -I $(NETLIST_GRAPH_PATH)/include
CFLAGS = -Wall -fPIC -std=c++14 # language standard c++ 2014 
LDFLAGS = -L ./lib -lpcb -L $(NETLIST_GRAPH_PATH)/lib -lgpp 

GPPLIB = $(NETLIST_GRAPH_PATH)/lib/libgpp.a

LIB = libpcb.a	
BIN = pcb_test

PYTHON = python 	# default python binary
PYTHON_INCLUDE_DIR = /usr/include/python3.8

SHARED_DEPS = _node.so _edge.so _graph.so _board.so pyfiles/node.py pyfiles/edge.py pyfiles/graph.py pyfiles/board.py

all : library test_app

library : ./lib/$(LIB)

test_app : ./build/$(BIN)

deps : $(SHARED_DEPS)

./lib/$(LIB) : ./build/pcb.o
	@echo "Using the GNU archiver to create library"
	mkdir -p ./lib
	$(CROSS_COMPILE)$(AR) $(ARFLAGS) $@ $^

	@echo ""
	@echo "Library creation was successful. The library is located at ./lib/$(LIB)"

./build/$(BIN) : ./lib/$(LIB) $(GPPLIB) ./build/$(BIN).o
	mkdir -p ./build/
	@echo "Linking and generating the binary executable \"$(BIN)\""
	$(CROSS_COMPILE)$(CC) $(word 3,$^) -o $@ $(LDFLAGS)
				
	@echo ""
	@echo "The binary file is located at ./build/$(BIN)"

run_test_app : ./build/$(BIN)
	$^ ../boards/bistable_oscillator_with_555_timer_and_ldo.edges ../boards/bistable_oscillator_with_555_timer_and_ldo.nodes ../boards/bistable_oscillator_with_555_timer_and_ldo.board

./build/%.o : ./libsrc/%.cpp
	mkdir -p ./build 
	@echo "Compiling $< to $@"
	$(CROSS_COMPILE)$(CC) -c -o $@ $< $(CFLAGS) $(INCLUDES)

./build/$(BIN).o : ./src/main.cpp
	mkdir -p ./build
	@echo "Compiling $< to $@"
	$(CROSS_COMPILE)$(CC) -c -o $@ $< $(CFLAGS) $(INCLUDES)
	
swig/%_wrap.cxx : swig/%.i
	@mkdir -p pyfiles
	@echo "Generating $@ from $^"
	swig -c++ -python -outdir pyfiles -o $@ $^

build/swig/%.o : swig/%.cxx
	@mkdir -p build/swig/
	$(CROSS_COMPILE)$(CC) $(CFLAGS) $(INCLUDES) -c $^ -o $@ -I $(PYTHON_INCLUDE_DIR) 

_%.so : ./lib/$(LIB) $(GPPLIB) build/swig/%_wrap.o
	$(CC) -shared $(word 3,$^) -o $@ $(LDFLAGS) 
	
shared_libs : _pcb.so $(SHARED_DEPS)

$(SHARED_DEPS):
	make -j8 -C $(NETLIST_GRAPH_PATH) CROSS_COMPILE=$(CROSS_COMPILE) shared_libs
	@cp -vr $(NETLIST_GRAPH_PATH)/pyfiles ./
	@cp -vr $(NETLIST_GRAPH_PATH)/*.so ./

python_test : _pcb.so $(SHARED_DEPS)
	@echo "Creating \'generated\' directory ..."
	@mkdir -p ./generated
	@echo "Starting python test ..."
	@sleep 1
	$(PYTHON) main.py 
	@echo "Starting python test ..."
	@sleep 1
	$(PYTHON) parse_graph_from_pcb_file.py
	@echo "Tests passed!"
	
python_package : _pcb.so ./pyfiles/pcb.py
	@echo "Copying shared library and python header"
	@cp -v ./_pcb.so $(PYTHON_PACKAGE_PATH)/src/pcb
	@cp -v ./pyfiles/pcb.py $(PYTHON_PACKAGE_PATH)/src/pcb

	$(MAKE) -C $(PYTHON_PACKAGE_PATH) package
	
clean_python_package :
	$(MAKE) -C $(PYTHON_PACKAGE_PATH) clean

uninstall_python_package :
	$(MAKE) -C $(PYTHON_PACKAGE_PATH) uninstall

install_python_package : 
	$(MAKE) -C $(PYTHON_PACKAGE_PATH) install

reinstall_python_package : 
	$(MAKE) -C $(PYTHON_PACKAGE_PATH) reinstall
	
test_python_package : 
	$(MAKE) -C $(PYTHON_PACKAGE_PATH) test	
	
python_package_all : 
	$(MAKE) clean_python_package
	$(MAKE) python_package 
	$(MAKE) reinstall_python_package 
	$(MAKE) test_python_package	

$(GPPLIB) :
	make -j8 -C $(NETLIST_GRAPH_PATH) CROSS_COMPILE=$(CROSS_COMPILE) library	
	
clean :
	@echo "Cleaning ... "
	@echo -n "Attempting to clean the build directory ... "
	@if [ ! -d "build" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./build ; \
 	fi
# 	@echo ""	# Newline for visual segmentation
	@echo -n "Attempting to clean the lib directory ... "
	@if [ ! -d "lib" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./lib ; \
 	fi
# 	@echo ""	# Newline for visual segmentation
	@echo "Deleting swig generated files ... "
	@if [ -d "swig" ]; then \
		if [ $(shell ls swig/*.cxx 2> /dev/null | wc -l) != "0" ]; then \
			rm -fvr swig/*.cxx ; \
		fi \
	fi	
	@if [ -d "swig" ]; then \
		if [ $(shell ls swig/*.c 2> /dev/null | wc -l) != "0" ]; then \
			rm -fvr swig/*.c ; \
		fi \
	fi	
	@echo -n "Attempting to clean the pyfiles directory ... "
	@if [ ! -d "pyfiles" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./pyfiles ; \
 	fi
	@if [ $(shell ls *.so 2> /dev/null | wc -l) != "0" ]; then \
		rm -fvr ./*.so ; \
	fi
	
	make -j8 -C $(NETLIST_GRAPH_PATH) clean
	make -j8 -C $(PYTHON_PACKAGE_PATH) clean

clean_generated_outputs:
	@echo "Cleaning generated outputs ... "
	@echo "Deleting generated directory"
	@rm -fvr ./generated
	
help :
	@echo "make all          : builds library and test program."
	@echo "make library      : builds only the library."
	@echo "make test_app     : builds only the test program. Library is a pre-requisite for this step and will be built if not available."
	@echo "make run_test_app : runs the test application."
	@echo "make clean        : recursively deletes the build and lib directories."
