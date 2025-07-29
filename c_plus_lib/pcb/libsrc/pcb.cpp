/*
 * pcb.cpp
 *
 *  Created on: Jan 15, 2022
 *      Author: luke
 */

#include "pcb.hpp"

int pcb::write_pcb_file_from_individual_files(std::string &fileName, const std::string &nodes, const std::string &edges, const std::string &board, bool generated)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	// Check filename extension
	std::cout << "Testing file extension ... ";
	if(fileName.substr(fileName.find_last_of(".") + 1) == "pcb") { std::cout << "file contains '.pcb' extension." << std::endl; }
	else { std::cout << "file does not contain '.pcb' extension." << std::endl; fileName.append(".pcb"); }

	std::cout << "Using file with filename '" << fileName << "'" << std::endl;

	file.open(fileName, std::ios::out);

	file << "filename=" << fileName << std::endl;
	file << "timestamp=" << time(0) << std::endl;

	file.close();

	status = append_pcb_file_from_individual_files(fileName, nodes, edges, board, generated);

	return status;
}

int pcb::append_pcb_file_from_individual_files(std::string &fileName, const std::string &nodes, const std::string &edges, const std::string &board, bool generated)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	std::cout << "Checking for file '" << fileName << "' ... ";
	if (check_for_file_existance(fileName) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << nodes << "' ... ";
	if (check_for_file_existance(nodes) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << edges << "' ... ";
	if (check_for_file_existance(edges) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << board << "' ... ";
	if (check_for_file_existance(board) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	file.open(fileName, std::ios::app);
    
    file << std::fixed;
    file << std::setprecision(8);

	file << "pcb " << "begin" << std::endl;
	file << "\t" << ".kicad_pcb=" << kicad_pcb << std::endl;
	//file << "\t" << "generated=" << generated << std::endl;
	file << "\ttimestamp=" << time(0) << std::endl;
	file << "\t" << "graph begin" << std::endl;
	file << "\t\t" << "nodes begin" << std::endl;

	rd_file.open(nodes, std::ios::in);
	std::string line;
	// getline returns a stream.
	// When used in a boolean context, the compiler converts it into a type that can be
	// used in the boolean context.
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "nodes end" << std::endl;

	file << "\t\t" << "edges begin" << std::endl;
	rd_file.open(edges, std::ios::in);
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "edges end" << std::endl;
	file << "\t" << "graph end" << std::endl;

	file << "\t" << "board begin" << std::endl;
	rd_file.open(board, std::ios::in);
	while(std::getline(rd_file, line))
	{
		file << "\t\t" << line << std::endl;

	}
	file << "\t" << "board end" << std::endl;

	file << "" << "pcb end" << std::endl;

	file.close();
	if (file.is_open() == false) status = 0;

	return status;
}


int pcb::process_pcb_line(std::string &line)
{
	std::string key;
	std::string value;

	key = line.substr(0,line.find_first_of("="));
	value = line.substr(line.find_first_of("=")+1);

	//std::cout << "'" << __FUNCTION__ << "' - key=" << key << ", value=" << value << std::endl;

	if (key == ".kicad_pcb") kicad_pcb = value;
    else if ( key == "parent" ) parent_kicad_pcb = value;
	else if ( key == "id" ) id = stoi(value);
	else if ( key == "generated" ) generated = (bool) stoi(value);

	return 0;
}

// can remove??
int write_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, bool generated, int pcb_id)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	// Check filename extension
	std::cout << "Testing file extension ... ";
	if(fileName.substr(fileName.find_last_of(".") + 1) == "pcb") { std::cout << "file contains '.pcb' extension." << std::endl; }
	else { std::cout << "file does not contain '.pcb' extension." << std::endl; fileName.append(".pcb"); }

	std::cout << "Using file with filename '" << fileName << "'" << std::endl;

	file.open(fileName, std::ios::out);
    
    file << std::fixed;
	file << std::setprecision(8);

	file << "filename=" << fileName << std::endl;
	file << "timestamp=" << time(0) << std::endl;

	file.close();

	status = append_pcb_file_from_individual_files(fileName, nodes, edges, board, generated, pcb_id);

	return status;
}

int append_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, bool generated, int pcb_id)
{
	std::string kicad_parser = "";
	return append_pcb_file_from_individual_files(fileName, nodes, edges, board, kicad_parser, generated, pcb_id);
}

