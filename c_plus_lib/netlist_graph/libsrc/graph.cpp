#include "graph.hpp"

graph::graph(void)
{
	graph_name = "";
	graph_id = -1;
	kicad_pcb_file = "";
}

// Constructor. Initializes graph private variables with with node(_V) and edge(E) values.
graph::graph(std::vector<node> &n, std::vector<edge> &e)
{
	_V = n;
	V = n;
	E = e;

	graph_name = "";
	graph_id = -1;
	kicad_pcb_file = "";
	hpwl = 0;
}

graph::graph(std::vector<node> &n)
{
	_V = n;
	V = n;
	E.clear();

	graph_name = "";
	graph_id = -1;
	kicad_pcb_file = "";
	hpwl = 0;
}

graph::graph(std::vector<edge> &e)
{
	_V.clear();
	V.clear();
	E = e;

	graph_name = "";
	graph_id = -1;
	kicad_pcb_file = "";
	hpwl = 0;

}

int8_t graph::add_node_from_string_short( std::string s )
{
	node n;
	n.create_from_string_short(s);

	_V.push_back(n);
	V.push_back(n);
	return 0;
}

int8_t graph::add_node_from_string_long( std::string s )
{
	node n;
	n.create_from_string_long(s);

	_V.push_back(n);
	V.push_back(n);
	return 0;
}

int8_t graph::add_edge_from_string_short( std::string s )
{
	edge e;
	e.create_from_string_short(s);

	E.push_back(e);

	return 0;
}

int8_t graph::add_edge_from_string_long( std::string s )
{
	edge e;
	e.create_from_string_long(s);

	E.push_back(e);

	return 0;
}

std::string graph::get_node_name_by_id ( int id )
{
	for (auto v : V)
	{
		if (v.get_id() == id) return v.get_name();
	}

	return "";
}

std::set<int> graph::get_set_net_ids ()
{
	std::set<int> net_ids;
	for (auto e : E)
	{
		net_ids.insert(e.get_net_id());
	}

	return net_ids;
}


int graph::statistics( void )
{
	std::cout << "Graph statistics" << std::endl;
	std::cout << "================" << std::endl;
	std::cout << "Number of nodes: " << V.size() << std::endl;
	std::cout << "Number of edges: " << E.size() << std::endl;

	return 0;
}

std::vector<std::pair<int,int>> graph::get_nodes_connectivity_list(int power_rail)
{
	int id, edges;
	std::vector<std::pair<int,int>> edges_vector; 		// id, no of connectivity edges

	for (auto v : V)
	{
		id = v.get_id();
		edges = 0;
		for (auto e : E)
		{
			for(int i=0; i <2; i++)
			{
				if (e.get_instance_id(i) == id)
				{
					if (e.get_power_rail() == power_rail) edges++;
				}
			}
		}
		edges_vector.push_back(std::make_pair(id,edges));

	}

	// sort conn_edge by pair second element in descending order
	sort(edges_vector.begin(), edges_vector.end(), sortbysec);

	return edges_vector;
}


std::vector<std::pair<int,double>> graph::get_nodes_area_list( void )
{
	int id;
	double area;
	std::vector<std::pair<int,double>> nodes_area; 		// id, no of connectivity edges

	for (auto v : V)
	{
		id = v.get_id();
		area = v.get_area();
		nodes_area.push_back(std::make_pair(id,area));
	}

	// sort conn_edge by pair second element in descending order
	sort(nodes_area.begin(), nodes_area.end(), sortbysec);

	return nodes_area;
}

std::vector<std::pair<int,int>> graph::get_neighbor_nodes_connectivity_list( int id, int power_rail )
{
	// Create a vector of pairs having instance id in position one and a vector of instance id corresponding to neighboring connections.
	std::vector<int> neighbour_nodes;
	std::vector<std::pair<int,int>> tally;

	for (auto v : V)
	{

		if (v.get_id() == id)
		{

			for (auto e : E)
			{
				//Ignore self loops
				if( e.get_instance_id(0) == e.get_instance_id(1) ) continue;

				if (e.get_instance_id(0) == id)
				{
					if (e.get_power_rail() == 0) neighbour_nodes.push_back(e.get_instance_id(1));
				}

				if (e.get_instance_id(1) == id)
				{
					if (e.get_power_rail() == 0) neighbour_nodes.push_back(e.get_instance_id(0));
				}
			}
			break;
		}

	}

	// Now tally the connections and sort in descending order.
	return tally_contents(neighbour_nodes);
}

// print number of connected nodes and edges for each nodes
int graph::node_statistics( void )
{
	std::vector<std::pair<int,int>> conn_edge; 		// id, no of connectivity edges
	std::vector<std::pair<int,int>> power_edge;		// id, no of power edges
	std::vector<std::pair<int,int>> tally;


	std::cout << std::endl;	// Newline for visual segmentation

    std::cout << "Instances and their connectivity\nprinted in descending order." << std::endl;
    std::cout << "================================" << std::endl;

    conn_edge = get_nodes_connectivity_list( 0 );
    for (auto conn : conn_edge)
    {
    	std::cout << "\t" << get_node_name_by_id(conn.first) << "\t" << conn.second << std::endl;
    }
    std::cout << std::endl;	// Newline for visual segmentation

    std::cout << "Instances and their power connectivity\nprinted in descending order." << std::endl;
    std::cout << "======================================" << std::endl;
    power_edge.clear();
    power_edge = get_nodes_connectivity_list( 1 );

    for (auto conn : power_edge)
    {
    	std::cout << "\t" << get_node_name_by_id(conn.first) << "\t" << conn.second << std::endl;
    }
    std::cout << std::endl;	// Newline for visual segmentation



    std::cout << "Instances and their neighboring connectivity\nprinted in descending order." << std::endl;
    std::cout << "============================================" << std::endl;
    for ( auto v : V)
    {
    	tally.clear();
    	tally = get_neighbor_nodes_connectivity_list( v.get_id(), 0 );
    	std::cout << "\t" << get_node_name_by_id(v.get_id());
		for (auto i:tally) std::cout << ",(" << get_node_name_by_id(i.first) << "," << i.second << ")";
		std::cout << std::endl;
    }
    std::cout << std::endl;	// Newline for visual segmentation

	return 0;
}

int graph::embed_neighbour_nodes( void )
{
	std::vector<std::pair<int,int>> tally;

    for ( auto &v : V)
    {
    	tally.clear();
    	tally = get_neighbor_nodes_connectivity_list( v.get_id(), 0 );
    	v.set_neighbors(tally);
    }

    return 0;
}

std::set<int> graph::get_neighbor_node_ids( int id, int power_rail, bool ignore_self_loops )
{
	std::set<int> nn;
	nn.clear();

	for ( node& v : V)
	{
		if (v.get_id() == id)
		{

			for (edge& e : E)
			{
				//Ignore self loops
				if( e.get_instance_id(0) == e.get_instance_id(1) )
				{
					if (ignore_self_loops == true) continue;
				}

//				if (power_rail > 0)
//				{
					for (int i=0; i < 2; i++)
					{
						if (e.get_instance_id(i) == id)
						{
								if (e.get_power_rail() == power_rail) nn.insert(e.get_instance_id(1-i));
						}
					}
//				}
//				else
//				{
//					if(e.get_power_rail() > 0) {continue;}
//					for (int i=0; i < 2; i++)
//					{
//						if (e.get_instance_id(i) == id)
//						{
//							nn.insert(e.get_instance_id(1-i));
//						}
//					}
//				}
			}
			break;
		}
	}

	return nn;
}

int graph::get_average_pad_position( int id, std::vector<std::tuple<int, double, double, int, double, double>> &pads_avg_pos )
{
	int status = -1;
	node n;
	std::vector<std::pair<int,int>> neighbors;
	std::tuple<int, double, double, int, double, double> t;
	std::pair<double, double> pad;

	pads_avg_pos.clear();

	if (get_node_by_id(id, n) == 0)
	{
		// DEBUG
		//std::cout << "Printing average pad position between instance " << id << " and its neighbors." << std::endl;
		//std::cout << "===================================================================" << std::endl;

		if (n.get_neighbors(neighbors) == 0)
		{
			status = 0;
			for (auto neighbor : neighbors)
			{
				t = std::make_tuple(id, 0.0, 0.0, neighbor.first, 0.0, 0.0);
				for (auto e: E)
				{
					for (int i = 0; i < 2; i++)		// 0%2 = 0, 1%2 = 1, 2%2 = 0
					{
						if (e.get_power_rail() != 0) continue;
						// i == 0 => 0 1, i == 1 => 1 0
						if (e.get_instance_id(i%2) == id && e.get_instance_id((i+1)%2) == neighbor.first)
						{
							//std::cout << i << ","; // DEBUG
							pad = e.get_pos(i%2);
							std::get<1>(t) = std::get<1>(t) + pad.first;
							std::get<2>(t) = std::get<2>(t) + pad.second;
							//std::cout << id << "(" << pad.first << "," << pad.second << "),"; // DEBUG

							pad = e.get_pos((i+1)%2);
							std::get<4>(t) = std::get<4>(t) + pad.first;
							std::get<5>(t) = std::get<5>(t) + pad.second;
							//std::cout << neighbor.first << "(" << pad.first << "," << pad.second << ")" << std::endl; // DEBUG
						}
					}
				}

				std::get<1>(t) /= neighbor.second;
				std::get<2>(t) /= neighbor.second;
				std::get<4>(t) /= neighbor.second;
				std::get<5>(t) /= neighbor.second;

				// DEBUG
				//std::cout 	<< neighbor.second << ","
				//		    << std::get<1>(t) << ","
				//			<< std::get<2>(t) << ","
				//			<< std::get<4>(t) << ","
				//			<< std::get<5>(t) << std::endl;

				//std::cout << std::endl;

				pads_avg_pos.push_back(t);

			}
		}
		else
		{
			std::cout << "Failed to get neighbors for node with id " << id <<  ". Exiting." << std::endl;
			return status;
		}
	}
	else
	{
		std::cout << "Failed to get node with id " << id <<  ". Exiting." << std::endl;
		return status;
	}

	return status;

}

