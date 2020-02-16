from dataclasses import dataclass
from .isa import inst_arch_closure
from hwtypes import BitVector, Bit, Tuple
import magma as m
from .common import DATAWIDTH

def asm_arch_closure(arch):
    Inst_fc = inst_arch_closure(arch)
    Inst = Inst_fc(Bit.get_family())
    Data = BitVector[DATAWIDTH]
    LUT_t = Inst.lut
    Cond_t = Inst.cond
    Mode_t = Inst.regd
    ALU_t_list_type = Inst.alu
    Signed_t = Inst.signed
    BitConst = Inst.bit0

    Mode_t_list_type = Inst.reg
    Data_list_type = Inst.data
    
    if arch.num_mux_in0 > 0:
        mux_list_type_in0 = Inst.mux_in0
    if arch.num_mux_in1 > 0:
        mux_list_type_in1 = Inst.mux_in1
    if arch.num_reg_mux > 0:
        mux_list_type_reg = Inst.mux_reg

    #Lut Constants
    # B0 = BitVector[8]([0, 1, 0, 1, 0, 1, 0, 1])
    # B1 = BitVector[8]([0, 0, 1, 1, 0, 0, 1, 1])
    # B2 = BitVector[8]([0, 0, 0, 0, 1, 1, 1, 1])

    def gen_inst(alu, mux_in0, mux_in1, mux_reg, signed=Signed_t.unsigned, lut=0, cond=Cond_t.Z,
            reg_mode=[Mode_t.BYPASS for _ in range(arch.num_inputs)], reg_const=[Data(0) for _ in range(arch.num_inputs)],  
            rd_mode=Mode_t.BYPASS, rd_const=0,
            re_mode=Mode_t.BYPASS, re_const=0,
            rf_mode=Mode_t.BYPASS, rf_const=0):
        """
        https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
        Format a configuration of the PE - sets all fields
        """
        if arch.num_reg_mux > 0:
            if arch.num_mux_in0 > 0 and arch.num_mux_in1 > 0:
                return Inst(ALU_t_list_type(*alu), mux_list_type_in0(*mux_in0), mux_list_type_in1(*mux_in1), mux_list_type_reg(*mux_reg), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
            elif arch.num_mux_in0 > 0:
                return Inst(ALU_t_list_type(*alu), mux_list_type_in0(*mux_in0), mux_list_type_reg(*mux_reg), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
            elif arch.num_mux_in1 > 0:
                return Inst(ALU_t_list_type(*alu), mux_list_type_in1(*mux_in1), mux_list_type_reg(*mux_reg), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
            else:
                return Inst(ALU_t_list_type(*alu), mux_list_type_reg(*mux_reg), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
        else:
            if arch.num_mux_in0 > 0 and arch.num_mux_in1 > 0:
                return Inst(ALU_t_list_type(*alu), mux_list_type_in0(*mux_in0), mux_list_type_in1(*mux_in1), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
            elif arch.num_mux_in0 > 0:
                return Inst(ALU_t_list_type(*alu), mux_list_type_in0(*mux_in0), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
            elif arch.num_mux_in1 > 0:
                return Inst(ALU_t_list_type(*alu), mux_list_type_in1(*mux_in1), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
            else:
                return Inst(ALU_t_list_type(*alu), signed, LUT_t(lut), cond,
                            Mode_t_list_type(*reg_mode), Data_list_type(*reg_const), Mode_t(rd_mode), BitConst(rd_const),
                            Mode_t(re_mode), BitConst(re_const), Mode_t(rf_mode),
                            BitConst(rf_const))
    return gen_inst

# helper functions to format configurations

# def add(**kwargs):
#     return inst(ALU_t.Add, **kwargs)

# def sub(**kwargs):
#     return inst(ALU_t.Sub, **kwargs)

# def adc(**kwargs):
#     return inst(ALU_t.Adc, **kwargs)

# def sbc(**kwargs):
#     return inst(ALU_t.Sbc, **kwargs)

# def neg(**kwargs):
#     return inst(ALU_t.Sub, **kwargs)

# def umult0(**kwargs):
#     return inst(ALU_t.Mult0, **kwargs)

# def umult1(**kwargs):
#     return inst(ALU_t.Mult1, **kwargs)

# def umult2(**kwargs):
#     return inst(ALU_t.Mult2, **kwargs)

# def smult0(**kwargs):
#     return inst(ALU_t.Mult0, signed=Signed_t.signed, **kwargs)

# def smult1(**kwargs):
#     return inst(ALU_t.Mult1, signed=Signed_t.signed, **kwargs)

# def smult2(**kwargs):
#     return inst(ALU_t.Mult2, signed=Signed_t.signed, **kwargs)

# def fgetmant(**kwargs):
#     return inst(ALU_t.FGetMant, **kwargs)

# def fp_add(**kwargs):
#     return inst(ALU_t.FP_add, **kwargs)

# def fp_sub(**kwargs):
#     return inst(ALU_t.FP_sub, **kwargs)

# def fp_mul(**kwargs):
#     return inst(ALU_t.FP_mult, **kwargs)

# def fp_cmp(cond, **kwargs):
#     return inst(ALU_t.FP_cmp, cond=cond, **kwargs)

# def fp_gt(**kwargs):
#     return fp_cmp(Cond_t.FP_GT, **kwargs)

# def fp_ge(**kwargs):
#     return fp_cmp(Cond_t.FP_GE, **kwargs)

# def fp_lt(**kwargs):
#     return fp_cmp(Cond_t.FP_LT, **kwargs)

# def fp_le(**kwargs):
#     return fp_cmp(Cond_t.FP_LE, **kwargs)

# def fp_eq(**kwargs):
#     return fp_cmp(Cond_t.FP_EQ, **kwargs)

# def fp_neq(**kwargs):
#     return fp_cmp(Cond_t.FP_NE, **kwargs)


# def faddiexp(**kwargs):
#     return inst(ALU_t.FAddIExp, **kwargs)

# def fsubexp(**kwargs):
#     return inst(ALU_t.FSubExp, **kwargs)

# def fcnvexp2f(**kwargs):
#     return inst(ALU_t.FCnvExp2F, **kwargs)

# def fgetfint(**kwargs):
#     return inst(ALU_t.FGetFInt, **kwargs)

# def fgetffrac(**kwargs):
#     return inst(ALU_t.FGetFFrac, **kwargs)

# def fcnvsint2f(**kwargs):
#     return inst(ALU_t.FCnvInt2F, signed=Signed_t.signed, **kwargs)

# def fcnvuint2f(**kwargs):
#     return inst(ALU_t.FCnvInt2F, signed=Signed_t.unsigned, **kwargs)


# def and_(**kwargs):
#     return inst(ALU_t.And, **kwargs)

# def or_(**kwargs):
#     return inst(ALU_t.Or, **kwargs)

# def xor(**kwargs):
#     return inst(ALU_t.XOr, **kwargs)

# def lsl(**kwargs):
#     return inst(ALU_t.SHL, **kwargs)

# def lsr(**kwargs):
#     return inst(ALU_t.SHR, **kwargs)

# def asr(**kwargs):
#     return inst(ALU_t.SHR, signed=Signed_t.signed, **kwargs)

# def sel(**kwargs):
#     return inst(ALU_t.Sel, **kwargs)

# def abs(**kwargs):
#     return inst(ALU_t.Abs, signed=Signed_t.signed, **kwargs)

# def umin(**kwargs):
#     return inst(ALU_t.LTE_Min, cond=Cond_t.ALU, **kwargs)

# def umax(**kwargs):
#     return inst(ALU_t.GTE_Max, cond=Cond_t.ALU, **kwargs)

# def smin(**kwargs):
#     return inst(ALU_t.LTE_Min, signed=Signed_t.signed, cond=Cond_t.ALU, **kwargs)

# def smax(**kwargs):
#     return inst(ALU_t.GTE_Max, signed=Signed_t.signed, cond=Cond_t.ALU, **kwargs)

# def eq(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.Z, **kwargs)

# def ne(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.Z_n, **kwargs)

# def ult(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.ULT, **kwargs)

# def ule(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.ULE, **kwargs)

# def ugt(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.UGT, **kwargs)

# def uge(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.UGE, **kwargs)

# def slt(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.SLT, **kwargs)

# def sle(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.SLE, **kwargs)

# def sgt(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.SGT, **kwargs)

# def sge(**kwargs):
#     return inst(ALU_t.Sub, cond=Cond_t.SGE, **kwargs)

# # implements a constant using a register and add by zero
# def const(val):
#     return inst(ALU_t.Add,
#                 ra_mode=Mode_t.CONST, ra_const=val,
#                 rb_mode=Mode_t.CONST, rb_const=0)

# def lut(val):
#     return inst(ALU_t.Add, lut=val, cond=Cond_t.LUT)

# #Using bit1 and bit2 since bit0 can be used in the ALU_t
# def lut_and():
#     return lut(B1&B2)

# def lut_or():
#     return lut(B1|B2)

# def lut_xor():
#     return lut(B1^B2)

# def lut_not():
#     return lut(~B1)

# def lut_mux():
#     return lut((B2&B1)|((~B2)&B0))

