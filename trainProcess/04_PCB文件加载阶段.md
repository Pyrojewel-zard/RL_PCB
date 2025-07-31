# 04. PCB文件加载阶段

## 概述
PCB文件加载阶段是训练流程的核心环节，负责解析`training.pcb`文件，构建PCB数据结构，并为每个未放置的组件创建智能体。

## 详细流程

### 4.1 环境构造函数
```python
def __init__(self, parameters):
    self.parameters = parameters
    
    # 创建PCB向量容器
    self.pv = pcb.vptr_pcbs()
    
    # 读取PCB文件
    pcb.read_pcb_file(self.parameters.pcb_file, self.pv)
    
    # 验证PCB索引
    if (self.parameters.idx != -1) and (self.parameters.idx >= len(self.pv)):
        print("The supplied pcb index exceeds the number of layouts in the training set ... Program terminating")
        sys.exit()
    
    # 设置随机数生成器
    self.rng = np.random.default_rng(seed=self.parameters.seed)
    
    # 初始化环境状态
    self.initialize_environment_state_from_pcb(init=True, idx=self.parameters.idx)
    self.tracker = tracker()
```

### 4.2 PCB文件解析过程

#### 4.2.1 read_pcb_file函数
```python
def read_pcb_file(filename: str, pcb_vector: VPtrPCBs) -> int:
    """读取PCB文件"""
    status = -1
    
    if check_for_file_existance(filename) != 0:
        return status
    
    try:
        with open(filename, 'r') as rd_file:
            pcb_i = None
            nodes = False
            edges = False
            board = False
            pcb_tag = False
            graph_tag = False
            optimals = False
            
            for line in rd_file:
                # 处理缩进
                i = 0
                for i in range(5):
                    if i >= len(line) or line[i] != '\t':
                        break
                
                if i > 3:
                    print("解析错误：读取了5个制表符，但最多只能有3个。")
                    return status
                
                line = line[i:].strip()
                
                # 解析标签
                if line == "pcb begin":
                    pcb_i = PCB()
                    pcb_tag = True
                    continue
                elif line == "pcb end":
                    pcb_vector.append(pcb_i)
                    pcb_tag = False
                    continue
                elif line == "graph begin":
                    graph_tag = True
                    continue
                elif line == "graph end":
                    graph_tag = False
                    continue
                elif line == "nodes begin":
                    nodes = True
                    continue
                elif line == "nodes end":
                    nodes = False
                    continue
                elif line == "optimals begin":
                    optimals = True
                    continue
                elif line == "optimals end":
                    optimals = False
                    continue
                elif line == "edges begin":
                    edges = True
                    continue
                elif line == "edges end":
                    edges = False
                    continue
                elif line == "board begin":
                    board = True
                    continue
                elif line == "board end":
                    board = False
                    continue
                
                # 处理内容
                if nodes and pcb_i:
                    pcb_i.add_node_to_graph_from_long_line(line)
                
                if optimals and pcb_i:
                    pcb_i.update_node_optimal(line)
                
                if edges and pcb_i:
                    pcb_i.add_edge_to_graph_from_long_line(line)
                
                if board and pcb_i:
                    pcb_i.process_board_line(line)
                
                if pcb_tag and not graph_tag and not board and pcb_i:
                    pcb_i.process_pcb_line(line)
        
        status = 0
        
    except Exception as e:
        print(f"读取PCB文件时出错: {e}")
        status = -1
    
    return status
```

### 4.3 training.pcb文件结构分析

#### 4.3.1 文件头部信息
```
filename=./05_3_multi_agent_no_power_0.pcb
timestamp=1659266776
```

#### 4.3.2 PCB实例结构
```
pcb begin
	.kicad_pcb=bistable_oscillator_with_555_timer_and_ldo_2lyr_setup_00.kicad_pcb
	timestamp=1659266776
	id=0
```