int write_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &kicad_pcb, bool generated, int pcb_id)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	// Check filename extension
	std::cout << "Testing file extension ... ";
	if(fileName.substr(fileName.find_last_of(".") + 1) == "pcb") { std::cout << "file contains '.pcb' extension." << std::endl; }
	else { std::cout << "file does not contain '.pcb' extension." << std::endl; fileName.append(".pcb"); }

	std::cout << "Using file with filename '" << fileName << "'" << std::endl;

	file.open(fileName, std::ios::out);
    
    file << std::fixed;
	file << std::setprecision(8);

	file << "filename=" << fileName << std::endl;
	file << "timestamp=" << time(0) << std::endl;

	file.close();

	status = append_pcb_file_from_individual_files(fileName, nodes, edges, board, kicad_pcb, generated, pcb_id);

	return status;
}

int write_pcb_file_from_individual_files_and_optimals(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &optimals, std::string &kicad_pcb, bool generated, int pcb_id)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	// Check filename extension
	std::cout << "Testing file extension ... ";
	if(fileName.substr(fileName.find_last_of(".") + 1) == "pcb") { std::cout << "file contains '.pcb' extension." << std::endl; }
	else { std::cout << "file does not contain '.pcb' extension." << std::endl; fileName.append(".pcb"); }

	std::cout << "Using file with filename '" << fileName << "'" << std::endl;

	file.open(fileName, std::ios::out);

    file << std::fixed;
	file << std::setprecision(8);

	file << "filename=" << fileName << std::endl;
	file << "timestamp=" << time(0) << std::endl;

	file.close();

	status = append_pcb_file_from_individual_files_and_optimals(fileName, nodes, edges, board, optimals, kicad_pcb, generated, pcb_id);

	return status;
}

