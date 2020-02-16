from lassen.sim import arch_closure
from lassen.arch import read_arch
import sys
from peak import Peak, family_closure, assemble
from peak.mapper import ArchMapper
from peak.mapper.utils import pretty_print_binding

@family_closure
def Add_fc(family):
    Data = family.BitVector[16]
    @assemble(family, locals(), globals())
    class Add(Peak):
        def __call__(self, a: Data, b:Data) -> Data:
            return a + b
    return Add

def test_add():
    arch = read_arch(str(sys.argv[1]))
    PE_fc = arch_closure(arch)

    arch_fc = PE_fc
    ir_fc = Add_fc
    arch_mapper = ArchMapper(arch_fc)
    ir_mapper = arch_mapper.process_ir_instruction(ir_fc)
    solution = ir_mapper.solve('z3')
    pretty_print_binding(solution.ibinding)
    assert solution.solved

test_add()