#!/usr/bin/env python3

class RowAdder2_1:
    def __init__(self, colnum):
        self.colnum = colnum
        self.modulename = f'rowadder2_1_{self.colnum}'

    def gen_module(self):
        code = ''
        code += f'module {self.modulename}({self.get_module_arguments()});\n'
        code += self.gen_wires()
        code += f'endmodule\n'
        return code

    def gen_wires(self):
        code = ''
        return code

    def get_module_arguments(self):
        args = []
        args += [f'input [{self.colnum-1}:0] src0']
        args += [f'[{self.colnum-1}:0] src1']
        args += [f'output [{self.colnum}:0] dst0']
        return ', '.join(args)

    def lut5_2_initializer(self):
        gene, prop = 0, 0
        for num in range(4):
            gene |= int(f'{num:b}'.count('1') in [2, 3]) << num
            prop |= int(f'{num:b}'.count('1') in [1, 3]) << num
        return gene, prop

if __name__ == '__main__':
    ra21 = RowAdder2_1(64)
    print(ra21.gen_module())
