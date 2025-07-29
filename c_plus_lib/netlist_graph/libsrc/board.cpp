/*
 * board.cpp
 *
 *  Created on: Jan 5, 2022
 *      Author: luke
 */

#include "board.hpp"


board::board()
{
	bb_min_x = 0.0;
	bb_min_y = 0.0;
	bb_max_x = 0.0;
	bb_max_y = 0.0;


	board_name = "";
	board_id = -1;
	kicad_pcb_file = "";		// If empty means that the graph is generated.
}

int board::get_board_size( std::pair<double, double> &board_size )
{
	board_size.first = bb_max_x - bb_min_x;
	board_size.second = bb_max_y - bb_min_y;

	return 0;
}

int board::process_line(std::string &line)
{
	int status = 0;
	std::vector<std::string> fields;

	fields.clear();
	get_fields(line, fields);

	if (fields[0] == "bb_min_x") set_bb_min_x(stod(fields[1]));
	else if (fields[0] == "bb_min_y") set_bb_min_y(stod(fields[1]));
	else if (fields[0] == "bb_max_x") set_bb_max_x(stod(fields[1]));
	else if (fields[0] == "bb_max_y") set_bb_max_y(stod(fields[1]));
	else status = -1;

	return status;
}

int board::write_to_file(std::string filename)
{
	int status = -1;
	std::ofstream file;
	std::cout << "Attempting to open file '" << filename + ".board" << " ... ";
	file.open(filename + ".board", std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << std::fixed;
		file << std::setprecision(8);

		file << "bb_min_x," << bb_min_x << std::endl;
		file << "bb_min_y," << bb_min_y << std::endl;
		file << "bb_max_x," << bb_max_x << std::endl;
		file << "bb_max_y," << bb_max_y << std::endl;
		file.close();
		if (!file.is_open()) status = 0;
	}
	else
	{
		std::cout << "Failed to open file for writing." << std::endl;
	}
	return status;
}

void board::print ( void )
{
	std::cout << "bb_min_x," << bb_min_x << std::endl;
	std::cout << "bb_min_y," << bb_min_y << std::endl;
	std::cout << "bb_max_x," << bb_max_x << std::endl;
	std::cout << "bb_max_y," << bb_max_y << std::endl;
}



int process_board_file( std::string board_file, board &b )
{
	std::ifstream file;

	std::cout << "Opening '" << board_file << "' for parsing ... ";
	file.open(board_file, std::ios::in);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;
		std::string line;
		// getline returns a stream.
		// When used in a boolean context, the compiler converts it into a type that can be
		// used in the boolean context.
		while(std::getline(file, line))
		{
			if (b.process_line(line) != 0)
			{
				std::cout << "Failed to process board parameter. The contents of the line are '" << line << "'." << std::endl;
			}
		}

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;

		return 0;
	}
	else
	{
		std::cout << "Failed" << std::endl;

		return 1;
	}
}

int get_fields(std::string &s, std::vector<std::string> &v)
{
	std::stringstream ss(s);
	std::string field;

	while(ss.good())
	{
		getline(ss,field,',');
		v.push_back(field);
	}

	return 0;
}

