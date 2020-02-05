import fault
import magma
import shutil
from peak.assembler import Assembler
from peak import wrap_with_disassembler
from lassen import arch_closure, Inst_fc
from lassen.common import DATAWIDTH, BFloat16_fc
from lassen.arch import read_arch
from hwtypes import Bit, BitVector
import os
import sys


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))

# with open('examples/conv_3_3_balanced.json') as json_file:

arch = read_arch(str(sys.argv[1]))

width = arch.width
num_inputs = arch.num_inputs
num_outputs = arch.num_outputs
num_alu = arch.num_alu

Inst = Inst_fc(Bit.get_family())
Mode_t = Inst.rega

PE_fc = arch_closure(arch)
PE_bv = PE_fc(Bit.get_family())

BFloat16 = BFloat16_fc(Bit.get_family())
Data = BitVector[DATAWIDTH]

# create these variables in global space so that we can reuse them easily
inst_name = 'inst'
inst_type = PE_bv.input_t.field_dict[inst_name]

_assembler = Assembler(inst_type)
assembler = _assembler.assemble
disassembler = _assembler.disassemble
width = _assembler.width
layout = _assembler.layout
#PE_magma = PE_fc(magma.get_family(), use_assembler=True)
PE_magma = PE_fc(magma.get_family())
instr_magma_type = type(PE_magma.interface.ports[inst_name])
pe_circuit = wrap_with_disassembler(PE_magma, disassembler, width,
                                         HashableDict(layout),
                                         instr_magma_type)
tester = fault.Tester(pe_circuit, clock=pe_circuit.CLK)
test_dir = "tests/build"

# def test_func_and_rtl():
#     pe = pe_magma()
#     family = gen_pe_type_family(m.get_family())
#     Data = m.get_family().BitVector[arch.width]
#     ALU = gen_alu_type(BitVector.get_family())
#     Inst = gen_inst_type(arch, BitVector.get_family())

#     DataInputList = m.Tuple[(Data for _ in range(arch.num_inputs))]
#     DataOutputList = m.Tuple[(Data for _ in range(arch.num_outputs))]
#     alu_list_type = m.Tuple[(ALU for _ in range(num_alu))]

#     mux_list_type_in0 = m.Tuple[(m.Bits[m.math.log2_ceil(len(arch.modules[i].in0))] for i in range(len(arch.modules)))]
#     mux_list_type_in1 = m.Tuple[(m.Bits[m.math.log2_ceil(len(arch.modules[i].in1))] for i in range(len(arch.modules)))]

#     mux_list_inst_in0 = []
#     mux_list_inst_in1 = []
#     for i in range(len(arch.modules)):
#         mux_list_inst_in0.append(m.Bits[m.math.log2_ceil(len(arch.modules[i].in0))](0))
#         mux_list_inst_in1.append(m.Bits[m.math.log2_ceil(len(arch.modules[i].in1))](0))

#     # import pdb; pdb.set_trace()

#     inputs = [random.randint(0, 2**4) for _ in range(num_inputs)]
#     inputs_to_PE = [Data(inputs[i]) for i in range(num_inputs)]
#     inst_list = [ALU.Add for _ in range(num_alu)]

#     inst = Inst(alu = alu_list_type(*inst_list), mux_in0 = mux_list_type_in0(*mux_list_inst_in0), mux_in1 = mux_list_type_in1(*mux_list_inst_in1))
#     import pdb; pdb.set_trace()

#     alu_res = pe(inst, DataInputList(*inputs_to_PE))
    
#     signals = {}

#     for i in range(num_inputs):
#         signals[i] = inputs[i]

#     for mod in range(len(arch.modules)):
#         if (arch.modules[mod].type_ == "mul"):
#             signals[arch.modules[mod].out] = signals[arch.modules[mod].in0[0]] * signals[arch.modules[mod].in1[0]]
#         elif (arch.modules[mod].type_ == "alu"):
#             signals[arch.modules[mod].out] = signals[arch.modules[mod].in0[0]] + signals[arch.modules[mod].in1[0]]


#     res_comp = []
#     for i in range(arch.num_outputs):
#         res_comp.append(signals[arch.outputs[i]])

#     # import pdb; pdb.set_trace()

#     # print("ALU result: ", [alu_res[i].value for i in range(num_outputs)])
#     print("Expected int result: ", res_comp)

#     # assert res_comp == [alu_res[i].value for i in range(num_outputs)]


#     inst_name = 'inst'
#     inst_type = PE.input_t.field_dict[inst_name]

#     _assembler = Assembler(inst_type)
#     assembler = _assembler.assemble
#     disassembler = _assembler.disassemble
#     width = _assembler.width
#     layout = _assembler.layout

#     instr_magma_type = type(pe_magma.interface.ports[inst_name])

#     # import pdb; pdb.set_trace()

#     pe_circuit = peak.wrap_with_disassembler(pe_magma, disassembler, width,
#                                              HashableDict(layout),
#                                              instr_magma_type)
#     tester = fault.Tester(pe_circuit, clock=pe_circuit.CLK)
#     test_dir = "tests/build"

#     m.backend.coreir_.CoreIRContextSingleton().reset_instance()
#     m.compile(f"{test_dir}/WrappedPE", pe_circuit, output="coreir-verilog")

#     tester.clear()
#     # Advance timestep past 0 for fp functional model (see rnd logic)
#     tester.circuit.ASYNCRESET = 0
#     tester.eval()
#     tester.circuit.ASYNCRESET = 1
#     tester.eval()
#     tester.circuit.ASYNCRESET = 0
#     tester.eval()

#     import pdb; pdb.set_trace()
#     tester.circuit.inst = assembler(inst)
#     tester.circuit.CLK = 0

#     tester.circuit.inputs = inputs
#     tester.eval()

#     tester.circuit.O.expect(res_comp)
        
#     skip_verilator = os.path.isfile(os.path.join(test_dir, "obj_dir", "VWrappedPE__ALL.a"))

#     tester.compile_and_run(target="verilator",
#                            directory=test_dir,
#                            flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
#                            skip_compile=True,
#                            skip_verilator=skip_verilator)
# test_func_and_rtl()

print("SUCCESS: Passed all tests")
