CC = g++

#DEPENDENCIES
NETLIST_GRAPH_PATH = ../../../netlist_graph
PCB_PATH = ../..

INCLUDES = -I $(NETLIST_GRAPH_PATH)/include -I $(PCB_PATH)/include
CFLAGS = -Wall -fPIC -std=c++14 # language standard c++ 2014 
LDFLAGS = -L $(PCB_PATH)/lib -lpcb -L $(NETLIST_GRAPH_PATH)/lib -lgpp
		
BIN = optimal_rw_single_design

./build/$(BIN) : ./build/main.o 
	@if [ ! -d "build" ]; then echo "Creating build directory."; mkdir -p ./build ; fi
	@echo "Linking and generating the binary executable \"$(BIN)\""
	$(CROSS_COMPILE)$(CC) $< -o $@ $(LDFLAGS)
				
	@echo ""
	@echo "The binary file is located at ./build/$(BIN)"

run : ./build/$(BIN)
	$^ ./test/bistable_oscillator_with_555_timer_and_ldo/bistable_oscillator_with_555_timer_and_ldo.nodes ./test/bistable_oscillator_with_555_timer_and_ldo/bistable_oscillator_with_555_timer_and_ldo.edges ./test/bistable_oscillator_with_555_timer_and_ldo/bistable_oscillator_with_555_timer_and_ldo.board | tee test/test_app.log

./build/%.o : ./src/%.cpp
	@if [ ! -d "build" ]; then echo "Creating build directory."; mkdir -p ./build ; fi
	@echo "Compiling $< to $@"
	$(CROSS_COMPILE)$(CC) -c -o $@ $< $(CFLAGS) $(INCLUDES)
	
clean :
	@echo "Cleaning ... "
	@echo -n "Attempting to clean the build directory ... "
	@if [ ! -d "build" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./build ; \
 	fi
	
help :
	@echo "make all          	: builds library and test program."
	@echo "make run         	: runs the application."
	@echo "make clean        	: recursively deletes the build directory."
