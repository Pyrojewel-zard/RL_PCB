CC = g++
AR = ar
ARFLAGS = -rcs	# r - replace existing or replace new file(s) to archive
		# c - do not warn if the library had to be created.
		# s - create an archive index (cf. ranlib)
		
PYTHON_PACKAGE_PATH = ./package/graph
		
INCLUDES = -I ./include
CFLAGS = -Wall -fPIC -std=c++14 # language standard c++ 2014 
LDFLAGS = -L ./lib -lgpp -lboost_system -lboost_filesystem

LIB = libgpp.a	# graph pre-processing
BIN = test_app

PYTHON = python 	# default python binary
PYTHON_INCLUDE_DIR = /usr/include/python3.8

all : library $(BIN)

library : ./lib/$(LIB)

test_app : ./build/$(BIN)

./lib/$(LIB) : ./build/board.o ./build/edge.o ./build/graph.o ./build/node.o ./build/optimal.o ./build/utils.o
	@echo "Using the GNU archiver to create library"
	mkdir -p ./lib
	$(CROSS_COMPILE)$(AR) $(ARFLAGS) $@ $^

	@echo ""
	@echo "Library creation was successful. The library is located at ./lib/$(LIB)"

./build/$(BIN) : ./lib/$(LIB) ./build/main.o ./build/argparse.o
	@if [ ! -d "build" ]; then echo "Creating build directory."; mkdir -p ./build ; fi
	@echo "Linking and generating the binary executable \"$(BIN)\""
	$(CROSS_COMPILE)$(CC) $(word 2,$^) $(word 3, $^) -o $@ $(LDFLAGS)
				
	@echo ""
	@echo "The binary file is located at ./build/$(BIN)"

run_test_app : ./build/$(BIN)
	$^ ./test/bistable_oscillator_with_555_timer_and_ldo/bistable_oscillator_with_555_timer_and_ldo.nodes ./test/bistable_oscillator_with_555_timer_and_ldo/bistable_oscillator_with_555_timer_and_ldo.edges ./test/bistable_oscillator_with_555_timer_and_ldo/bistable_oscillator_with_555_timer_and_ldo.board | tee test/test_app.log


./build/%.o : ./libsrc/%.cpp
	@if [ ! -d "build" ]; then echo "Creating build directory."; mkdir -p ./build ; fi
	@echo "Compiling $< to $@"
	$(CROSS_COMPILE)$(CC) -c -o $@ $< $(CFLAGS) $(INCLUDES)

./build/%.o : ./src/%.cpp
	@if [ ! -d "build" ]; then echo "Creating build directory."; mkdir -p ./build ; fi
	@echo "Compiling $< to $@"
	$(CROSS_COMPILE)$(CC) -c -o $@ $< $(CFLAGS) $(INCLUDES)
	
./swig/%_wrap.cxx : swig/%.i
	@mkdir -p pyfiles
	@echo "Generating $@ from $^"
	swig -c++ -python -outdir pyfiles -o $@ $^

./build/swig/%.o : swig/%.cxx
	@mkdir -p build/swig/
	$(CROSS_COMPILE)$(CC) $(CFLAGS) -c $^ -o $@ -I $(PYTHON_INCLUDE_DIR) $(INCLUDES)

_%.so : ./lib/$(LIB) ./build/swig/%_wrap.o
	$(CC) -shared $(word 2,$^) -o $@ $(LDFLAGS) 

shared_libs : _graph.so _node.so _edge.so _board.so

python_test :
	$(PYTHON) main.py 

docs : dconfig
	doxygen dconfig
	
python_package : _board.so _edge.so _graph.so _node.so #pyfiles/placer.py
	@echo "Copying shared library and python header"
	@cp -v ./_board.so $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./_edge.so $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./_graph.so $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./_node.so $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./pyfiles/board.py $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./pyfiles/edge.py $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./pyfiles/graph.py $(PYTHON_PACKAGE_PATH)/src/graph
	@cp -v ./pyfiles/node.py $(PYTHON_PACKAGE_PATH)/src/graph

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
	
clean_all : clean clean_test_outputs
	
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
	
	make -j8 -C $(PYTHON_PACKAGE_PATH) clean

	
clean_test_outputs :
	@echo "Removing logfiles in the test directory."
	@rm -v ./test/*.log 2> /dev/null 	# redirect standard error to /dev/null supressing errors when no log files are present.

clean_docs :
	@echo "Removing docs directory ... "
	@rm -fr ./docs	
	
help :
	@echo "make all          	: builds library and test program."
	@echo "make library      	: builds only the library."
	@echo "make test_app    	: builds only the test program. Library is a pre-requisite for this step and will be built if not available."
	@echo "make run_test_app 	: runs the test application."
	@echo "make clean        	: recursively deletes the build and lib directories."
	@echo "make clean_test_outputs	: deletes all logfiles generated in the test directory."
	@echo "make clean_all		: cleans all generated outputs. That is build files, libraries and test logfiles.
