from lib import *
import sys

# Accessing command-line arguments
arguments = sys.argv

if len(arguments) != 4:
    raise ValueError(f"Need 3 Arguments: '[filename] [core count]', Got {len(arguments)-1} arguments!")

# Extracting command-line arguments
source_code_file_name = arguments[1]
memory_file_name = arguments[2]
multi_core_count = arguments[3]

if not multi_core_count.isdigit():
    raise ValueError(f"Core Count is not a digit! Got '{multi_core_count}' instead?")

# Converting the multi_core_count to an integer
multi_core_count = int(arguments[3])

# Checking if source code file and memory file exist in the 'input' folder
if not os.path.isfile(input_folder + source_code_file_name):
    raise ValueError(f"'{source_code_file_name}' does not exist in folder 'input'")
if not os.path.isfile(input_folder + memory_file_name):
    raise ValueError(f"'{memory_file_name}' does not exist in folder 'input'")

# Updating the source code file name and memory file name with the input folder path
source_code_file_name = input_folder + arguments[1]
memory_file_name = input_folder + arguments[2]

# Reading the content of the source code file
with open(source_code_file_name, "r") as handler:
    content = handler.read()

# Parsing the source code using the Parser class
parse_instance = Parser()
IR, depend, indep, line_depend = parse_instance.parse(content)

print(f"Generating IR from '{source_code_file_name}'")
print('"""')
pprint(IR)
print('"""')
print("\n\n\n")

# Initializing Code Generator Class for single core and multi-core
single_core_code_gen = CodeGen(1, path=single_core_code_path)
multi_core_code_gen = CodeGen(multi_core_count, path=multi_core_code_path)

# Running Code Generation for single core
print("Running Single Core Code Generation")
single_core_code_gen.generate_compiled_code(IR)
print()

# Running Code Generation for multi-core
print("Running Multi Core Code Generation")
multi_core_code_gen.generate_compiled_code(IR)
print("\n\n\n")

# Initializing Simulators for single core and multi-core
single_core_simulator = Simulator(1, single_core_code_path)
multi_core_simulator = Simulator(multi_core_count, multi_core_code_path)

# Running Simulations
mem = load_mem(memory_file_name)
for address, value in mem:
    single_core_simulator.MEM[address] = value
    multi_core_simulator.MEM[address] = value
print("Added Address Value Pairs to Memory")

# Simulating Single Core Code
print("Simulating Single Core Code")
print(f'Intial Single Core Memory:', single_core_simulator.MEM)
print('"""')
final_single_core_cycle = single_core_simulator.run()
print('"""')
print(f'Final Single Core Memory:', single_core_simulator.MEM)
print("\n\n")

# Simulating Multi Core Code
print("Simulating Multi Core Code")
print(f'Intial Multi Core Memory:', multi_core_simulator.MEM)
print('"""')
final_multi_core_cycle = multi_core_simulator.run()
print('"""')
print(f'Final Multi Core Memory:', multi_core_simulator.MEM)
print()

print(f"Final Cycle Count: Single Core {final_single_core_cycle}, Multi-Core {final_multi_core_cycle}. Speed Up {round(final_single_core_cycle/final_multi_core_cycle,3)}")

# Checking if the single core and multi-core memories are equal
if single_core_simulator.MEM == multi_core_simulator.MEM:
    print(f'Single Core and Multi Core Memory Equal. Code ran correctly!')
else:
    print(f'Single Core and Multi Core Memory Not Equal! Code ran incorrectly.')
    print(f'Final Single Core Memory:', single_core_simulator.MEM)
    print(f'Final Multi Core Memory:', multi_core_simulator.MEM)
