from peak import Peak, name_outputs, family_closure, assemble, Enum_fc
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH, BFloat16_fc
from functools import lru_cache
import magma
# simulate the PE MUL
#
#   inputs
#
#   mul is the MUL operations
#   signed is whether the inputs are unsigned or signed
#   a, b - 16-bit operands
#   d - 1-bit operatnd
#
#
#   returns res, res_p, Z, N, C, V
#
#   res - 16-bit result
#   res_p - 1-bit result
#   Z (result is 0)
#   N (result is negative)
#   C (carry generated)
#   V (overflow generated)

@lru_cache(None)
def MUL_t_fc(family):
    Enum = Enum_fc(family)

    class Signed_t(Enum):
        unsigned = 0
        signed = 1

    return Signed_t


@family_closure
def MUL_fc(family):

    Data = family.BitVector[DATAWIDTH]
    SInt = family.Signed
    SData = SInt[DATAWIDTH]
    UInt = family.Unsigned
    UData = UInt[DATAWIDTH]
    Signed_t = MUL_t_fc(family)

    # @assemble(family, locals(), globals())
    # class MUL(Peak):
        #@name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
    def MUL(signed_: Signed_t, a:Data, b:Data) -> (Data):
        if signed_ == Signed_t.signed:
            a_s = SData(a)
            b_s = SData(b)
            mula, mulb = a_s.sext(16), b_s.sext(16)
            
        else:
            a_u = UData(a)
            b_u = UData(b)
            mula, mulb = a_u.zext(16), b_u.zext(16)
        mul = mula * mulb

        return mul[0:16]

    if family.Bit is magma.Bit:
        return magma.circuit.combinational(MUL)

    return MUL
