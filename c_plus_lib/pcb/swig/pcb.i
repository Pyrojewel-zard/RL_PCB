%include <std_string.i>
%include <typemaps.i>

%apply std::string& INOUT {std::string& fileName}

%include "std_vector.i"


%module pcb
%{
/* Includes the header file in the wrapper code */
#include "pcb.hpp"
%}

namespace std {
  %template(vectorpcbs) vector<pcb>;
  %template(vptr_pcbs) vector<pcb*>;
};

%apply std::vector& INOUT {std::vector& p}

/* Parse the header file to generate wrappers */
%include "../include/pcb.hpp"
