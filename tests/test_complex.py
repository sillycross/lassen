from lassen.stdlib import gen_FMA, gen_Add32
from lassen.isa import DATAWIDTH
from hwtypes import BitVector, Bit, SIntVector
from lassen.sim import gen_pe
import lassen.asm as asm
import pytest
import random

Bit = Bit
Data = BitVector[DATAWIDTH]
SData = SIntVector[DATAWIDTH]
Data32 = SIntVector[DATAWIDTH*2]

NTESTS=16

FMA = gen_FMA(BitVector.get_family())
Add32 = gen_Add32(BitVector.get_family())

@pytest.mark.parametrize("args", [
    (random.randint(-10,10),
     random.randint(-10,10),
     random.randint(-10,10))
    for _ in range(NTESTS) ] )
def test_fma(args):
    fma = FMA()
    assert SData(args[0]*args[1]+args[2]) == fma(SData(args[0]), SData(args[1]), SData(args[2]))


def test_add32_targeted():
    add32 = Add32()
    assert Data32(10) == add32(Data32(2),Data32(8))
    assert Data32(100000) == add32(Data32(20000),Data32(80000))
    assert Data32(2**17-2) == add32(Data32(2**16-1),Data32(2**16-1))
    assert Data32(2**31-2) == add32(Data32(2**30-1),Data32(2**30-1))

@pytest.mark.parametrize("args", [
    (SIntVector.random(32),SIntVector.random(32))
        for _ in range(NTESTS)
])
def test_add32(args):
    add32 = Add32()
    in0 = args[0]
    in1 = args[1]
    out = in0 + in1
    assert out == add32(in0,in1)

