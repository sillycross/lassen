import json

class Arch():
    def __init__(self, width, num_inputs, num_outputs, num_alu, num_mul, num_reg, num_mux_in0, num_mux_in1, num_reg_mux, inputs, outputs, enable_input_regs, enable_output_regs):
        self.width = width
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.num_alu = num_alu
        self.num_mul = num_mul
        self.num_reg = num_reg
        self.num_mux_in0 = num_mux_in0
        self.num_mux_in1 = num_mux_in1
        self.num_reg_mux = num_reg_mux
        self.inputs = inputs
        self.outputs = outputs
        self.modules = []
        self.regs = []
        self.enable_input_regs = enable_input_regs
        self.enable_output_regs = enable_output_regs
			
class module():
    def __init__(self, id, type_, in0, in1):
        self.id = id
        self.type_ = type_
        self.in0 = in0
        self.in1 = in1

class reg():
    def __init__(self, id, in_):
        self.id = id
        self.in_ = in_

def read_arch(json_file_str):
    # with open('examples/test_json.json') as json_file:

    with open(json_file_str) as json_file:
        json_in = json.loads(json_file.read())
        num_alu = 0
        num_mul = 0
        num_reg = 0
        num_mux_in0 = 0
        num_mux_in1 = 0
        num_reg_mux = 0
        modules_json = json_in['modules']
        modules = []
        regs = []
        inputs = []
        ids = []

        for module_json in modules_json:
            if module_json['type'] == "reg":
                num_reg += 1
                new_reg = reg(module_json['id'], module_json['in'])
                
                if not isinstance(new_reg.in_, list):
                    new_reg.in_ = [new_reg.in_]

                for in0 in new_reg.in_:
                    if in0 not in inputs:
                        inputs.append(in0)
                if len(new_reg.in_) > 1:
                    num_reg_mux += 1

                if new_reg.id in inputs:
                    inputs.remove(new_reg.id)

                if new_reg.id in ids:
                    raise ValueError('Two modules with the same ID')
                else:
                    ids.append(new_reg.id)

                regs.append(new_reg)
            else:
                new_module = module( module_json['id'], module_json['type'], module_json['in0'], module_json.get('in1'))
                
                if new_module.type_ == "alu":
                    num_alu += 1
                elif new_module.type_ == "mul":
                    num_mul += 1
                else:
                    raise ValueError('Unrecognized module type in specification')

                if not isinstance(new_module.in0, list):
                    new_module.in0 = [new_module.in0]
                for in0 in new_module.in0:
                    if in0 not in inputs:
                        inputs.append(in0)
                if len(new_module.in0) > 1:
                    num_mux_in0 += 1

                if not isinstance(new_module.in1, list):
                    new_module.in1 = [new_module.in1]
                for in1 in new_module.in1:
                    if in1 not in inputs:
                        inputs.append(in1)
                if len(new_module.in1) > 1:
                    num_mux_in1 += 1

                if new_module.id in ids:
                    raise ValueError('Two modules with the same ID')
                else:
                    ids.append(new_module.id)

                modules.append(new_module)

        unique_inputs = list(set(inputs) - set(ids))
        num_inputs = len(unique_inputs)
        num_outputs = len(json_in['outputs'])

        print(unique_inputs)

        for module_ in modules:
            if not isinstance(module_.in0, list):
                module_.in0 = [module_.in0]
            if not isinstance(module_.in1, list):
                module_.in1 = [module_.in1]


        arch = Arch(json_in.get('width', 16), num_inputs, num_outputs, num_alu, num_mul, 
                    num_reg, num_mux_in0, num_mux_in1, num_reg_mux, unique_inputs, json_in['outputs'], 
                    json_in.get('enable_input_regs', False), json_in.get('enable_output_regs', False))
        arch.modules = modules
        arch.regs = regs
        return arch


def graph_arch(arch: Arch):
    from graphviz import Digraph

    graph = Digraph()

    for module in arch.modules:
        if module.type_ == "alu":
            graph.node(str(module.id), "alu")
        elif module.type_ == "mul":
            graph.node(str(module.id), "mul")
        
        for in0 in module.in0:
            graph.edge(str(in0), str(module.id))
        for in1 in module.in1:
            graph.edge(str(in1), str(module.id))

    for reg in arch.regs:
        graph.node(str(reg.id), "reg")

        for in_ in reg.in_:
            graph.edge(str(in_), str(reg.id))

    for i, output in enumerate(arch.outputs):
        graph.edge(str(output), "out_" + str(i))

    print(graph.source)
    graph.render("arch_graph", view=True)