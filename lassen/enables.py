from .common import DATAWIDTH
from peak import Const, Product_fc, family_closure, Tuple_fc
import magma as m

def enables_arch_closure(arch):
    @family_closure
    def Enables_fc(family):
        Data = family.BitVector[DATAWIDTH]
        Bit = family.Bit

        enablesList = Tuple_fc(family)[(Bit for _ in range(arch.num_reg))]


        class Enables(Product_fc(family)):

            clk_en = Bit

            if (arch.num_reg > 0):
                reg_enables = enablesList


        return Enables
    return Enables_fc
