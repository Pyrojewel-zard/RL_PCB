/*
 * utils.cpp
 *
 *  Created on: Jan 10, 2022
 *      Author: luke
 */

#include "utils.hpp"

double round_up(double numToRound, double multiple)
{
    if (multiple == 0)
        return numToRound;

    double r = remainder(fabs(numToRound), multiple);
    if (r == 0)
    	return numToRound;
    else if (r < 0)
    	r += multiple;

    if (numToRound < 0)
        return -(fabs(numToRound) - r);
    else
        return numToRound + multiple - r;
}

double round_down(double numToRound, double multiple)
{
    if (multiple == 0)
        return numToRound;

    double r = remainder(fabs(numToRound), multiple);
    if (r == 0)
        return numToRound;

    if (numToRound < 0)
        return -(fabs(numToRound) + multiple - r);
    else
        return numToRound - r;
}

double round_nearest(double numToRound, double multiple)
{
    if (multiple == 0)
        return numToRound;

    double r = remainder(fabs(numToRound), multiple);

    if (r > multiple/2) return round_up(numToRound, multiple);
    else return round_down(numToRound, multiple);

}

int rotate(std::pair<double, double> &pt, double angle)
{
	 // --             --     -- --
	 // | cos()  -sin() | \/  | x |
	 // | sin()   cos() | /\  | y |
	 // --             --     -- --

	std::pair<double, double> p = pt;
	double theta =  M_PI * (angle / 180.0);
	//std::cout << theta << std::endl;
	pt.first = p.first * cos( theta ) - p.second * sin( theta );
	pt.second = p.first * sin( theta ) + p.second * cos( theta );

	return 0;
}

int kicad_rotate(std::pair<double, double> &pt, double angle)
{
	 // --             --     -- --
	 // |  cos()   sin() | \/  | x |
	 // | -sin()   cos() | /\  | y |
	 // --             --     -- --

	std::pair<double, double> p = pt;
	double theta =  M_PI * (angle / 180.0);
	//std::cout << theta << std::endl;
	pt.first = p.first * cos( theta ) + p.second * sin( theta );
	pt.second = - p.first * sin( theta ) + p.second * cos( theta );

	return 0;
}

int mirror_y_then_rotate(std::pair<double, double> &pt, double angle)
{
	// Combined y - axis mirror followed by counter clockwise rotation
	// Remember the order in which the matrices on the LHS are multiplied is important.
	// --    --    --             --     -- --
	// | 1  0 | \/ | cos()  -sin() | \/  | x |
	// | 0 -1 | /\ | sin()   cos() | /\  | y |
	// --    --    --             --     -- --
	//

	// Simplified ...
	// --              --     -- --
	// |  cos()  -sin() | \/  | x |
	// | -sin()  -cos() | /\  | y |
	// --              --     -- --

	std::pair<double, double> p = pt;
	double theta =  M_PI * (angle / 180.0);
	//std::cout << theta << std::endl;
	pt.first = p.first * cos( theta ) - p.second * sin( theta );
	pt.second = -(p.first * sin( theta ) + p.second * cos( theta ));


    return 0;
}


