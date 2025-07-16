#!/bin/bash

# This script consolidates the environment setup and tool installation.
# It was created by merging env.sh and install_tools_and_virtual_environment.sh.

CPU_ONLY=false
UPDATE_UTILITY_BINARIES=false
SKIP_REPOSITORY_CHECK=false
date="2023/08/06" # This seems to be a date from the original script

# --- Start of functions ---

update_utility_binaries() {
	date="2023/05/06"

	kicadParser_branch=parsing_and_plotting
	SA_PCB_branch=crtYrd_bbox
	pcbRouter_branch=updating_dependencies

	#GIT=https://www.github.com/
	#GIT_USER=lukevassallo
	#GIT=git@gitlab.lukevassallo.com:
	GIT=https://gitlab.lukevassallo.com/
    GIT_USER=luke

	CLEAN_ONLY=false
	CLEAN_BEFORE_BUILD=false
	RUN_PLACER_TESTS=false
	RUN_ROUTER_TESTS=false

	printf "\n"
	printf "  **** Luke Vassallo M.Sc - 02_update_utility_binaries.sh\n"
	printf "   *** Program to to update kicad parsing utility and place and route tols.\n"
	printf "    ** Last modification time %s\n" $date
	printf "\n"
	sleep 1

	print_help_update_utility() {
		echo "Sub-script help for --update_utility_binaries:"
		echo "  --clean_only                removes the git repositories and exits."
		echo "  --clean_before_build        removes the git repositories then clones and builds binaries."
		echo "  --run_placer_tests          runs automated tests to verify placer."
		echo "  --run_router_tests          runs automated tests to verify router."
	}

    # Use getopts for better argument parsing in the function
    local OPTIND
    while getopts ":-:" opt; do
        case $opt in
            -)
                case "${OPTARG}" in
                    clean_only)
                        CLEAN_ONLY=true
                        ;;
                    clean_before_build)
                        CLEAN_BEFORE_BUILD=true
                        ;;
                    run_placer_tests)
                        RUN_PLACER_TESTS=true
                        ;;
                    run_router_tests)
                        RUN_ROUTER_TESTS=true
                        ;;
                    help)
                        print_help_update_utility
                        return
                        ;;
                    *)
                        echo "Unknown option --${OPTARG}" >&2
                        exit 1
                        ;;
                esac;;
            \?)
                echo "Invalid option: -$OPTARG" >&2
                exit 1
                ;;
        esac
    done
    shift $((OPTIND-1))


    if [ -d "bin" ]; then
        cd bin
    else
        mkdir bin && cd bin
    fi

    if [ "$CLEAN_ONLY" = true ] || [ "$CLEAN_BEFORE_BUILD" = true ]; then
        echo -n "Attempting to clean the KicadParser repository ... "
        if [ ! -d "KicadParser" ]; then
            echo "Not found, therefore nothing to clean.";
        else
            echo "Found, deleting."
            rm -fr KicadParser
        fi

        echo -n "Attempting to clean the SA_PCB repository ... "
        if [ ! -d "SA_PCB" ]; then
            echo "Not found, therefore nothing to clean.";
        else
            echo "Found, deleting."
            rm -fr SA_PCB
        fi

        echo -n "Attempting to clean the pcbRouter repository ... "
        if [ ! -d "pcbRouter" ]; then
            echo "Not found, therefore nothing to clean.";
        else
            echo "Found, deleting."
            rm -fr pcbRouter
        fi

        if [ "$CLEAN_ONLY" = true ]; then
            exit 0
        fi
    fi

    echo -n "Building kicad pcb parsing utility. Checking for repository ... "
    ORIGIN=${GIT}${GIT_USER}/kicadParser
    response=$(curl -sL -I -o /dev/null -w "%{http_code}" "$ORIGIN")
    if [[ $response -eq 200 ]] || [ "$SKIP_REPOSITORY_CHECK" = true ]; then
        echo "Repository exists."
        if [ -d "KicadParser" ]; then
            echo "Found, cleaning"
            cd KicadParser
            make clean
                git pull $ORIGIN ${kicadParser_branch}
            #git submodule update --remote --recursive
        else
            echo "Not found, cloning."
            git clone --branch ${kicadParser_branch} ${ORIGIN} --recurse-submodules KicadParser
            cd KicadParser
        fi
        make -j$(nproc)
        cp -v build/kicadParser_test ../kicadParser
        cd ..
    else
        echo "Repository does not exist."
    fi

    echo -n "Building simulated annealing pcb placer. Checking for repository ... "
    ORIGIN=${GIT}${GIT_USER}/SA_PCB
    response=$(curl -sL -I -o /dev/null -w "%{http_code}" "$ORIGIN")
    if [[ $response -eq 200 ]] || [ "$SKIP_REPOSITORY_CHECK" = true ]; then
        echo "Repository exists."
        if [ -d "SA_PCB" ]; then
            echo "Found, cleaning"
            cd SA_PCB
            make clean
            git pull ${ORIGIN} ${SA_PCB_branch}
            #git submodule update --remote --recursive
        else
            echo "Not found, cloning."
            git clone --branch ${SA_PCB_branch} ${ORIGIN} --recurse-submodules
            cd SA_PCB
        fi
        make -j$(nproc)
        if [ "$RUN_PLACER_TESTS" = true ]; then
            make test_place_excl_power
            make test_place_incl_power
        fi

        #cp -v ./build/sa_placer_test ../bin/sa_placer
        cp -v ./build/sa_placer_test ../sa
        cd ..
    else
        echo "Repository does not exist."
    fi

    echo -n "Building pcbRouter binary. Checking for repository ... "
    ORIGIN=${GIT}${GIT_USER}/pcbRouter
    response=$(curl -sL -I -o /dev/null -w "%{http_code}" "$ORIGIN")
    if [[ $response -eq 200 ]] || [ "$SKIP_REPOSITORY_CHECK" = true ]; then
        echo "Repository exists."
        if [ -d "pcbRouter" ]; then
            echo "Found, cleaning"
            cd pcbRouter
            make clean
                git pull ${ORIGIN} ${pcbRouter_branch}
            #git submodule update --remote --recursive
        else
            echo "Not found, cloning."
            git clone --branch ${pcbRouter_branch} ${ORIGIN} --recurse-submodules
            cd pcbRouter
        fi
        make -j$(nproc)
        if [ "$RUN_ROUTER_TESTS" = true ]; then
            make test_route_excl_power
            make test_route_incl_power
        fi

        cp -v build/pcbRouter_test ../pcb_router
        cd ..
    else
        echo "Repository does not exist."
    fi

    cd ..
}

