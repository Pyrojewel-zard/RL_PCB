/*
 * utils.hpp
 *
 *  Created on: Jan 10, 2022
 *      Author: luke
 */

#ifndef INCLUDES_UTILS_HPP_
#define INCLUDES_UTILS_HPP_

#include <cmath>
#include <utility> 	// std::pair

//! Returns an up rounded version of numToRound to the nearest multiple.
double round_up(double numToRound, double multiple);

//! Returns an down rounded version of numToRound to the nearest multiple.
double round_down(double numToRound, double multiple);

//! Returns the nearest rounded version of numToRound to the nearest multiple.
double round_nearest(double numToRound, double multiple);

//! Rotates the values of the pair by angle degrees counter clockwise
int rotate(std::pair<double, double> &pt, double angle);

//! Uses the coordinate system employed by kicad
//! Rotates the values of the pair by angle degrees counter clockwise
int kicad_rotate(std::pair<double, double> &pt, double angle);


//! Mirrors the y-axis then perfoms a counter clockwise rotation by angle degrees.
int mirror_y_then_rotate(std::pair<double, double> &pt, double angle);

#endif /* INCLUDES_UTILS_HPP_ */
