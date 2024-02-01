#!/usr/bin/env python3

from rowadder2_1_codegen import RowAdder2_1
import random

class MultiStage2_1:
    def __init__(self, colnum, rownum):
        assert(rownum >= 2)
        self.rownum = rownum
        self.colnum = colnum
        self.finalcol = self.colnum + (self.rownum - 1).bit_length()
        self.build_netheap()
        self.modulename = f'multistage{self.rownum}_1_{self.colnum}'
        self.indent = '   '

    def build_netheap(self):
        self.netheap = [{'type': 'dst', 'idx': 0, 'length': self.finalcol}]
        nodenum = self.rownum * 2 - 1
        for idx in range(1, nodenum):
            isleaf = idx * 2 + 1 >= nodenum
            stage = (idx + 1).bit_length() - 1
            if isleaf:
                self.netheap += [{'type': 'src', 'idx':(idx - (nodenum - self.rownum)), 'length': self.colnum}]
            else:
                self.netheap += [{'type': 'sum', 'idx': idx, 'length': self.finalcol - stage}]
        self.rowadders = set()
        for idx, wire in enumerate(self.netheap):
            if wire['type'] in ['sum', 'dst']:
                self.rowadders.add(wire['length'] - 1)

    def gen_module(self):
        code = ''
        code += f'module {self.modulename}('
        code += self.get_module_arguments()
        code += ');\n'
        code += self.gen_wire_declarations()
        code += self.gen_rowadder_instantiations()
        code += 'endmodule\n'
        return code

    def get_module_arguments(self):
        args = []
        for idx in range(self.rownum):
            args += [f'input [{self.colnum - 1}:0] src{idx}']
        args += [f'output [{self.finalcol - 1}:0] dst0']
        return ', '.join(args)

    def gen_wire_declarations(self, indentlevel=1):
        code = ''
        for wire in self.netheap:
            if wire['type'] == 'sum':
                code += self.indent * indentlevel + f'wire [{wire["length"]-1}:0] sum{wire["idx"]};\n'
        return code

    def gen_rowadder_instantiations(self, indentlevel=1):
        code = ''
        for idx, wire in enumerate(self.netheap):
            if wire['type'] in ['sum', 'dst']:
                src0 = self.netheap[idx * 2 + 1]
                src1 = self.netheap[idx * 2 + 2]
                def padded(base, num):
                    if num > 0:
                        return f'{{{num}\'h0, {base}}}'
                    else:
                        return base
                code += self.indent * indentlevel + f'rowadder2_1_{wire["length"] - 1} rowadder{idx}('
                code += padded(f'{src0["type"]}{src0["idx"]}', wire['length'] - src0['length'] - 1) + ', '
                code += padded(f'{src1["type"]}{src1["idx"]}', wire['length'] - src1['length'] - 1) + ', '
                code += f'{wire["type"]}{wire["idx"]});\n'
        return code

