/*
 * optimal.hpp
 *
 *  Created on: Jul 26, 2022
 *      Author: luke
 */

#ifndef INCLUDE_OPTIMAL_HPP_
#define INCLUDE_OPTIMAL_HPP_

#include <iostream>
#include <sstream>
#include <string>
#include <limits>
#include <vector>

class optimal
{
	int id;						//! The id of the node the following optimal values correspond to
	std::string name;			//! The name of the node the following optimal values correspond to

	double euclidean_distance;	//! best known euclidean distance
	double hpwl;				//! best known half-perimeter wirelength

public:

	optimal(void);

	int8_t create_from_string( std::string s );

	int8_t format_string( std::string& line );

	int get_id() { return id; }
	int set_id(int id) { this->id = id; return 0; }

	std::string get_name() { return name; }
	int set_name(std::string name) { this->name = name; return 0; }

	double get_euclidean_distance(void) { return euclidean_distance; }
	int set_euclidean_distance(double euclidean_distance) { this->euclidean_distance = euclidean_distance; return 0; }

	double get_hpwl( void ) { return hpwl; }
	int set_hpwl(double hpwl) { this->hpwl = hpwl; return 0; }

};

#endif /* INCLUDE_OPTIMAL_HPP_ */
