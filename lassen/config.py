from .common import DATAWIDTH
from peak import Const, Product_fc, family_closure
import magma as m
from hwtypes import Tuple
"""
https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
"""
def config_arch_closure(arch):
    @family_closure
    def Config_fc(family):
        Data = family.BitVector[DATAWIDTH]
        Bit = family.Bit
        BitConfigData = family.BitVector[3]

        # Need this to be magma to use Tuple
        if family.Bit is m.Bit:
            ConfigDataList = m.Tuple[(Data for _ in range(arch.num_const_reg))]
        else:
            ConfigDataList = Tuple[(Data for _ in range(arch.num_const_reg))]


        class Config(Product_fc(family)):

            config_data_bits = BitConfigData

            if (arch.num_const_reg > 0):
                config_data = ConfigDataList


        return Config
    return Config_fc