print_help() {
    echo "Usage: ./setup_dev.sh [options]"
    echo "Options:"
    echo "  --cpu_only                  installs the cpu only version of pyTorch."
    echo "  --update_utility_binaries   cleans the git repositories then clones, builds and tests the place and route binaries."
    echo "  --skip-repository-check     skips existance checks when cloning dependent repositories for place and route tools."
    echo "  --help                      print this help and exit."
    print_help_update_utility
}

# --- End of functions ---

# --- Main script execution ---

printf "\n"
printf "  **** Luke Vassallo M.Sc - RL_PCB Environment Setup Script\n"
printf "   *** Program to setup the environment for RL_PCB and baseline place and route tools.\n"
printf "\033[32m"       # Green text color
printf "       RL_PCB is an end-to-end Reinforcement Learning PCB placement methodology.\n"
printf "\033[0m"        # Black text color
printf "    ** Last modification time %s\n" $date
printf "\n"
sleep 3

# Parse main script arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cpu_only)
            CPU_ONLY=true
            shift
            ;;
        --update_utility_binaries)
            UPDATE_UTILITY_BINARIES=true
            shift
            ;;
        --skip-repository-check)
            SKIP_REPOSITORY_CHECK=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            # Unknown option
            echo "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done


echo "--- Step 1: Installing system dependencies ---"
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    libboost-dev \
    libboost-filesystem-dev \
    python3.10 \
    python3.10-venv \
    python3-virtualenv
echo "--- System dependencies installation complete ---"
echo

# Source setup.sh to export RL_PCB and other environment variables
source setup.sh

if [ "$UPDATE_UTILITY_BINARIES" == true ]; then
    echo "--- Updating utility binaries ---"
	update_utility_binaries --clean_before_build --run_placer_tests --run_router_tests
    echo "--- Utility binaries updated ---"
    exit 0
fi

if [ ! -d "bin" ]; then
    echo "--- Installing KiCad PCB parsing utility and PCB place and route tools ---"
    update_utility_binaries --run_placer_tests --run_router_tests
    echo "--- Tool installation complete ---"
fi

echo
echo "--- Step 2: Setting up Python virtual environment ---"
if [ ! -d "venv" ]; then
	echo "Creating virtual environment..."
	python3.10 -m venv venv
else
	echo "Virtual environment 'venv' already exists."
fi
source venv/bin/activate
echo "Virtual environment activated."
echo

echo "--- Step 3: Installing Python packages ---"
echo "Upgrading pip and setuptools..."
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install --upgrade setuptools==65.5.0 -i https://mirrors.aliyun.com/pypi/simple/

echo "Installing packages from requirements.txt..."
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

echo "Installing PyTorch..."
if [ "$CPU_ONLY" == true ]; then
	python -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu -i https://mirrors.aliyun.com/pypi/simple/
else
    # Assuming CUDA 12.1 as per setup.sh, can be made more robust
	python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -i https://mirrors.aliyun.com/pypi/simple/
fi
echo "PyTorch installation complete."
echo

echo "Installing local libraries..."
python -m pip install ${RL_PCB}/lib/pcb_netlist_graph-0.0.1-py3-none-any.whl
python -m pip install ${RL_PCB}/lib/pcb_file_io-0.0.1-py3-none-any.whl
echo "Local libraries installation complete."
echo

echo "--- Step 4: Verifying installation ---"
if [ -f "${RL_PCB}/tests/00_verify_machine_setup/test_setup.py" ]; then
    python "${RL_PCB}/tests/00_verify_machine_setup/test_setup.py"
else
    echo "Verification script not found at ${RL_PCB}/tests/00_verify_machine_setup/test_setup.py"
fi
echo "--- Environment setup finished ---"
echo
echo "To activate the environment in your shell, run:"
echo "source venv/bin/activate" 