/*
 * graph.hpp
 *
 *  Created on: Dec 22, 2021
 *      Author: luke
 */

#ifndef INCLUDES_GRAPH_HPP_
#define INCLUDES_GRAPH_HPP_

#include<algorithm>
#include <limits>	//In C++, the preferred version is usually std::numeric_limits<double>::max() (for which you #include <limits>).
#include <iostream>
#include <fstream>
#include <sstream>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include "board.hpp"
#include "edge.hpp"
#include "node.hpp"
#include "optimal.hpp"

enum ABSTRACTION
{
	COMPONENT = 0,
	PADD = 1
};

enum FILE_FORMAT
{
	SHORT=0,
	LONG
};

class graph
{
	std::vector<node> _V;	// Must remain untouch after populating from .nodes file
	std::vector<node> V;
	std::vector<edge> E;

	std::string graph_name;
	uint32_t graph_id;
	std::string kicad_pcb_file;		// If empty means that the graph is generated.
	double hpwl;					// If computed should have the negative sum of the hpwl of all nets. Otherwise 0.

public:

	//! Default constructor. Initializes graph with default values.
	graph(void);

	//! Constructor. Initializes graph private variables with with node(_V, V) and edge(E) values.
	graph(std::vector<node> &n, std::vector<edge> &e);

	//! Constructor. Initializes graph private variables with with node(_V,V) values only.
	graph(std::vector<node> &n);

	//! Constructor. Initializes graph private variables with with edge(E) values only.
	graph(std::vector<edge> &e);

	void set_graph_name( std::string graph_name) { this->graph_name = graph_name; }

    //! Update the private member variable kicad_pcb_file with a new .kicad_pcb filename
	void set_kicad_pcb_file ( std::string kicad_pcb_file ) { this->kicad_pcb_file = kicad_pcb_file; }

	//! Return .kicad_pcb filename as a string
    std::string get_kicad_pcb_file ( void ) { return kicad_pcb_file; }

	int8_t add_node_from_string_short( std::string s );
	int8_t add_node_from_string_long( std::string s );

	int8_t add_edge_from_string_short( std::string s );
	int8_t add_edge_from_string_long( std::string s );

	//! Traverses the list of nodes and returns the node name matching with id passed as argument.
	//! Returns an empty list it nothing is found.
	std::string get_node_name_by_id ( int id );

	//! Returns a set of ids of all the available nets
	std::set<int> get_set_net_ids ();

	int statistics( void );

	//! Returns a vectors with instanceid-neighbour connection pairs sorted in descending order
	//! Accept a power rail argument to filter between nets
	std::vector<std::pair<int,int>> get_nodes_connectivity_list(int power_rail);

	//! Returns a vectors with instanceid-areaa connection pairs sorted in descending order
	std::vector<std::pair<int,double>> get_nodes_area_list( void );

	//! Returns a vector with pairs of neighbour ids and associated connections in descending order. This is returned
	//! for a given instance id.
	std::vector<std::pair<int,int>> get_neighbor_nodes_connectivity_list( int id, int power_rail );

	int node_statistics( void );

	//! Embeds the vectors of neighbor id, connection pairs (sorted in descending order).
	int embed_neighbour_nodes( void );

	//! Returns a set of neighbor ids. By default considers only connectivity nets and ignores self loops.
	std::set<int> get_neighbor_node_ids( int id, int power_rail=0, bool ignore_self_loops=true );

	int get_number_of_nodes (void) { return V.size(); }

	int get_number_of_edges (void) { return E.size(); }

	//! Computes the average of the instance pad position and neighbor pad position
	//! returns a int to indicate success or failure.
	//! Contents are returned as a vector of tuples with instance (x,y) and neighbor (x,y)
	int get_average_pad_position( int id, std::vector<std::tuple<int, double, double, int, double, double>> &pads_avg_pos );

	//! Returns 0 if found, -1 otherwise. Node is stored in n.
	int get_node_by_id( int id, node &n );

	//! Returns a handle to the node. If not found an exception is thrown because NULL cannot be returned when having a reference return type.
	node& get_node_by_id( int id );

	//! Returns a list of connections between nodes (components) for the power_rail passed as an argument.
	//! Duplicate edges are ignored
	std::set<std::pair<int,int>> get_edges_by_power_rail( int power_rail, ABSTRACTION type );

	//! Returns a list of connections between nodes (components) for the net_id passed as an argument.
	//! Duplicate edges (e.g. three pins shorted) are represented with a single edge.
	std::set<std::pair<int,int>> get_edges_by_net_id( int net_id, ABSTRACTION type );