#### 4.3.3 图形节点信息
```
graph begin
	nodes begin
		0,C3,3.30000000,1.46000000,116.30000000,94.20000000,0.00000000,0,0,2,2,0,-1
		1,LED2,3.35000000,1.85000000,104.29000000,95.72000000,90.00000000,0,0,2,2,0,-1
		2,R2,3.70000000,1.90000000,115.55000000,88.74000000,270.00000000,0,0,2,2,0,-1
		3,R3,3.70000000,1.90000000,116.45000000,91.80000000,180.00000000,0,0,2,2,0,-1
		4,R4,3.70000000,1.90000000,104.26000000,91.65000000,270.00000000,0,0,2,2,0,-1
		5,U1,7.40000000,5.40000000,110.00000000,90.01000000,0.00000000,0,1,8,8,0,-1
	nodes end
```

**节点数据格式（长格式）：**
根据C++代码中的`node::create_from_string_long`函数，节点数据包含13个字段：

`节点ID,组件名,宽度,高度,X坐标,Y坐标,旋转角度,层号,是否放置,引脚数,引脚数,引脚数,类型`

具体字段说明：
- `字段0`: 节点ID (int)
- `字段1`: 组件名称 (string)
- `字段2`: 宽度 (double)
- `字段3`: 高度 (double)
- `字段4`: X坐标 (double)
- `字段5`: Y坐标 (double)
- `字段6`: 旋转角度 (double)
- `字段7`: 层号 (int)
- `字段8`: 是否放置 (bool, 0=未放置, 1=已放置)
- `字段9`: 引脚数 (int)
- `字段10`: SMD引脚数 (int)
- `字段11`: 通孔引脚数 (int)
- `字段12`: 组件类型 (int)

#### 4.3.4 优化目标信息
```
optimals begin
	0,C3,1000000.00000000,1000000.00000000
	1,LED2,1000000.00000000,1000000.00000000
	2,R2,1000000.00000000,1000000.00000000
	3,R3,1000000.00000000,1000000.00000000
	4,R4,1000000.00000000,1000000.00000000
	5,U1,1000000.00000000,1000000.00000000
optimals end
```

**优化数据格式：**
根据C++代码中的`optimal::create_from_string`函数，优化数据包含4个字段：

`节点ID,组件名,欧几里得距离,HPWL`

具体字段说明：
- `字段0`: 节点ID (int)
- `字段1`: 组件名称 (string)
- `字段2`: 欧几里得距离 (double)
- `字段3`: HPWL (Half-Perimeter Wire Length) (double)

#### 4.3.5 连接边信息
```
edges begin
	0,1,2,1.07500000,0.95000000,0.86250000,0.00000000,0,1,0,1,0.95000000,0.95000000,-0.75000000,0.00000000,0,1,GND,1
	# ... 更多连接信息
edges end
```

**边数据格式（长格式）：**
根据C++代码中的`edge::create_from_string_long`函数，边数据包含19个字段：

`节点A_ID,节点A_PAD_ID,节点A_PAD名称,节点A_宽度,节点A_高度,节点A_X坐标,节点A_Y坐标,节点A_是否放置,节点B_ID,节点B_PAD_ID,节点B_PAD名称,节点B_宽度,节点B_高度,节点B_X坐标,节点B_Y坐标,节点B_是否放置,网络ID,网络名称,电源轨`

具体字段说明：
- `字段0`: 节点A的ID (int)
- `字段1`: 节点A的PAD ID (int)
- `字段2`: 节点A的PAD名称 (string)
- `字段3`: 节点A的宽度 (double)
- `字段4`: 节点A的高度 (double)
- `字段5`: 节点A的X坐标 (double)
- `字段6`: 节点A的Y坐标 (double)
- `字段7`: 节点A是否放置 (bool, 0=未放置, 1=已放置)
- `字段8`: 节点B的ID (int)
- `字段9`: 节点B的PAD ID (int)
- `字段10`: 节点B的PAD名称 (string)
- `字段11`: 节点B的宽度 (double)
- `字段12`: 节点B的高度 (double)
- `字段13`: 节点B的X坐标 (double)
- `字段14`: 节点B的Y坐标 (double)
- `字段15`: 节点B是否放置 (bool, 0=未放置, 1=已放置)
- `字段16`: 网络ID (int)
- `字段17`: 网络名称 (string)
- `字段18`: 电源轨 (int)

#### 4.3.6 电路板边界信息
```
board begin
	bb_min_x,100.00000000
	bb_min_y,80.00000000
	bb_max_x,120.00000000
	bb_max_y,100.00000000
board end
```

### 4.4 环境状态初始化

