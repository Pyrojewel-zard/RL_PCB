%include <std_string.i>
%include <std_pair.i>
%include <std_vector.i>
%include <typemaps.i>

%module node
%{
/* Includes the header file in the wrapper code */
#include "node.hpp"
%}

namespace std {
  %template(n_vec) vector<node>;
  %template(db_pair) std::pair<double,double>;
};

/* Parse the header file to generate wrappers */
%include "../include/node.hpp"
