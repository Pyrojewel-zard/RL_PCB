/*
 * node.hpp
 *
 *  Created on: Dec 22, 2021
 *      Author: luke
 */

#ifndef INCLUDES_NODE_HPP_
#define INCLUDES_NODE_HPP_

#include <iostream>
#include <vector>

#include <optimal.hpp>
#include "utils.hpp"

class node
{
	int id;
	std::string name;
	double size_x;
	double size_y;

	double pos_x;
	double pos_y;
	double orientation;
	int layer;
	bool isPlaced;

	int pins;
	int pins_smd;
	int pins_th;

	int type;

	std::vector<std::pair<int,int>> neighbors;	// neighbor instance id, connections to neighbor
	optimal opt;

public:

	node(void);

	int8_t create_from_string_short( std::string s);
	int8_t create_from_string_long( std::string s);
	int get_id() { return id; }
	std::string get_name() { return name; }

	std::pair<double,double> get_size()
	{
		std::pair<double, double> p;
		p.first = size_x; p.second=size_y;
		return p;
	}

	int set_size( std::pair<double, double> &size) { size_x = size.first; size_y = size.second; return 0; }

	std::pair<double,double> get_pos()
	{
		std::pair<double, double> p;
		p.first = pos_x; p.second=pos_y;
		return p;
	}

	int get_layer ( void ) { return layer; }
	int get_type( void ) { return type; }
	int get_pin_count( void ) { return pins; }
	int get_smd_pin_count( void ) { return pins_smd; }
	int get_th_pin_count( void ) { return pins_th; }
	int get_isPlaced() { return isPlaced; }
	int set_isPlaced() { isPlaced = true; return 0; }
	int unset_isPlaced() { isPlaced = false; return 0; }

	int set_pos( std::pair<double, double> p ) { pos_x = p.first; pos_y = p.second; return 0; }

	void set_orientation( double orient ) { while (orient >=  360) orient -= 360; orientation = orient; }
	double get_orientation() { return orientation; }

	int set_neighbors( std::vector<std::pair<int,int>> n) { neighbors = n; return 0; }
	int get_neighbors( std::vector<std::pair<int,int>> &n) { n = neighbors; return 0; }

	//! Returns the grid bounding box rounded up to the nearest grid_resolution
	//! Always returns 0
	int get_inst_bb_coords(int &xmin, int &xmax, int &ymin, int &ymax, double grid_resolution);

	//! Return the centre coordinate and size in grid spaces.
	//! In case the shape has an even size the the center is biased to the left down
	//! Always returns 0
	int get_inst_bb_centre_size(int &xc, int &yc, int &x, int &y, double grid_resolution);

	//! prints node to console. The result is formatted in short or long form and is identical to that of the .nodes file.
	void print_to_console( bool format );

	//! Prints node id, name, size, position and orientation, and placed
	void print( bool print_csv );

	void set_id(int id) { this->id = id; opt.set_id(id); }
	void set_name(std::string name) { this->name = name; opt.set_name(name); }
	void set_layer( int layer ) { this->layer = layer; }
	void set_isPlaced (bool isPlaced ) { this->isPlaced = isPlaced; }
	void set_pins (int pins) { this->pins = pins; }
	void set_pins_smd (int pins_smd) { this->pins_smd = pins_smd; }
	void set_pins_th (int pins_th) { this->pins_th = pins_th; }
	void set_type( int type ) { this->type = type; }

	//! formats node information in a long string. Returns formatted string.
	//! If information is missing it is simply omitted but placeholder is retained.
	int format_string_long( std::string& line );

	//! returns the area of the current node.
	double get_area();

	//! opt getter and setter methods
	int set_opt_id(int id) { return opt.set_id(id); }
	int set_opt_name(std::string name) { return opt.set_name(name); }
	int set_opt_euclidean_distance(double euclidean_distance) { return opt.set_euclidean_distance(euclidean_distance); }
	int set_opt_hpwl(double hpwl) { return opt.set_hpwl(hpwl); }

	int get_opt_id(void) { return opt.get_id(); }
	std::string get_opt_name(void) { return opt.get_name(); }
	double get_opt_euclidean_distance(void) { return opt.get_euclidean_distance(); }
	double get_opt_hpwl(void) { return opt.get_hpwl(); }

	int get_opt_formatted_string( std::string &s ) { return opt.format_string(s); }
};



#endif /* INCLUDES_NODE_HPP_ */
