from pyfiles import node, edge, graph, board, pcb

p = pcb.pcb()
g = graph.graph()
b = board.board()

# Create a vector of pcb pointers to hold the list of pcbs to be read from a .pcb file.
pv = pcb.vptr_pcbs()

# Create empty vectors for nodes and edges
nv = node.n_vec()
ev = edge.e_vec()

# Read pcb file
pcb.read_pcb_file('./test/102000303_0.56_BananaSchplit_w_connectors_and_mounting_holes_2lyr.pcb',pv)

p = pv[0]                   # load pcb 
p.get_graph(g)          # copy graph
p.get_board(b)          # copy board

g.set_component_origin_to_zero(b)       # set component origin to zero

print("")
nv = g.get_nodes()
ev = g.get_edges()

V = []
E = []

duplicate = 0

for n in nv:
    v = []
    
    size = n.get_size()
    v.append(float(size[0]))
    v.append(float(size[1]))
    
    pos = n.get_pos()
    v.append(float(pos[0]))
    v.append(float(pos[1]))

    v.append(float(n.get_orientation()))
    v.append(float(n.get_pin_count()))
    #n.print_to_console(True)
    print(v)
    V.append(v)
    
print('')
    
    
for edge in ev:
    e = []
    duplicate_found = False
    # Omit all power edges
    #if (edge.get_power_rail() > 0):
        #continue
    
    # Omit GND edges only
    if (edge.get_power_rail() == 1):    
        continue
    
    e.append(int(edge.get_instance_id(0)))
    e.append(int(edge.get_instance_id(1)))
    #edge.print_to_console(True)
    print(e)
    
    for e2 in E:
        if ((e[0] == e2[0] and e[1] == e2[1]) or (e[0] == e2[1] and e[1] == e2[0])):
            duplicate += 1
            duplicate_found = True
            break
        
    if not duplicate_found:
        E.append(e)
    #print('')
    
print(f'Vertices in the graph : {len(V)}')
print(f'Edges in the graph    : {len(E)} exclusing {duplicate} duplicate edges')

