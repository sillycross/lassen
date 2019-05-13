import lassen.asm as asm
from lassen.sim import gen_pe
from lassen.isa import DATAWIDTH
from hwtypes import BitVector, Bit
from lassen.tlut import tlut
from lassen.utils import float2bfbin, bfbin2float, get_random_float
import pytest
import math

Bit = Bit
Data = BitVector[DATAWIDTH]

def test_and():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    # format an 'and' instruction
    inst = asm.and_()
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(1), Data(3))
    assert res==1
    assert res_p==0
    assert irq==0

def test_or():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.or_()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==3
    assert res_p==0
    assert irq==0

def test_xor():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.xor()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==2
    assert res_p==0
    assert irq==0

def test_inv():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sub()
    res, res_p, irq = pe(inst, Data(0xffff),Data(1))
    assert res==0xfffe
    assert res_p==0
    assert irq==0

def test_neg():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.neg()
    res, res_p, irq = pe(inst, Data(0),Data(1))
    assert res==0xffff
    assert res_p==0
    assert irq==0

def test_add():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.add()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==4
    assert res_p==0
    assert irq==0

def test_sub():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sub()
    res, res_p, irq = pe(inst, Data(1),Data(3))
    assert res==-2
    assert res_p==0
    assert irq==0

def test_mult0():
    pe = gen_pe(BitVector.get_family())()

    inst = asm.umult0()
    res, res_p, irq = pe(inst, Data(2),Data(3))
    assert res==6
    assert res_p==0
    assert irq==0

    inst = asm.smult0()
    res, res_p, irq = pe(inst, Data(-2),Data(3))
    assert res==-6
    assert res_p==0
    assert irq==0

def test_mult1():
    pe = gen_pe(BitVector.get_family())()

    inst = asm.umult1()
    res, res_p, irq = pe(inst, Data(0x200),Data(3))
    assert res==6
    assert res_p==0
    assert irq==0

    inst = asm.smult1()
    res, res_p, irq = pe(inst, Data(-512),Data(3))
    assert res==-6
    assert res_p==0
    assert irq==0

def test_mult2():
    pe = gen_pe(BitVector.get_family())()

    inst = asm.umult2()
    res, res_p, irq = pe(inst, Data(0x200),Data(0x300))
    assert res==6
    assert res_p==0
    assert irq==0

    inst = asm.smult2()
    res, res_p, irq = pe(inst, Data(-2*256),Data(3*256))
    assert res==-6
    assert res_p==0
    assert irq==0

def test_fp_add():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fp_add()
    # [sign, exponent (decimal), mantissa (binary)]:
    # a   = [0, -111, 1.0000001]
    # b   = [0, -112, 1.0000010]
    # res = [0, -111, 1.1000010]
    res, res_p, irq = pe(inst, Data(0x801),Data(0x782))
    assert res==0x842
    assert res_p==0
    assert irq==0

def test_fp_mult():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fp_mult()
    # [sign, exponent (decimal), mantissa (binary)]:
    # a   = [0, 2, 1.0000000]
    # b   = [0, 1, 1.0000001]
    # res = [0, 3, 1.0000001]
    # mant = mant(a) * mant(b)
    # exp = exp(a) + exp(b)
    res, res_p, irq = pe(inst, Data(0x4080),Data(0x4001))
    assert res==0x4101
    assert res_p==0
    assert irq==0

def test_lsl():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.lsl()
    res, res_p, irq = pe(inst, Data(2),Data(1))
    assert res==4
    assert res_p==0
    assert irq==0

def test_lsr():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.lsr()
    res, res_p, irq = pe(inst, Data(2),Data(1))
    assert res==1
    assert res_p==0
    assert irq==0

def test_asr():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.asr()
    res, res_p, irq = pe(inst, Data(-2),Data(1))
    assert res==65535
    assert res_p==0
    assert irq==0

def test_sel():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sel()
    res, res_p, irq = pe(inst, Data(1),Data(2),Bit(0))
    assert res==2
    assert res_p==0
    assert irq==0

def test_umin():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.umin()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==1
    assert res_p==0
    assert irq==0

def test_umax():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.umax()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==2
    assert res_p==0
    assert irq==0

def test_smin():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.smin()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==1
    assert res_p==0
    assert irq==0

def test_smax():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.smax()
    res, res_p, irq = pe(inst, Data(1),Data(2))
    assert res==2
    assert res_p==0
    assert irq==0

def test_abs():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.abs()
    res, res_p, irq = pe(inst,Data(-1))
    assert res==1
    assert res_p==0
    assert irq==0

def test_eq():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.eq()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ne():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ne()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_uge():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.uge()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ule():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ule()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_ugt():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ugt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_ult():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.ult()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_sge():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sge()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_sle():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sle()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==1

def test_sgt():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sgt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_slt():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.slt()
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p==0

