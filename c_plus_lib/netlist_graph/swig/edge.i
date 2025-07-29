%include <std_string.i>
%include <std_vector.i>
%include <typemaps.i>

%module edge
%{
/* Includes the header file in the wrapper code */
#include "edge.hpp"
%}

namespace std {
  %template(e_vec) vector<edge>;
};

/* Parse the header file to generate wrappers */
%include "../include/edge.hpp"
