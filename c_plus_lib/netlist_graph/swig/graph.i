%include <std_string.i>
%include <std_vector.i>
%include <std_set.i>
%include <typemaps.i>

%module graph
%{
/* Includes the header file in the wrapper code */
#include "graph.hpp"
%}

namespace std {
  %template(n_vec) vector<node>;
  %template(e_vec) vector<edge>;
  %template(set_i) set<int>;
};

/* Parse the header file to generate wrappers */
%include "../include/graph.hpp"
