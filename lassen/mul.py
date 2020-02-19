from peak import Peak, name_outputs, family_closure, assemble, Enum_fc
from peak.mapper.utils import rebind_type
from .common import DATAWIDTH, BFloat16_fc
from functools import lru_cache
import magma


@family_closure
def MUL_t_fc(family):
    Enum = Enum_fc(family)
    class MUL_t(Enum):

        Mult0 = 0x0
        Mult1 = 0x1
        Mult2 = 0x2


    """
    Whether the operation is unsigned (0) or signed (1)
    """
    class Signed_t(Enum):
        unsigned = 0
        signed = 1

    return MUL_t, Signed_t


@family_closure
def MUL_fc(family):

    Data = family.BitVector[DATAWIDTH]
    SInt = family.Signed
    SData = SInt[DATAWIDTH]
    UInt = family.Unsigned
    UData = UInt[DATAWIDTH]
    MUL_t, Signed_t = MUL_t_fc(family)

    # @assemble(family, locals(), globals())
    # class MUL(Peak):
        #@name_outputs(res=Data, res_p=Bit, Z=Bit, N=Bit, C=Bit, V=Bit)
    def MUL(instr: MUL_t, signed_: Signed_t, a:Data, b:Data) -> (Data):


        if signed_ == Signed_t.signed:
            a_s = SData(a)
            b_s = SData(b)
            mula, mulb = a_s.sext(16), b_s.sext(16)
        else:
            a_u = UData(a)
            b_u = UData(b)
            mula, mulb = a_u.zext(16), b_u.zext(16)
        mul = mula * mulb

        if instr == MUL_t.Mult0:
            res = mul[:16]
           
        elif instr == MUL_t.Mult1:
            res = mul[8:24]
           
        else:
            res = mul[16:32]
            
        return res

    if family.Bit is magma.Bit:
        return magma.circuit.combinational(MUL)

    return MUL
