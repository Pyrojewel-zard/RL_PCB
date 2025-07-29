/*
 * board.hpp
 *
 *  Created on: Jan 5, 2022
 *      Author: luke
 */

#ifndef INCLUDES_BOARD_HPP_
#define INCLUDES_BOARD_HPP_

#include <iostream>
#include <iomanip>	// Required for std::setprecision
#include <fstream>
#include <string>
#include <sstream>
#include <vector>

class board
{
private:
	double bb_min_x;
	double bb_min_y;
	double bb_max_x;
	double bb_max_y;

	std::string board_name;
	uint32_t board_id;
	std::string kicad_pcb_file;		// If empty means that the graph is generated.

public:

	//! Default constructor. Initializes all variables to zero.
	board();

	double get_bb_min_x() { return bb_min_x; }
	double get_bb_min_y() { return bb_min_y; }
	double get_bb_max_x() { return bb_max_x; }
	double get_bb_max_y() { return bb_max_y; }

	void set_bb_min_x(double val) { bb_min_x = val; }
	void set_bb_min_y(double val) { bb_min_y = val; }
	void set_bb_max_x(double val) { bb_max_x = val; }
	void set_bb_max_y(double val) { bb_max_y = val; }

	//! Returns 0 on success. This function is always successful.
	//! board_size will be populated with the width ( x ) and height ( y ), specifically in that order.
	int get_board_size( std::pair<double, double> &board_size );

	//! Parses a line of text and update instance parameters with it's contents.
	//! Returns 0 on success and -1 otherwise (i.e. if parsing fails).
	int process_line(std::string &line);

	//! Writes object to file. That is creates .board file.
	int write_to_file(std::string filename);

	//! prints board information to console
	void print ( void );

	//! returns the width of the board
	double get_width( void ) { return abs(bb_max_x - bb_min_x); }

	//! returns the height of the board
	double get_height( void ) { return abs(bb_max_y - bb_min_y); }
};

//! Processes a generation 1 board file, that is a simple csv file without any headers.
int process_board_file( std::string board_file, board &b );
int get_fields(std::string &s, std::vector<std::string> &v);


#endif /* INCLUDES_BOARD_HPP_ */
