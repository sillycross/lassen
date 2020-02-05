import json

class Arch():
    def __init__(self, width, num_inputs, num_outputs, num_alu, num_mul, outputs):
        self.width = width
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.num_alu = num_alu
        self.num_mul = num_mul
        self.outputs = outputs
        self.modules = []
			
class module():
    def __init__(self, type_, out, in0, in1):
        self.type_ = type_
        self.out = out
        self.in0 = in0
        self.in1 = in1

def read_arch(json_file_str):
    # with open('examples/test_json.json') as json_file:

    with open(json_file_str) as json_file:
        json_in = json.loads(json_file.read())
        num_alu = 0
        num_mul = 0
        modules_json = json_in['modules']
        modules = []
        for module_json in modules_json:
            modules.append(module(module_json['type'], module_json['out'], module_json['in0'], module_json['in1']))
            if module_json['type'] == "alu":
                num_alu += 1
            elif module_json['type'] == "mul":
                num_mul += 1
            else:
                raise ValueError('Unrecognized module type in specification')
        arch = Arch(json_in['width'], json_in['num_inputs'], json_in['num_outputs'], num_alu, num_mul, json_in['outputs'])
    
    # modules_sorted = []
    # signals = list(range(arch.num_inputs))

    # counter = len(modules)

    # while len(modules) > 0:
    #     if counter == 0:
    #         raise ValueError('Make sure there are no self-loops in your specification')
    #     module_ = modules[0]
    #     signals_in_list = True
    #     for in0 in module_.in0:
    #         if in0 not in signals:
    #             signals_in_list = False
    #     for in1 in module_.in1:
    #         if in1 not in signals:
    #             signals_in_list = False
    #     if signals_in_list:
    #         counter = len(modules)
    #         making_progress = True
    #         signals.append(module_.out)
    #         modules_sorted.append(module_)
    #         modules.remove(module_)
    #     else:
    #         counter -= 1
    #         modules.remove(module_)
    #         modules.append(module_)

    signals = list(range(arch.num_inputs))
    for module_ in modules:
        signals_in_list = True
        for in0 in module_.in0:
            if in0 not in signals:
                raise ValueError('Make sure there are no self-loops in your specification')
        for in1 in module_.in1:
            if in1 not in signals:
                raise ValueError('Make sure there are no self-loops in your specification')
        signals.append(module_.out)

    arch.modules = modules
    return arch