int append_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &kicad_pcb, bool generated, int pcb_id)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	std::cout << "Checking for file '" << fileName << "' ... ";
	if (check_for_file_existance(fileName) == 0) { std::cout << "OK" << std::endl; }
	else
	{
		std::cout << "Not found ... Calling 'write_pcb_file_from_individual_files(...)' " << std::endl;
		return write_pcb_file_from_individual_files(fileName,nodes,edges,board,kicad_pcb,generated, pcb_id);
	}

	std::cout << "Checking for file '" << nodes << "' ... ";
	if (check_for_file_existance(nodes) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << edges << "' ... ";
	if (check_for_file_existance(edges) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << board << "' ... ";
	if (check_for_file_existance(board) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	file.open(fileName, std::ios::app);
    
    file << std::fixed;
	file << std::setprecision(8);

	file << "pcb " << "begin" << std::endl;
	file << "\t" << ".kicad_pcb=" << kicad_pcb << std::endl;
	//file << "\t" << "generated=" << generated << std::endl;
	file << "\ttimestamp=" << time(0) << std::endl;
	file << "\tid=" << pcb_id << std::endl;
	file << "\t" << "graph begin" << std::endl;
	file << "\t\t" << "nodes begin" << std::endl;

	rd_file.open(nodes, std::ios::in);
	std::string line;
	// getline returns a stream.
	// When used in a boolean context, the compiler converts it into a type that can be
	// used in the boolean context.
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "nodes end" << std::endl;

	file << "\t\t" << "edges begin" << std::endl;
	rd_file.open(edges, std::ios::in);
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "edges end" << std::endl;
	file << "\t" << "graph end" << std::endl;

	file << "\t" << "board begin" << std::endl;
	rd_file.open(board, std::ios::in);
	while(std::getline(rd_file, line))
	{
		file << "\t\t" << line << std::endl;

	}
	file << "\t" << "board end" << std::endl;

	file << "" << "pcb end" << std::endl;

	file.close();
	if (file.is_open() == false) status = 0;

	return status;
}

int append_pcb_file_from_individual_files_and_optimals(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &optimals, std::string &kicad_pcb, bool generated, int pcb_id)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	std::cout << "Checking for file '" << fileName << "' ... ";
	if (check_for_file_existance(fileName) == 0) { std::cout << "OK" << std::endl; }
	else
	{
		std::cout << "Not found ... Calling 'write_pcb_file_from_individual_files(...)' " << std::endl;
		return write_pcb_file_from_individual_files_and_optimals(fileName, nodes, edges, board, optimals, kicad_pcb, generated, pcb_id);
	}

	std::cout << "Checking for file '" << nodes << "' ... ";
	if (check_for_file_existance(nodes) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << edges << "' ... ";
	if (check_for_file_existance(edges) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	std::cout << "Checking for file '" << board << "' ... ";
	if (check_for_file_existance(board) == 0) { std::cout << "OK" << std::endl; }
	else { std::cout << "Not found. Exiting." << std::endl; return status; }

	file.open(fileName, std::ios::app);

    file << std::fixed;
	file << std::setprecision(8);

	file << "pcb " << "begin" << std::endl;
	file << "\t" << ".kicad_pcb=" << kicad_pcb << std::endl;
	//file << "\t" << "generated=" << generated << std::endl;
	file << "\ttimestamp=" << time(0) << std::endl;
	file << "\tid=" << pcb_id << std::endl;
	file << "\t" << "graph begin" << std::endl;
	file << "\t\t" << "nodes begin" << std::endl;

	rd_file.open(nodes, std::ios::in);
	std::string line;
	// getline returns a stream.
	// When used in a boolean context, the compiler converts it into a type that can be
	// used in the boolean context.
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "nodes end" << std::endl;

	file << "\t\t" << "optimals begin" << std::endl;

	rd_file.open(optimals, std::ios::in);
	// getline returns a stream.
	// When used in a boolean context, the compiler converts it into a type that can be
	// used in the boolean context.
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "optimals end" << std::endl;

	file << "\t\t" << "edges begin" << std::endl;
	rd_file.open(edges, std::ios::in);
	while(std::getline(rd_file, line))
	{
		file << "\t\t\t" << line << std::endl;

	}
	rd_file.close();
	file << "\t\t" << "edges end" << std::endl;
	file << "\t" << "graph end" << std::endl;

	file << "\t" << "board begin" << std::endl;
	rd_file.open(board, std::ios::in);
	while(std::getline(rd_file, line))
	{
		file << "\t\t" << line << std::endl;

	}
	file << "\t" << "board end" << std::endl;

	file << "" << "pcb end" << std::endl;

	file.close();
	if (file.is_open() == false) status = 0;

	return status;
}

//! Consider removing
int write_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, bool placement_task, std::string &placer)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	// Check filename extension
	std::cout << "Testing file extension ... ";
	if(fileName.substr(fileName.find_last_of(".") + 1) == "pcb") { std::cout << "file contains '.pcb' extension." << std::endl; }
	else { std::cout << "file does not contain '.pcb' extension." << std::endl; fileName.append(".pcb"); }

	std::cout << "Using file with filename '" << fileName << "'" << std::endl;

	file.open(fileName, std::ios::out);
    
    file << std::fixed;
	file << std::setprecision(8);

	file << "filename=" << fileName << std::endl;
	file << "timestamp=" << time(0) << std::endl;

	file.close();

	status = append_pcb_file_from_graph_and_board(fileName, g, b, placement_task, placer);

	return status;
}

//! Consider removing
int append_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, bool placement_task, std::string &placer)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	std::cout << "Checking for file '" << fileName << "' ... ";
	if (check_for_file_existance(fileName) == 0) { std::cout << "OK" << std::endl; }
	else
	{
		std::cout << "Not found ... Calling 'write_pcb_file_from_graph_and_board(...)' " << std::endl;
		return write_pcb_file_from_graph_and_board(fileName,g,b,placement_task,placer);
	}

	file.open(fileName, std::ios::app);
    
    file << std::fixed;
	file << std::setprecision(8);

	file << "pcb " << "begin" << std::endl;
	//file << "\t" << ".kicad_pcb=" << kicad_pcb << std::endl;
	//file << "\t" << "generated=" << generated << std::endl;
	//file << "\t" << "placement_task=" << (placement_task ? "yes" : "no") << std::endl;
	//file << "\t" << "placer=" << placer << std::endl;
	file << "\ttimestamp=" << time(0) << std::endl;
	file << "\t" << "graph begin" << std::endl;
	file << "\t\t" << "hpwl=" << g.get_hpwl() << std::endl;

	file << "\t\t" << "nodes begin" << std::endl;

	std::vector<node> nodes = g.get_nodes();
	std::vector<edge> edges = g.get_edges();

	std::string line;

	for (auto &n : nodes)
	{
		n.format_string_long(line);
		file << "\t\t\t" << line;
	}
	file << "\t\t" << "nodes end" << std::endl;
	file << "\t\t" << "edges begin" << std::endl;
	for (auto &e : edges)
	{
		e.format_string_long(line);
		file << "\t\t\t" << line;
	}
	file << "\t\t" << "edges end" << std::endl;
	file << "\t" << "graph end" << std::endl;

	file << "\t" << "board begin" << std::endl;

	file << "\t" << "board end" << std::endl;

	file << "" << "pcb end" << std::endl;

	file.close();
	if (file.is_open() == false) status = 0;

	return status;
}

