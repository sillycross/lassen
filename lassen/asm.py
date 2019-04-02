from dataclasses import dataclass
from .cond import gen_cond_type
from .mode import gen_mode_type
from .lut import gen_lut_type
from .isa import *
from .sim import gen_pe_type_family
from hwtypes import BitVector

sim_family = gen_pe_type_family(BitVector.get_family())
Mode = gen_mode_type(sim_family)
ALU = gen_alu_type(sim_family)
Inst = gen_inst_type(sim_family)
LUT = gen_lut_type(sim_family)
Signed = gen_signed_type(sim_family)
DataConst = sim_family.BitVector[DATAWIDTH]
BitConst = sim_family.Bit
Cond = gen_cond_type(sim_family)


def inst(alu, signed=0, lut=0, cond=Cond.Z,
         ra_mode=Mode.BYPASS, ra_const=0,
         rb_mode=Mode.BYPASS, rb_const=0,
         rd_mode=Mode.BYPASS, rd_const=0,
         re_mode=Mode.BYPASS, re_const=0,
         rf_mode=Mode.BYPASS, rf_const=0):
    """
    https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
    Format a configuration of the PE - sets all fields
    """
    return Inst(alu, Signed(signed), LUT(lut), cond,
                Mode(ra_mode), DataConst(ra_const), Mode(rb_mode),
                DataConst(rb_const), Mode(rd_mode), BitConst(rd_const),
                Mode(re_mode), BitConst(re_const), Mode(rf_mode),
                BitConst(rf_const))

# helper functions to format configurations

def add(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.Add, ra_mode=ra_mode, rb_mode=rb_mode)

def sub ():
    return inst(ALU.Sub)

def neg ():
    return inst(ALU.Sub)

def umult0 ():
    return inst(ALU.Mult0)

def umult1 ():
    return inst(ALU.Mult1)

def umult2 ():
    return inst(ALU.Mult2)

def smult0 ():
    return inst(ALU.Mult0, signed=1)

def smult1 ():
    return inst(ALU.Mult1, signed=1)

def smult2 ():
    return inst(ALU.Mult2, signed=1)

def fgetmant ():
    return inst(ALU.FGetMant)

def fp_add():
    return inst(ALU.FP_add)

def fp_mult():
    return inst(ALU.FP_mult)

def faddiexp ():
    return inst(ALU.FAddIExp)

def fsubexp ():
    return inst(ALU.FSubExp)

def fcnvexp2f ():
    return inst(ALU.FCnvExp2F)

def fgetfint ():
    return inst(ALU.FGetFInt)

def fgetffrac ():
    return inst(ALU.FGetFFrac)

def and_(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.And, ra_mode=ra_mode, rb_mode=rb_mode)

def or_(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.Or, ra_mode=ra_mode, rb_mode=rb_mode)

def xor(ra_mode=Mode.BYPASS, rb_mode=Mode.BYPASS):
    return inst(ALU.XOr, ra_mode=ra_mode, rb_mode=rb_mode)

def lsl():
    return inst(ALU.SHL)

def lsr():
    return inst(ALU.SHR)

def asr():
    return inst(ALU.SHR, signed=1)

def sel():
    return inst(ALU.Sel)

def abs():
    return inst(ALU.Abs, signed=1)

def umin():
    return inst(ALU.LTE_Min)

def umax():
    return inst(ALU.GTE_Max)

def smin():
    return inst(ALU.LTE_Min, signed=1)

def smax():
    return inst(ALU.GTE_Max, signed=1)

def eq():
    return inst(ALU.Sub, cond=Cond.Z)

def ne():
    return inst(ALU.Sub, cond=Cond.Z_n)

def ult():
    return inst(ALU.Sub, cond=Cond.ULT)

def ule():
    return inst(ALU.Sub, cond=Cond.ULE)

def ugt():
    return inst(ALU.Sub, cond=Cond.UGT)

def uge():
    return inst(ALU.Sub, cond=Cond.UGE)

def slt():
    return inst(ALU.Sub, cond=Cond.SLT)

def sle():
    return inst(ALU.Sub, cond=Cond.SLE)

def sgt():
    return inst(ALU.Sub, cond=Cond.SGT)

def sge():
    return inst(ALU.Sub, cond=Cond.SGE)
