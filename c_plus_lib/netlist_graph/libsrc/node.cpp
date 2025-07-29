#include "node.hpp"

#include <sstream>
#include <vector>

node::node(void)
{
	id = -1;
	name = "";
	size_x = 0.0;
	size_y = 0.0;

	pos_x = 0.0;
	pos_y = 0.0;
	orientation = 0.0;
	layer = -1;
	isPlaced = false;

	pins = 0;
	pins_smd = 0;
	pins_th = 0;

	type = -1;

	neighbors.clear();

}

int8_t node::create_from_string_short( std::string s)
{
	std::stringstream ss(s);
	std::vector<std::string> fields;
	std::string field;

	while(ss.good())
	{
		getline(ss,field,',');
		fields.push_back(field);
	}

	id = stoi(fields[0]);
	size_x = stod(fields[1]);
	size_y = stod(fields[2]);
	pos_x = stod(fields[3]);
	pos_y = stod(fields[4]);
	orientation = stod(fields[5]);
	layer = stoi(fields[6]);
	isPlaced = (bool) stoi(fields[7]);	// Correspond to isLocked when importing from .nodes file.
	pins = stoi(fields[8]);
	pins_smd = stoi(fields[9]);
	pins_th = stoi(fields[10]);

	return 0;
}

int8_t node::create_from_string_long( std::string s)
{
	std::stringstream ss(s);
	std::vector<std::string> fields;
	std::string field;

	while(ss.good())
	{
		getline(ss,field,',');
		fields.push_back(field);
	}

	id = stoi(fields[0]);
	name = fields[1];
	size_x = stod(fields[2]);
	size_y = stod(fields[3]);
	pos_x = stod(fields[4]);
	pos_y = stod(fields[5]);
	orientation = stod(fields[6]);
	layer = stoi(fields[7]);
	isPlaced = (bool) stoi(fields[8]);	// Correspond to isLocked when importing from .nodes file.
	pins = stoi(fields[9]);
	pins_smd = stoi(fields[10]);
	pins_th = stoi(fields[11]);
	type = stoi(fields[12]);

	return 0;
}

/*int8_t node::add_keywords_from_list( std::vector< std::string > fields )
{
	if(fields[1] == "capacitor") type = 0;
	else if (fields[1] == "resistor") type = 1;
	else if (fields[1] == "diode") type = 2;
	else if (fields[1] == "integrated circuit (IC)") type = 3;
	else if (fields[1] == "light emitting diode (LED)") type = 4;
	else if (fields[1] == "dc power jack") type = 5;
	else
	{
		std::cout << "Warning : Unknown type for '" << fields[1] <<"'. Setting type for instance id " << id << " to -1." << std::endl;
		type = -1;
	}

	return 0;

}*/

int node::get_inst_bb_coords(int &xmin, int &xmax, int &ymin, int &ymax, double grid_resolution)
{
	std::pair<double, double> node_size, node_pos;

	node_size = get_size();
	node_pos = get_pos();

	// LV @ 2022/02/25
	double orientation = get_orientation();
	if ( orientation == 90 || orientation == 270 )
	{
		double tmp = node_size.first;
		node_size.first = node_size.second;
		node_size.second = tmp;
	}
#ifdef DEBUG_INFO
	std::cout << "'" << __FUNCTION__ << "' - pos (" << node_pos.first << "," << node_pos.second << "), size (" << node_size.first << "," << node_size.second << ")" << std::endl;
#endif
	node_pos.first = round_up(node_pos.first, grid_resolution/1000);
	node_pos.second = round_up(node_pos.second, grid_resolution/1000);

	node_size.first = round_up(node_size.first, grid_resolution/1000);
	node_size.second = round_up(node_size.second, grid_resolution/1000);
#ifdef DEBUG_INFO
	std::cout << "'" << __FUNCTION__ << "' - pos (" << node_pos.first << "," << node_pos.second << "), size (" << node_size.first << "," << node_size.second << ")" << std::endl;
#endif
	xmin = (int) ( node_pos.first - (int) round_nearest((node_size.first / 2),0.5) );
	xmax = (int) round_nearest(( node_size.first + xmin),0.5);

	ymin = (int) (node_pos.second - ((int) round_nearest((node_size.second / 2),0.5)));
	ymax = (int) round_nearest((node_size.second + ymin),0.5);
#ifdef DEBUG_INFO
	std::cout << "'" << __FUNCTION__ << "' - (xmin,xmax) = (" << xmin << "," << xmax<< "), (ymin,ymax) = (" << ymin << "," << ymax << ")" << std::endl;
#endif

	return 0;
}

// In case the shape has an even size the the center is biased to the left down
int node::get_inst_bb_centre_size(int &xc, int &yc, int &x, int &y, double grid_resolution)
{
	std::pair<double, double> node_size, node_pos;
	int xmin, ymin, xmax, ymax;

	get_inst_bb_coords(xmin, xmax, ymin, ymax, grid_resolution);

	x = xmax-xmin;
	y = ymax-ymin;

	xc = x / 2;
	yc = y / 2;

	return 0;
}

void node::print_to_console( bool format )
{
	std::cout << id << ",";
	if(format) std::cout << name << ",";
	std::cout << size_x << ","
		<< size_y << ","
		<< pos_x << ","
		<< pos_y << ","
		<< orientation << ","
		<< layer << ","
		<< isPlaced << ","
		<< pins << ","
		<< pins_smd << ","
		<< pins_th << ","
		<< type
		<< std::endl ;
}

void node::print(bool print_csv)
{
	if ( print_csv )
	{
		std::cout << id << ",";
		if (name != "") std::cout << name << ",";
		std::cout << size_x << "," << size_y << ",";
		std::cout << pos_x << "," << pos_y << ",";
		std::cout << orientation << ",";
		std::cout << isPlaced << std::endl;

	}
	else
	{
		std::cout << "Node " << id;
		if (name != "") std::cout << "(" << name << ")" << std::endl;

		std::cout << "  Size        : (" << size_x << "," << size_y << ")" << std::endl;
		std::cout << "  Position    : (" << pos_x << "," << pos_y << ")" << std::endl;
		std::cout << "  Orientation : " << orientation << std::endl;
		std::cout << "  Placed      : " << (isPlaced ? "Yes" : "No") << std::endl;
		std::cout << std::endl;
	}
}

int node::format_string_long( std::string& line )
{
	std::stringstream l;

	l << id << ","
		<< name << ","
		<< size_x << ","
		<< size_y << ","
		<< pos_x << ","
		<< pos_y << ","
		<< orientation << ","
		<< layer << ","
		<< isPlaced << ","
		<< pins << ","
		<< pins_smd << ","
		<< pins_th << ","
		<< type
		<< std::endl;

	line = l.str();
	return 0;
}

double node::get_area()
{
	if (size_x <= 0.0) std::cout << "Warning in function '" << __FUNCTION__ << "' size_x is less or equal to 0.0." << std::endl;
	if (size_y <= 0.0) std::cout << "Warning in function '" << __FUNCTION__ << "' size_y is less or equal to 0.0." << std::endl;

	return size_x * size_y;
}