int write_pcb_file_from_pcb(std::string& full_filename, pcb *p, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params)
{
	int status = -1;
	std::ofstream file;

	// Check filename extension
//	std::cout << "Testing file extension ... ";
	if(full_filename.substr(full_filename.find_last_of(".") + 1) == "pcb")
	{
//		std::cout << "file contains '.pcb' extension." << std::endl;
	}
	else
	{
//		std::cout << "file does not contain '.pcb' extension." << std::endl;
		full_filename.append(".pcb");
	}

//	std::cout << "Using file with filename '" << full_filename << "' ... ";

	file.open(full_filename, std::ios::out);
	if (file.is_open())
	{
//		std::cout << "OK" << std::endl;
        
        file << std::fixed;
        file << std::setprecision(8);
    
		file << "filename=" << full_filename << std::endl;
		file << "timestamp=" << time(0) << std::endl;

		for (auto p : global_params)
		{
			file << p.first << "=" << p.second << std::endl;
		}

		file.close();

		status = append_pcb_file_from_pcb(full_filename, p, global_params, local_params);

	}
	else
	{
		std::cout << "Failed to open file." << std::endl;
	}


	return status;
}

int append_pcb_file_from_pcb(std::string& full_filename, pcb *p, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

//	std::cout << "Checking for file '" << full_filename << "' ... ";
	if (check_for_file_existance(full_filename) == 0)
	{
//		std::cout << "OK" << std::endl;
	}
	else
	{
//		std::cout << "Not found ... Calling 'write_pcb_file_from_pcb(...)'" << std::endl;
		return write_pcb_file_from_pcb(full_filename,p,global_params,local_params);
	}

	file.open(full_filename, std::ios::app);
    
    file << std::fixed;
	file << std::setprecision(8);

	file << "pcb " << "begin" << std::endl;
	file << "\t" << ".kicad_pcb=" << p->get_kicad_pcb() << std::endl;
	//file << "\t" << "generated=" << p->get_generated() << std::endl;
	for (auto p : local_params)
	{
		file << "\t" << p.first << "=" << p.second << std::endl;

	}
	file << "\ttimestamp=" << time(0) << std::endl;

	graph g; p->get_graph(g);
	board b; p->get_board(b);
	std::vector<node> nodes = g.get_nodes();
	std::vector<edge> edges = g.get_edges();

	file << "\t" << "graph begin" << std::endl;
	file << "\t\t" << "hpwl=" << g.get_hpwl() << std::endl;
	file << "\t\t" << "nodes begin" << std::endl;

	std::string line;

	for (auto &n : nodes)
	{
		n.format_string_long(line);
		file << "\t\t\t" << line;
	}
	file << "\t\t" << "nodes end" << std::endl;
	file << "\t\t" << "edges begin" << std::endl;
	for (auto &e : edges)
	{
		e.format_string_long(line);
		file << "\t\t\t" << line;
	}
	file << "\t\t" << "edges end" << std::endl;
	file << "\t" << "graph end" << std::endl;

	file << "\t" << "board begin" << std::endl;
	file << "\t\tbb_min_x," << b.get_bb_min_x() << std::endl;
	file << "\t\tbb_min_y," << b.get_bb_min_y() << std::endl;
	file << "\t\tbb_max_x," << b.get_bb_max_x() << std::endl;
	file << "\t\tbb_max_y," << b.get_bb_max_y() << std::endl;
	file << "\t" << "board end" << std::endl;

	file << "" << "pcb end" << std::endl;

	file.close();
	if (file.is_open() == false) status = 0;

	return status;
}

