/*
 * argparse.cpp
 *
 * Created on: Feb 13, 2021
 *     Author: Luke
 */

#include "argparse.hpp"

const char *argp_program_version =      "program_config vx.y.z";
const char *argp_program_bug_address =  "luke.vassallo95@gmail.com";

/* Program description */
const char doc[] = "processing tools for generating and working with pcb netlist graphs";

/* Usage - A description of the compulsory arguments we require*/
const char args_doc[] = "";

/* Parse a single option. */
static error_t parse_opt (int key, char *arg, struct argp_state *state)
{
  /* Get the input argument from argp_parse, which we
     know is a pointer to our arguments structure. */
  struct arguments *arguments = (struct arguments *) state->input;
  int tmp;

  switch (key)
  {
  case 'n':
      if (arguments->nodes != NULL)
      {
        free(arguments->nodes);
      }
      arguments->nodes = (char *) malloc((strlen(arg)+1) * sizeof(char));  // space for null character.
      strcpy(arguments->nodes,arg);
#ifdef DEBUG_ARGPARSE
      std::cout << "'" << __FUNCTION__ << "' - Parsed 'nodes' argument containing value - '" << arguments->nodes << "'" << std::endl;
#endif
  	break;

  case 'e':
      if (arguments->edges != NULL)
      {
        free(arguments->edges);
      }
      arguments->edges = (char *) malloc((strlen(arg)+1) * sizeof(char));  // space for null character.
      strcpy(arguments->edges,arg);
#ifdef DEBUG_ARGPARSE
      std::cout << "'" << __FUNCTION__ << "' - Parsed 'edges' argument containing value - '" << arguments->edges << "'" << std::endl;
#endif
  	break;

  case 'b':
      if (arguments->board != NULL)
      {
        free(arguments->board);
      }
      arguments->board = (char *) malloc((strlen(arg)+1) * sizeof(char));  // space for null character.
      strcpy(arguments->board,arg);
#ifdef DEBUG_ARGPARSE
      std::cout << "'" << __FUNCTION__ << "' - Parsed 'board' argument containing value - '" << arguments->board << "'" << std::endl;
#endif
  	break;

  case 257:
	  arguments->generate_gml = true;
  	break;

  case 258:
	  arguments->generate_graphviz = true;
  	break;

  case ARGP_KEY_END:	// this case iis executed after all arguments have been parsed.
#ifdef DEBUG_ARGPARSE
  	printf("parse_opt: parsed all arguments.\n\n");
#endif
  	/*if ( (arguments->mru_ip == NULL) || (arguments->mru_port == NULL) )
  	{
  		argp_usage (state);
  	}*/
   	break;

  default:
    return ARGP_ERR_UNKNOWN;
  }
  return 0;
}

// Our argp parser.
static struct argp argp = { options, parse_opt, args_doc, doc };

int init_arguments(struct arguments *args)
{
  args->nodes = NULL;
  args->edges = NULL;
  args->board = NULL;
  args->generate_gml = false;
  args->generate_graphviz = false;
  return 0;
}

int parse_args(int argc, char **argv, struct arguments *args)
{
#ifdef DEBUG_ARGPARSE
	printf("argc has the valuf of %d.\n",argc);
	puts("command line arguments:");
	for (int i =0; i < argc; i++)
	{
		printf("argv[%d] %s\n",i, argv[i]);
	}
	puts("");
#endif

	/* Default values. */
	//args = (struct arguments *) malloc(sizeof(struct arguments));     // Allocate memory for the temporary argument structure.
	init_arguments(args);                        // Initialize the temperorary argument structure.

	argp_parse(&argp, argc, argv, 0, 0, args);  // Parse for the first time with the aim of finding a configuration file.

	return 0;
}
