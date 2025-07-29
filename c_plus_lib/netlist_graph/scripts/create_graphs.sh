#!/bin/bash
ver="v0.0.1"
date="2021/12/07"

printf "  **** WinCorp create_graphs.sh\n"
printf "   *** Automated script for generating\n"
printf "       graphviz graphs.\n"
printf "    ** SW Build %s %s\n" $ver $date
printf "\n\n"
sleep 1



for var in "$@"
do
	file_name=${var%.*}
	echo -n "Compiling $file_name ... "	# -n option supresses the default newline character
	dot -Tpng $file_name.gv -o $file_name.png
	
	if [[ $? == "0" ]]
	then
		echo "OK"
	else
		echo "Failed"
	fi
done	


# v0.0.1 - Initial Release 
# Iterates through the input lists and generates the associated .png graph from graphviz .gv file.
