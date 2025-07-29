from pyfiles import pcb
from pyfiles import graph as graph     # Necessary for graph related methods
from pyfiles import board as board     # Necessary for board related methods
from pyfiles import node as node       # Necessary for node related methods
from pyfiles import edge as edge       # Necessary for edge related methods

import numpy as np

input_file_a = "./input_files/bistable_oscillator_with_555_timer.pcb"
output_file_create_a = "./output_files/bistable_oscillator_with_555_timer.pcb"
output_file_append_a = "./output_files/bistable_oscillator_with_555_timer_append.pcb"

input_file_b = "./input_files/boards.pcb"
output_file_create_b = "./output_files/boards.pcb"
output_file_append_b = "./output_files/boards_append.pcb"

pv = pcb.vptr_pcbs()
pcb.read_pcb_file(input_file_a, pv)           # Read pcb file
rng = np.random.default_rng(seed=3142)

for i in range(len(pv)):
    p = pv[i]
    g = p.get_graph()
    nn = g.get_nodes()
    
    for i in range(len(nn)):
        print(f'{nn[i].get_id()}, {nn[i].get_name()}, {nn[i].get_opt_id()}, {nn[i].get_opt_name()}, {nn[i].get_opt_euclidean_distance()}, {nn[i].get_opt_hpwl()}')
        
        nn[i].set_opt_euclidean_distance(rng.normal())
        nn[i].set_opt_hpwl(rng.normal())
        
    print()
    print("Reading back randomly written optimal values ... ")
    for i in range(len(nn)):
        print(f'{nn[i].get_opt_id()}, {nn[i].get_opt_name()}, {nn[i].get_opt_euclidean_distance()}, {nn[i].get_opt_hpwl()}')
        
    pcb.write_pcb_file(output_file_create_a, pv, False)  # Create
    pcb.write_pcb_file(output_file_append_a, pv, True)   # Append
    
print("Single desgin file write test finished. Press enter to run multiple PCB design files.")
input()
    
pv = pcb.vptr_pcbs()
pcb.read_pcb_file(input_file_b, pv)           # Read pcb file
rng = np.random.default_rng(seed=3142)

for i in range(len(pv)):
    p = pv[i]
    g = p.get_graph()
    nn = g.get_nodes()
    
    for i in range(len(nn)):
        print(f'{nn[i].get_id()}, {nn[i].get_name()}, {nn[i].get_opt_id()}, {nn[i].get_opt_name()}, {nn[i].get_opt_euclidean_distance()}, {nn[i].get_opt_hpwl()}')
        
        nn[i].set_opt_euclidean_distance(rng.normal())
        nn[i].set_opt_hpwl(rng.normal())
        
    print()
    print("Reading back randomly written optimal values ... ")
    for i in range(len(nn)):
        print(f'{nn[i].get_opt_id()}, {nn[i].get_opt_name()}, {nn[i].get_opt_euclidean_distance()}, {nn[i].get_opt_hpwl()}')
        
pcb.write_pcb_file(output_file_create_b, pv, False)  # Create
pcb.write_pcb_file(output_file_append_b, pv, True)   # Append
