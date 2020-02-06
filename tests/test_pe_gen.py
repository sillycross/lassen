import fault
import magma
import shutil
from peak.assembler import Assembler
from peak import wrap_with_disassembler
from lassen import arch_closure, inst_arch_closure
from lassen.common import DATAWIDTH, BFloat16_fc
from lassen.arch import read_arch
from lassen.asm import asm_arch_closure
from lassen.alu import ALU_t_fc
from hwtypes import Bit, BitVector
import os
import sys
import random

class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))

# with open('examples/conv_3_3_balanced.json') as json_file:

arch = read_arch(str(sys.argv[1]))

width = arch.width
num_inputs = arch.num_inputs
num_outputs = arch.num_outputs
num_alu = arch.num_alu

Inst_fc = inst_arch_closure(arch)
Inst = Inst_fc(Bit.get_family())
ALU_t, Signed_t = ALU_t_fc(Bit.get_family())
Mode_t = Inst.rega
gen_inst = asm_arch_closure(arch)

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

magma.backend.coreir_.CoreIRContextSingleton().reset_instance()
magma.compile(f"{test_dir}/WrappedPE", pe_circuit, output="coreir-verilog",
              coreir_libs={"float_DW"})

def test_func_and_rtl():


    alu_list = [ALU_t.Add for _ in range(num_alu)]
    mux_list_inst_in0 = []
    mux_list_inst_in1 = []
    for i in range(len(arch.modules)):
        mux_list_inst_in0.append(BitVector[magma.math.log2_ceil(len(arch.modules[i].in0))](0))
        mux_list_inst_in1.append(BitVector[magma.math.log2_ceil(len(arch.modules[i].in1))](0))


    inst_gen = gen_inst(alu_list, mux_list_inst_in0, mux_list_inst_in1)

    inputs = [random.randint(0, 2**4) for _ in range(num_inputs)]
    inputs_to_PE = [Data(inputs[i]) for i in range(num_inputs)]

    
    signals = {}

    for i in range(num_inputs):
        signals[i] = inputs[i]

    for mod in range(len(arch.modules)):
        if (arch.modules[mod].type_ == "mul"):
            signals[arch.modules[mod].out] = signals[arch.modules[mod].in0[0]] * signals[arch.modules[mod].in1[0]]
        elif (arch.modules[mod].type_ == "alu"):
            signals[arch.modules[mod].out] = signals[arch.modules[mod].in0[0]] + signals[arch.modules[mod].in1[0]]


    res_comp = []
    for i in range(arch.num_outputs):
        res_comp.append(signals[arch.outputs[i]])

    print("Expected int result: ", res_comp)

    tester.clear()
    # Advance timestep past 0 for fp functional model (see rnd logic)
    tester.circuit.ASYNCRESET = 0
    tester.eval()
    tester.circuit.ASYNCRESET = 1
    tester.eval()
    tester.circuit.ASYNCRESET = 0
    tester.eval()

    # import pdb; pdb.set_trace()
    tester.circuit.inst = assembler(inst_gen)
    tester.circuit.CLK = 0

    tester.circuit.inputs = inputs_to_PE
    tester.eval()
    tester.circuit.O0.expect(res_comp)
        
    import pdb; pdb.set_trace()
    skip_verilator = os.path.isfile(os.path.join(test_dir, "obj_dir", "VWrappedPE__ALL.a"))

    tester.compile_and_run(target="verilator",
                           directory=test_dir,
                           flags=['-Wno-UNUSED', '-Wno-PINNOCONNECT'],
                           skip_compile=True,
                           skip_verilator=skip_verilator)
test_func_and_rtl()

print("SUCCESS: Passed all tests")
