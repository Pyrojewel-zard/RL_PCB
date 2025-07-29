/*
 * edge.hpp
 *
 *  Created on: Dec 22, 2021
 *      Author: luke
 */

#ifndef INCLUDES_EDGE_HPP_
#define INCLUDES_EDGE_HPP_

#include <iostream>
#include <vector>

class edge
{
	int a_id;					//! Refers to node (instance of a component)
	std::string a_name;			//! Refers to node name (instance name of a component)
	int a_pad_id;
	std::string a_pad_name;
	double a_size_x;
	double a_size_y;
	double a_pos_x;
	double a_pos_y;
	bool a_isPlaced;

	int b_id;
	std::string b_name;
	int b_pad_id;
	std::string b_pad_name;
	double b_size_x;
	double b_size_y;
	double b_pos_x;
	double b_pos_y;
	bool b_isPlaced;

	int net_id;
	std::string net_name;
	//int common_net_points;
	//int uncommon_net_points;

	int power_rail;

public:

	edge(void);

	int8_t create_from_string_short( std::string s );
	int8_t create_from_string_long( std::string s );
	int get_net_id() { return net_id; }
	std::string get_net_name() { return net_name; }
	int get_power_rail() { return power_rail; }

	//! returns the instance id of node passed as argument.
	//! node = 0 => a_id otherwise b_id
	int get_instance_id ( int node ) { return node ? b_id : a_id; }

	int get_instance_isPlaced (int node) { return node ? b_isPlaced : a_isPlaced; }

	//! returns the pad name of the associated node passed as argument.
	//! node = 0 => a_pad_name otherwise b_pad_name
	std::string get_pad_name ( int node ) { return node ? b_pad_name : a_pad_name; }

	//! returns the pad id of the associated node passed as argument.
	//! node = 0 => a_pad_id otherwise b_pad_id
	int get_pad_id ( int node ) { return node ? b_pad_id : a_pad_id; }

	//! returns a pair with the id of connected nodes. i.e (a_id, b_id
	std::pair<int,int> get_edge_connectivity()
	{
		std::pair<int,int> edge;
		edge.first = a_id;
		edge.second = b_id;

		return edge;
	}

	std::pair<double, double> get_size(int id);
	int set_size(int id, std::pair<double, double> p);

	std::pair<double, double> get_pos(int id);
	int set_pos(int id, std::pair<double, double> p);

	//! prints edge to console. The result is formatted in short or long form and is identical to that of the .edges file.
	void print_to_console( bool format );

	//! Prints edge information to standard output.
	int print( bool print_csv );

	void set_id(int node, int id) { if(node) this->b_id = id; else this->a_id = id; }
	void set_name(int node, std::string name) {  if(node) this->b_name = name; else this->a_name = name; }
	void set_pad_id(int node, int pid) { if(node) this->b_pad_id = pid; else this->a_pad_id = pid; }
	void set_pad_name(int node, std::string pname) {  if(node) this->b_pad_name = pname; else this->a_pad_name = pname; }
	void set_isPlaced (int node, bool isPlaced ) { if(node) this->b_isPlaced = isPlaced; else this->a_isPlaced = isPlaced; }
	void set_net_id(int net_id) { this->net_id = net_id; }
	void set_net_name(std::string &net_name) { this->net_name = net_name; }
	void set_power_rail(int power_rail) { this->power_rail = power_rail; }

	//! formats edge information in a long string. Returns formatted string.
	//! If information is missing it is simply omitted but placeholder is retained.
	int format_string_long( std::string& line );
};




#endif /* INCLUDES_EDGE_HPP_ */