int write_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	// Check filename extension
	std::cout << "Testing file extension ... ";
	if(fileName.substr(fileName.find_last_of(".") + 1) == "pcb") { std::cout << "file contains '.pcb' extension." << std::endl; }
	else { std::cout << "file does not contain '.pcb' extension." << std::endl; fileName.append(".pcb"); }

	std::cout << "Using file with filename '" << fileName << "'" << std::endl;

	file.open(fileName, std::ios::out);

    file << std::fixed;
	file << std::setprecision(8);

	file << "filename=" << fileName << std::endl;
	file << "timestamp=" << time(0) << std::endl;

	file.close();

	status = append_pcb_file_from_graph_and_board(fileName, g, b, global_params, local_params);

	return status;
}

int append_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params)
{
	int status = -1;
	std::ofstream file;
	std::ifstream rd_file;

	std::cout << "Checking for file '" << fileName << "' ... ";
	if (check_for_file_existance(fileName) == 0) { std::cout << "OK" << std::endl; }
	else
	{
		std::cout << "Not found ... Calling 'write_pcb_file_from_graph_and_board(...)' " << std::endl;
		return write_pcb_file_from_graph_and_board(fileName,g,b,global_params,local_params);
	}

	file.open(fileName, std::ios::app);

    file << std::fixed;
	file << std::setprecision(8);

	file << "pcb " << "begin" << std::endl;
	for (auto p : local_params)
	{
		file << "\t" << p.first << "=" << p.second << std::endl;

	}
	//file << "\t" << ".kicad_pcb=" << kicad_pcb << std::endl;
	//file << "\t" << "generated=" << generated << std::endl;
	//file << "\t" << "placement_task=" << (placement_task ? "yes" : "no") << std::endl;
	//file << "\t" << "placer=" << placer << std::endl;
	file << "\ttimestamp=" << time(0) << std::endl;
	file << "\t" << "graph begin" << std::endl;
	file << "\t\t" << "hpwl=" << g.get_hpwl() << std::endl;

	file << "\t\t" << "nodes begin" << std::endl;

	std::vector<node> nodes = g.get_nodes();
	std::vector<edge> edges = g.get_edges();

	std::string line;

	for (auto &n : nodes)
	{
		n.format_string_long(line);
		file << "\t\t\t" << line;
	}
	file << "\t\t" << "nodes end" << std::endl;
	file << "\t\t" << "edges begin" << std::endl;
	for (auto &e : edges)
	{
		e.format_string_long(line);
		file << "\t\t\t" << line;
	}
	file << "\t\t" << "edges end" << std::endl;
	file << "\t" << "graph end" << std::endl;

	file << "\t" << "board begin" << std::endl;
	file << "\t\tbb_min_x," << b.get_bb_min_x() << std::endl;
	file << "\t\tbb_min_y," << b.get_bb_min_y() << std::endl;
	file << "\t\tbb_max_x," << b.get_bb_max_x() << std::endl;
	file << "\t\tbb_max_y," << b.get_bb_max_y() << std::endl;
	file << "\t" << "board end" << std::endl;

	file << "" << "pcb end" << std::endl;

	file.close();
	if (file.is_open() == false) status = 0;

	return status;
}