int graph::get_node_by_id( int id, node &n )
{
	int status = -1;

	for ( auto v : V )
	{
		if (v.get_id() == id)
		{
			n = v;
			status = 0;
			break;
		}
	}

	return status;
}

node& graph::get_node_by_id( int id )
{
	for ( auto &v : V )
	{
		if (v.get_id() == id)
		{
			return v;
		}
	}

	throw std::invalid_argument( "received negative value" );
}

std::set<std::pair<int,int>> graph::get_edges_by_power_rail( int power_rail, ABSTRACTION type )
{
	std::set<std::pair<int,int>> edges;

	for (auto e : E)
	{
		if (e.get_power_rail() == power_rail)
		{
			edges.insert(e.get_edge_connectivity());
		}
	}

	return edges;
}

std::set<std::pair<int,int>> graph::get_edges_by_net_id( int net_id, ABSTRACTION type )
{
	std::set<std::pair<int,int>> edges;

	for (auto e : E)
	{
		if (e.get_net_id() == net_id)
		{
			edges.insert(e.get_edge_connectivity());
		}
	}

	return edges;
}

std::set<std::pair<int,int>> graph::get_edges_by_instance_id( int i_id, int power_rail )
{
	std::set<std::pair<int,int>> edges;

	for (auto e : E)
	{
		if (e.get_power_rail() != power_rail) continue;
		if ( e.get_instance_id(0) == i_id || e.get_instance_id(1) == i_id)
		{
			edges.insert(e.get_edge_connectivity());
		}
	}

	return edges;
}

std::vector<edge> graph::get_all_edges_by_instance_id( int i_id, int power_rail )
{
	std::vector<edge> edges;

	for (auto e : E)
	{
		if (e.get_power_rail() != power_rail) continue;
		if ( e.get_instance_id(0) == i_id || e.get_instance_id(1) == i_id)
		{
			edges.push_back(e);
		}
	}

	return edges;
}


int8_t graph::partial_graph( std::string fileName, int power_rail, bool unique)
{
	std::set<std::pair<int,int>> edges;
	std::set<node> nodes;
	std::string net_name;
	std::string node_name_a, node_name_b;

	std::stringstream ss;

	if (unique == true)
	{
		edges = get_edges_by_power_rail( power_rail, COMPONENT );
	}
	else
	{
		std::cout << "Feature is not yet implemented. Function exiting. " << std::endl;
		return -1;
	}

	if (fileName == "")
	{
		ss << "partial_graph_" << power_rail << ".gv";

		fileName = ss.str();
	}
	std::cout << "Using file " << fileName << std::endl;

	std::ofstream file;

	std::cout << "Opening '" << fileName << "' for writing ... ";
	file.open(fileName, std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << "digraph G {" << std::endl;

		// title
		file << "\tlabelloc=\"t\"" << std::endl;
		file << "\tlabel=\"power_rail: " << power_rail << "\"" <<  std::endl;

		for (auto e : edges)
		{
			node_name_a = get_node_name_by_id(e.first);
			if (node_name_a == "") std::cout << "Warning: node_name_a with corresponding node id " << e.first << " is empty." << std::endl;

			node_name_b = get_node_name_by_id(e.second);
			if (node_name_b == "") std::cout << "Warning: node_name_b with corresponding node id " << e.first << " is empty." << std::endl;

			if (node_name_a == "" && node_name_b == "") file << "\t{" << e.first  << "} -> {" << e.second << "}";	// directed
			else file << "\t{" << node_name_a  << "} -> {" << node_name_b << "}";	// directed
			// Optionally add options here
			file << "[dir=none]";
			file << ";" <<std::endl;
		}

		file <<  "}" << std::endl;

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;
	}
	else std::cout << "Failed" << std::endl;


	return 0;
}

int8_t graph::net_graphviz( std::string fileName, int net_id, ABSTRACTION type )
{
	std::set<std::pair<int,int>> edges;
	std::set<node> nodes;
	std::string net_name;
	std::string node_name_a, node_name_b;

	std::stringstream ss;

	edges = get_edges_by_net_id( net_id, COMPONENT );

	for (auto e : E)
	{
		if (e.get_net_id() == net_id)
		{
			net_name = e.get_net_name();

			// https://www.tutorialspoint.com/how-to-remove-certain-characters-from-a-string-in-cplusplus
			// The remove function takes the starting and ending address of the string, and a character that will be removed.
			net_name.erase(remove(net_name.begin(), net_name.end(), '\"'), net_name.end());
		}
	}

	if (fileName == "")
	{
		if (net_name != "")
		{
			ss << "net_" << net_id << "_" << net_name << ".gv";
		}
		else
		{
			ss << "net_" << net_id << "_" << net_name << ".gv";
		}
		fileName = ss.str();
	}
	std::cout << "Using file " << fileName << std::endl;

	std::ofstream file;

	std::cout << "Opening '" << fileName << "' for writing ... ";
	file.open(fileName, std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << "digraph G {" << std::endl;

		// title
		file << "\tlabelloc=\"t\"" << std::endl;
		file << "\tlabel=\"net_id: " << net_id << "," << net_name << "\"" <<  std::endl;

		for (auto e : edges)
		{
			node_name_a = get_node_name_by_id(e.first);
			if (node_name_a == "") std::cout << "Warning: node_name_a with corresponding node id " << e.first << " is empty." << std::endl;

			node_name_b = get_node_name_by_id(e.second);
			if (node_name_b == "") std::cout << "Warning: node_name_b with corresponding node id " << e.first << " is empty." << std::endl;

			if (node_name_a == "" && node_name_b == "") file << "\t{" << e.first  << "} -> {" << e.second << "}";	// directed
			else file << "\t{" << node_name_a  << "} -> {" << node_name_b << "}";	// directed
			// Optionally add options here
			file << "[dir=none]";
			file << ";" <<std::endl;
		}

		file <<  "}" << std::endl;

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;
	}
	else std::cout << "Failed" << std::endl;

	return 0;
}

int8_t graph::instance_graphviz( std::string fileName, int i_id, int power_rail )
{
	std::set<std::pair<int,int>> edges;

	std::string instance_name;
	std::string node_name_a, node_name_b;

	std::stringstream ss;

	edges = get_edges_by_instance_id( i_id, power_rail );

	for (auto inst : V)
	{
		if (inst.get_id() == i_id)
		{
			instance_name = inst.get_name();

			// https://www.tutorialspoint.com/how-to-remove-certain-characters-from-a-string-in-cplusplus
			// The remove function takes the starting and ending address of the string, and a character that will be removed.
			instance_name.erase(remove(instance_name.begin(), instance_name.end(), '\"'), instance_name.end());
		}
	}

	if (fileName == "")
	{
		if (instance_name != "")
		{
			ss << "inst_" << i_id << "_" << instance_name << "_" << power_rail << ".gv";
		}
		else
		{
			ss << "inst_" << i_id << "_" << power_rail << ".gv";
		}
		fileName = ss.str();
	}
	std::cout << "Using file " << fileName << std::endl;

	std::ofstream file;

	std::cout << "Opening '" << fileName << "' for writing ... ";
	file.open(fileName, std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << "digraph G {" << std::endl;

		// title
		file << "\tlabelloc=\"t\"" << std::endl;
		file << "\tlabel=\"inst_id: " << i_id << "," << instance_name << "\"" <<  std::endl;

		for (auto e : edges)
		{
			node_name_a = get_node_name_by_id(e.first);
			if (node_name_a == "") std::cout << "Warning: node_name_a with corresponding node id " << e.first << " is empty." << std::endl;

			node_name_b = get_node_name_by_id(e.second);
			if (node_name_b == "") std::cout << "Warning: node_name_b with corresponding node id " << e.first << " is empty." << std::endl;

			if (node_name_a == "" && node_name_b == "") file << "\t{" << e.first  << "} -> {" << e.second << "}";	// directed
			else file << "\t{" << node_name_a  << "} -> {" << node_name_b << "}";	// directed
			// Optionally add options here
			file << "[dir=none]";
			file << ";" <<std::endl;
		}

		file <<  "}" << std::endl;

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;
	}
	else std::cout << "Failed" << std::endl;

	return 0;
}