	//! Returns a list of connections between nodes (components) involving the instance with instance id passed as an argument.
	//! Includes duplicate edges ( duplicate edges represent connections between instances' pads )
	std::set<std::pair<int,int>> get_edges_by_instance_id( int i_id, int power_rail );

	std::vector<edge> get_all_edges_by_instance_id( int i_id, int power_rail );

	//! Plots a subset of the graph according to the value of power_rail. power_rail = 0 represents general connectivity, power rails otherwise.
	//! If unique is set to true, the graph is generated with unique edges between nodes. In other words if multiple connections are present
	//! between edges, they are represented as one.
	int8_t partial_graph( std::string fileName, int power_rail, bool unique);

	//! Plot graph for a single net within the netlist
	//! Duplicate edges (e.g. three pins shorted) are represented with a single edge.
	int8_t net_graphviz( std::string fileName, int net_id, ABSTRACTION type );

	//! Plot graph capturing a single instance within the netlishh
	//! Duplicate edges (e.g. three pins shorted) are represented with a single edge.
	int8_t instance_graphviz( std::string fileName, int i_id, int power_rail );

	//! Plot graph capturing all of an instances' pads within the netlist
	int8_t instance_pads_graphviz( std::string fileName, int i_id, int power_rail );

	//! Plots a subset of the graph according to the value of power_rail. power_rail = 0 represents general connectivity, power rails otherwise.
	//! If unique is set to true, the graph is generated with unique edges between nodes. In other words if multiple connections are present
	//! between edges, they are represented as one.
	//! The file formatting is as expected for a gml graph.
	int8_t partial_graph_gml( std::string fileName, int power_rail, bool unique);

	//! Normalize graph
	int normalize( void );

	//! Returns a feature vector made up of the concatenation of current node, and the two most connected neighbor nodes.
	int get_feature_vector( int id, std::vector<double> &fv, int MAX_NEIGHBORS=0 );

	//! Returns a simplified feature vector made up of the concatenation of current node, and the two most connected neighbor nodes.
	//! replaces size with area, saving (1 + neighbors) input nodes
	//! removes parent and neighbor ids saving (2*neighbors) input nodes
	//! drop type, (1 + neighbors) input nodes
	int get_simplified_feature_vector( int id, std::vector<double> &fv, int MAX_NEIGHBORS=0 );

	//! Prints a feature vector in human readable form.
	int print_feature_vector( std::vector<double> &fv );

	//! Prints a simplified feature vector in human readable form.
	int print_simplified_feature_vector( std::vector<double> &fv );

	//! Normalizes the feature feature vector by:
	//! a) dividing the component size by the largest component size
	//! b) pin count by the largest amount of pins
	//! c) position by grid size. ( grid size supplied as an argument )
	int normalize_feature_vector( std::vector<double> &fv, double grd_x, double grd_y);

	//! Normalizes the simplified feature vector by:
	//! a) dividing the area by the largest component area
	//! b) pin count by the largest amount of pins
	//! c) position by grid size. ( grid size supplied as an argument )
	int normalize_simplified_feature_vector( std::vector<double> &fv, double grd_x, double grd_y);

	//! Find the largest component (by area) and returns it x and y dimensions
	//! used to normalize the feature vector (at the time of writing the simplified_feature_vector)
	int get_dimensions_of_largest_component(double &x, double &y);

	//! Returns the largest x size value in the graph
	double get_largest_x_size( void );

	//! Returns the largest y size value in the graph
	double get_largest_y_size( void );

	//! Finds the comonent with the largest amount of pins and returns it's pin count.
	//! used to normalize the feature vector
	int get_largest_pin_count(int &pins);
	int get_largest_pin_count( void );


	//! Identifies the id of the next instance to place
	//! Returns a non-negative integer number as a valid instance id. If none are available for placement -1 is returned
	//! If an unknown ordering value is provided, the first unplaced node is returned.
	//! The following orderings are implemented: 'connection_density' and 'area'
	//! connection_density - Linearly traverses the list of instances (sorted in descending order by connectivity) and returns the first instance id that has an unset isPlaced field.
	//! area - traverses the list of instances (sorted in in descending order by area) and returns the first instance id that has an unset isPlaced field.
	int get_next_component_id_to_place( const std::string& ordering );

	//! Updates node's position and sets isPlaced to true.
	// TODO: Add orientation
	int update( int id, std::pair<double, double> pos );