def test_get_mant():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fgetmant() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0000))
    assert res==0xA
    assert res_p==0
    assert irq==0

def test_add_exp_imm():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    inst = asm.faddiexp() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0005))
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # Add 5 to exp => Sign=0; Exp=0x04; Mant=0x0A i.e. float  = 0x020A
    assert res==0x020A
    assert res_p==0
    assert irq==0

def test_sub_exp():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fsubexp() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x4005))
    # 7F8A => Sign=0; Exp=0xFF; Mant=0x0A
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101)
    # res: 7F0A => Sign=0; Exp=0xFE; Mant=0x0A (0111 1111 0000 1010)
    assert res==0x7F0A
    assert res_p==0
    assert irq==0

def test_cnvt_exp_to_float():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fcnvexp2f() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4005), Data(0x0000))
    # 4005 => Sign=0; Exp=0x80; Mant=0x05 (0100 0000 0000 0101) i.e. unbiased exp = 1
    # res: 3F80 => Sign=0; Exp=0x7F; Mant=0x00 (0011 1111 1000 0000)
    assert res==0x3F80
    assert res_p==0
    assert irq==0

def test_get_float_int():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fgetfint() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: int(2.5) =  2
    assert res==0x2
    assert res_p==0
    assert irq==0

def test_get_float_frac():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    inst = asm.fgetffrac() 
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: frac(2.5) = 0.5D = 0.1B i.e. 1000 0000
    assert res==0x40
    assert res_p==0
    assert irq==0

def test_int_to_float():
    test_vectors = []
    for vector_count in range(50):
      num            = int(math.floor(get_random_float(3)))
      num_bfloat_str = float2bfbin(float(num))
      min_accuracy = 2
      test_vectors.append([num, float2bfbin(0),num_bfloat_str, min_accuracy])

    test_vectors.append([2, float2bfbin(0), float2bfbin(2.0), min_accuracy])
    test_vectors.append([1, float2bfbin(0), float2bfbin(1.0), min_accuracy])
    test_vectors.append([0, float2bfbin(0), float2bfbin(0.0), min_accuracy])
    test_vectors.append([-9, float2bfbin(0), float2bfbin(-9.0), min_accuracy])
    # START_TEST result = i2f(op_a)
    pe_signed  = gen_pe(BitVector.get_family())()
    inst1 = asm.fcnvsi2f()
    
    for test_vector in test_vectors:
      op_a    = Data(test_vector[0])
      op_b    = Data(int(test_vector[1],2))
      exp_res =      int(test_vector[2],2)
      acc     =          test_vector[3]

      result         ,d1, d2   = pe_signed(inst1, op_a, op_b)
      assert abs(exp_res-int(result)) <= acc


def test_div():
    test_vectors = []
    for vector_count in range(50):
      divident_sp = get_random_float()
      divisor_sp  = get_random_float()
      divident_bfloat_str = float2bfbin(divident_sp)
      divisor_bfloat_str = float2bfbin(divisor_sp)
      divident_bfp = bfbin2float(divident_bfloat_str)
      divisor_bfp  = bfbin2float(divisor_bfloat_str)
      quotient_bfp = bfbin2float(float2bfbin(divident_bfp / divisor_bfp))
      quotient_bfloat_str = float2bfbin(quotient_bfp)
      min_accuracy = 2
      test_vectors.append([divident_bfloat_str, divisor_bfloat_str, quotient_bfloat_str, min_accuracy])

    #START_TEST result = op_a / op_b
    pe_get_mant  = gen_pe(BitVector.get_family())()
    mem_lut      = tlut()
    pe_scale_res = gen_pe(BitVector.get_family())()
    pe_mult      = gen_pe(BitVector.get_family())()

    inst1 = asm.fgetmant()
    inst2 = asm.fsubexp()
    inst3 = asm.fp_mult()
    
    for test_vector in test_vectors:
      op_a    = Data(int(test_vector[0],2))
      op_b    = Data(int(test_vector[1],2))
      exp_res =      int(test_vector[2],2)
      acc     =          test_vector[3]

      mant           ,d1 ,d2   = pe_get_mant(inst1,op_b,Data(0))
      lookup_result            = mem_lut.div_lut(mant)
      scaled_result  ,d3 ,d4   = pe_scale_res(inst2, lookup_result, op_b)
      result         ,d5 ,d6   = pe_mult(inst3, scaled_result, op_a)

      print("div",bfbin2float(test_vector[0]),bfbin2float(test_vector[1]),bfbin2float(test_vector[2]),bfbin2float("{:016b}".format(int(result))))
      assert abs(exp_res-int(result)) <= acc