int8_t graph::instance_pads_graphviz( std::string fileName, int i_id, int power_rail )
{
	std::vector<edge> edges;

	std::string instance_name;
	std::string node_name_a, node_name_b;

	std::stringstream ss;

	edges = get_all_edges_by_instance_id( i_id, power_rail );

	// get instance name
	for (auto inst : V)
	{
		if (inst.get_id() == i_id)
		{
			instance_name = inst.get_name();

			// https://www.tutorialspoint.com/how-to-remove-certain-characters-from-a-string-in-cplusplus
			// The remove function takes the starting and ending address of the string, and a character that will be removed.
			instance_name.erase(remove(instance_name.begin(), instance_name.end(), '\"'), instance_name.end());
		}
	}

	// setup filename
	if (fileName == "")
	{
		if (instance_name != "")
		{
			ss << "pads_inst_" << i_id << "_" << instance_name << "_" << power_rail << ".gv";
		}
		else
		{
			ss << "pads_inst_" << i_id << "_" << power_rail << ".gv";
		}
		fileName = ss.str();
	}
	std::cout << "Using file " << fileName << std::endl;

	std::ofstream file;
	std::vector<std::string> node_names_used;
	bool found = false;

	std::cout << "Opening '" << fileName << "' for writing ... ";
	file.open(fileName, std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << "digraph G {" << std::endl;

		// title
		file << "\tlabelloc=\"t\"" << std::endl;
		file << "\tlabel=\"pads_inst_id: " << i_id << "," << instance_name << "\"" <<  std::endl;

		for (auto e : edges)
		{
			node_name_a = get_node_name_by_id(e.get_instance_id(0));
			node_name_a.append("_");
			node_name_a.append(e.get_pad_name(0));
			if (node_name_a == "") std::cout << "Warning: node_name_a with corresponding node id " << e.get_instance_id(0) << "." << e.get_pad_id(0) << " is empty." << std::endl;

			if (e.get_instance_id(0) == i_id)
			{
				// some filtering to prevent printing duplicate options and overloading the graph file with crap.
				for(auto nn : node_names_used)
				{
					found = false;
					if (nn == node_name_a)
					{
						found = true;
						break;
					}
				}
				if (!found)
				{
					node_names_used.push_back(node_name_a);
					//file << "\t" << node_name_a << " [color=indigo, style=filled, fillcolor=lightcoral];" << std::endl;
					file << "\t" << node_name_a << " [color=chocolate, style=filled, fillcolor=burlywood1];" << std::endl;

				}
			}

			node_name_b = get_node_name_by_id(e.get_instance_id(1));
			node_name_b.append("_");
			node_name_b.append(e.get_pad_name(1));
			if (node_name_b == "") std::cout << "Warning: node_name_b with corresponding node id " << e.get_instance_id(1) << "." << e.get_pad_id(1) << " is empty." << std::endl;

			if (e.get_instance_id(1) == i_id)
			{
				// some filtering to prevent printing duplicate options and overloading the graph file with crap.
				for(auto nn : node_names_used)
				{
					found = false;
					if (nn == node_name_b)
					{
						found = true;
						break;
					}
				}
				if (!found)
				{
					node_names_used.push_back(node_name_b);
					//file << "\t" << node_name_b << " [color=indigo, style=filled, fillcolor=lightcoral];" << std::endl;
					file << "\t" << node_name_b << " [color=chocolate, style=filled, fillcolor=burlywood1];" << std::endl;
				}
			}

			if (node_name_a == "" && node_name_b == "") file << "\t{" << e.get_instance_id(0) << "." << e.get_pad_id(0) << "} -> {" << e.get_instance_id(1) << "." << e.get_pad_id(1) << "}";	// directed
			else file << "\t{" << node_name_a  << "} -> {" << node_name_b << "}";	// directed
			// Optionally add options here
			file << "[dir=none]";
			file << ";" <<std::endl;
		}

		file <<  "}" << std::endl;

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;
	}
	else std::cout << "Failed" << std::endl;

	return 0;
}

int8_t graph::partial_graph_gml( std::string fileName, int power_rail, bool unique)
{
	std::set<std::pair<int,int>> edges;
	std::set<std::pair<int,std::string>> nodes;
	std::string net_name;
	std::string node_name_a, node_name_b;

	std::stringstream ss;

	if (unique == true)
	{
		edges = get_edges_by_power_rail( power_rail, COMPONENT );
	}
	else
	{
		std::cout << "Feature is not yet implemented. Function exiting. " << std::endl;
		return -1;
	}

	if (fileName == "")
	{
		ss << "partial_graph_" << power_rail << ".gml";

		fileName = ss.str();
	}
	std::cout << "Using file " << fileName << std::endl;

	std::ofstream file;

	std::cout << "Opening '" << fileName << "' for writing ... ";
	file.open(fileName, std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << "graph" << std::endl;
		file << "[" << std::endl;

//		// title
//		file << "\tlabelloc=\"t\"" << std::endl;
//		file << "\tlabel=\"power_rail: " << power_rail << "\"" <<  std::endl;
//
//		for (auto e : edges)
//		{
//			node_name_a = get_node_name_by_id(e.first);
//			if (node_name_a == "") std::cout << "Warning: node_name_a with corresponding node id " << e.first << " is empty." << std::endl;
//
//			node_name_b = get_node_name_by_id(e.second);
//			if (node_name_b == "") std::cout << "Warning: node_name_b with corresponding node id " << e.first << " is empty." << std::endl;
//
//			if (node_name_a == "" && node_name_b == "") file << "\t{" << e.first  << "} -> {" << e.second << "}";	// directed
//			else file << "\t{" << node_name_a  << "} -> {" << node_name_b << "}";	// directed
//			// Optionally add options here
//			file << "[dir=none]";
//			file << ";" <<std::endl;
//		}

		std::string nn;
		std::pair<int, std::string> p;
		for (auto e : edges)
		{
			p = std::make_pair(e.first, get_node_name_by_id(e.first));
			nodes.insert(p);

			p = std::make_pair(e.second, get_node_name_by_id(e.second));
			nodes.insert(p);
		}
		std::set<std::pair<int,std::string>>::iterator it = nodes.begin();

		while (it != nodes.end())
		{
		    // Print the element
		    file << "\tnode" << std::endl << "\t[" << std::endl
		    		<< "\t\tid\t"  << ((*it).first) << std::endl
					<< "\t\tlabel\t\""  << ( (*it).second) << "\"" << std::endl
		    		<< "\t]" << std::endl;
		    //Increment the iterator
		    it++;
		}

		for (auto e : edges)
		{
		    file << "\tedge" << std::endl << "\t[" << std::endl
				<< "\t\tsource\t"  << (e.first) << std::endl
				<< "\t\ttarget\t"  << (e.second) << std::endl
				<< "\t]" << std::endl;
		}

		file <<  "]" << std::endl;

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;
	}
	else std::cout << "Failed" << std::endl;

	return 0;
}

int graph::normalize( void )
{
	std::pair<double, double> size_p; 	// Size of component
	std::pair<double,double> p;			// pos / size of pad

	for (auto &e : E)
	{
		for (int i = 0; i < 2; i++)
		{
			// Get instance id
			int id = e.get_instance_id(i);
			for ( auto n : V )
			{
				// get instance size and update normalize pads
				if (n.get_id() == id)
				{
					// Component size
					size_p = n.get_size();

					// normalize size
					p = e.get_size(i);
					e.set_size(i, std::make_pair(p.first/size_p.first, p.second/size_p.second));

					// normalize position
					size_p.first /= 2;		// pad position is relative to origin of component footprint
					size_p.second /= 2;		// pad position is relative to origin of component footprint

					p = e.get_pos(i);
					e.set_pos(i, std::make_pair(p.first/size_p.first, p.second/size_p.second));

					break;
				}
			}
		}
	}

	return 0;
}

