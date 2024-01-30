#!/usr/bin/env python3

def ceil4(num):
    return num if num % 4 == 0 else num + 4 - num % 4

class RowAdder2_1:
    def __init__(self, colnum):
        self.colnum = colnum
        self.ceiled = ceil4(self.colnum)
        self.modulename = f'rowadder2_1_{self.colnum}'
        self.indent = '   '

    def gen_module(self):
        code = ''
        code += f'module {self.modulename}({self.get_module_arguments()});\n'
        code += self.gen_wires()
        code += self.gen_lut_instantiations()
        code += self.gen_carry4_instantiations()
        code += self.gen_assignment()
        code += f'endmodule\n'
        return code

    def gen_wires(self, indentlevel=1):
        code = ''
        code += self.indent * indentlevel + f'wire [{self.colnum - 1}:0] gene;\n'
        code += self.indent * indentlevel + f'wire [{self.colnum - 1}:0] prop;\n'
        code += self.indent * indentlevel + f'wire [{self.ceiled - 1}:0] out;\n'
        code += self.indent * indentlevel + f'wire [{self.ceiled - 1}:0] carryout;\n'
        return code

    def gen_assignment(self, indentlevel=1):
        return self.indent * indentlevel + f'assign dst0 = {{carryout[{self.colnum-1}], out[{self.colnum-1}:0]}};\n'

    def gen_lut_instantiations(self, indentlevel=1):
        def gen_lut2_1(init, idx, name, outwire):
            code = ''
            code += self.indent * indentlevel + f'LUT2 #(\n'
            code += self.indent * (indentlevel + 1) + f'.INIT(4\'h{init:01x})\n'
            code += self.indent * indentlevel + f') {name} (\n'
            code += self.indent * (indentlevel + 1) + f'.I0(src0[{idx}]),\n'
            code += self.indent * (indentlevel + 1) + f'.I1(src1[{idx}]),\n'
            code += self.indent * (indentlevel + 1) + f'.O({outwire}[{idx}])\n'
            code += self.indent * indentlevel + f');\n'
            return code
        code = ''
        gene, prop = self.lut_initializer()
        for idx in range(self.colnum):
            code += gen_lut2_1(gene, idx, f'lut_{idx}_gene', 'gene')
            code += gen_lut2_1(prop, idx, f'lut_{idx}_prop', 'prop')
        return code

    def gen_carry4_instantiations(self, indentlevel=1):
        def gen_carry4(idx, name):
            code = ''
            code += self.indent * indentlevel + f'CARRY4 {name} (\n'
            code += self.indent * (indentlevel + 1) + f'.CO(carryout[{idx+3}:{idx}]),\n'
            code += self.indent * (indentlevel + 1) + f'.O(out[{idx+3}:{idx}]),\n'
            code += self.indent * (indentlevel + 1) + f'.CI(1\'h0),\n'
            code += self.indent * (indentlevel + 1) + f'.CYINIT(1\'h0),\n'
            if self.colnum - 1 >= idx + 3:
                code += self.indent * (indentlevel + 1) + f'.DI(gene[{idx+3}:{idx}]),\n'
                code += self.indent * (indentlevel + 1) + f'.S(prop[{idx+3}:{idx}])\n'
            else:
                remain = 4 - self.colnum % 4
                code += self.indent * (indentlevel + 1) + f'.DI({{{remain}\'h0, gene[{self.colnum - 1}:{idx}]}}),\n'
                code += self.indent * (indentlevel + 1) + f'.S({{{remain}\'h0, prop[{self.colnum - 1}:{idx}]}})\n'
            code += self.indent * indentlevel + f');\n'
            return code
        code = ''
        for idx in range(0, self.ceiled, 4):
            code += gen_carry4(idx, f'carry4_{idx+3}_{idx}')
        return code

    def get_module_arguments(self):
        args = []
        args += [f'input [{self.colnum - 1}:0] src0']
        args += [f'input [{self.colnum - 1}:0] src1']
        args += [f'output [{self.colnum}:0] dst0']
        return ', '.join(args)

    def lut_initializer(self):
        gene, prop = 0, 0
        for num in range(4):
            gene |= int(f'{num:b}'.count('1') in [2, 3]) << num
            prop |= int(f'{num:b}'.count('1') in [1, 3]) << num
        return gene, prop

if __name__ == '__main__':
    ra21 = RowAdder2_1(63)
    print(ra21.gen_module())
