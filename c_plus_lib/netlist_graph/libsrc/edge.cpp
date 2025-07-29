#include "edge.hpp"

#include <sstream>
#include <vector>

#include "node.hpp"

edge::edge( void )
{
	a_id = -1;				// Refers to node (instance of a component)
	a_name = "";			// Refers to node name (instance name of a component)
	a_pad_id = -1;
	a_pad_name = "";
	a_size_x = 0.0;
	a_size_y = 0.0;
	a_pos_x = 0.0;
	a_pos_y = 0.0;
	a_isPlaced = false;

	b_id = -1;
	b_name = "";
	b_pad_id = -1;
	b_pad_name = "";
	b_size_x = 0.0;
	b_size_y = 0.0;
	b_pos_x = 0.0;
	b_pos_y = 0.0;
	b_isPlaced = false;

	net_id = -1;
	net_name = "";
	//common_net_points = 0;
	//uncommon_net_points = 0;

	power_rail = 0;
}

int8_t edge::create_from_string_short( std::string s )
{
	std::stringstream ss(s);
	std::vector<std::string> fields;
	std::string field;

	while(ss.good())
	{
		getline(ss,field,',');
		fields.push_back(field);
	}

	a_id = stoi(fields[0]);
	a_size_x = stod(fields[1]);
	a_size_y = stod(fields[2]);
	a_pos_x = stod(fields[3]);
	a_pos_y = stod(fields[4]);
	a_isPlaced = (bool) stoi(fields[5]);

	b_id = stoi(fields[6]);
	b_size_x = stod(fields[7]);
	b_size_y = stod(fields[8]);
	b_pos_x = stod(fields[9]);
	b_pos_y = stod(fields[10]);
	b_isPlaced = (bool) stoi(fields[11]);

	net_id = stoi(fields[12]);

	//common_net_points = stoi(fields[13]);
	//uncommon_net_points = stoi(fields[14]);

	power_rail = stoi(fields[13]);

	return 0;
}

int8_t edge::create_from_string_long( std::string s )
{
	std::stringstream ss(s);
	std::vector<std::string> fields;
	std::string field;

	while(ss.good())
	{
		getline(ss,field,',');
		fields.push_back(field);
	}

	a_id = stoi(fields[0]);
	a_pad_id = stoi(fields[1]);
	a_pad_name = fields[2];

	a_size_x = stod(fields[3]);
	a_size_y = stod(fields[4]);
	a_pos_x = stod(fields[5]);
	a_pos_y = stod(fields[6]);
	a_isPlaced = (bool) stoi(fields[7]);

	b_id = stoi(fields[8]);
	b_pad_id = stoi(fields[9]);
	b_pad_name = fields[10];

	b_size_x = stod(fields[11]);
	b_size_y = stod(fields[12]);
	b_pos_x = stod(fields[13]);
	b_pos_y = stod(fields[14]);
	b_isPlaced = (bool) stoi(fields[15]);

	net_id = stoi(fields[16]);
	net_name = fields[17];
	//common_net_points = stoi(fields[18]);
	//uncommon_net_points = stoi(fields[19]);

	power_rail = stoi(fields[18]);

	return 0;
}

std::pair<double, double> edge::get_size(int id)
{
	std::pair<double,double> p;

	if (id == 0) p = std::make_pair(a_size_x, a_size_y);
	else p = std::make_pair(b_size_x, b_size_y);

	return p;
}

int edge::set_size(int id, std::pair<double, double> p)
{
	if (id == 0) { a_size_x = p.first; a_size_y = p.second; }
	else { b_size_x = p.first; b_size_y = p.second; }

	return 0;
}

std::pair<double, double> edge::get_pos(int id)
{
	std::pair<double,double> p;

	if (id == 0) p = std::make_pair(a_pos_x, a_pos_y);
	else p = std::make_pair(b_pos_x, b_pos_y);

	return p;
}

int edge::set_pos(int id, std::pair<double, double> p)
{
	if (id == 0) { a_pos_x = p.first; a_pos_y = p.second; }
	else { b_pos_x = p.first; b_pos_y = p.second; }

	return 0;
}

void edge::print_to_console( bool format )
{

    std::cout << a_id << ",";                                               // instance id
    if(format)
    {
            std::cout << a_pad_id << ","            // pad id
                    << a_pad_name << ",";   // pad name

    }
    std::cout << a_size_x << ","
                    << a_size_y << ","
                    << a_pos_x << ","
                    << a_pos_y << ","
                    << a_isPlaced << ","
                    //<< n1 << ", "
                    << b_id << ",";
    if(format)
    {
            std::cout << b_pad_id << ","
                    << b_pad_name<< ",";

    }
    std::cout << b_size_x << ","
                    << b_size_y << ","
                    << b_pos_x << ","
                    << b_pos_y << ","
                    << b_isPlaced << ","
                    //<< n2 << ", "
                    << net_id << ",";
    if(format) std::cout << net_name << ",";
    //std::cout << common_net_points << ","
    //              << uncommon_net_points << ",";
    std::cout << power_rail
                    << std::endl;

}

int edge::print( bool print_csv )
{
	if(print_csv)
	{
		if (a_name == "") std::cout << a_id << ",";
		else std::cout << a_name << ",";
		std::cout << a_size_x << "," << a_size_y << ",";
		std::cout << a_pos_x << "," << a_pos_y << ",";

		if (b_name == "") std::cout << b_id << ",";
		else std::cout << b_name << ",";
		std::cout << b_size_x << "," << b_size_y << ",";
		std::cout << b_pos_x << "," << b_pos_y << ",";
		std::cout << std::endl;
	}
	else
	{
		std::cout << "Edge ";

		std::cout << a_id;
		if (a_name != "") std::cout << "(" << a_name << ")";
		std::cout << " - ";
		std::cout << b_id;
		if (b_name != "") std::cout << "(" << b_name << ")";
		std::cout << std::endl;

		std::cout << "  Size        : (" << a_size_x << "," << a_size_y << ") - (" << b_size_x << "," << b_size_y << ")" << std::endl;
		std::cout << "  Position    : (" << a_pos_x << "," << a_pos_y << ") - (" << b_pos_x << "," << b_pos_y << ")" << std::endl;
	    std::cout << std::endl;
	}



	return 0;
}


int edge::format_string_long( std::string& line )
{
	std::stringstream l;

	l << a_id << ","
		<< a_pad_id << ","
		<< a_pad_name << ","
		<< a_size_x << ","
		<< a_size_y << ","
		<< a_pos_x << ","
		<< a_pos_y << ","
		<< a_isPlaced << ","
		<< b_id << ","
		<< b_pad_id << ","
		<< b_pad_name << ","
		<< b_size_x << ","
		<< b_size_y << ","
		<< b_pos_x << ","
		<< b_pos_y << ","
		<< b_isPlaced << ","
		<< net_id << ","
		<< net_name << ","
		<< power_rail
		<< std::endl;

	line = l.str();
	return 0;
}
