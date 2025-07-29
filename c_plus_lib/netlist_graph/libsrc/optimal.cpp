/*
 * optimal.cpp
 *
 *  Created on: Jul 26, 2022
 *      Author: luke
 */

#include <optimal.hpp>

optimal::optimal(void)
{
	id = -1;
	name = "NULL";
//	euclidean_distance = std::numeric_limits<double>::max();
//	hpwl = std::numeric_limits<double>::max();
	euclidean_distance = 1000000;
	hpwl = 1000000;
}

int8_t optimal::create_from_string( std::string s )
{
	std::stringstream ss(s);
	std::vector<std::string> fields;
	std::string field;

	while(ss.good())
	{
		getline(ss,field,',');
		fields.push_back(field);
	}

	id = stoi(fields[0]);
	name = fields[1];
	euclidean_distance = stod(fields[2]);
	hpwl = stod(fields[3]);


	return 0;
}

int8_t optimal::format_string( std::string& line )
{
	std::stringstream l;

	l << id << ","
		<< name << ","
		<< euclidean_distance << ","
		<< hpwl
		<< std::endl;

	line = l.str();
	return 0;
}
