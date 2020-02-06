from .cond import Cond_t_fc
from .mode import Mode_t_fc
from .lut import LUT_t_fc
from .alu import ALU_t_fc
from .common import DATAWIDTH
from peak import Const, Product_fc, family_closure
import magma as m
from hwtypes import Tuple
"""
https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
"""
def inst_arch_closure(arch):
    @family_closure
    def Inst_fc(family):
        Data = family.BitVector[DATAWIDTH]
        Bit = family.Bit

        LUT_t, _ = LUT_t_fc(family)
        Cond_t = Cond_t_fc(family)
        Mode_t = Mode_t_fc(family)

        # Need this to be magma to use Tuple

        if family.Bit is m.Bit:
            ALU_t, Signed_t = ALU_t_fc(m.get_family())
            ALU_t_list_type = m.Tuple[(ALU_t for _ in range(arch.num_alu))]
            mux_list_type_in0 = m.Tuple[(family.BitVector[m.math.log2_ceil(len(arch.modules[i].in0))] for i in range(len(arch.modules)))]
            mux_list_type_in1 = m.Tuple[(family.BitVector[m.math.log2_ceil(len(arch.modules[i].in1))] for i in range(len(arch.modules)))]
        else:
            ALU_t, Signed_t = ALU_t_fc(family)
            ALU_t_list_type = Tuple[(ALU_t for _ in range(arch.num_alu))]
            mux_list_type_in0 = Tuple[(family.BitVector[m.math.log2_ceil(len(arch.modules[i].in0))] for i in range(len(arch.modules)))]
            mux_list_type_in1 = Tuple[(family.BitVector[m.math.log2_ceil(len(arch.modules[i].in1))] for i in range(len(arch.modules)))]



        class Inst(Product_fc(family)):
            alu= ALU_t_list_type          # ALU operation
            mux_in0 = mux_list_type_in0
            mux_in1 = mux_list_type_in1
            signed= Signed_t     # unsigned or signed
            lut= LUT_t          # LUT operation as a 3-bit LUT
            cond= Cond_t        # Condition code (see cond.py)
            rega= Mode_t        # RegA mode (see mode.py)
            data0= Data         # RegA constant (16-bits)
            regb= Mode_t        # RegB mode
            data1= Data         # RegB constant (16-bits)
            regd= Mode_t        # RegD mode
            bit0= Bit           # RegD constant (1-bit)
            rege= Mode_t        # RegE mode
            bit1= Bit           # RegE constant (1-bit)
            regf= Mode_t        # RegF mode
            bit2= Bit           # RegF constant (1-bit)
        return Inst
    return Inst_fc
