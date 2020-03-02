from peak import Peak, gen_register, family_closure, assemble, Enum_fc
from hwtypes.adt_util import rebind_type
from functools import lru_cache

@lru_cache(None)
def gen_register_mode(T, init=0):
    @family_closure
    def RegisterWithConst_fc(family):
        T_f = rebind_type(T, family)
        Reg = gen_register(T_f, init)(family)
        Bit = family.Bit

        @assemble(family, locals(), globals())
        class RegisterWithConst(Peak):
            def __init__(self):
                self.register: Reg = Reg()

            #Outputs <based on mode>, register_value
            def __call__(self, config_data : T_f, config_we : Bit, clk_en: Bit) -> (T_f, T_f):
                if config_we==Bit(1):
                    reg_val = self.register(config_data, Bit(1))
                else:
                    reg_val = self.register(config_data, Bit(0))

                return reg_val, reg_val
        return RegisterWithConst
    return RegisterWithConst_fc