	//! Resets the graph by setting E from _E
	//! _E contains the node information as parsed from the .nodes file.
	int reset( void );

	//! Returns 0 if there are still instances to be placed otherwise 1.
	//! Parses all the node vector polling the isPlaced field.
	int isDone( void );

	int _V_set( void ) { _V = V; return 0; }

	//! Subtracts bb_min_x and bb_min_y from all component_positions
	int set_component_origin_to_zero( board &b );

	//! Adds bb_min_x and bb_min_y to all component_positions
	int reset_component_origin( board &b );

	//! Reverses the operation done by set_component_origin_to_zero( board &b )
	//! Adds bb_min_x and bb_min_y to all component_positions
	int set_original_component_origin( board &b );

	//! Returns a set of nets that connect to the instance's pads.
	//! Returns 0. Always successful
	int get_nets_associated_with_instance( int id, std::set<int> &nets, int power_rail );

	//! Search the vector of edges with instance ids and net id. If preserve_order is set to true
	//! id a will be used to match against edge id_a and id_b will be used to match against id_b.
	//! Otherwise any edge with the two instances will be stored.
	//! Returns the number of edges found.
	int get_edges_with_net_and_inst_ids(int inst_id_a, int inst_id_b, int net_id, bool preserve_order, std::vector<edge> &edges);

	//! Computes the half perimeter wirelength (HPWL) of a single instance.
	//! Enumerates all pads of the netlist between the instance an its neighbors then accumulates the HPWL of each net.
	double calc_hpwl_of_inst(int id);

	//! If instance is not placed, it updates the center coordinates but does not set the isPlaced flag.
	//! Returns 0 is successful, -1 if instance is already placed.
	int place_set_centroid(int id, double cx, double cy);

	//! If instance is not placed, it updates the orientation but does not set the isPlaced flag.
	//! Returns 0 is successful, -1 if instance is already placed.
	int place_set_orientation(int id, double orientation);

	//! If instance is not placed, it swaps its size (i.e. length with breadth) but does not set the isPlaced flag.
	//! Returns 0 is successful, -1 if instance is already placed.
	int place_swap_size(int id);

	//! Sets the isPlaced flag.
	//! Returns 0 is successful, -1 if instance is already placed.
	int place_confirm(int id);

	//! Returns the full graph hpwl without ignoring any components or net types (e.g. power)
	double calc_full_hpwl(void);

	//! Returns HPWL of the whole graph. unplaced components are ignored by default.
	//! Connectivity nets only!
	double calc_hpwl( bool do_not_ignore_unplaced=false );

	//! Returns HPWL of the whole graph ignore all nets (if found) in vector nets_to_ignore
	//! All nets, potentially
	double calc_hpwl( std::vector<std::string>& nets_to_ignore );

	// Returns the id of the net having name equal to net_name
	// If not found returns -1
	int get_net_id_from_name(std::string& net_name);

	//! Enumerates all net ids with the associated power_rail.
	int get_all_nets( std::set<int> &nets, int power_rail);

	//! Returns the name of the net corresponding to net_id.
	int get_net_name( int net_id, std::string &net_name );

	//! Returns HPWL of the net with net_id. unplaced components are ignored by default.
	//! The optional argument 'do_not_ignore_unplaced' will compute the HPWL over all the components. Use with caution.
	//! Returns HPWL if successful -1 otherwise.
	double calc_hpwl_of_net( int net_id, bool do_not_ignore_unplaced=false );

	//! Zero's out the position of all unplaced instances.
	//! Returns zero on success. This function is always successfull
	int zero_unplaced_inst_pos( void );

	//! Prints graph information, followed by node and edge information.
	void print( bool print_csv );

	//! Write nodes to a .nodes file.
	int write_nodes_to_file(std::string filename, FILE_FORMAT format);

	//! Write edges to a .edges file.
	int write_edges_to_file(std::string filename, FILE_FORMAT format);

	//! Write optimals to a .optimals file.
	int write_optimals_to_file(std::string filename);

	int update_original_nodes_with_current_optimals( void );

	//! Update a node optimals value. This function uses the data in the line to search the node list and update the according node's optimal object.
	//! This function returns 0 when successful (i.e. Corresponding node is upated with optimal information), -1 otherwise.
	int update_node_optimal(std::string line);

