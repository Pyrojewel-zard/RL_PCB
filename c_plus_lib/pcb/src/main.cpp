/*
 * main.cpp
 *
 *  Created on: Jan 15, 2022
 *      Author: luke
 */

#include <iostream>
#include <ctime>

#include "pcb.hpp"

int test_kicad_parser( void );

int main( void )
{
	time_t seconds_since_1970;

	seconds_since_1970 = time(0);
	// time(0) returns the seconds elapsed since 1970. ctime formats that result into a string,

	std::cout << "Program started " << ctime(&seconds_since_1970);

	PCB::build_info();

	test_kicad_parser();

	// time(0) returns the seconds elapsed since 1970. ctime formats that result into a string,
	seconds_since_1970 = time(0);
	std::cout << "Program terminated " << ctime(&seconds_since_1970);

	return 0;
}

int test_kicad_parser( void )
{
	pcb p;
	std::vector<pcb*> p_vec;

	std::cout << "Entered function '" << __FUNCTION__ << "'" << std::endl << std::endl;

	std::string nodes_file = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.nodes";
	std::string edges_file = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.edges";
	std::string board_file = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.board";
	std::string filename = "./test/kicad_parser/output/bistable_oscillator_with_555_timer_and_ldo";
	p.write_pcb_file_from_individual_files(filename, nodes_file, edges_file, board_file,true);

	std::cout << std::endl;

	filename = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo_append.pcb";
	p.append_pcb_file_from_individual_files(filename, nodes_file, edges_file, board_file,false);

	filename = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.pcb";
	read_pcb_file( filename, p_vec );

	std::cout << "Size of p_vec is " << p_vec.size() << std::endl;

	p_vec[0]->print_graph(true);

	// TODO: delete pcbs ?

	std::cout << std::endl << "Exiting function '" << __FUNCTION__ << "'" << std::endl;

	return 0;
}


