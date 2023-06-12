from lib import *
import sys
import os

# Accessing command-line arguments
arguments = sys.argv

if len(arguments) != 4:
    raise(ValueError(f"Need 3 Arguments: '[filename] [core count]', Got {len(arguments)-1} arguments!"))


source_code_file_name = arguments[1]
memory_file_name = arguments[2]
multi_core_count= arguments[3]

if not multi_core_count.isdigit():
    raise(ValueError(f"Core Count is not a digit! Got '{multi_core_count}' instead?"))
else:
    multi_core_count= int(arguments[3])


if not os.path.isfile(input_folder+source_code_file_name):
    raise(ValueError(f"'{source_code_file_name}' does not exist in folder 'input'"))
if not os.path.isfile(input_folder+memory_file_name):
    raise(ValueError(f"'{memory_file_name}' does not exist in folder 'input'"))

source_code_file_name = input_folder+arguments[1]
memory_file_name = input_folder+arguments[2]

with open(source_code_file_name, "r") as handler:
    content = handler.read()


parse_instance = Parser()
IR,depend,indep,line_depend= parse_instance.parse(content)

print("Generated IR")
print('"""')
pprint(IR)
print('"""')
print("\n\n\n")

#Intialize Code Generator Class
single_core_code_gen = CodeGen(1,path="single_core_code/")
multi_core_code_gen = CodeGen(multi_core_count,path="multi_core_code/")

#Run Code Gen
print("Running Single Core Code Generation")
single_core_code_gen.generate_backend_code(IR)
print()
print("Running Multi Core Code Generation")
multi_core_code_gen.generate_backend_code(IR)
print("\n\n\n")

#Intialize 
single_core_simulator = Simulator(1,'single_core_code/')
multi_core_simulator = Simulator(multi_core_count,'multi_core_code/')


#Running Simulations
mem = load_mem(memory_file_name)
for address, value in mem:
    single_core_simulator.MEM[address]= value
    multi_core_simulator.MEM[address]= value
print("Added Address Value Pairs to Memory")

print("Simulating Single Core Code")
print(f'Intial Single Core Memory:',single_core_simulator.MEM)
print('"""')
single_core_simulator.run()
print('"""')
print(f'Final Single Core Memory:',single_core_simulator.MEM)
print("\n\n")


print("Simulating Multi Core Code")
print(f'Intial Multi Core Memory:',multi_core_simulator.MEM)
print('"""')
multi_core_simulator.run()
print('"""')
print(f'Final Multi Core Memory:',multi_core_simulator.MEM)
print()


if single_core_simulator.MEM == multi_core_simulator.MEM:
    print(f'Single Core and Multi Core Memory Equal. Code ran correctly!')
else:
    print(f'Single Core and Multi Core Memory Not Equal! Code ran incorrectly.')
    print(f'Final Single Core Memory:',single_core_simulator.MEM)
    print(f'Final Multi Core Memory:',multi_core_simulator.MEM)