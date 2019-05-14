from collections import namedtuple
import operator
import lassen.asm as asm
from lassen.sim import gen_pe
from lassen.isa import DATAWIDTH
from hwtypes import SIntVector, UIntVector, BitVector, Bit
import pytest

Bit = Bit
Data = BitVector[DATAWIDTH]

op = namedtuple("op", ["name", "func"])
NTESTS = 16

@pytest.mark.parametrize("op", [
    op('and_', lambda x, y: x&y),
    op('or_',  lambda x, y: x|y),
    op('xor',  lambda x, y: x^y),
    op('add',  lambda x, y: x+y),
    op('sub',  lambda x, y: x-y),
    op('lsl',  lambda x, y: x << y),
    op('lsr',  lambda x, y: x >> y),
    op('umin',  lambda x, y: (x < y).ite(x, y)),
    op('umax',  lambda x, y: (x > y).ite(x, y))
])
def test_unsigned_binary(op):
    pe = gen_pe(BitVector.get_family())()
    inst = getattr(asm, op.name)()
    for _ in range(NTESTS):
        x = UIntVector.random(DATAWIDTH)
        y = UIntVector.random(DATAWIDTH)
        res, _, _ = pe(inst, Data(x), Data(y))
        assert res==op.func(x,y)

@pytest.mark.parametrize("op", [
    op('asr',  lambda x, y: x >> y),
    op('smin',  lambda x, y: (x < y).ite(x, y)),
    op('smax',  lambda x, y: (x > y).ite(x, y)),
])
def test_signed_binary(op):
    pe = gen_pe(BitVector.get_family())()
    inst = getattr(asm, op.name)()
    for _ in range(NTESTS):
        x = SIntVector.random(DATAWIDTH)
        y = SIntVector.random(DATAWIDTH)
        res, _, _ = pe(inst, Data(x), Data(y))
        assert res==op.func(x,y)

@pytest.mark.parametrize("op", [
    op('abs',  lambda x: x if x > 0 else -x),
])
def test_signed_unary(op):
    pe = gen_pe(BitVector.get_family())()
    inst = getattr(asm, op.name)()
    for _ in range(NTESTS):
        x = SIntVector.random(DATAWIDTH)
        res, _, _ = pe(inst, Data(x))
        assert res == op.func(x)

@pytest.mark.parametrize("op", [
    op('eq',   lambda x, y: x == y),
    op('ne',   lambda x, y: x != y),
    op('ugt',  lambda x, y: x >  y),
    op('uge',  lambda x, y: x >= y),
    op('ult',  lambda x, y: x <  y),
    op('ule',  lambda x, y: x <= y),
])
def test_unsigned_relation(op):
    pe = gen_pe(BitVector.get_family())()
    inst = getattr(asm, op.name)()
    for _ in range(NTESTS):
        x = UIntVector.random(DATAWIDTH)
        y = UIntVector.random(DATAWIDTH)
        _, res_p, _ = pe(inst, Data(x), Data(y))
        assert res_p==op.func(x,y)

@pytest.mark.parametrize("op", [
    op('sgt',  lambda x, y: x >  y),
    op('sge',  lambda x, y: x >= y),
    op('slt',  lambda x, y: x <  y),
    op('sle',  lambda x, y: x <= y),
])
def test_signed_relation(op):
    pe = gen_pe(BitVector.get_family())()
    inst = getattr(asm, op.name)()
    for _ in range(NTESTS):
        x = SIntVector.random(DATAWIDTH)
        y = SIntVector.random(DATAWIDTH)
        _, res_p, _ = pe(inst, Data(x), Data(y))
        assert res_p==op.func(x,y)

def test_sel():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.sel()
    for _ in range(NTESTS):
        x = UIntVector.random(DATAWIDTH)
        y = UIntVector.random(DATAWIDTH)
        res, _, _ = pe(inst, Data(x), Data(y), Bit(0))
        assert res==y
        res, _, _ = pe(inst, Data(x), Data(y), Bit(1))
        assert res==x