#### 4.4.1 initialize_environment_state_from_pcb函数
```python
def initialize_environment_state_from_pcb(self, init=False, idx=-1):
    if len(self.pv) == 0:
        raise ValueError(f"[ERROR] No PCB data found. Please check your training.pcb file.")
    
    # 选择PCB实例
    if idx == -1:
        self.idx = int(self.rng.integers(len(self.pv)))
    else:
        self.idx = idx
    
    self.p = self.pv[self.idx]
    
    # 初始化智能体列表
    if init:
        self.agents = []
    
    # 获取图形和电路板
    self.g = self.p.get_graph()
    self.g.reset()
    self.b = self.p.get_board()
    
    # 设置组件原点为零
    self.g.set_component_origin_to_zero(self.b)
    
    # 为每个未放置的组件创建智能体
    nn = self.g.get_nodes()
    for i in range(len(nn)):
        if nn[i].get_isPlaced() == 0:  # 未放置的组件
            node_id = nn[i].get_id()
            nets = []
            
            # 获取邻居节点
            neighbor_ids = self.g.get_neighbor_node_ids(node_id)
            neighbors = []
            for n_id in neighbor_ids:
                neighbors.append(self.g.get_node_by_id(n_id))
            
            # 获取相关边
            ee = self.g.get_edges()
            eoi = []
            for e in ee:
                if e.get_instance_id(0) == node_id or e.get_instance_id(1) == node_id:
                    eoi.append(e)
                    nets.append(e.get_net_id())
            
            # 创建智能体参数
            if init:
                agent_params = agent_parameters({
                    "board": self.b,
                    "graph": self.g,
                    "board_width": self.b.get_width(),
                    "board_height": self.b.get_height(),
                    "node": nn[i],
                    "neighbors": neighbors,
                    "eoi": eoi,
                    "net": self.parameters.net,
                    "step_size": 1.0,
                    "max_steps": self.parameters.max_steps,
                    "opt_euclidean_distance": True,
                    "opt_hpwl": True,
                    "seed": self.parameters.seed,
                    "nets": nets,
                    "max_action": self.parameters.agent_max_action,
                    "expl_noise": self.parameters.agent_expl_noise,
                    "n": self.parameters.n,      # 欧几里得距离权重
                    "m": self.parameters.m,      # 重叠惩罚权重
                    "p": self.parameters.p,      # HPWL权重
                    "ignore_power": self.parameters.ignore_power,
                    "log_file": self.parameters.log_dir
                })
                self.agents.append(agent(agent_params))
```

### 4.5 数据增强配置

#### 4.5.1 数据增强器初始化
```python
if self.parameters.use_dataAugmenter is True:
    # 配置最大平移限制
    nn = self.g.get_nodes()
    c_sz = 0
    b_sz = np.minimum(self.b.get_width(), self.b.get_height())
    
    # 找到锁定的组件
    for i in range(len(nn)):
        if nn[i].get_isPlaced() == 1:
            c_sz = np.maximum(nn[i].get_size()[0], nn[i].get_size()[1])
            break
    
    sz = (b_sz - c_sz) / 2.0
    translation_limits = [0.66*sz, 0.66*sz]
    
    # 创建数据增强器
    self.dA = dataAugmenter(
        board_size=[self.b.get_width(), self.b.get_height()],
        max_translation=translation_limits,
        goal=[[-1,-1, 0]],
        augment_position=self.parameters.augment_position,
        augment_orientation=self.parameters.augment_orientation,
        rng=self.rng
    )
```

## 关键数据结构

### PCB类
- **功能**：表示单个PCB实例
- **包含**：图形、电路板、优化信息

### Graph类
- **功能**：表示PCB的图形结构
- **包含**：节点、边、连接关系

### Board类
- **功能**：表示电路板物理属性
- **包含**：边界、尺寸、约束

### Agent类
- **功能**：表示单个组件的智能体
- **包含**：动作空间、状态空间、策略网络

## 输出信息
```
[INFO] Loading PCB file: /path/to/training.pcb
[INFO] Found 1 PCB instances
[INFO] Initializing environment with PCB index: 0
[INFO] Created 6 agents for unplaced components
[INFO] Data augmentation enabled
```

## 下一步
进入[05_智能体初始化阶段](./05_智能体初始化阶段.md) 