int read_pcb_file( std::string &fileName, std::vector<pcb*> &p )
{
	int status = -1, i = 0;
	std::ifstream rd_file;
	std::string line;

	bool nodes = false, edges = false, board = false, pcb_tag =false, graph_tag=false;
	bool optimals = false;
	pcb *pcb_i;

	//std::cout << "Checking for file '" << fileName << "' ... ";
	if (check_for_file_existance(fileName) == 0) 
    { 
        ;//std::cout << "OK" << std::endl;
    }
	//else { std::cout << "Not found. Exiting." << std::endl; return status; }

	rd_file.open(fileName, std::ios::in);

	while(std::getline(rd_file, line))
	{
		for(i=0; i<5; i++)
		{
			if (line[i] != '\t') break;
 		}

		if (i>3) { std::cout << " Error while parsing : Read 5 tab spaces while expecting a maximum of 3." << std::endl; rd_file.close(); return status; }

		line.erase(0,i);
		if (line == "pcb begin")
		{
			//std::cout << "Found start of pcb." << std::endl;
			pcb_i = new pcb;
			pcb_tag = true; continue;
		}
		else if (line == "pcb end")
		{
			//std::cout << "Found end of pcb." << std::endl << std::endl;
			p.push_back(pcb_i);
			pcb_tag = false; continue;
		}
		else if (line == "graph begin")
		{
			//std::cout << "Found start of graph." << std::endl;
			graph_tag=true; continue;
		}
		else if (line == "graph end")
		{
			//std::cout << "Found end of graph." << std::endl;
			graph_tag=false; continue;
		}

		else if (line == "nodes begin")
		{
			//std::cout << "Found start of nodes." << std::endl;
			nodes = true; continue;
		}
		else if (line == "nodes end")
		{
			//std::cout << "Found end of nodes." << std::endl;
			nodes = false; continue;
		}
		else if (line == "optimals begin")
		{
//			std::cout << "Found start of optimals." << std::endl;
			optimals = true; continue;
		}
		else if (line == "optimals end")
		{
//			std::cout << "Found end of optimals." << std::endl;
			optimals = false; continue;
		}
		else if (line == "edges begin")
		{
			//std::cout << "Found start of edges." << std::endl;
			edges = true; continue;
		}
		else if (line == "edges end")
		{
			//std::cout << "Found end of edges." << std::endl;
			edges = false; continue;
		}
		else if (line == "board begin")
		{
			//std::cout << "Found start of board." << std::endl;
			board = true; continue;
		}
		else if (line == "board end")
		{
			//std::cout << "Found end of board." << std::endl;
			board = false; continue;
		}

		if (nodes)
		{
			//std::cout << "\t" << line << std::endl;
			//pcb_i->grph.add_node_from_string_long(line);
			pcb_i->add_node_to_graph_from_long_line(line);
		}

		if (optimals)
		{
			//std::cout << "\t" << line << std::endl;
			//pcb_i->grph.add_node_from_string_long(line);
			pcb_i->update_node_optimal(line);
		}

		if (edges)
		{
			//std::cout << "\t" << line << std::endl;
			//pcb_i->grph.add_edge_from_string_long(line);
			pcb_i->add_edge_to_graph_from_long_line(line);
		}
		if (board)
		{
			//std::cout << "\t" << line << std::endl;
			//pcb_i->brd.process_line(line);
			pcb_i->process_board_line(line);
		}

		if (pcb_tag && !graph_tag && !board)
		{
			pcb_i->process_pcb_line(line);
		}
	}

	status = 0;
	return status;
}