int graph::get_feature_vector( int id, std::vector<double> &fv, int MAX_NEIGHBORS )
{
	node inst;
	std::vector<std::pair<int,int>> n;
	std::vector<std::tuple<int, double, double, int, double, double>> pads_avg_pos;
	int mn = 0;

	get_node_by_id(id, inst);
	fv.clear();
	fv.push_back((double) inst.get_size().first);		// current node size_x
	fv.push_back((double) inst.get_size().second);		// current node size_y
	fv.push_back((double) inst.get_type());
	fv.push_back((double) inst.get_pin_count());

//	std::cout << "============================================" << std::endl;	// DEBUG
//	std::cout << "Current node : " << inst.get_name() << "(" << inst.get_id() << ")" << std::endl;	// DEBUG
//	std::cout << "  Size          : (" << inst.get_size().first << "," << inst.get_size().second << ")" << std::endl;	// DEBUG
//	std::cout << "  Type          : " << inst.get_type() << std::endl;	// DEBUG
//	std::cout << "  Pins          : " << inst.get_pin_count() << std::endl;	// DEBUG

	get_average_pad_position( id, pads_avg_pos );
//	std::cout << std::endl;	// DEBUG

	mn = 0;
	for (auto j : pads_avg_pos)
	{
		if (++mn > MAX_NEIGHBORS) break;
		get_node_by_id(std::get<3>(j), inst);
//		std::cout << "Neighbor node : " << inst.get_name() << "(" << inst.get_id() << ")" << std::endl;	// DEBUG

		if (id != std::get<0>(j)) std::cout << "Expected parent id " << id << " by got instead " << std::get<0>(j) << "." << std::endl;

//		std::cout << "  Size          : (" << inst.get_size().first << "," << inst.get_size().second << ")" << std::endl;	// DEBUG
//		std::cout << "  Position      : (" 	<< (inst.get_isPlaced() ? inst.get_pos().first : 0.0) << ","					// DEBUG
//											<< (inst.get_isPlaced() ? inst.get_pos().second : 0.0) << ")" << std::endl;		// DEBUG
//		std::cout << "  Type          : " << inst.get_type() << std::endl;	// DEBUG
//		std::cout << "  Pins          : " << inst.get_pin_count() << std::endl;	// DEBUG
//
//		std::cout << "  Parent id     : " << std::get<0>(j);	// DEBUG
//		std::cout << " (" << std::get<1>(j) << "," << std::get<2>(j) << ")" << std::endl;	// DEBUG
//
//		std::cout << "  Neighbor id   : " << std::get<3>(j);	// DEBUG
//		std::cout << " (" << std::get<4>(j) << "," << std::get<5>(j) << ")" << std::endl;	// DEBUG
//		std::cout << std::endl;	// DEBUG
		fv.push_back((double) inst.get_size().first);		// neighbor node size_x
		fv.push_back((double) inst.get_size().second);		// neighbor node size_y
		fv.push_back((double) (inst.get_isPlaced() ? inst.get_pos().first : 0.0));		// neighbor node position_x
		fv.push_back((double) (inst.get_isPlaced() ? inst.get_pos().second : 0.0));		// neighbor node position_y
		fv.push_back((double) inst.get_type());
		fv.push_back((double) inst.get_pin_count());
		fv.push_back((double) std::get<1>(j));		// parent pad average x
		fv.push_back((double) std::get<2>(j));		// parent pad average y
		fv.push_back((double) std::get<4>(j));		// neighbor pad average x
		fv.push_back((double) std::get<5>(j));		// neighbor pad average y
	}

	if (mn < MAX_NEIGHBORS)
	{
		do
		{
//			std::cout << "Neighbor node : NULL(-1)" << std::endl;	// DEBUG
//
//			std::cout << "  Size          : (0.0,0.0)" << std::endl;	// DEBUG
//			std::cout << "  Position      : (0.0,0.0)" << std::endl;	// DEBUG
//			std::cout << "  Type          : -1" << std::endl;	// DEBUG
//			std::cout << "  Pins          : 0" << std::endl;	// DEBUG
//
//			std::cout << "  Parent id     : -1" ;	// DEBUG
//			std::cout << " (0.0,0.0)" << std::endl;	// DEBUG
//
//			std::cout << "  Neighbor id   : -1" ;	// DEBUG
//			std::cout << " (0.0,0.0)" << std::endl;	// DEBUG
//			std::cout << std::endl;	// DEBUG
			fv.push_back((double) 0.0);		// neighbor node size_x
			fv.push_back((double) 0.0);		// neighbor node size_y
			fv.push_back((double) 0.0);		// neighbor node position_x
			fv.push_back((double) 0.0);		// neighbor node position_y
			fv.push_back((double) -1);
			fv.push_back((double) 0);

			fv.push_back((double) 0.0);		// parent pad average x
			fv.push_back((double) 0.0);		// parent pad average y
			fv.push_back((double) 0.0);		// neighbor pad average x
			fv.push_back((double) 0.0);		// neighbor pad average y
		} while (++mn < MAX_NEIGHBORS);
	}

	return 0;
}

int graph::get_simplified_feature_vector( int id, std::vector<double> &fv, int MAX_NEIGHBORS )
{
	node inst;
	std::vector<std::pair<int,int>> n;
	std::vector<std::tuple<int, double, double, int, double, double>> pads_avg_pos;
	int mn = 0;

	get_node_by_id(id, inst);
	fv.clear();
	fv.push_back((double) (inst.get_size().first * inst.get_size().second)); // Area of current node.
//	fv.push_back((double) inst.get_type());
	fv.push_back((double) inst.get_pin_count());

//	std::cout << "============================================" << std::endl;	// DEBUG
//	std::cout << "Current node : " << inst.get_name() << "(" << inst.get_id() << ")" << std::endl;	// DEBUG
//	std::cout << "  Size          : " << inst.get_size().first * inst.get_size().second << std::endl;	// DEBUG
//	std::cout << "  Type          : " << inst.get_type() << std::endl;	// DEBUG
//	std::cout << "  Pins          : " << inst.get_pin_count() << std::endl;	// DEBUG

	get_average_pad_position( id, pads_avg_pos );
//	std::cout << std::endl;	// DEBUG

	mn = 0;
	for (auto j : pads_avg_pos)
	{
		if (++mn > MAX_NEIGHBORS) break;
		get_node_by_id(std::get<3>(j), inst);
//		std::cout << "Neighbor node : " << inst.get_name() << "(" << inst.get_id() << ")" << std::endl;	// DEBUG

		if (id != std::get<0>(j)) std::cout << "Expected parent id " << id << " by got instead " << std::get<0>(j) << "." << std::endl;

//		std::cout << "  Area          : " << inst.get_size().first * inst.get_size().second << std::endl;	// DEBUG
//		std::cout << "  Position      : (" 	<< (inst.get_isPlaced() ? inst.get_pos().first : 0.0) << ","					// DEBUG
//											<< (inst.get_isPlaced() ? inst.get_pos().second : 0.0) << ")" << std::endl;		// DEBUG
//		std::cout << "  Type          : " << inst.get_type() << std::endl;	// DEBUG
//		std::cout << "  Pins          : " << inst.get_pin_count() << std::endl;	// DEBUG
//		std::cout << std::endl;	// DEBUG
		fv.push_back((double) (inst.get_size().first * inst.get_size().second)); // Area of neighbor node.
		fv.push_back((double) (inst.get_isPlaced() ? inst.get_pos().first : 0.0));		// neighbor node position_x
		fv.push_back((double) (inst.get_isPlaced() ? inst.get_pos().second : 0.0));		// neighbor node position_y
//		fv.push_back((double) inst.get_type());
		fv.push_back((double) inst.get_pin_count());
	}

	if (mn < MAX_NEIGHBORS)
	{
		do
		{
//			std::cout << "Neighbor node : NULL(-1)" << std::endl;	// DEBUG
//
//			std::cout << "  Area          : 0.0" << std::endl;	// DEBUG
//			std::cout << "  Position      : (0.0,0.0)" << std::endl;	// DEBUG
//			std::cout << "  Type          : -1" << std::endl;	// DEBUG
//			std::cout << "  Pins          : 0" << std::endl;	// DEBUG
//
//			std::cout << std::endl;	// DEBUG
			fv.push_back((double) 0.0);		// neighbor node area
			fv.push_back((double) 0.0);		// neighbor node position_x
			fv.push_back((double) 0.0);		// neighbor node position_y
//			fv.push_back((double) -1);
			fv.push_back((double) 0);

		} while (++mn < MAX_NEIGHBORS);
	}

	return 0;
}

int graph::print_feature_vector( std::vector<double> &fv )
{
	std::cout << "============================================" << std::endl;
	std::cout << "Current node : " << std::endl;
	std::cout << "  Size          : (" << fv[0] << "," << fv[1] << ")" << std::endl;
	std::cout << "  Type          : " << fv[2] << std::endl;
	std::cout << "  Pins          : " << fv[3] << std::endl;

	std::cout << std::endl;

	for (uint32_t i=4; i<fv.size(); i+=10)
	{
		std::cout << "Neighbor node : " << std::endl;

		std::cout << "  Size          : (" << fv[i] << "," << fv[i+1] << ")" << std::endl;
		std::cout << "  Position      : (" 	<< fv[i+2] << "," << fv[i+3] << ")" << std::endl;
		std::cout << "  Type          : " << fv[i+4] << std::endl;
		std::cout << "  Pins          : " << fv[i+5] << std::endl;
		std::cout << "  Parent id     : ";
		std::cout << " (" << fv[i+6] << "," << fv[i+7] << ")" << std::endl;

		std::cout << "  Neighbor id   : ";
		std::cout << " (" << fv[i+8] << "," << fv[i+9] << ")" << std::endl;
		std::cout << std::endl;

	}

	return 0;
}

