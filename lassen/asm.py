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

    if arch.num_alu > 0:
        ALU_t_list_type = Inst.alu

    if arch.num_mul > 0:
        MUL_t_list_type = Inst.mul

    if arch.num_reg > 0:
        REG_t_list_type = Inst.reg_en
        
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
    if arch.num_output_mux > 0:
        mux_list_type_output = Inst.mux_out

    if arch.num_counter > 0:
        counter_en_list_type = Inst.counter_en
        counter_rst_list_type = Inst.counter_rst

    #Lut Constants
    # B0 = BitVector[8]([0, 1, 0, 1, 0, 1, 0, 1])
    # B1 = BitVector[8]([0, 0, 1, 1, 0, 0, 1, 1])
    # B2 = BitVector[8]([0, 0, 0, 0, 1, 1, 1, 1])

    def gen_inst(alu, mul, reg_en, mux_in0, mux_in1, mux_reg, mux_out, counter_en, counter_rst, signed=Signed_t.unsigned, lut=0, cond=Cond_t.Z,
            reg_mode=[Mode_t.BYPASS for _ in range(arch.num_inputs)], reg_const=[Data(0) for _ in range(arch.num_inputs)],  
            rd_mode=Mode_t.BYPASS, rd_const=0,
            re_mode=Mode_t.BYPASS, re_const=0,
            rf_mode=Mode_t.BYPASS, rf_const=0):
        """
        https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec
        Format a configuration of the PE - sets all fields
        """

        args = []

        if arch.num_alu > 0:
            args.append(ALU_t_list_type(*alu))

        if arch.num_mul > 0:
            args.append(MUL_t_list_type(*mul) )

        if arch.num_reg > 0:
            args.append(REG_t_list_type(*reg_en) )

        if arch.num_mux_in0 > 0:
            args.append(mux_list_type_in0(*mux_in0) )

        if arch.num_mux_in1 > 0:
            args.append(mux_list_type_in1(*mux_in1) )

        if arch.num_reg_mux > 0:
            args.append(mux_list_type_reg(*mux_reg) )

        if arch.num_output_mux > 0:
            args.append(mux_list_type_output(*mux_out) )

        if arch.num_counter > 0:
            args.append(counter_en_list_type(*counter_en))
            args.append(counter_rst_list_type(*counter_rst))

        args.append(signed )
        args.append(LUT_t(lut) )
        args.append(cond)
        args.append(Mode_t_list_type(*reg_mode) )
        args.append(Data_list_type(*reg_const) )
        args.append(Mode_t(rd_mode) )
        args.append(BitConst(rd_const))
        args.append(Mode_t(re_mode) )
        args.append(BitConst(re_const) )
        args.append(Mode_t(rf_mode))
        args.append(BitConst(rf_const))

        return Inst(*args)

    return gen_inst
