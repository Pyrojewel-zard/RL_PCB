/*
 * argparse.hpp
 *
 * Created on: Feb 13, 2021
 *     Author: Luke
 */

#ifndef ARGPARSE_HPP_
#define ARGPARSE_HPP_

#include <argp.h>
#include <stdlib.h>
#include <string.h>

/* The options we understand */
static struct argp_option options[] = {
		{"nodes", 						'n',	"<file>",		0,	".nodes file containing node information."	, OPTION_ARG_OPTIONAL},
		{"edges", 						'e', 	"<file>", 		0,  ".edges file containing edge information."	, OPTION_ARG_OPTIONAL},
		{"board",            		    'b',  	"<file>",       0,  ".board file containing board information.", OPTION_ARG_OPTIONAL},
		{"generate_gml",					257,			0,		0,  "When provided gml plot code is generated.", OPTION_ARG_OPTIONAL},
		{"generate_graphviz",					258,			0,		0,  "When provided graphviz plot code is generated.", OPTION_ARG_OPTIONAL},
		{ 0 }
};

/* Used by main to communicate with parse_opt. */
struct arguments
{
  char *nodes, *edges, *board;
  bool generate_gml, generate_graphviz;
};

static error_t parse_opt (int key, char *arg, struct argp_state *state);

int init_arguments(struct arguments *args);

int parse_args(int argc, char **argv, struct arguments *args);

#endif
