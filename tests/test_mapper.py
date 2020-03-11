from lassen.sim import arch_closure
from lassen.arch import read_arch
import sys
from peak import Peak
from peak.mapper import ArchMapper
from peak.mapper.utils import pretty_print_binding

# @family_closure
# def Add_fc(family):
#     Data = family.BitVector[16]
#     @assemble(family, locals(), globals())
#     class Add(Peak):
#         def __call__(self, a: Data, b:Data) -> Data:
#             return a + b
#     return Add

def test_add():
    arch = read_arch(str(sys.argv[1]))
    PE_fc = arch_closure(arch)

    arch_fc = PE_fc
    # ir_fc = Add_fc
    arch_mapper = ArchMapper(arch_fc)
    # ir_mapper = arch_mapper.process_ir_instruction(ir_fc)
    # solution = ir_mapper.solve('z3')
    # pretty_print_binding(solution.ibinding)
    # assert solution.solved

test_add()


# from lassen.sim import arch_closure
# from lassen.arch import read_arch
# import sys
# import lassen.asm as asm
# from hwtypes import BitVector
# import coreir
# import metamapper as mm
# import pytest
# import json
# from lassen import rules as Rules
# from lassen import LassenMapper

# def test_init():
#     c = coreir.Context()
#     mapper = LassenMapper(c)
#     for rr in Rules:
#         mapper.add_rr_from_description(rr)

#     #test the mapper on simple add4 app
#     app = c.load_from_file("tests/examples/add4.json")
#     mapper.map_app(app)
#     imap = mapper.extract_instr_map(app)
#     assert len(imap) == 3