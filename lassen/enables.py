from .common import DATAWIDTH
from peak import Const, Product_fc, family_closure
import magma as m
from hwtypes import Tuple

def enables_arch_closure(arch):
    @family_closure
    def Enables_fc(family):
        Data = family.BitVector[DATAWIDTH]
        Bit = family.Bit

        # Need this to be magma to use Tuple
        if family.Bit is m.Bit:
            enablesList = m.Tuple[(Bit for _ in range(arch.num_reg))]
        else:
            enablesList = Tuple[(Bit for _ in range(arch.num_reg))]


        class Enables(Product_fc(family)):

            clk_en = Bit

            if (arch.num_reg > 0):
                reg_enables = enablesList


        return Enables
    return Enables_fc
