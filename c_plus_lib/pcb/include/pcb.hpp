/*
 * pcb.hpp
 *
 *  Created on: Jan 15, 2022
 *      Author: luke
 */

#ifndef INCLUDES_PCB_HPP_
#define INCLUDES_PCB_HPP_

#include "stdint.h"
#include "board.hpp"
#include "graph.hpp"

#include <fstream>
#include <iostream>
#include <vector>

//! Pcb class is mostly an aggregation of two classes, namely, graph and board.
//! Extra general information is also stored in the class.

class pcb
{
private:
	std::string file;
	std::string kicad_pcb;
    std::string parent_kicad_pcb;
	bool generated;

	graph grph;
	board brd;

	int id;		// id will identify a pcb in a vector of pcbs.

public:

	pcb( void ) { file = ""; kicad_pcb = "", parent_kicad_pcb = "", generated = false; id = -1;  }

	pcb( std::string &file, std::string &kicad_pcb, bool generated ) { this->file = file, this->kicad_pcb =kicad_pcb, parent_kicad_pcb = "", this->generated =generated; id = -1; }

	void set_kicad_pcb( std::string &kicad_pcb ) { this->kicad_pcb = kicad_pcb; }
	std::string& get_kicad_pcb( void ) { return this->kicad_pcb; }

	//! Returns kicad_pcb as an std::string
	std::string get_kicad_pcb2( void ) { return this->kicad_pcb; }

    void get_parent_kicad_pcb( std::string &parent_kicad_pcb ) { this->parent_kicad_pcb = parent_kicad_pcb; }
	std::string& get_parent_kicad_pcb( void ) { return this->parent_kicad_pcb; }

	//! Returns kicad_parent_pcb as an std::string
	std::string get_parent_kicad_pcb2( void ) { return this->parent_kicad_pcb; }

    void set_filename( std::string &file ) { this->file = file; }
	int get_filename( std::string &file ) { file = this->file; return 0; }
	std::string get_filename( void ) { return file; }

	bool get_generated( void ) { return this->generated; }

	void get_graph( graph &g ) { g = this->grph; }
	graph & get_graph( void ) { return this->grph; }

	void get_board( board &b ) { b = this->brd; }
	board & get_board( void ) { return this->brd; }

	void set_graph( graph &g ) { this->grph = g; }

	void set_board( board &b ) { this->brd = b; }

	// Used for kicad parser
	int write_pcb_file_from_individual_files(std::string &fileName, const std::string &nodes, const std::string &edges, const std::string &board, bool generated);

	int append_pcb_file_from_individual_files(std::string &fileName, const std::string &nodes, const std::string &edges, const std::string &board, bool generated);

	int process_board_line(std::string &line) { return brd.process_line(line); }

	int process_pcb_line(std::string &line);

	int add_edge_to_graph_from_long_line(std::string &line) { return grph.add_edge_from_string_long(line); }

	int add_node_to_graph_from_long_line(std::string &line) { return grph.add_node_from_string_long(line); }

	int update_node_optimal(std::string &line) { return grph.update_node_optimal(line); }

	// Used for placer
	//int read_pcb_file();

	//int write_pcb_file();

	void print_graph( bool print_csv );

	void set_id( int id ) { this->id = id; }
	int get_id( void ) { return this->id; }

};

int write_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &kicad_pcb, bool generated, int pcb_id=-1);

int write_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, bool generated, int pcb_id=-1);

//! Generate a .pcb file from nodes, edges, board and optimals by first creating the file then appending.
int write_pcb_file_from_individual_files_and_optimals(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &optimals, std::string &kicad_pcb, bool generated, int pcb_id=-1);

int append_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &kicad_pcb, bool generated, int pcb_id=-1);

int append_pcb_file_from_individual_files(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, bool generated, int pcb_id=-1);

//! Generate a .pcb file from nodes, edges, board and optimals files by appending.
int append_pcb_file_from_individual_files_and_optimals(std::string &fileName, std::string &nodes, std::string &edges, std::string &board, std::string &optimals, std::string &kicad_pcb, bool generated, int pcb_id=-1);

int read_pcb_file( std::string &fileName, std::vector<pcb*> &p );

int write_pcb_file( std::string &fileName, std::vector<pcb*> &p, bool append=true );

//! Consider removing
int write_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, bool placement_task, std::string &placer);
//! Consider removing
int append_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, bool placement_task, std::string &placer);

int write_pcb_file_from_pcb(std::string& full_filename, pcb *p, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params);

//! global params are only used when the file with name 'full_filename' does not exist and needs to created. In this scenario, this function calls 'write_pcb_file_from_pcb' to create the file and populate its global params.
int append_pcb_file_from_pcb(std::string& full_filename, pcb *p, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params);

//! Writes ( appends to if file exists ) a pcb from graph and board objects.
//! global_params are ignored if file already exists.
//! Consider always passing a local parameter for '.kicad_pcb" example : .kicad_pcb=PModBoard_connectors_only.kicad_pcb . This parameter is available only in pcb objects and thus has to be explicitly provided.
int write_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params);

//! Appends ( creates file and writes to if file does not exists ) a pcb from graph and board objects.
//! global_params are ignored if file already exists.
//! Consider always passing a local parameter for '.kicad_pcb" example : .kicad_pcb=PModBoard_connectors_only.kicad_pcb . This parameter is available only in pcb objects and thus has to be explicitly provided.
int append_pcb_file_from_graph_and_board(std::string &fileName, graph &g, board &b, const std::vector<std::pair<std::string, std::string>>& global_params, const std::vector<std::pair<std::string, std::string>>& local_params);

//! Checks for the existence of a file.
//! Returns 0 if a file exists, -1 if not found.
int check_for_file_existance( const std::string &filename );

namespace PCB
{
// version 0.0.2 - preliminary testing
const unsigned int VERSION_MAJOR = 0;	// Notice that #defines are not bound by namspaces.
const unsigned int VERSION_MINOR = 0;
const unsigned int PATCH_NUMBER = 12;

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

//! Prints the dependency information by calling build_info for each dependent library.
int dependency_info( void );

//! Prints the dependency information by calling build_info for each dependent library as a string.
std::string dependency_info_as_string( void );

}

#endif /* INCLUDES_PCB_HPP_ */
