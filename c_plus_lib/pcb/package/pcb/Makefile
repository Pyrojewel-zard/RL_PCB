PYTHON := python3

package : src/pcb/pcb.py src/pcb/_pcb.so
	@echo -n "Using "; $(PYTHON) -V
	$(PYTHON) -m build
	
# -y automatically accepts the confirmation presented.	
uninstall : 
	@echo -n "Uninstalling python package 'pcb_file_io' ... "
	@if [ $(shell $(PYTHON) -m pip list | grep pcb-file-io | wc -l) != "0" ]; then \
		echo "Found, uninstalling."; \
		$(PYTHON) -m pip uninstall -y pcb-file-io; \
	else \
		echo "package is not installed, therefore nothing to remove."; \
	fi
	
install : dist/pcb_file_io-0.0.1-py3-none-any.whl
	@echo "Installing python package 'pcb_file_io'"
	$(PYTHON) -m pip install $<
	
reinstall : 
	$(MAKE) uninstall
	$(MAKE) install
	
test : 
	@echo "Running test to verify package installation."
	$(PYTHON) ../main.py
	
clean :
	@echo "Cleaning ... "
	@echo -n "Attempting to clean the dist directory ... "
	@if [ ! -d "dist" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./dist ; \
 	fi
	
	@echo -n "Attempting to clean the src/pcb_file_io.egg-info directory ... "
	@if [ ! -d "src/pcb_file_io.egg-info" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./src/pcb_file_io.egg-info ; \
 	fi

	@echo -n "Attempting to clean the src/pcb/*.py file ... "
	@if [ ! -e "src/pcb/pcb.py" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./src/pcb/pcb.py ; \
 	fi

	@echo -n "Attempting to clean the src/pcb/*.so shared library file ... "
	@if [ ! -e "src/pcb/_pcb.so" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./src/pcb/*.so ; \
 	fi 	

	@echo -n "Attempting to clean the src/pcb/__pycache__ directory ... "
	@if [ ! -d "src/pcb/__pycache__" ]; then \
		echo "Not found, therefore nothing to clean."; \
 	else \
 		echo "Found, deleting."; \
 		rm -fvr ./src/pcb/__pycache__ ; \
 	fi