def test_smult():
    def mul(x,y):
        mulx, muly = x.sext(DATAWIDTH), y.sext(DATAWIDTH)
        return mulx * muly
    pe = gen_pe(BitVector.get_family())()
    smult0 = asm.smult0()
    smult1 = asm.smult1()
    smult2 = asm.smult2()
    for _ in range(NTESTS):
        x = SIntVector.random(DATAWIDTH)
        y = SIntVector.random(DATAWIDTH)
        xy = mul(x,y)
        res, _, _ = pe(smult0, Data(x), Data(y))
        assert res == xy[0:DATAWIDTH]
        res, _, _ = pe(smult1, Data(x), Data(y))
        assert res == xy[DATAWIDTH//2:DATAWIDTH//2+DATAWIDTH]
        res, _, _ = pe(smult2, Data(x), Data(y))
        assert res == xy[DATAWIDTH:]

def test_umult():
    def mul(x,y):
        mulx, muly = x.zext(DATAWIDTH), y.zext(DATAWIDTH)
        return mulx * muly
    pe = gen_pe(BitVector.get_family())()
    umult0 = asm.umult0()
    umult1 = asm.umult1()
    umult2 = asm.umult2()
    for _ in range(NTESTS):
        x = UIntVector.random(DATAWIDTH)
        y = UIntVector.random(DATAWIDTH)
        xy = mul(x,y)
        res, _, _ = pe(umult0, Data(x), Data(y))
        assert res == xy[0:DATAWIDTH]
        res, _, _ = pe(umult1, Data(x), Data(y))
        assert res == xy[DATAWIDTH//2:DATAWIDTH//2+DATAWIDTH]
        res, _, _ = pe(umult2, Data(x), Data(y))
        assert res == xy[DATAWIDTH:]


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
    res, res_p, irq = pe(inst,Data(1),Data(1))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(1), Data(2))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(2), Data(1))
    assert res_p == 0

def test_umax():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.umax()
    res, res_p, irq = pe(inst, Data(1), Data(2))
    assert res == 2
    assert res_p == 0
    res, res_p, irq = pe(inst, Data(2), Data(1))
    assert res == 2
    assert res_p == 1

def test_smin():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.smin()
    res, res_p, irq = pe(inst, Data(-1), Data(2))
    assert res == Data(-1)
    assert res_p == 1
    res, res_p, irq = pe(inst, Data(2), Data(-1))
    assert res == Data(-1)
    assert res_p == 0
    res, res_p, irq = pe(inst, Data(-1), Data(-1))
    assert res == Data(-1)
    assert res_p == 1

def test_smax():
    pe = gen_pe(BitVector.get_family())()
    inst = asm.smax()
    res, res_p, irq = pe(inst, Data(-1), Data(2))
    assert res == 2
    assert res_p == 0
    res, res_p, irq = pe(inst, Data(2), Data(-1))
    assert res == 2
    assert res_p == 1
    res, res_p, irq = pe(inst, Data(-1), Data(-1))
    assert res == Data(-1)
    assert res_p == 1

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
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(1), Data(2))
    assert res_p == 1
    res, res_p, _ = pe(inst, Data(2), Data(1))
    assert res_p == 0

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
    # format an 'and' instruction
    inst = asm.fgetmant()
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x7F8A), Data(0x0000))
    assert res==0xA
    assert res_p==0
    assert irq==0

def test_add_exp_imm():
    # instantiate an PE - calls PE.__init__
    pe = gen_pe(BitVector.get_family())()
    # format an 'and' instruction
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
    # format an 'and' instruction
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
    # format an 'and' instruction
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
    # format an 'and' instruction
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
    # format an 'and' instruction
    inst = asm.fgetffrac()
    # execute PE instruction with the arguments as inputs -  call PE.__call__
    res, res_p, irq = pe(inst, Data(0x4020), Data(0x0000))
    #2.5 = 10.1 i.e. exp = 1 with 1.01 # biased exp = 128 i.e 80
    #float is 0100 0000 0010 0000 i.e. 4020
    # res: frac(2.5) = 0.5D = 0.1B i.e. 1000 0000
    assert res==0x80
    assert res_p==0
    assert irq==0
