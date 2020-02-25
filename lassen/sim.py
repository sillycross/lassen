from peak import Peak, family_closure, name_outputs, assemble, gen_register
from functools import lru_cache
import magma as m
import hwtypes
import ast_tools
from ast_tools.passes import begin_rewrite, end_rewrite, loop_unroll, if_inline
from ast_tools.macros import inline
import inspect
from .common import *
from .mode import gen_register_mode
from .lut import LUT_fc
from .alu import ALU_fc
from .add import ADD_fc
from .cond import Cond_fc
from .isa import inst_arch_closure
from .arch import *
from .mul import MUL_fc
from .counter import Counter_fc

def arch_closure(arch):
    @family_closure
    def PE_fc(family):
        BitVector = family.BitVector

        #Hack
        def BV1(bit):
            return bit.ite(family.BitVector[1](1), family.BitVector[1](0))
        Data = family.BitVector[DATAWIDTH]
        UBit = family.Unsigned[1]
        Data8 = family.BitVector[8]
        Data32 = family.BitVector[32]
        UData32 = family.Unsigned[32]
        Bit = family.Bit
        RegisterWithConst = gen_register_mode(Data, 0)(family)
        Register = gen_register(Data, 0)(family)
        BitReg = gen_register_mode(Bit, 0)(family)
        Counter = Counter_fc(family)
        ALU = ALU_fc(family)
        ADD = ADD_fc(family)
        Cond = Cond_fc(family)
        LUT = LUT_fc(family)
        MUL = MUL_fc(family)
        Inst_fc = inst_arch_closure(arch)
        Inst = Inst_fc(family)

        if family.Bit is m.Bit:
            DataInputList = m.Tuple[(Data for _ in range(arch.num_inputs))]
            DataOutputList = m.Tuple[(Data for _ in range(arch.num_outputs))]
        else:
            DataInputList = hwtypes.Tuple[(Data for _ in range(arch.num_inputs))]
            DataOutputList = hwtypes.Tuple[(Data for _ in range(arch.num_outputs))]




        @assemble(family, locals(), globals())
        class PE(Peak):
            @end_rewrite()
            @if_inline()
            @loop_unroll()
            @begin_rewrite()
            def __init__(self):

                # Data registers
                if inline(arch.enable_input_regs):
                    for init_unroll in ast_tools.macros.unroll(range(arch.num_inputs)):
                        self.input_reg_init_unroll: Register = Register()

                if inline(arch.enable_output_regs):
                    for init_unroll in ast_tools.macros.unroll(range(arch.num_outputs)):
                        self.output_reg_init_unroll: Register = Register()

                for init_unroll in ast_tools.macros.unroll(range(arch.num_reg)):
                    self.regs_init_unroll: Register = Register()

                # for init_unroll in ast_tools.macros.unroll(range(len(arch.counters))):
                #     self.counter_init_unroll: Counter = Counter()
                # Bit Registers
                self.regd: BitReg = BitReg()
                self.rege: BitReg = BitReg()
                self.regf: BitReg = BitReg()

                #Condition code
                self.cond: Cond = Cond()

                #Lut
                self.lut: LUT = LUT()

            @end_rewrite()
            @if_inline()
            @loop_unroll()
            @loop_unroll()
            @begin_rewrite()
            @name_outputs(PE_res=DataOutputList, res_p=UBit, read_config_data=UData32)
            def __call__(self, inst: Inst, \
                inputs : DataInputList, \
                bit0: Bit = Bit(0), bit1: Bit = Bit(0), bit2: Bit = Bit(0), \
                clk_en: Global(Bit) = Bit(1), \
                config_addr : Data8 = Data8(0), \
                config_data : Data32 = Data32(0), \
                config_en : Bit = Bit(0) \
            ) -> (DataOutputList, Bit, Data32):
                # Simulate one clock cycle


                data01_addr = (config_addr[:3] == BitVector[3](DATA01_ADDR))
                bit012_addr = (config_addr[:3] == BitVector[3](BIT012_ADDR))

                # input registers
                reg_we = (data01_addr & config_en)
                reg_config_wdata = config_data[DATA0_START:DATA0_START+DATA0_WIDTH]

                #rd
                rd_we = (bit012_addr & config_en)
                rd_config_wdata = config_data[BIT0_START]

                #re
                re_we = rd_we
                re_config_wdata = config_data[BIT1_START]

                #rf
                rf_we = rd_we
                rf_config_wdata = config_data[BIT2_START]

                signals = {}
                rdata = {}

                if inline(arch.enable_input_regs):
                    for init_unroll in ast_tools.macros.unroll(range(arch.num_inputs)):
                        signals[arch.inputs[init_unroll]] = self.input_reg_init_unroll(inputs[init_unroll], clk_en)
                        
                else:
                    for i in ast_tools.macros.unroll(range(arch.num_inputs)):
                        signals[arch.inputs[i]] = inputs[i]
                        

                rd, rd_rdata = self.regd(inst.regd, inst.bit0, bit0, clk_en, rd_we, rd_config_wdata)
                re, re_rdata = self.rege(inst.rege, inst.bit1, bit1, clk_en, re_we, re_config_wdata)
                rf, rf_rdata = self.regf(inst.regf, inst.bit2, bit2, clk_en, rf_we, rf_config_wdata)


                #Calculate read_config_data
                read_config_data = BV1(rd_rdata).concat(BV1(re_rdata)).concat(BV1(rf_rdata)).concat(BitVector[32-3](0))


                for init_unroll in ast_tools.macros.unroll(range(arch.num_reg)):
                    signals[arch.regs[init_unroll].id] = self.regs_init_unroll(Data(0), 0)

                # for init_unroll in ast_tools.macros.unroll(range(len(arch.counters))):
                #     signals[arch.counters[init_unroll].id] = self.counter_init_unroll(Inst.counter_en[init_unroll], Inst.counter_rst[init_unroll], clk_en)


                mux_idx_in0 = 0
                mux_idx_in1 = 0
                mul_idx = 0
                alu_idx = 0

                for mod_index in ast_tools.macros.unroll(range(len(arch.modules))):

                    if inline(len(arch.modules[mod_index].in0) == 1):
                        in0 = signals[arch.modules[mod_index].in0[0]]  
                    else:
                        in0_mux_select = inst.mux_in0[mux_idx_in0]
                        mux_idx_in0 = mux_idx_in0 + 1
                        for mux_inputs in ast_tools.macros.unroll(range(len(arch.modules[mod_index].in0))):
                            if in0_mux_select == family.BitVector[m.math.log2_ceil(len(arch.modules[mod_index].in0))](mux_inputs):
                                in0 = signals[arch.modules[mod_index].in0[mux_inputs]]
                            
                    if inline(len(arch.modules[mod_index].in1) == 1):
                        in1 = signals[arch.modules[mod_index].in1[0]]  
                    else:
                        in1_mux_select = inst.mux_in1[mux_idx_in1]
                        mux_idx_in1 = mux_idx_in1 + 1
                        for mux_inputs in ast_tools.macros.unroll(range(len(arch.modules[mod_index].in1))):
                            if in1_mux_select == family.BitVector[m.math.log2_ceil(len(arch.modules[mod_index].in1))](mux_inputs):
                                in1 = signals[arch.modules[mod_index].in1[mux_inputs]]

                    if inline(arch.modules[mod_index].type_ == "mul"):
                        signals[arch.modules[mod_index].id] = MUL(inst.mul[mul_idx], inst.signed, in0, in1)
                        mul_idx = mul_idx + 1
                        
                    elif inline(arch.modules[mod_index].type_ == "alu"):
                        signals[arch.modules[mod_index].id], alu_res_p, Z, N, C, V = ALU(inst.alu[alu_idx], inst.signed, in0, in1, rd)
                        alu_idx = alu_idx + 1

                    elif inline(arch.modules[mod_index].type_ == "add"):
                        signals[arch.modules[mod_index].id], alu_res_p, Z, N, C, V = ADD(in0, in1)
                            

                reg_mux_idx = 0

                for init_unroll in ast_tools.macros.unroll(range(arch.num_reg)):
                    if inline(len(arch.regs[init_unroll].in_) == 1):
                        in_ = signals[arch.regs[init_unroll].in_[0]]  
                    else:
                        in_mux_select = inst.mux_reg[reg_mux_idx]
                        reg_mux_idx = reg_mux_idx + 1

                        for mux_inputs in ast_tools.macros.unroll(range(len(arch.regs[init_unroll].in_))):
                            if in_mux_select == family.BitVector[m.math.log2_ceil(len(arch.regs[init_unroll].in_))](mux_inputs):
                                in_ = signals[arch.regs[init_unroll].in_[mux_inputs]]
                            
                    signals[arch.regs[init_unroll].id] = self.regs_init_unroll(in_, clk_en.ite(inst.reg_en[init_unroll], Bit(0)))

                # calculate lut results
                lut_res = self.lut(inst.lut, rd, re, rf)

                # calculate 1-bit result
                res_p = self.cond(inst.cond, alu_res_p, lut_res, Z, N, C, V)

                
                outputs = []
                mux_idx_out = 0
                for out_index in ast_tools.macros.unroll(range(arch.num_outputs)):
                    if inline(len(arch.outputs[out_index]) == 1):
                        output_temp = signals[arch.outputs[out_index][0]]
                    else:
                        out_mux_select = inst.mux_out[mux_idx_out]
                        mux_idx_out = mux_idx_out + 1
                        for mux_inputs in ast_tools.macros.unroll(range(len(arch.outputs[out_index]))):
                            if out_mux_select == family.BitVector[m.math.log2_ceil(len(arch.outputs[out_index]))](mux_inputs):
                                output_temp = signals[arch.outputs[out_index][mux_inputs]]
                    outputs.append(output_temp)


                # for i in ast_tools.macros.unroll(range(arch.num_outputs)):
                #     outputs.append(signals[arch.outputs[i]])

                if inline(arch.enable_output_regs):
                    outputs_from_reg = []
                    for init_unroll in ast_tools.macros.unroll(range(arch.num_outputs)):
                        temp = self.output_reg_init_unroll(outputs[init_unroll], clk_en)
                        outputs_from_reg.append(temp)

                    # return 16-bit result, 1-bit result
                    return DataOutputList(*outputs_from_reg), res_p, read_config_data
                else:
                    return DataOutputList(*outputs), res_p, read_config_data

            print(inspect.getsource(__init__)) 
            print(inspect.getsource(__call__)) 
        return PE
    return PE_fc