int graph::print_simplified_feature_vector( std::vector<double> &fv )
{
	std::cout << "============================================" << std::endl;
	std::cout << "Current node : " << std::endl;
	std::cout << "  Area          : " << fv[0] << std::endl;
	std::cout << "  Pins          : " << fv[1] << std::endl;

	std::cout << std::endl;

	for (uint32_t i=2; i<fv.size(); i+=4)
	{
		std::cout << "Neighbor node : " << std::endl;

		std::cout << "  Size          : " << fv[i] << std::endl;
		std::cout << "  Position      : (" 	<< fv[i+1] << "," << fv[i+2] << ")" << std::endl;
		std::cout << "  Pins          : " << fv[i+3] << std::endl;

		std::cout << std::endl;
	}

	return 0;
}

int graph::normalize_feature_vector( std::vector<double> &fv, double grd_x, double grd_y)
{
	double size_x=0, size_y=0;
	int pins;

	get_dimensions_of_largest_component(size_x, size_y);
	get_largest_pin_count(pins);

	fv[0] /= size_x;
	fv[1] /= size_y;
	fv[3] /= pins;

	for (uint32_t i=4; i<fv.size(); i+=10)
	{
		fv[i] /= size_x;
		fv[i+1] /= size_y;
		fv[i+2] /= grd_x;
		fv[i+3] /= grd_y;

		fv[i+6] /= grd_x;
		fv[i+7] /= grd_y;
		fv[i+8] /= grd_x;
		fv[i+9] /= grd_y;
	}

	return 0;
}

int graph::normalize_simplified_feature_vector( std::vector<double> &fv, double grd_x, double grd_y)
{
	double size_x=0, size_y=0;
	int pins;

	get_dimensions_of_largest_component(size_x, size_y);
	get_largest_pin_count(pins);

	fv[0] /= (size_x*size_y);
	fv[1] /= pins;

	for (uint32_t i=2; i<fv.size(); i+=4)
	{

		fv[i] /= (size_x*size_y);
		fv[i+1] /= grd_x;
		fv[i+2] /= grd_y;
		fv[i+3] /= pins;
	}

	return 0;
}

int graph::get_dimensions_of_largest_component(double &x, double &y)
{
	double area = 0;
	std::pair<double, double> size;
	for (auto v : V)
	{
		size = v.get_size();

		if (area < (size.first * size.second))
		{
			area = (size.first * size.second);
			x=size.first;
			y=size.second;
		};
	}

	return 0;
}

double graph::get_largest_x_size( void )
{
	std::pair<double, double> size;
	double x = 0;
	for (auto v : V)
	{
		size = v.get_size();
		if (size.first > x) x = size.first;
	}

	return x;
}

double graph::get_largest_y_size( void )
{
	std::pair<double, double> size;
	double y = 0;
	for (auto v : V)
	{
		size = v.get_size();
		if (size.second > y) y = size.second;
	}

	return y;
}


int graph::get_largest_pin_count(int &pins)
{
	pins = 0;
	for (auto v : V)
	{
		if (pins < v.get_pin_count()) pins = v.get_pin_count();
	}

	return 0;
}

int graph::get_largest_pin_count()
{
	int pins;
	get_largest_pin_count(pins);

	return pins;
}

int graph::get_next_component_id_to_place( const std::string& ordering )
{
	int status = -1;
	node inst;

	//std::cout << "In function '" << __FUNCTION__ << "' using ordering scheme '" << ordering << "'" << std::endl;

	if ( ordering == "connection_density" )
	{
		std::vector<std::pair<int,int>> nodes;
		nodes.clear();

		nodes = get_nodes_connectivity_list( 0 );	// Return number of connections for each instance sorted in descending order.

		// an element of n is a pair in the form of <id, connections>

		for ( auto n : nodes )
		{
			get_node_by_id(n.first, inst);
			if (inst.get_isPlaced()) continue;
			else { status = n.first; break; }
		}
	}
	else if ( ordering == "area" )
	{
		std::vector<std::pair<int,double>> nodes_area;
		nodes_area.clear();

		nodes_area = get_nodes_area_list();
		for ( auto n : nodes_area )
		{
			get_node_by_id(n.first, inst);
			if (inst.get_isPlaced()) continue;
			else { status = n.first; break; }
		}
	}
	else // random
	{
		for ( auto v : V )
		{
			if (v.get_isPlaced()) continue;
			else { status = v.get_id(); break; }
		}
	}

	return status;
}

int graph::update( int id, std::pair<double, double> pos )
{
	int status = -1;
	for (auto &v : V)
	{
		if (v.get_id() == id)
		{
			if (v.get_isPlaced()) std::cout << "Warning: Node with id " << id << " has isPlaced set. Updating regardless." << std::endl;
			v.set_pos( pos );
			v.set_isPlaced();
			status = 0;
			break;
		}
	}

	return status;
}


//! Resets the graph by setting V from _V
//! _V contains the node information as parsed from the .nodes file.
int graph::reset( void )
{
	V = _V;
	return 0;
}

int graph::set_component_origin_to_zero( board &b )
{
	std::pair<double, double> pos;

	for( auto &v : V)
	{
		pos = v.get_pos();
		pos.first -= b.get_bb_min_x();
		pos.second -= b.get_bb_min_y();
		v.set_pos( pos );
	}

	return 0;
}

int graph::reset_component_origin( board &b )
{
	std::pair<double, double> pos;

	for( auto &v : V)
	{
		pos = v.get_pos();
		pos.first += b.get_bb_min_x();
		pos.second += b.get_bb_min_y();
		v.set_pos( pos );
	}

	return 0;
}

int graph::set_original_component_origin( board &b )
{
	std::pair<double, double> pos;

	for( auto &v : V)
	{
		pos = v.get_pos();
		pos.first += b.get_bb_min_x();
		pos.second += b.get_bb_min_y();
		v.set_pos( pos );
	}

	return 0;
}

int graph::get_nets_associated_with_instance( int id, std::set<int> &nets, int power_rail )
{

	nets.clear();

	for (auto e : E)
	{
		if (e.get_power_rail() != power_rail) continue;

		if (e.get_instance_id(0) == id || e.get_instance_id(1) == id)
		{
			nets.insert(e.get_net_id());
		}
	}

	return 0;
}


//! Returns 0 if there are still instances to be placed otherwise 1.
//! Parses all the node vector polling the isPlaced field.
int graph::isDone( void )
{
	int status = 1;
	for (auto v : V)
	{
		if (!v.get_isPlaced()) { status = 0; break; }
	}

	return status;
}

int process_nodes_file( std::string nodes_file, bool file_format, graph *g )
{
	std::ifstream file;

	std::cout << "Opening '" << nodes_file << "' for parsing ... ";
	file.open(nodes_file, std::ios::in);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;
		std::string line;
		// getline returns a stream.
		// When used in a boolean context, the compiler converts it into a type that can be
		// used in the boolean context.
		while(std::getline(file, line))
		{
			if ( file_format )
			{
				g->add_node_from_string_long(line);
			}
			else
			{
				g->add_node_from_string_short(line);
			}
		}

		std::cout << "Done. Closing ... ";
		file.close();
		if (file.is_open()) std::cout << "Failed" << std::endl;
		else std::cout << "OK" << std::endl;

		g->_V_set();

		return 0;
	}
	else
	{
		std::cout << "Failed" << std::endl;

		return 1;
	}
}

