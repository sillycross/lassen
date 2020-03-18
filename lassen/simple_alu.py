from peak import Peak, name_outputs, family_closure, assemble, Enum_fc
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH
import magma

@family_closure
def ALU_t_fc(family):
    Enum = Enum_fc(family)
    class ALU_t(Enum):
        Add = 0
        Sub = 1

    """
    Whether the operation is unsigned (0) or signed (1)
    """
    class Signed_t(Enum):
        unsigned = 0
        signed = 1

    return ALU_t, Signed_t

def overflow(a, b, res):
    msb_a = a[-1]
    msb_b = b[-1]
    N = res[-1]
    return (msb_a & msb_b & ~N) | (~msb_a & ~msb_b & N)

@family_closure
def ALU_fc(family):
    def ALU_bw(width):
        BitVector = family.BitVector
        Data = family.BitVector[width]
        Bit = family.Bit
        SInt = family.Signed
        SData = SInt[width]
        UInt = family.Unsigned
        UData = UInt[width]
        UData32 = UInt[32]

        ALU_t, Signed_t = ALU_t_fc(family)

        @assemble(family, locals(), globals())
        class ALU(Peak):
            @name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
            def __call__(self, alu: ALU_t, signed_: Signed_t, a: Data, b: Data, d:Bit) -> (Data, Bit, Bit, Bit, Bit, Bit):
                


                res = Data(0)
                res_p = Bit(0)

                
                if (alu == ALU_t.Sub):
                    b = ~b
                    Cin = Bit(1)
                else:
                    Cin = Bit(0)

                C = Bit(0)
                V = Bit(0)
                # if (alu == ALU_t.Add) | (alu == ALU_t.Sub):
                    #adc needs to be unsigned
                res, C = UData(a).adc(UData(b), Cin)
                V = overflow(a, b, res)
                res_p = C
                
                N = Bit(res[-1])
                Z = (res == 0)

                return res, res_p, Z, N, C, V

        return ALU
    return ALU_bw