def test_ln():
    test_vectors = []
    for vector_count in range(50):
      num            = math.fabs(get_random_float())
      num_bfloat_str = float2bfbin(num)
      num_bfp        = bfbin2float(num_bfloat_str)
      res_bfp        = bfbin2float(float2bfbin(math.log(num_bfp)))
      res_bfloat_str = float2bfbin(res_bfp)
      min_accuracy = 2
      test_vectors.append([num_bfloat_str, float2bfbin(0),res_bfloat_str, min_accuracy])

    test_vectors.append([float2bfbin(2.0), float2bfbin(0), float2bfbin(math.log(2)), min_accuracy])
    # START_TEST result = ln(op_a)
    pe_get_mant  = gen_pe(BitVector.get_family())()
    pe_get_exp   = gen_pe(BitVector.get_family())()
    mem_lut      = tlut()
    pe_mult      = gen_pe(BitVector.get_family())()
    pe_add       = gen_pe(BitVector.get_family())()

    inst1 = asm.fgetmant()
    inst2 = asm.fcnvexp2f()
    inst3 = asm.fp_mult()
    inst4 = asm.fp_add()
    
    ln2 = math.log(2)
    ln2_bf = int(float2bfbin(ln2),2)

    for test_vector in test_vectors:
      op_a    = Data(int(test_vector[0],2))
      op_b    = Data(int(test_vector[1],2))
      exp_res =      int(test_vector[2],2)
      acc     =          test_vector[3]

      const1  = Data(ln2_bf)

      mant           ,d1, d2   = pe_get_mant(inst1,op_a,op_b)
      fexp           ,d1, d2   = pe_get_exp(inst2,op_a,op_b)
      lut_res                  = mem_lut.ln_lut(mant)
      mult           ,d1, d2   = pe_mult(inst3, fexp, const1)
      result         ,d1, d2   = pe_mult(inst4, Data(lut_res), mult)
      print("ln",bfbin2float(test_vector[0]),bfbin2float(test_vector[1]),bfbin2float(test_vector[2]),bfbin2float("{:016b}".format(int(result))))
      assert abs(exp_res-int(result)) <= acc


def test_exp():
    test_vectors = []
    for vector_count in range(50):
      num            = get_random_float(2)
      num_bfloat_str = float2bfbin(num)
      num_bfp        = bfbin2float(num_bfloat_str)
      res_bfp        = bfbin2float(float2bfbin(math.exp(num_bfp)))
      res_bfloat_str = float2bfbin(res_bfp)
      min_accuracy = 2
      test_vectors.append([num_bfloat_str, float2bfbin(0),res_bfloat_str, min_accuracy])

    test_vectors.append([float2bfbin(2.0), float2bfbin(0), float2bfbin(math.exp(2)), min_accuracy])
    test_vectors.append([float2bfbin(-2.0), float2bfbin(0), float2bfbin(math.exp(-2)), min_accuracy])
    test_vectors.append([float2bfbin(1.0), float2bfbin(0), float2bfbin(math.exp(1.0)), min_accuracy])
    test_vectors.append([float2bfbin(0.0), float2bfbin(0), float2bfbin(math.exp(0)), min_accuracy])
    test_vectors.append([float2bfbin(-10.0), float2bfbin(0), float2bfbin(math.exp(-10)), min_accuracy])
    test_vectors.append([float2bfbin(5.0), float2bfbin(0), float2bfbin(math.exp(5)), min_accuracy])
    # START_TEST result = exp(op_a)
    pe_get_int   = gen_pe(BitVector.get_family())()
    pe_get_frac  = gen_pe(BitVector.get_family())()
    mem_lut      = tlut()
    pe_incr_exp  = gen_pe(BitVector.get_family())()

    pe_div_mult  = gen_pe(BitVector.get_family())()

    ln2_inv = 1.4453125 #1.0/math.log(2)
    ln2_inv_bf = int(float2bfbin(ln2_inv),2)
    const1  = Data(ln2_inv_bf)

    for test_vector in test_vectors:
      op_a    = Data(int(test_vector[0],2))
      op_b    = Data(int(test_vector[1],2))
      exp_res =      int(test_vector[2],2)
      acc     =          test_vector[3]

      # Perform op_a/ln(2)
      inst1 = asm.fp_mult()
      div_res         ,d5 ,d6   = pe_div_mult(inst1, const1 , op_a)

      # Compute 2**op_a
      inst2 = asm.fgetfint()
      inst3 = asm.fgetffrac()
      inst4 = asm.faddiexp()
      
      fint            ,d1, d2  = pe_get_int(inst2,div_res,op_b)
      ffrac           ,d1, d2  = pe_get_frac(inst3,div_res,op_b)
      lut_res                  = mem_lut.exp_lut(ffrac)
      result          ,d1, d2  = pe_incr_exp(inst4,lut_res,fint)
      print("exp",bfbin2float(test_vector[0]),bfbin2float(test_vector[1]),bfbin2float(test_vector[2]),bfbin2float("{:016b}".format(int(result))))    
      assert abs(exp_res-int(result)) <= acc
