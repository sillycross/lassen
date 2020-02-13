import json

class Arch():
    def __init__(self, width, num_inputs, num_outputs, num_alu, num_mul, num_mux_in0, num_mux_in1, inputs, outputs, enable_input_regs, enable_output_regs):
        self.width = width
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.num_alu = num_alu
        self.num_mul = num_mul
        self.num_mux_in0 = num_mux_in0
        self.num_mux_in1 = num_mux_in1
        self.inputs = inputs
        self.outputs = outputs
        self.modules = []
        self.enable_input_regs = enable_input_regs
        self.enable_output_regs = enable_output_regs
			
class module():
    def __init__(self, id, type_, in0, in1):
        self.id = id
        self.type_ = type_
        self.in0 = in0
        self.in1 = in1

def read_arch(json_file_str):
    # with open('examples/test_json.json') as json_file:

    with open(json_file_str) as json_file:
        json_in = json.loads(json_file.read())
        num_alu = 0
        num_mul = 0
        num_mux_in0 = 0
        num_mux_in1 = 0
        modules_json = json_in['modules']
        modules = []
        inputs = []
        ids = []

        for module_json in modules_json:
            new_module = module( module_json['id'], module_json['type'], module_json['in0'], module_json['in1'])
            modules.append(new_module)
            
            if new_module.type_ == "alu":
                num_alu += 1
            elif new_module.type_ == "mul":
                num_mul += 1
            else:
                raise ValueError('Unrecognized module type in specification')
            if isinstance(new_module.in0, list) and len(new_module.in0) > 1:
                num_mux_in0 += 1
                for in0 in new_module.in0:
                    if in0 not in inputs:
                        inputs.append(in0)
            else:
                if new_module.in0 not in inputs:
                    inputs.append(new_module.in0)

            if isinstance(new_module.in1, list) and len(new_module.in1) > 1:
                num_mux_in1 += 1
                for in1 in new_module.in1:
                    if in1 not in inputs:
                        inputs.append(in1)
            else:
                if new_module.in1 not in inputs:
                    inputs.append(new_module.in1)

            if new_module.id in ids:
                raise ValueError('Two modules with the same ID')
            else:
                ids.append(new_module.id)

        unique_inputs = list(set(inputs) - set(ids))
        num_inputs = len(unique_inputs)
        num_outputs = len(json_in['outputs'])

        print(unique_inputs)

        signals = unique_inputs
        for module_ in modules:
            if not isinstance(module_.in0, list):
                module_.in0 = [module_.in0]
            if not isinstance(module_.in1, list):
                module_.in1 = [module_.in1]

            for in0 in module_.in0:
                if in0 not in signals:
                    raise ValueError('Make sure there are no self-loops in your specification')
            for in1 in module_.in1:
                if in1 not in signals:
                    raise ValueError('Make sure there are no self-loops in your specification')
            signals.append(module_.id)

        arch = Arch(json_in.get('width', 16), num_inputs, num_outputs, num_alu, num_mul, num_mux_in0, num_mux_in1, unique_inputs, json_in['outputs'], json_in.get('enable_input_regs', False), json_in.get('enable_output_regs', False))
        arch.modules = modules
        return arch


