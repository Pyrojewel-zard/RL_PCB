#include <iostream>
#include <ctime>
#include <limits>

#include <optimal.hpp>

using namespace std;

/* Test procedure
 * 1. Create an object and verify default constructor
 * 2. Assign test values to object and generate formatted string
 * 3. Create a second object from the formatted string
 * 4. Verfiy the data of the second object against the test values.
 */

int8_t verify_default_constructor( void )
{
    int8_t status = 0;
    optimal opt;
    
    if (opt.get_id() != -1) { std::cout << "id of optimal object expected to be initialised to -1 by default constructor." << std::endl; status = -1; }
    if (opt.get_name() != "NULL") { std::cout << "name of optimal object expected to be initialised to 'NULL' by default constructor." << std::endl; status = -1; }
//     if (opt.get_euclidean_distance() != std::numeric_limits<double>::max()) { std::cout << "euclidean_distance of optimal object expected to be initialised to std::numeric_limits<double>::max() by default constructor." << std::endl; status = -1; }
//     if (opt.get_hpwl() != std::numeric_limits<double>::max()) { std::cout << "hpwl of optimal object expected to be initialised to std::numeric_limits<double>::max() by default constructor." << std::endl; status = -1; }
    if (opt.get_euclidean_distance() != 1000000) { std::cout << "euclidean_distance of optimal object expected to be initialised to 1000000 by default constructor." << std::endl; status = -1; }
    if (opt.get_hpwl() != 1000000) { std::cout << "hpwl of optimal object expected to be initialised to s1000000 by default constructor." << std::endl; status = -1; }
    
    if (status != 0) { std::cout << "Default constructor verification test failed." << std::endl; }
    else { std::cout << "Default constructor verification test successful." << std::endl; }
    
    return status;    
}

int8_t compare_optimals(optimal &opt_a, optimal &opt_b)
{
    int8_t status = 0;
    optimal opt;
    
    if (opt_a.get_id() != opt_b.get_id()) { std::cout << "id mismatch" << std::endl; status = -1; }
    if (opt_a.get_name() != opt_b.get_name()) { std::cout << "name mismatch." << std::endl; status = -1; }
    if (opt_a.get_euclidean_distance() != opt_b.get_euclidean_distance()) { std::cout << "euclidean_distance mismatch, with opt_a=" << opt_a.get_euclidean_distance() << " and opt_b=" << opt_b.get_euclidean_distance() << std::endl; status = -1; }
    if (opt_a.get_hpwl() != opt_b.get_hpwl()) { std::cout << "hpwl mismatch, with opt_a=" << opt_a.get_hpwl() << " and opt_b=" << opt_b.get_hpwl() << std::endl; status = -1; }

    
    if (status != 0) { std::cout << "Comparision test failed." << std::endl; }
    else { std::cout << "Comparision verification test successful." << std::endl; }
    
    return status; 
}
int main(void)
{
    time_t seconds_since_1970;

	seconds_since_1970 = time(0);
	// time(0) returns the seconds elapsed since 1970. ctime formats that result into a string,

	std::cout << "Program started " << ctime(&seconds_since_1970);
    
    verify_default_constructor();
    
    int TEST_id = 6;
    std::string TEST_name = "IC206";
    double TEST_euclidean_distance = 5.64789;
    double TEST_hpwl = 45.45356;
    std::string TEST_string = "";
    
    optimal opt_a, opt_b; 
    opt_a.set_id(TEST_id);
    opt_a.set_name(TEST_name);
    opt_a.set_euclidean_distance(TEST_euclidean_distance);
    opt_a.set_hpwl(TEST_hpwl);
    
    opt_a.format_string(TEST_string);
    
    opt_b.create_from_string(TEST_string);
    
    compare_optimals(opt_a, opt_b);
    
    // time(0) returns the seconds elapsed since 1970. ctime formats that result into a string,
	seconds_since_1970 = time(0);
	std::cout << "Program terminated " << ctime(&seconds_since_1970);
    return 0;
}