int write_pcb_file( std::string &fileName, std::vector<pcb*> &p_vec, bool append )
{
	int status = -1, i = 0;
	std::ofstream file;
	std::string line;

	if (append == true)	file.open(fileName, std::ios::app);
	else file.open(fileName, std::ios::out);

    file << std::fixed;
	file << std::setprecision(8);

	for ( auto *p : p_vec )
	{
		graph g;
		board b;
		p->get_graph(g);
		p->get_board(b);
		file << "pcb " << "begin" << std::endl;
		file << "\t" << ".kicad_pcb=" << p->get_kicad_pcb() << std::endl;
		//file << "\t" << "generated=" << generated << std::endl;
		//file << "\t" << "placement_task=" << (placement_task ? "yes" : "no") << std::endl;
		//file << "\t" << "placer=" << placer << std::endl;
		file << "\ttimestamp=" << time(0) << std::endl;
		file << "\t" << "graph begin" << std::endl;
		file << "\t\t" << "hpwl=" << g.get_hpwl() << std::endl;

		file << "\t\t" << "nodes begin" << std::endl;

		std::vector<node> nodes = g.get_nodes();
		std::vector<edge> edges = g.get_edges();

		std::string line;

		for (auto &n : nodes)
		{
			n.format_string_long(line);
			file << "\t\t\t" << line;
		}
		file << "\t\t" << "nodes end" << std::endl;

		file << "\t\t" << "optimals begin" << std::endl;
		for (auto &n : nodes)
		{
			n.get_opt_formatted_string(line);
			file << "\t\t\t" << line;
		}
		file << "\t\t" << "optimals end" << std::endl;

		file << "\t\t" << "edges begin" << std::endl;
		for (auto &e : edges)
		{
			e.format_string_long(line);
			file << "\t\t\t" << line;
		}
		file << "\t\t" << "edges end" << std::endl;
		file << "\t" << "graph end" << std::endl;

		file << "\t" << "board begin" << std::endl;
		file << "\t\tbb_min_x," << b.get_bb_min_x() << std::endl;
		file << "\t\tbb_min_y," << b.get_bb_min_y() << std::endl;
		file << "\t\tbb_max_x," << b.get_bb_max_x() << std::endl;
		file << "\t\tbb_max_y," << b.get_bb_max_y() << std::endl;
		file << "\t" << "board end" << std::endl;

		file << "" << "pcb end" << std::endl;
	}

	file.close();
	if (file.is_open() == false) status = 0;

	status = 0;
	return status;
}

void pcb::print_graph( bool print_csv )
{
	grph.print(print_csv);
}


int check_for_file_existance( const std::string &filename )
{
	int status;
	std::ifstream file;

	file.open(filename, std::ios::in);
	if(file.is_open()) { status = 0; file.close(); }
	else { status = -1; }

	return status;
}

int PCB::get_library_version(int &maj, int &min, int &patch)
{
	maj = VERSION_MAJOR;
	min = VERSION_MINOR;
	patch = PATCH_NUMBER;

	return 0;
}

int PCB::get_build_time( std::string &s )
{
	std::string tmp;
	s.clear();
	tmp = __DATE__; s += tmp;
	s += " ";
	tmp = __TIME__; s += tmp;

	return 0;
}

int PCB::get_cpp_standard ( std::string &s )
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

int PCB::build_info( void )
{
	int maj=0, min=0, patch=0;
	std::string s;

	get_library_version(maj, min, patch);

	std::cout << std::endl;		// newline for visual segmentation
	std::cout << "pcb library: generation of .pcb files." << std::endl;
	std::cout << "Library version    : " << maj << "." << min << "." << patch << std::endl;
	get_cpp_standard ( s );
	std::cout << "Library built with : " << s << std::endl;
	get_build_time( s );
	std::cout << "Library built on   : " << s << std::endl;
    std::cout << std::endl;

	return 0;
}

std::string PCB::build_info_as_string( void )
{
	int maj=0, min=0, patch=0;
	std::string s;
	std::stringstream ss;

	get_library_version(maj, min, patch);

	ss << std::endl;		// newline for visual segmentation
	ss << "pcb library: generation of .pcb files." << std::endl;
	ss << "Library version    : " << maj << "." << min << "." << patch << std::endl;
	get_cpp_standard ( s );
	ss << "Library built with : " << s << std::endl;
	get_build_time( s );
	ss << "Library built on   : " << s << std::endl;
    ss << std::endl;

	return ss.str();
}

std::string PCB::get_library_version( void )
{
	int maj, min, patch;
	get_library_version(maj, min, patch);
	return ("v" + std::to_string(maj) + "." + std::to_string(min) + "." + std::to_string(patch));
}

int PCB::dependency_info( void )
{
	GRAPH::build_info();
	std::cout << std::endl;

	return 0;
}

std::string PCB::dependency_info_as_string( void )
{
	return GRAPH::build_info_as_string();
}
