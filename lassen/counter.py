from peak import Peak, gen_register, family_closure, assemble
from functools import lru_cache
from .common import *

@lru_cache(None)
@family_closure
def Counter_fc(family):
    
    Data = family.BitVector[DATAWIDTH]
    Bit = family.Bit
    Reg = gen_register(Data, 0)(family)

    @assemble(family, locals(), globals())
    class Counter(Peak):
        def __init__(self):
            self.register: Reg = Reg()

        def __call__(self, en: Bit, rst: Bit, clk_en: Bit) -> (Data):
            
            # prev_count = self.register.value
            
            # new_count = prev_count
            # if rst == Bit(1):
            #     self.register(Data(0), clk_en)
            #     count = 0
            # elif en == Bit(1):
            #     count = self.register(new_count, clk_en)
            # else:
                # count = self.register(prev_count, Bit(0))
            
            return self.register(Data(0), clk_en)
    
    return Counter
    
