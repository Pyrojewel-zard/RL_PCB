/*
 * main.cpp
 *
 *  Created on: Dec 22, 2021
 *      Author: luke
 */
#include <boost/filesystem.hpp>

#include <string.h>

#include "board.hpp"
#include "edge.hpp"
#include "graph.hpp"
#include "node.hpp"

#ifndef LEGACY_ARGPARSE
#include "argparse.hpp"
#endif

#define FILE_FORMAT_LONG 1

// Hyper parameters
#define MAX_NEIGHBORS 2		// Maxmimum number of neighbours to used as input to the NN.

#ifdef LEGACY_ARGPARSE
#define NUM_ARGS_EXPECTED (int) 4
int find_file_with_ext( std::string &s, std::string ext, int argc, char **argv )
{
	int status = -1;
	std::string tmp;
	for (int i=0; i < argc; i++)
	{
		tmp = argv[i];
		size_t found = tmp.find(ext, 0);
		if (found != std::string::npos)
		{
			s = tmp;
			return 0;
		}
	}

	return status;
}
#endif

int main( int argc, char **argv )
{
	std::string nodes_file, edges_file, board_file;
	int status = -1;
	std::cout << "Program started." << std::endl;

	GRAPH::build_info();
    std::cout << std::endl;

	std::cout << "Parsing inline arguments ... ";
#ifdef LEGACY_ARGPARSE
	//if (argc != NUM_ARGS_EXPECTED)
	if (argc < NUM_ARGS_EXPECTED)
	{
		std::cout << "Failed." << std::endl;
		std::cout << "Expected " << NUM_ARGS_EXPECTED << " but got " << argc << "." << std::endl;
		return -1;
	}
	else
	{
		if (find_file_with_ext(nodes_file, ".nodes", argc, argv) != 0)
		{
			std::cout << "Failed." << std::endl;
			std::cout << "Failed to find '.nodes' file." << std::endl;
		}

		if (find_file_with_ext(edges_file, ".edges", argc, argv) != 0)
		{
			std::cout << "Failed." << std::endl;
			std::cout << "Failed to find '.edges' file." << std::endl;
		}

		if (find_file_with_ext(board_file, ".board", argc, argv) != 0)
		{
			std::cout << "Failed." << std::endl;
			std::cout << "Failed to find '.board' file." << std::endl;
		}
	}
#else
	struct arguments args;
	status = parse_args(argc, argv, &args);
	if (status == 0)
	{
		nodes_file = args.nodes;
		edges_file = args.edges;
		board_file = args.board;
	}
	else
	{
		std::cout << "Failed" << std::endl;
		return status;
	}
#endif

	std::cout << "OK" << std::endl;
	std::cout << "Nodes file : " << nodes_file << std::endl;
	std::cout << "Edges file : " << edges_file << std::endl;
	std::cout << "Board file : " << board_file << std::endl;
    std::cout << std::endl;


	graph g;
	board b;
	process_nodes_file(nodes_file, FILE_FORMAT_LONG, &g );
	process_edges_file(edges_file, FILE_FORMAT_LONG, &g );
	process_board_file(board_file, b);
    std::cout << std::endl;

	std::pair<double, double> board_size;
	b.get_board_size(board_size);
	std::cout << "Board size (W x L) : " << board_size.first << "mm x " << board_size.second << "mm" << std::endl;
	std::cout << std::endl; 	// newline for visual segmentation.

	g.statistics();
	g.node_statistics();
	g.embed_neighbour_nodes();
	g.set_component_origin_to_zero(b);
	g.set_original_component_origin(b);

	std::cout << "Creating directory 'generated'" << std::endl;
	boost::filesystem::create_directory("generated");

	if (args.generate_gml)
	{
	std::cout << "Creating .gml partial graphs." << std::endl;
	g.partial_graph_gml("generated/graph.gml", 0, true);
	g.partial_graph_gml("generated/graph_ground.gml", 1, true);
	g.partial_graph_gml("generated/graph_+3v3.gml", 2, true);
	g.partial_graph_gml("generated/graph_+5v0.gml", 3, true);
	std::cout << "Done generating .gml partial graphs." << std::endl;
	}

	if (args.generate_graphviz)
	{

//	g.normalize();

		// Graphviz plots
		std::set<int> net_ids = g.get_set_net_ids();
		for ( auto nid : net_ids)
		{
			g.net_graphviz("", nid, COMPONENT);
			std::cout << std::endl;
		}

		for(int i=0; i< 3; i++)
		{
			g.partial_graph("", i, true);
		}

		for (int i=0; i<g.get_number_of_nodes(); i++)
		{
			// power_rail = 0 => connectivity
			// power_rail = 1 => GND ( fully connected )
			// power_rail = 2 => +3V3 ( fully connected )
			g.instance_graphviz("", i, 0);
			g.instance_pads_graphviz("", i, 0);
		}
	}
//
//	system("./create_graphs.sh *.gv");


	node inst;	// DEBUG
	std::vector<std::pair<int,int>> n;
	std::vector<std::tuple<int, double, double, int, double, double>> pads_avg_pos; // DEBUG
	std::vector<double> feature_vector;
	int mn = 0; // DEBUG
	n = g.get_nodes_connectivity_list( 0 );	// Return number of connections for each instance sorted in descending order.

	for (auto i : n)
	{
		// >>>> Test feature vector <<<<<
		g.get_feature_vector(i.first, feature_vector, MAX_NEIGHBORS );
		std::cout << "Size of feature vector is : " << feature_vector.size() << "." << std::endl;
		g.print_feature_vector(feature_vector);
		g.update(i.first, std::make_pair(6.9, 6.9));
		std::cout << "Done : " << (g.isDone() ? "Yes" : "No") << std::endl;

		g.get_node_by_id(i.first, inst);
		std::cout << "============================================" << std::endl;	// DEBUG
		std::cout << "Current node : " << inst.get_name() << "(" << inst.get_id() << ")" << std::endl;	// DEBUG
		std::cout << "  Size          : (" << inst.get_size().first << "," << inst.get_size().second << ")" << std::endl;	// DEBUG
		std::cout << "  Type          : " << inst.get_type() << std::endl;	// DEBUG
		std::cout << "  Pins          : " << inst.get_pin_count() << std::endl;	// DEBUG

		g.get_average_pad_position( i.first, pads_avg_pos );
		std::cout << std::endl;	// DEBUG

		mn = 0;
		for (auto j : pads_avg_pos)
		{
			if (++mn > MAX_NEIGHBORS) break;
			g.get_node_by_id(std::get<3>(j), inst);
			std::cout << "Neighbor node : " << inst.get_name() << "(" << inst.get_id() << ")" << std::endl;	// DEBUG

			if (i.first != std::get<0>(j)) std::cout << "Expected parent id " << i.first << " by got instead " << std::get<0>(j) << "." << std::endl;

			std::cout << "  Size          : (" << inst.get_size().first << "," << inst.get_size().second << ")" << std::endl;	// DEBUG
			std::cout << "  Position      : (" 	<< (inst.get_isPlaced() ? inst.get_pos().first : 0.0) << ","					// DEBUG
												<< (inst.get_isPlaced() ? inst.get_pos().second : 0.0) << ")" << std::endl;		// DEBUG
			std::cout << "  Type          : " << inst.get_type() << std::endl;	// DEBUG
			std::cout << "  Pins          : " << inst.get_pin_count() << std::endl;	// DEBUG

			std::cout << "  Parent id     : " << std::get<0>(j);	// DEBUG
			std::cout << " (" << std::get<1>(j) << "," << std::get<2>(j) << ")" << std::endl;	// DEBUG

			std::cout << "  Neighbor id   : " << std::get<3>(j);	// DEBUG
			std::cout << " (" << std::get<4>(j) << "," << std::get<5>(j) << ")" << std::endl;	// DEBUG
			std::cout << std::endl;	// DEBUG
		}

		if (mn < MAX_NEIGHBORS)
		{
			do
			{
				std::cout << "Neighbor node : NULL(-1)" << std::endl;	// DEBUG

				std::cout << "  Size          : (0.0,0.0)" << std::endl;	// DEBUG
				std::cout << "  Position      : (0.0,0.0)" << std::endl;	// DEBUG
				std::cout << "  Type          : -1" << std::endl;	// DEBUG
				std::cout << "  Pins          : 0" << std::endl;	// DEBUG

				std::cout << "  Parent id     : -1" ;	// DEBUG
				std::cout << " (0.0,0.0)" << std::endl;	// DEBUG

				std::cout << "  Neighbor id   : -1" ;	// DEBUG
				std::cout << " (0.0,0.0)" << std::endl;	// DEBUG
				std::cout << std::endl;	// DEBUG
			} while (++mn < MAX_NEIGHBORS);
		}

	}

//		std::cout << "============================================" << std::endl;	// DEBUG
// 		std::cout << std::endl;	// DEBUG

	std::cout << std::endl;			// Newline for visual segmentation
	std::cout << "Resetting graph ... ";
	if (g.reset() == 0) std::cout << "OK" << std::endl;
	else std::cout << "Failed" << std::endl;
	std::cout << "Done : " << (g.isDone() ? "Yes" : "No") << std::endl;

	std::set<int> nets;
	std::set<int>::iterator iter;

	std::cout << "Getting net id for instance with id 12 .. " << std::endl;
	g.get_nets_associated_with_instance(12, nets, 0);	// 0 -> connectivity only.
	iter = nets.begin();
	for (uint32_t i=0; i < nets.size(); i++) { std::cout << "Net : " << *iter << std::endl; std::advance(iter, 1); }

    std::cout << std::endl;
	std::cout << "Program terminated." << std::endl;

	return 0;
}