	//! Returns the node vector. V is the one that is worked upon and _V contains the original contents as processed from the kicad database file.
	std::vector<node>& get_nodes( void ) { return V; }
	//! Returns the original node vector. V is the one that is worked upon and _V contains the original contents as processed from the kicad database file.
	std::vector<node>& get_original_nodes( void ) { return _V; }
	//! Returns the edges vector.
	std::vector<edge>& get_edges( void ) { return E; }

	//! setter and getter functions for hpwl
	void set_hpwl( double hpwl ) { this->hpwl = hpwl; }
	double get_hpwl( void ) { return hpwl; }
	
    void update_hpwl( bool do_not_ignore_unplaced=false ) { this->hpwl = calc_hpwl(do_not_ignore_unplaced); }

	//! Returns the number of components that have been placed. (That is the number of componnet that have the isPlaced flag set.)
	int components_placed( void );
	//! Returns the number of components that have not yet been placed. (That is the number of componnet that do not have the isPlaced flag set.)
	int components_to_place( void );
	//! Returns the placement completion ( value in the range of 0 to 1 ).
	double graph_placement_completion( void ) { return ((double) components_placed() / (double) V.size()); }

	//! prints current graph state (The rationale for this member function was to test 1) components_placed 2) components_to_place and 3) graph_placement_completion through python)
	void print_graph_placement_status(void);

	//! Traverses the node list and returns the id of the first encountered node.
	//! Returns -1 if there are no unplaced nodes.
	//! WARNING: Use with caution as graph may be left in an unusable state and exhibit erratic behavior
	int find_unplaced_node( void );

	//! Removes node with associated node id = id
	//! Returns is on success, -1 if node is not found
	//! WARNING: Use with caution as graph may be left in an unusable state and exhibit erratic behavior
	int remove_node( int id );

	//! Traverses the edges list to find a net that is involved in the connecting node with id=id.
	//! Returns net_id (available only when loading data in long string format!) if a net is found otherwise 0.
	int find_edge_connecting_to_node(int id);

	//! Removes edges with associated net id = net_id
	//! Returns net_id on success, -1 if node is not found
	//! WARNING: Use with caution as graph may be left in an unusable state and exhibit erratic behavior
	int remove_edge( int net_id );

	//! Removes all edges with associated with node having id
	//! Return number of removed edges.
	//! WARNING: Use with caution as graph may be left in an unusable state and exhibit erratic behavior
	int remove_edges_associated_with_node( int id );

	//! Removes all unplaced nodes and associated edges. Returns true on success false otherwise. Method is always successful.
	//! WARNING: Use with caution as graph may be left in an unusable state and exhibit erratic behavior
	bool remove_unplaced_nodes_and_associated_edges( void );

	//! This function should be used after removing nodes from the graph.
	//! It re-orders the node id's and associated edges.
	//! Always returns 0.
	int reorder( void );

	//! Prints node, area pair information.
	void print_node_area_pairs( void );

	//! Returns the number of distinct components involved in net.
	int components_in_net(std::string net_name );

};

//! Processes a generation 1 nodes file, that is a simple csv file without any headers.
int process_nodes_file( std::string nodes_file, bool file_format, graph *g );
//! Processes a generation 1 edges file, that is a simple csv file wihtout any headers.
int process_edges_file( std::string edges_file, bool file_format, graph *g );

std::vector<std::pair<int,int>> tally_contents( std::vector<int> vec);
bool sortbysec(const std::pair<int,int> &a, const std::pair<int,int> &b);

namespace GRAPH
{
// version 0.0.1 - preliminary testing
const unsigned int VERSION_MAJOR = 0;
const unsigned int VERSION_MINOR = 1;
const unsigned int PATCH_NUMBER = 16;

//! Updates the argument reference variables with major, minor and patch numbers of the library.
//! These numbers are defined using the #define directive.
int get_library_version(int &maj, int &min, int &patch);

//! Updates the argument reference variable with timestamp corresponding to the library build time.
int get_build_time( std::string &s );

//! Update the argument reference variable with the cpp standard.
int get_cpp_standard ( std::string &s );

//! Prints the build information using infromation from get_library_version( ... ), get_build_time( ... ) and get_cpp_standard( ... ).
int build_info( void );

//! Returns the build information using infromation from get_library_version( ... ), get_build_time( ... ) and get_cpp_standard( ... ) as a string.
std::string build_info_as_string( void );

//! Returns the library version in the following format : 'v[MAJOR].[MINOR].[PATCH]'
std::string get_library_version();
}


#endif /* INCLUDES_GRAPH_HPP_ */
