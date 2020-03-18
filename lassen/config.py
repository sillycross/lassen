from .common import DATAWIDTH
from peak import Const, Product_fc, family_closure, Tuple_fc
import magma as m

def config_arch_closure(arch):
    @family_closure
    def Config_fc(family):
        Data = family.BitVector[arch.input_width]
        Bit = family.Bit
        BitConfigData = family.BitVector[3]

        ConfigDataList = Tuple_fc(family)[(Data for _ in range(arch.num_const_reg))]


        class Config(Product_fc(family)):

            config_data_bits = BitConfigData

            if (arch.num_const_reg > 0):
                config_data = ConfigDataList


        return Config
    return Config_fc
