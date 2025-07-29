from pyfiles import pcb
from pyfiles import graph

graph.build_info()
pcb.build_info()

p = pcb.pcb()

nodes_file = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.nodes"
edges_file = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.edges"
board_file = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.board"
filename = "./test/kicad_parser/output/bistable_oscillator_with_555_timer_and_ldo"
p.write_pcb_file_from_individual_files(filename, nodes_file, edges_file, board_file, True)

filename = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo_append.pcb"
p.append_pcb_file_from_individual_files(filename, nodes_file, edges_file, board_file, False);

filename = "./test/kicad_parser/bistable_oscillator_with_555_timer_and_ldo.pcb";
