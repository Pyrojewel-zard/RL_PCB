%module board
%{
/* Includes the header file in the wrapper code */
#include "board.hpp"
%}

namespace std {
};

/* Parse the header file to generate wrappers */
%include "../include/board.hpp"