int process_edges_file( std::string edges_file, bool file_format, graph *g )
{
	std::ifstream file;

	std::cout << "Opening '" << edges_file << "' for parsing ... ";
	file.open(edges_file, std::ios::in);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;
		std::string line;
		// getline returns a stream.
		// When used in a boolean context, the compiler converts it into a type that can be
		// used in the boolean context.
		while(std::getline(file, line))
		{
			if ( file_format )
			{
				g->add_edge_from_string_long(line);
			}
			else
			{
				g->add_edge_from_string_short(line);
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

// Driver function to sort the vector elements
// by second element of pairs
bool sortbysec(const std::pair<int,int> &a,
              const std::pair<int,int> &b)
{
    return (a.second > b.second);
}

std::vector<std::pair<int,int>> tally_contents( std::vector<int> vec)
{
	std::vector<std::pair<int,int>> tally;
	bool found = false;

	for(auto v : vec)
	{
		found = false;
		for(auto &p : tally)
		{
			if (v == p.first)
			{
				p.second++;
				found = true;
			}
		}

		if (!found) tally.push_back(std::make_pair(v,1));
	}

	// sort a vector of pairs according to the function sortbysec
	// sory by default sorts the vectors of pairs by the pair's 1st element. This behaviour can be overridden through a user defined function.
    sort(tally.begin(), tally.end(), sortbysec);
	return tally;
}

int graph::get_edges_with_net_and_inst_ids(int inst_id_a, int inst_id_b, int net_id, bool preserve_order, std::vector<edge> &edges)
{
	int status = 0;
	for (auto e : E )
	{
		if (e.get_net_id() == net_id)
		{
			if (preserve_order == true)
			{
				if ( (e.get_instance_id(0) == inst_id_a && e.get_instance_id(1) == inst_id_b) )
				{
					edges.push_back(e);
					status++;
				}
			}
			else
			{
				if ( (e.get_instance_id(0) == inst_id_a || e.get_instance_id(1) == inst_id_a)
						&& (e.get_instance_id(0) == inst_id_b || e.get_instance_id(1) == inst_id_b) )
				{
					edges.push_back(e);
					status++;
				}
			}
		}
	}

	return status;
}

double graph::calc_hpwl_of_inst(int id)
{
	double hpwl = 0;
	double orientation;
	node n,nn;
	std::vector<edge> edges;
	std::vector<std::pair<int,int>> neighbors;
	get_node_by_id(id, n);

	std::set<int> nets;
	std::set<int>::iterator iter;
	std::string net_name;
	get_nets_associated_with_instance( id, nets, 0 );	// 0 -> connectivity only.

	std::vector< std::set< std::pair<double, double>> > hpwl_nets;
	std::set< std::pair<double,double> > hpwl_net;

	n.get_neighbors(neighbors);

	//std::cout << std::endl;	// newline for visual segmentation

	// for net in nets ...
	iter = nets.begin();
	hpwl_nets.clear();

	for (uint32_t i=0; i < nets.size(); i++)
	{
		get_net_name(*iter, net_name);
		//std::cout << "Net : " << *iter << " ( " << net_name << " )" << std::endl;	// DEBUG
		hpwl_net.clear();

		for (auto m : neighbors)
		{
			get_node_by_id(m.first, nn);
			//std::cout << "Neighbor node " << nn.get_name();	// DEBUG
			if (nn.get_isPlaced())
			{
				edges.clear();
				get_edges_with_net_and_inst_ids(id, nn.get_id(), *iter, false, edges);

				for( auto e : edges ) // convert edges into points that can be used to compute the HPWL box
				{
					//std::cout << " is placed.";	// DEBUG
					//std::cout << " Found " << edges.size() << " edges." << std::endl;	// DEBUG

					std::pair<double,double> p, pos;
					if (e.get_instance_id(0) == id)
					{
						// inst
						orientation = n.get_orientation();	// get orientation of inst
						p = e.get_pos(0);
						//std::cout << "'" << __FUNCTION__ << "' orientation of instance " << id << " is " << orientation << ", pad pos: (" << p.first <<"," << p.second << "), ";	// DEBUG
						kicad_rotate(p, orientation);

						pos = n.get_pos();
						//std::cout << "node pos : (" << pos.first <<"," << pos.second << ")" << std::endl;	// DEBUG
						pos.first += p.first;
						pos.second += p.second;	//! KiCAD has inverted y-axis!!
						hpwl_net.insert(pos);

						// neighbor
						orientation = nn.get_orientation();	// get orientation of neighbor
						p = e.get_pos(1);
						//std::cout << "'" << __FUNCTION__ << "' orientation of neighbor " << nn.get_id() << " is " << orientation << ", pad pos: (" << p.first <<"," << p.second << "), ";	// DEBUG
						kicad_rotate(p, orientation);

						pos = nn.get_pos();
						//std::cout << "node pos : (" << pos.first <<"," << pos.second << ")" << std::endl;	// DEBUG
						pos.first += p.first;
						pos.second += p.second;	//! KiCAD has inverted y-axis!!
						hpwl_net.insert(pos);
					}
					else
					{
						// inst
						orientation = n.get_orientation();	// get orientation of inst
						p = e.get_pos(1);
						//std::cout << "'" << __FUNCTION__ << "' orientation of instance " << id << " is " << orientation << ", pad pos: (" << p.first <<"," << p.second << "), ";;	// DEBUG
						kicad_rotate(p, orientation);

						pos = n.get_pos();
						//std::cout << "node pos : (" << pos.first <<"," << pos.second << ")" << std::endl;	// DEBUG
						pos.first += p.first;
						pos.second += p.second;	//! KiCAD has inverted y-axis!!
						hpwl_net.insert(pos);

						// neighbor
						orientation = nn.get_orientation();	// get orientation of neighbor
						p = e.get_pos(0);
						//std::cout << "'" << __FUNCTION__ << "' orientation of neighbor " << nn.get_id() << " is " << orientation << ", pad pos: (" << p.first <<"," << p.second << "), ";	// DEBUG
						kicad_rotate(p, orientation);

						pos = nn.get_pos();
						//std::cout << "node pos : (" << pos.first <<"," << pos.second << ")" << std::endl;	// DEBUG
						pos.first += p.first;
						pos.second += p.second;	//! KiCAD has inverted y-axis!!
						hpwl_net.insert(pos);
					}
				}

			}
			//else std::cout << " is not placed." << std::endl;	// DEBUG
		}

		if (hpwl_net.size() > 0) hpwl_nets.push_back(hpwl_net);
		std::advance(iter, 1);
	}

	//std::cout << std::endl;
	//std::cout << "The size of hpwl_nets is " << hpwl_nets.size() << std::endl;	// DEBUG
	//std::cout << "Computing half perimeter wire length ... " << std::endl;	// DEBUG

	std::set< std::pair<double,double> >::iterator pt;

	for(auto net : hpwl_nets)
	{
		//std::cout << "Computing bounding box of net with " << net.size() << " points." << std::endl;	// DEBUG
		pt = net.begin();
		//double xmin = grid_size/grid_resolution;
		//double ymin = grid_size/grid_resolution;
		double xmin = std::numeric_limits<double>::max();
		double ymin = std::numeric_limits<double>::max();
		double xmax = 0;
		double ymax = 0;

		for (uint32_t i=0; i < net.size(); i++)
		{


			//std::cout << pt->first << "," << pt->second << std::endl;	// Debug - prints list of points used in the computation of the HPWL for a given net.
			if (pt->first > xmax) xmax = pt->first;
			if (pt->first < xmin) xmin = pt->first;
			if (pt->second > ymax) ymax = pt->second;
			if (pt->second < ymin) ymin = pt->second;

			std::advance(pt, 1);
		}

		// Debug start - prints HPWL and the its associated box
//		std::cout << "X = " << (xmax - xmin) << " "
//				<< "Y = " << (ymax-ymin) << " "
//				<< "HPWL = " << ((xmax - xmin) + (ymax-ymin)) << std::endl;
		hpwl += ((xmax - xmin) + (ymax-ymin));
//		std::cout << std::endl;
		// Debug end
	}

	return hpwl;
}

int graph::place_set_centroid(int id, double cx, double cy)
{
	int status = -1;

	for (auto &v : V)
	{
		if (v.get_id() == id)
		{
			if (v.get_isPlaced()) { break; }
			else
			{
				v.set_pos(std::make_pair(cx,cy));
				status = 0;
				break;
			}
		}
	}

	return status;
}

int graph::place_set_orientation(int id, double orientation)
{
	int status = -1;

	for (auto &v : V)
	{
		if (v.get_id() == id)
		{
			if (v.get_isPlaced()) { break; }
			else
			{
				while (orientation >= 360) orientation -=360;
				v.set_orientation(orientation);
				status = 0;
				break;
			}
		}
	}

	return status;
}

int graph::place_swap_size(int id)
{
	int status = -1;
	std::pair <double, double> size;
	double tmp;

	for (auto &v : V)
	{
		if (v.get_id() == id)
		{
			if (v.get_isPlaced()) { break; }
			else
			{
				size = v.get_size();
				tmp = size.first;
				size.first = size.second;
				size.second = tmp;
				v.set_size(size);
				status = 0;
				break;
			}
		}
	}

	return status;
}

int graph::place_confirm(int id)
{
	int status = -1;

	for (auto &v : V)
	{
		if (v.get_id() == id)
		{
			if (v.get_isPlaced()) { break; }
			else
			{
				v.set_isPlaced();
				status = 0;
				break;
			}
		}
	}

	return status;
}

double graph::calc_full_hpwl(void)
{
	double hpwl = 0, tmp = 0;

	// 1. Enumerate all nets of a given power rail.
	std::set<int> net_ids;
	net_ids.clear();
	for(auto e : E)
	{
		net_ids.insert(e.get_net_id());
	}
	std::set<int>::iterator iter;


	// 2. Accumulate HPWL for each net
	iter = net_ids.begin();

	for (uint32_t i = 0; i < net_ids.size(); i++)
	{
		//std::cout << "Net id : " << *iter << std::endl;	// Debug
		tmp = calc_hpwl_of_net(*iter, true);
		if (tmp > 0) hpwl += tmp;	// 'calc_hpwl_of_net' returns -1 if the are insufficient points.q

		std::advance(iter, 1);
	}

	return hpwl;
}

double graph::calc_hpwl( bool do_not_ignore_unplaced )
{
	double hpwl = 0, tmp = 0;

	// 1. Enumerate all nets of a given power rail.
	std::set<int> net_ids;
	std::set<int>::iterator iter;

	get_all_nets(net_ids, 0);	// 0 -> all connectivity nets

	//std::cout << "Found " << net_ids.size() << " nets." << std::endl;	// Debug


	// 2. Accumulate HPWL for each net
	iter = net_ids.begin();

	for (uint32_t i = 0; i < net_ids.size(); i++)
	{
		//std::cout << "Net id : " << *iter << std::endl;	// Debug
		tmp = calc_hpwl_of_net(*iter, do_not_ignore_unplaced);
		if (tmp > 0) hpwl += tmp;	// 'calc_hpwl_of_net' returns -1 if the are insufficient points.q

		std::advance(iter, 1);
	}

	return hpwl;
}

double graph::calc_hpwl( std::vector<std::string>& nets_to_ignore )
{
	double hpwl = 0, tmp = 0;

	// 1. Enumerate all nets of a given power rail.
	std::set<int> net_ids;
	std::set<int>::iterator iter;

	get_all_nets(net_ids, -1);	// -1 -> all nets
//	std::cout << "Found " << net_ids.size() << " nets." << std::endl;	// Debug

	for ( std::string net_to_ignore : nets_to_ignore )
	{
		int id = get_net_id_from_name(net_to_ignore);
		if (id != -1)
		{
//			Achieves same result as erase.
//			for (iter = net_ids.begin(); iter != net_ids.end(); iter++)
//			{
//				if (*iter == id)
//				{
//					net_ids.erase(iter);
//				}
//			}
			net_ids.erase(id);
		}
	}
//	std::cout << "Found " << net_ids.size() << " nets." << std::endl;	// Debug


	// 2. Accumulate HPWL for each net
	iter = net_ids.begin();

	for (uint32_t i = 0; i < net_ids.size(); i++)
	{
		//std::cout << "Net id : " << *iter << std::endl;	// Debug
		tmp = calc_hpwl_of_net(*iter);
		if (tmp > 0) hpwl += tmp;	// 'calc_hpwl_of_net' returns -1 if the are insufficient points.q

		std::advance(iter, 1);
	}

	return hpwl;
}

int graph::get_net_id_from_name(std::string& net_name)
{
	int id = -1;
	for (edge &e : E)
	{
		if (e.get_net_name() == net_name)
		{
			id = e.get_net_id();
			break;
		}
	}

	return id;
}


int graph::get_all_nets( std::set<int> &nets, int power_rail)
{

	nets.clear();
	for(auto e : E)
	{
		if ((e.get_power_rail() == power_rail) || (power_rail == -1))
		{
			nets.insert(e.get_net_id());
		}
	}

	return 0;
}

int graph::get_net_name( int net_id, std::string &net_name )
{

	for( auto e : E )
	{
		if (e.get_net_id() == net_id)
		{
			net_name = e.get_net_name();
			break;
		}
	}
	return 0;
}

double graph::calc_hpwl_of_net( int net_id, bool do_not_ignore_unplaced )
{
	double hpwl = 0;
	node n;
	std::pair<double, double> node_pos, pad_pos;
	double orientation;

	double xmin = std::numeric_limits<double>::max();
	double ymin = std::numeric_limits<double>::max();
	double xmax = 0;
	double ymax = 0;

	std::set<std::pair<double,double>> pts;
	std::set<std::pair<double,double>>::iterator iter;
	pts.clear();
	for ( auto e : E)
	{
		if (e.get_net_id() == net_id) // if net of interest.
		{
			for (int i=0; i < 2; i++) // Two pads are in every edge
			{
				get_node_by_id(e.get_instance_id(i), n);

				if (n.get_isPlaced() || do_not_ignore_unplaced == true)
				{
					node_pos = n.get_pos();
					orientation = n.get_orientation();
					pad_pos = e.get_pos(i);
					kicad_rotate(pad_pos, orientation);
					node_pos.first += pad_pos.first;
					node_pos.second += pad_pos.second;

					pts.insert(node_pos);
				}
			}
		}
	}

	if (pts.size() < 2)
	{
#ifdef DEBUG_INFO
		std::cout << "There isn't sufficient points to compute the HPWL. Have " << pts.size() << ", expected minimum of two points." << std::endl;
#endif
		hpwl = -1;
	}
	else
	{
		iter = pts.begin();
		for (uint32_t i=0; i < pts.size(); i++)
		{
			if (iter->first > xmax) xmax = iter->first;
			if (iter->first < xmin) xmin = iter->first;
			if (iter->second > ymax) ymax = iter->second;
			if (iter->second < ymin) ymin = iter->second;

			std::advance(iter, 1);
		}
#ifdef DEBUG_INFO
		std::cout << "X = " << (xmax - xmin) << " "
				<< "Y = " << (ymax-ymin) << " "
				<< "HPWL = " << ((xmax - xmin) + (ymax-ymin)) << std::endl;
#endif
		hpwl += ((xmax - xmin) + (ymax-ymin));
	}

	// DEBUG begin
//	std::string net_name;
//	get_net_name(net_id, net_name);
//	std::cout << std::endl;
//	std::cout << "=============== " << net_name << " ===============" << std::endl;
//	iter = pts.begin();
//	for (uint32_t i=0; i < pts.size(); i++)
//	{
//		std::cout << iter->first << "," << iter->second << std::endl;
//		std::advance(iter, 1);
//	}
//	std::cout << std::endl;
    // DEBUG end


	return hpwl;
}

int graph::zero_unplaced_inst_pos( void )
{
	for (auto &v : V)
	{
		if (v.get_isPlaced()) continue;
		else
		{
			v.set_pos(std::make_pair(0.0,0.0));
		}
	}

	return 0;
}

void graph::print( bool print_csv )
{
	std::cout << "GRAPH" << std::endl;
	for(auto &v : V)
	{
		v.print(print_csv);
	}

	for(auto &e : E)
	{
		e.print(print_csv);
	}
}

int graph::write_nodes_to_file(std::string filename, FILE_FORMAT format)
{
	int status = -1;
	std::ofstream file;
	std::pair<double, double> pos, size;
	std::cout << "Attempting to open file '" << filename + ".nodes" << " ... ";
	file.open(filename + ".nodes", std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << std::fixed;
		file << std::setprecision(8);

		for (auto &v : V)
		{
			pos = v.get_pos();
			size = v.get_size();
			file << v.get_id() << ",";
			if(format == LONG) file << v.get_name() << ",";
			file << size.first << ","
				<< size.second << ","
				<< pos.first << ","
				<< pos.second << ","
				<< v.get_orientation() << ","
				<< v.get_layer() << ","
				<< v.get_isPlaced() << ","
				<< v.get_pin_count() << ","
				<< v.get_smd_pin_count() << ","
				<< v.get_th_pin_count() << ","
				<< v.get_type()
				<< std::endl ;
		}
		file.close();
		if (!file.is_open()) status = 0;
	}
	else
	{
		std::cout << "Failed to open file for writing." << std::endl;
	}
	return status;
}

int graph::write_edges_to_file(std::string filename, FILE_FORMAT format)
{
	int status = -1;
	std::ofstream file;
	std::pair<double, double> pos, size;

	std::cout << "Attempting to open file '" << filename + ".edges" << " ... ";
	file.open(filename + ".edges", std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << std::fixed;
		file << std::setprecision(8);

		for (auto &e : E)
		{
			file << e.get_instance_id(0) << ",";
			if(format == LONG)
			{
				file << e.get_pad_id(0) << ",";
				file << e.get_pad_name(0) << ",";
			}

			pos = e.get_pos(0);
			size = e.get_size(0);

			file << size.first << ","
				<< size.second << ","
				<< pos.first << ","
				<< pos.second << ","
				<< e.get_instance_isPlaced(0) << ",";

			file << e.get_instance_id(1) << ",";
			if(format == LONG)
			{
				file << e.get_pad_id(1) << ",";
				file << e.get_pad_name(1) << ",";
			}

			pos = e.get_pos(1);
			size = e.get_size(1);

			file << size.first << ","
				<< size.second << ","
				<< pos.first << ","
				<< pos.second << ","
				<< e.get_instance_isPlaced(1) << ","
				<< e.get_net_id() << ",";

			if (format == LONG)
			{
				file << e.get_net_name() << ",";
			}

			file << e.get_power_rail() << std::endl;
		}
		file.close();
		if (!file.is_open()) status = 0;
	}
	else
	{
		std::cout << "Failed to open file for writing." << std::endl;
	}
	return status;
}

int graph::write_optimals_to_file(std::string filename)
{
	int status = -1;
	double euclidean_distance, hpwl;
	std::ofstream file;
	std::cout << "Attempting to open file '" << filename + ".optimals" << " ... ";
	file.open(filename + ".optimals", std::ios::out);
	if (file.is_open())
	{
		std::cout << "OK" << std::endl;

		file << std::fixed;
		file << std::setprecision(8);

		for (auto &v : V)
		{
			euclidean_distance = v.get_opt_euclidean_distance();
			hpwl = v.get_opt_hpwl();

			file << v.get_opt_id() << ","
			<< v.get_opt_name() << ","
			<< euclidean_distance << ","
			<< hpwl
			<< std::endl;
		}
		file.close();
		if (!file.is_open()) status = 0;
	}
	else
	{
		std::cout << "Failed to open file for writing." << std::endl;
	}
	return status;
}

int graph::update_original_nodes_with_current_optimals( void )
{
	for (auto &v1 : V)
	{
		for (auto &v2 : _V)
		{
			if (v1.get_id() == v2.get_id())
			{
				v2.set_opt_euclidean_distance(v1.get_opt_euclidean_distance());
				v2.set_opt_hpwl(v1.get_opt_hpwl());
				continue;
			}
		}
	}

	return 0;
}

int graph::update_node_optimal(std::string line)
{
	int status = -1;
	optimal opt;
	opt.create_from_string(line);

	for (auto &v : _V)
	{
		if (v.get_id() == opt.get_id())
		{
			if (v.get_name() != opt.get_name()) std::cout << "Warning, node name and parsed optimal name do not match for instance with id " << v.get_id() << std::endl;
			v.set_opt_id(opt.get_id());
			v.set_opt_name(opt.get_name());
			v.set_opt_euclidean_distance(opt.get_euclidean_distance());
			v.set_opt_hpwl(opt.get_hpwl());
			status = 0;
			break;
		}
	}

	for (auto &v : V)
	{
		if (v.get_id() == opt.get_id())
		{
			if (v.get_name() != opt.get_name()) std::cout << "Warning, node name and parsed optimal name do not match for instance with id " << v.get_id() << std::endl;
			v.set_opt_id(opt.get_id());
			v.set_opt_name(opt.get_name());
			v.set_opt_euclidean_distance(opt.get_euclidean_distance());
			v.set_opt_hpwl(opt.get_hpwl());
			status = 0;
			break;
		}
	}
	return status;
}


int graph::components_placed( void )
{
	int i=0;
	for (auto v : V)
	{
		if (v.get_isPlaced()) i++;
	}

	return i;
}

int graph::components_to_place( void )
{
	return (V.size() - components_placed());
}

void graph::print_graph_placement_status(void)
{
	std::cout << "==========================================" << std::endl;
	std::cout << "======    Graph placement status    ======" << std::endl;
	std::cout << "==========================================" << std::endl;

	std::cout << "Components placed           : " << components_placed() << std::endl;
	std::cout << "Components to place         : " << components_to_place() << std::endl;
	std::cout << "Graph placement completion  : " << graph_placement_completion() << std::endl;
	std::cout << std::endl;
}

int graph::find_unplaced_node( void )
{
	int status = -1; // return -1 by default
	for (auto v : V)
	{
		if (!v.get_isPlaced())
		{
			status = v.get_id();
			break;
		}
	}
	return status;
}

int graph::remove_node( int id )
{
	int status = -1;
	std::vector<node>::iterator it;
#ifdef GRAPH_COMPONENT_REMOVAL_VERBOSITY
	std::cout << "'" << __FUNCTION__ << "' - attempting to remove node with id " << id << " ... ";
#endif
	for (it=V.begin(); it!=V.end(); it++)
	{
		if (it->get_id() == id)
		{
			status = it->get_id();
			V.erase(it);
#ifdef GRAPH_COMPONENT_REMOVAL_VERBOSITY
			std::cout << "OK" << std::endl;
#endif
			break;
		}
	}

	return status;
}

int graph::find_edge_connecting_to_node(int id)
{
	int status = -1;
	std::pair<int, int> net;

	for (auto e : E)
	{
		net = e.get_edge_connectivity();
		if(net.first == id || net.second  == id)
		{
			status = e.get_net_id();
			break;
		}
	}

	return status;
}

int graph::remove_edge( int net_id )
{
	int status = -1;
	std::vector<edge>::iterator it;
#ifdef GRAPH_COMPONENT_REMOVAL_VERBOSITY
	std::cout << "'" << __FUNCTION__ << "' - attempting to remove edge with id " << net_id << " ... ";
#endif    
	for (it=E.begin(); it!=E.end(); it++)
	{
		if (it->get_net_id() == net_id)
		{
			status = it->get_net_id();
			E.erase(it);
#ifdef GRAPH_COMPONENT_REMOVAL_VERBOSITY
			std::cout << "OK" << std::endl;
#endif            
			break;
		}
	}

	return status;
}

int graph::remove_edges_associated_with_node( int id )
{
	int status = 0;
	std::vector<edge>::iterator it;
	std::pair<int, int> net;


	//1. Find_edge_connecting_to_node(id)
	while(1)
	{

		for (it=E.begin(); it!=E.end(); it++)
		{
			net = it->get_edge_connectivity();
			if(net.first == id || net.second  == id)
			{
				E.erase(it);
				status++;
				break;
			}
		}

		if (it == E.end()) break;
	}

	return status;

}

bool graph::remove_unplaced_nodes_and_associated_edges( void )
{
	int status = true;
	int node_id;
	while(1)
	{
		node_id = find_unplaced_node();
		if(node_id == -1) // There are no unplaced nodes
		{
			break;
		}
		else
		{
			remove_node(node_id);

// remove_edges_associated_with_node implemented like this to remove compile time warning.
#ifdef GRAPH_COMPONENT_REMOVAL_VERBOSITY
			int nets_removed = remove_edges_associated_with_node( node_id );
			std::cout << "'" << __FUNCTION__ << "' removed " << nets_removed << " nets from the graph." << std::endl;
#else
			remove_edges_associated_with_node( node_id );

#endif
		}
	}

	return status;
}

int graph::reorder( void )
{
	std::vector<int> ids;
	ids.clear();

	for( auto v : V )
	{
		ids.push_back(v.get_id());
	}

	std::sort(ids.begin(), ids.end());

	int j = 0;
	for (int i : ids)
	{
		if (i != j)
		{
			// change all edges with value i to j
			for (auto &e : E)
			{
				if (e.get_instance_id(0) == i) e.set_id(0, j);
				if (e.get_instance_id(1) == i) e.set_id(1, j);
			}
			// change node id with value i to j
			for ( auto &v : V)
			{
				if (v.get_id() == i) v.set_id(j);
			}
		}
		j++;
	}

	return 0;
}

void graph::print_node_area_pairs( void )
{
	std::vector< std::pair<int, double>> node_area;
	node_area = get_nodes_area_list();
	node inst;

	for ( auto na : node_area )
		{
			get_node_by_id(na.first, inst);
			std::cout << "id=" << na.first << ", designator=" << inst.get_name() << ", area=" << na.second << "mm2" << std::endl;
		}

	return;
}

int graph::components_in_net(std::string net_name )
{
	std::set<int> comps;
	comps.clear();
	for (auto e : E)
	{
		if (e.get_net_name() == net_name)
		{
			comps.insert(e.get_instance_id(0));
			comps.insert(e.get_instance_id(1));
		}
	}

	return comps.size();
}



int GRAPH::get_library_version(int &maj, int &min, int &patch)
{
	maj = VERSION_MAJOR;
	min = VERSION_MINOR;
	patch = PATCH_NUMBER;

	return 0;
}

int GRAPH::get_build_time( std::string &s )
{
	std::string tmp;
	s.clear();
	tmp = __DATE__; s += tmp;
	s += " ";
	tmp = __TIME__; s += tmp;

	return 0;
}

int GRAPH::get_cpp_standard ( std::string &s )
{
	// the macro __cplusplus will be set to a value that differs from (is greater than) the current 199711L.

	s.clear();

	if (__cplusplus == 1) s = "pre C++98";
	else if (__cplusplus == 199711L) s = "C++98";
	else if (__cplusplus == 201103L) s = "C++11";
	else if (__cplusplus == 201402L) s = "C++14";
	else if (__cplusplus == 201703L) s = "C++17";
	else if (__cplusplus == 202002L) s = "C++20";
	else s = "unknown";

	return 0;
}

int GRAPH::build_info( void )
{
	int maj=0, min=0, patch=0;
	std::string s;

	get_library_version(maj, min, patch);

	std::cout << std::endl;		// newline for visual segmentation
	std::cout << "netlist_graph: Graph pre-processing library for PCB component placement." << std::endl;
	std::cout << "Library version    : " << maj << "." << min << "." << patch << std::endl;
	get_cpp_standard ( s );
	std::cout << "Library built with : " << s << std::endl;
	get_build_time( s );
	std::cout << "Library built on   : " << s << std::endl;

	return 0;
}

std::string GRAPH::build_info_as_string( void )
{
	int maj=0, min=0, patch=0;
	std::string s;
	std::stringstream ss;

	get_library_version(maj, min, patch);

	ss << std::endl;		// newline for visual segmentation
	ss << "netlist_graph: Graph pre-processing library for PCB component placement." << std::endl;
	ss << "Library version    : " << maj << "." << min << "." << patch << std::endl;
	get_cpp_standard ( s );
	ss << "Library built with : " << s << std::endl;
	get_build_time( s );
	ss << "Library built on   : " << s << std::endl;
    ss << std::endl;

	return ss.str();
}

std::string GRAPH::get_library_version( void )
{
	int maj, min, patch;
	get_library_version(maj, min, patch);
	return ("v" + std::to_string(maj) + "." + std::to_string(min) + "." + std::to_string(patch));
}
