from hwtypes import TypeFamily
from peak import Peak, name_outputs, PeakNotImplementedError
from .isa import *

width = 16
depth = 1024

def gen_mem(family, width=width,depth=depth):
    MemInstr, (Rom, Fifo, LineBuffer) = gen_mem_instr(family,width,depth)
    Bit = family.Bit
    Data = family.BitVector[width]

    class Mem(Peak):
        def __init__(self):
            pass
            #self.mem = RAM(Word, depth, [Data(0) for i in range(depth)])

        #TODO For now only define the ports relevant for the ROM
        @name_outputs(rdata=Data)
        def __call__(self,instr : MemInstr, ain : Data, din : Data):
            if instr[Rom].match:
                ain_int = int(ain)
                if ain_int >= depth:
                    raise ValueError("address out of range!")
                return instr[Rom].value.init[ain_int]
            else:
                raise PeakNotImplementedError("NYI")
    return Mem