class MultiStage2_1Testbench(MultiStage2_1):
    def __init__(self, colnum, rownum):
        super().__init__(colnum, rownum)
        self.testmodulename = f'{self.modulename}_test'

    def gen_module(self, count=1000):
        code = ''
        code += f'module {self.testmodulename}();\n'
        code += self.gen_reg_wire_declarations()
        code += self.gen_rowadder_instantiation()
        code += self.gen_combinational()
        code += self.gen_initial_block(count)
        code += f'endmodule\n'
        return code

    def gen_reg_wire_declarations(self, indentlevel=1):
        code = ''
        for idx in range(self.rownum):
            code += self.indent * indentlevel + f'reg [{self.colnum - 1}:0] src{idx};\n'
        code += self.indent * indentlevel + f'wire [{self.finalcol - 1}:0] dst;\n'
        code += self.indent * indentlevel + f'wire [{self.finalcol - 1}:0] sum;\n'
        code += self.indent * indentlevel + f'wire test;\n'
        return code

    def gen_rowadder_instantiation(self, indentlevel=1):
        code = ''
        code += self.indent * indentlevel + \
            f'{self.modulename} {self.modulename}_inst({self.get_module_arguments()});\n'
        return code

    def get_module_arguments(self):
        args = []
        for idx in range(self.rownum):
            args += [f'src{idx}']
        args += [f'dst']
        return ', '.join(args)

    def gen_combinational(self, indentlevel=1):
        srcs = [f'src{idx}' for idx in range(self.rownum)]
        exp = ' + '.join(srcs)
        code = ''
        code += self.indent * indentlevel + f'assign sum = {exp};\n'
        code += self.indent * indentlevel + f'assign test = sum == dst;\n'
        return code

    def gen_initial_block(self, count, indentlevel=1):
        code = ''
        code += self.indent * indentlevel + f'initial begin\n'
        code += self.indent * (indentlevel + 1) + f'$monitor("sum: 0x%x, dst: 0x%x, test: %d", sum, dst, test);\n'
        for idx in range(self.rownum):
            code += self.indent * (indentlevel + 1) + f'src{idx} <= {self.colnum}\'h0;\n'
        code += self.indent * (indentlevel + 1) + f'#1\n'
        for idx in range(self.rownum):
            code += self.indent * (indentlevel + 1) + f'src{idx} <= {self.colnum}\'h{(1<<(self.colnum))-1:x};\n'
        for _ in range(count):
            code += self.indent * (indentlevel + 1) + f'#1\n'
            for idx in range(self.rownum):
                code += self.indent * (indentlevel + 1) + f'src{idx} <= {self.colnum}\'h{random.randint(0, (1<<self.colnum)-1):x};\n'
        code += self.indent * indentlevel + f'end\n'
        return code

class MultiStage2_1ShiftRegister(MultiStage2_1):
    def __init__(self, colnum, rownum):
        super().__init__(colnum, rownum)
        self.testmodulename = f'{self.modulename}_shiftregister'

    def gen_module(self):
        code = ''
        code += f'module {self.testmodulename}('
        code += self.get_module_arguments()
        code += ');\n'
        code += self.gen_reg_declarations()
        code += self.gen_rowadder_instantiation()
        code += self.gen_initial_block()
        code += self.gen_always_block()
        code += f'endmodule\n'
        return code

    def get_module_arguments(self):
        args = []
        args += ['input clk']
        for idx in range(self.rownum):
            args += [f'input stream{idx}']
        args += [f'output [{self.finalcol - 1}:0] dst']
        return ', '.join(args)

    def gen_reg_declarations(self, indentlevel=1):
        code = ''
        for idx in range(self.rownum):
            code += self.indent * indentlevel + f'reg [{self.colnum - 1}:0] src{idx};\n'
        return code

    def gen_rowadder_instantiation(self, indentlevel=1):
        code = ''
        code += self.indent * indentlevel + f'{self.modulename} {self.modulename}_inst('
        args = [f'src{idx}' for idx in range(self.rownum)] + ['dst']
        code += ', '.join(args)
        code += ');\n'
        return code

    def gen_initial_block(self, indentlevel=1):
        code = ''
        code += self.indent * indentlevel + 'initial begin\n'
        for idx in range(self.rownum):
            code += self.indent * (indentlevel + 1) + f'src{idx} <= 0;\n'
        code += self.indent * indentlevel + 'end\n'
        return code

    def gen_always_block(self, indentlevel=1):
        code = ''
        code += self.indent * indentlevel + 'always @(posedge clk) begin\n'
        for idx in range(self.rownum):
            code += self.indent * (indentlevel + 1) + f'src{idx} <= {{src{idx}[{self.colnum - 2}:0], stream{idx}}};\n'
        code += self.indent * indentlevel + 'end\n'
        return code

if __name__ == '__main__':
    import sys
    colnum = int(sys.argv[1])
    rownum = int(sys.argv[2])
    mssr = MultiStage2_1ShiftRegister(colnum, rownum)
    print(mssr.gen_module())
    # mst = MultiStage2_1Testbench(colnum, rownum)
    # print(mst.gen_module())
    ms = MultiStage2_1(colnum, rownum)
    print(ms.gen_module())
    # for length in ms.rowadders:
    #     ra = RowAdder2_1(length)
    #     print(ra.gen_module())
