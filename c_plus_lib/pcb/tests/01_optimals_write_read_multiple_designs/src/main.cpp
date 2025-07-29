/*
 * main.cpp
 *
 *  Created on: Jul 28, 2022
 *      Author: luke
 */

#include "pcb.hpp"
#include "graph.hpp"
#include "optimal.hpp"
#include <stdlib.h>     // rand, srand
#include <vector>

int main(void)
{
    std::string input_file = "./input_files/boards.pcb";
    std::string output_file_create = "./output_files/boards.pcb";
    std::string output_file_append = "./output_files/boards_append.pcb";

    std::vector<pcb*> p_vec;
    std::vector<int> pcb_ids;
    
    srand(3142);
    
	PCB::build_info();
    
    GRAPH::build_info();
    
    // Read pcb file into vector
    read_pcb_file(input_file, p_vec);
    
    // Print all pcb_ids
    pcb_ids.clear();
	for ( auto *p : p_vec ) { pcb_ids.push_back( p->get_id() ); }
	std::cout << "Available pcb ids are : ";
	for ( auto pid : pcb_ids ) { std::cout << pid << ", "; }
	std::cout << std::endl;
    
    // For all pcb designs load and print all nodes.    
    for (auto *p : p_vec)
	{
        // p->get_graph(grph);      // Returns object
        graph& grph = p->get_graph();      // Returns handle to graph
        //nodes = grph.get_nodes();
		//p->get_board(brd);
        std::vector<node>& nodes = grph.get_nodes();    // Returns handle to node
    
        for (auto &n : nodes)
        {
            std::cout << n.get_id() << ", " << n.get_name() << std::endl;
            std::cout << n.get_opt_id() << ", " << n.get_opt_name() << ", " << n.get_opt_euclidean_distance() << ", " << n.get_opt_hpwl() << std::endl;
            n.set_opt_euclidean_distance(rand() % 1000); 
            n.set_opt_hpwl(rand() % 1000); 
        }
        
        std::cout << std::endl;
        
        for (auto n : nodes)
        {
            std::cout << n.get_id() << ", " << n.get_name() << std::endl;
            std::cout << n.get_opt_id() << ", " << n.get_opt_name() << ", " << n.get_opt_euclidean_distance() << ", " << n.get_opt_hpwl() << std::endl;
        }   
        
        std::cout << std::endl;
        
    }

    write_pcb_file(output_file_append, p_vec, true);       // append = true
    write_pcb_file(output_file_create, p_vec, false);      // append = false => overwrite/create
    
	return 0;
}
