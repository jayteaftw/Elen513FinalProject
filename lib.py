from graphviz import Digraph
from pprint import pprint
from time import sleep
import math
import copy
import json
import os

input_folder = "input/"
output_folder = "output/"
single_core_code_path=output_folder+"single_core_code/"
multi_core_code_path=output_folder+"multi_core_code/"

#Checks to see if required folders exist
for folder_path in [input_folder,output_folder,single_core_code_path,multi_core_code_path]:
    if not (os.path.exists(folder_path) and os.path.isdir(folder_path)):
        print(f"Creating Folder '{folder_path}' as it does not exist!")
        os.makedirs(folder_path)
print("\n\n")


#Checks if a number is a Float or Int
def is_number(string):
    """
    Checks if a string represents a valid float or integer number.
    
    Args:
        string (str): The string to be checked.

    Returns:
        bool: True if the string represents a float or integer, False otherwise.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def load_mem(file_name):
    """
    Input: file_name of memory file
    Output: list of address value pairs to be stored in memory

    Reads the contents of the specified memory file and processes each line to extract address-value pairs.
    Each line in the file should be in the format "address = value", where address is a string and value is a number.
    Returns a list of tuples, where each tuple contains the address-value pair extracted from the file.

    Raises a ValueError if a line in the file is not a valid address-value pair or if the value is not a number.

    Args:
        file_name (str): Name of the memory file.

    Returns:
        list: List of address-value pairs to be stored in memory.
    """

    with open(file_name, "r") as handler:
        contents = handler.readlines()
    
    mem_output = []
    for instruction in contents:
        to_mem = instruction.strip().replace(" ","").split("=")
        if len(to_mem) != 2:
            raise(ValueError(f"Error! '{instruction}' is not a valid memory address and value pair. \n Example: 'z = 30' stores 30 in memory address 'z'."))
        elif not is_number(to_mem[1]):
            raise(ValueError(f"Error! value'{to_mem[1]}' is not a float or int!"))
   
        to_mem[1] = float(to_mem[1])
        mem_output.append(to_mem)
    return mem_output

class Parser():
    """
    A class that parses an inputted code and generates an optimized IR.
    """
    def __init__(self) -> None:
        """
        Initializes the Parser class.

        - operators: List of arithmetic operators.
        - delims: List of delimiters.
        - symbol_to_name: Dictionary mapping operators to their corresponding names.
        - operator_map: Dictionary mapping operator names to their corresponding symbols.
        - dot: Graphviz Digraph object for visualizing the data flow graph.
        """
        self.operators = ["*","/","+","-","^"]
        self.delims = [" ", "(",")","="]
        self.symbol_to_name = { "+": "ADD",
                                "-": "SUB",
                                "*": "MUL",
                                "/": "DIV",
                                "^": "SQRT" }
        self.operator_map = {
                'ADD': '+',
                'SUB': '-',
                'MUL': '*',
                'DIV': '/',
            }
        self.dot = Digraph()
    
    def _gen_tokenized_list(self,instructions):
        """
        Generates a partial Intermediate Representation (IR) from a tokenized list.

        Args:
            tokenized_list (list): Tokenized list.

        Returns:
            list: Partial IR.
        """
        
        tokenized_list = []
        for instr in instructions[:]:
            tokens = []
            cur = ""
            pos = 0
            while pos < len(instr):
                if instr[pos] in self.delims or instr[pos] in self.operators:
                    if cur != "":
                        tokens.append(cur)
                    if instr[pos] != " ":
                        tokens.append(instr[pos].strip())
                    cur = ""
                else:
                    cur += instr[pos]
                pos += 1
            if cur != "":
                tokens.append(cur)
            tokenized_list.append(tokens)
        return tokenized_list

    def _gen_partial_IR(self, tokenized_list):
        """
        Generates a partial Intermediate Representation (IR) from a tokenized list, 
        and checks to see if all registers are proper.

        Args:
            tokenized_list (list): Tokenized list.

        Returns:
            list: Partial IR.
        """
        IR = []
        for tokens in tokenized_list:
            if "LOAD" in tokens:
                IR.append(("LOAD",tokens[0],tokens[4]))
            elif "=" in tokens:
                if len(tokens) == 3:
                    IR.append(("EQ",tokens[0],tokens[2]))
                elif tokens[2] != "^":
                    IR.append((self.symbol_to_name[tokens[3]],tokens[0],tokens[2],tokens[4]))
                else:
                    IR.append((self.symbol_to_name[tokens[2]],tokens[0],tokens[3]))
            elif "STORE" in tokens:
                IR.append(("STORE",tokens[2],tokens[4]))
        
        def register_checking(token,registers):
            for reg in registers:
                if not is_number(reg) and reg[0] != "t":
                    raise(ValueError(f"{reg} is not a proper register in instruction {token}. All register start with 't' such as 't8'."))

        for token in IR:
            if token[0] in ["LOAD"]:
                register_checking(token,token[1])
            elif token[0] in ["STORE"]:
                register_checking(token,token[2])
            elif token[0] in self.operator_map:
                print(token,token[1:4] )
                register_checking(token,token[1:4])
            elif token[0] in ['SQRT', 'EQ']:
                register_checking(token,token[1:3])
            
        return IR 

    def _gen_dependencies(self,IR):
        """
        Generates Read-after-Write (RAW) and Write-after-read (WAR) dependencies from a partial IR.

        Args:
            IR (list): Partial IR.

        Returns:
            tuple: IR, RAW, WAR, edges, and write_depend.
        """
        RAW, WAR = [], []
        write_depend, read_depend = [], [] #Pos of WAR, and RAW in list
        edges = []

        for instr in IR:
            depend_tokens = []
            depend_tokens_pos = []
            #Check Read Dependicies
            for token in  instr[2:]:
                #print(token,instr[2:],indep)  
                for pos, dep_token in reversed(list(enumerate(RAW))):
                    if token == dep_token:
                        if token not in depend_tokens: 
                            depend_tokens.append(token)
                            depend_tokens_pos.append(pos)
                        break
                    
            #Check Write Dependicies
            token = instr[1]
            read_tokens = []
            read_tokens_pos = []
            for pos , tokens in  enumerate(WAR):
                if token in tokens:
                    read_tokens.append(token)
                    read_tokens_pos.append(pos)


            read_depend.append(tuple(set(read_tokens_pos)))
            RAW.append('' if instr[1] == "STORE" else instr[1])
  
            WAR.append(depend_tokens)
            write_depend.append(tuple(set(depend_tokens_pos)))

        for x, ys in enumerate(write_depend):
            for y in ys:
                edges.append((y,x))

        for idx in range(len(IR)):
            all_depend = tuple(set((write_depend[idx]+read_depend[idx])))
            IR[idx] = IR[idx] +tuple((all_depend, ))
        
        return IR, RAW, WAR, edges, write_depend

    def _remove_duplicate_code(self, IR):
        """
        Removes duplicate code from the IR.

        Args:
            IR (list): IR.

        Returns:
            list: New partial IR without duplicate code.
        """
        new_partial_IR = []
        visited = set()
        for instruction in IR:
            if instruction not in visited:
                new_partial_IR.append(instruction[:len(instruction)-1])
                visited.add(instruction)

        return new_partial_IR

    def _dead_code_removal(self, IR, write_depend, instructions):
        """
        Removes dead code from the IR.
        Dead code refers to code that is not stored in memory.

        Args:
            IR (list): IR.
            write_depend (list): Positions of write dependencies.
            instructions (list): List of instructions.

        Returns:
            tuple: New instructions and new partial IR.
        """


        instructions_keep = set()
        store_instructions_pos = []
        for idx, instrc in enumerate(IR):
            if instrc[0] == "STORE":
                store_instructions_pos.append(idx)
        
        #Helper function to find which instructions are part 
        #of the dependency chain to a store instruction.
        def dfs(idx):
    
            if len(write_depend[idx]) ==0 or IR[idx][0] == "LOAD":
                instructions_keep.add(idx)
                return True
            results = False
            for pos in write_depend[idx]:
                if dfs(pos):
                    results = True or results
            if results:
                instructions_keep.add(idx)
            return results

        for instrc_idx in store_instructions_pos:
            dfs(instrc_idx)

        new_IR_Partial, new_instructions = [], []
        for idx, instruction in enumerate(IR):
            if idx in instructions_keep:
                new_IR_Partial.append(instruction[:len(instruction)-1])
                new_instructions.append(instructions[idx])

        return new_instructions, new_IR_Partial

    def _constant_folding(self,IR):
        """
        Applies constant folding to instructions that have constants as their read registers.
        Example: 'ADD t1, 1, 1' becomes 'EQ, t1, 2' 

        Args:
            IR (list): IR.

        Returns:
            list: New partial IR.
        """
        for idx, instruction in enumerate(IR):
            if instruction[0] in self.symbol_to_name.values():
                if instruction[0] == "SQRT":
                    if is_number(instruction[2]):
                        IR[idx] = ('EQ', instruction[1], str(math.sqrt(float(instruction[2]))), instruction[3] )   
                else:
                    if is_number(instruction[2]) and is_number(instruction[3]):
                        result = eval(instruction[2]  +  self.operator_map[instruction[0]]  + instruction[3])
                        IR[idx] = ('EQ', instruction[1], str(result), instruction[4] )
        return IR 

    def _constant_propogation(self, IR, write_depend):
        """
        Applies constant propagation to instructions that read from instructions that are constant.
        Example: 'EQ, t1, 1','ADD t1, t1, 2' becomes 'ADD t1, 1, 2'

        Args:
            IR (list): IR.
            write_depend (list): Positions of write dependencies.

        Returns:
            tuple: New partial IR and boolean indicating if any constant folding occurred.
        """
        bool = False
        for idx, instruction in enumerate(IR):

            if instruction[0] == "LOAD":
                continue

            value1 = instruction[2]
            value2 = instruction[3]
            
            for pos in write_depend[idx]:
                if IR[pos][0] != "EQ":
                    continue
                constant = IR[pos][1]
                value = IR[pos][2]

                if instruction[2] == constant:
                    value1 = value
                    bool = True

                if instruction[0] not in ["STORE","SQRT"]:
    
                    if instruction[3] == constant:
                        value2 = value
                        bool = True

            if len(IR[idx]) == 5:
                IR[idx] = (instruction[0], instruction[1], value1, value2, instruction[4])
            else:
                IR[idx] = (instruction[0], instruction[1], value1, instruction[3])


        new_partial_IR = []
        for idx, instruction in enumerate(IR):
            if instruction[0] != "EQ":
                if len(instruction) == 5:
                    x = (instruction[0],instruction[1],instruction[2],instruction[3])
                else:
                    x = (instruction[0],instruction[1],instruction[2])
                new_partial_IR.append(x)
        
        return  new_partial_IR, bool

    def _IR_to_instruction(self, IR):
        """
        Converts IR to an instruction list.

        Args:
            IR (list): IR.

        Returns:
            list: Instruction list.
        """
        instructions = []
        for instruction in IR:
            if instruction[0] == "LOAD":
                name = f'{instruction[1]}=LOAD({instruction[2]})'
            elif instruction[0] == "STORE":
                name = f'STORE({instruction[1]},{instruction[2]})'
            elif instruction[0] == "EQ": 
                name = f'{instruction[1]}={instruction[2]}'
            elif instruction[0] in self.operator_map: 
                name = f'{instruction[1]}={instruction[2]}{self.operator_map[instruction[0]]}{instruction[3]}'
            elif instruction[0] in "SQRT": 
                name = f'{instruction[1]}=^{instruction[2]}'
            instructions.append(name)
        return instructions

    def _dfg(self,instructions,edges):
        """
        Generates a data flow graph from the inputted instruction list and edges.
        """
        self.dot = Digraph()
        file_contents = ""
        for idx, instr in enumerate(instructions):
            self.dot.node(str(idx), str(idx)+": "+str(instr))
            file_contents += f"{idx}: {instr}\n"

        for x,y in edges:
            self.dot.edge(str(x),str(y))
            file_contents += f"{x}->{y}\n"
        
        with open(output_folder+"DFG.output", "w") as f:
            f.write(file_contents)

        self.dot.render(output_folder+'DFG_image',format='svg')

    def parse(self,code):
        """
        Parses the inputted code and generates the intermediate representation (IR), dependencies, write-after-read (WAR)
        dependencies, and write dependencies.

        Args:
            code (str): Code to parse.

        Returns:
            tuple: IR, dependencies, WAR dependencies, and write dependencies.
        """
    
        instructions = [instr.strip("\n") for instr in code.split(";")[:-1]]

        #Tokenize instruction set
        tokenized_list = self._gen_tokenized_list(instructions)
        
        #Generates partial IR without dependency list
        IR_partial = self._gen_partial_IR(tokenized_list)
        
        #Generates IR(with dependencies list)
        IR, writes, depend, edges, write_depend = self._gen_dependencies(IR_partial)
        
        #Remove Duplicate code
        IR, writes, depend, edges, write_depend = self._gen_dependencies(self._remove_duplicate_code(IR))

        #Handles WAW and insutrctions that have no dependecies
        instructions, IR_partial = self._dead_code_removal(IR, write_depend, instructions)

        #Regenerate New IR with update instruction list
        IR, writes, depend, edges, write_depend = self._gen_dependencies(IR_partial)
        
        #Constant Folding then Propgation Loop. 
        #Evaluates constant expressions and Replaces variables with constants.
        constant_folding_bool = True
        while(constant_folding_bool):
            #Constant Folding
            IR = self._constant_folding(IR)
            
            #Constant Propogation
            IR_partial, constant_folding_bool = self._constant_propogation(IR, write_depend)

            #Regenerate New IR with update instruction list
            IR, writes, depend, edges, write_depend = self._gen_dependencies(IR_partial)


        instructions = self._IR_to_instruction(IR)

        #Generate DFG output and image
        self._dfg(instructions,edges)
        
        return IR, depend, writes, write_depend

class CodeGen():
    """
    A class that generates compiled code for a multi-PE environment.
    """
    def __init__(self,num_PEs,path="/") -> None:
        """
        Initializes the CodeGen.

        Args:
            num_PEs (int): The number of processing elements (PEs).
            path (str, optional): The path to the input files. Defaults to "/".
        """
        self.file_path = path
        self.num_PEs = num_PEs
        with open(input_folder+'operation_latency.json', 'r') as f:
            self.cycle_times = json.load(f)
    
    def generate_compiled_code(self,IR):
        """
        Generates compiled code for a given set of intermediate representation (IR) tasks.

        Args:
            IR (list): The list of intermediate representation (IR) tasks.
        """
        
        # Step 1: Assign initial tasks to PEs
        assignments = self._initial_assignment(IR)
        
        #Step 2: calculates execution times for each PE
        execution_times = self._calculate_execution_times(assignments)

        # Step 3: Check workload imbalance
        max_execution_time = max(execution_times)
        min_execution_time = min(execution_times)
        cur_imbalance = max_execution_time - min_execution_time

        iteration = 0

        print(f"Iteration: {iteration}\t Initial Imbalance: {cur_imbalance}")
        #Repeat 4-6
        while True:
            
            iteration += 1 
            # Step 4: Task migration or swapping strategy
            new_assignments = self._rebalance_workload(assignments, execution_times)

            # Step 5: Calculate execution cost for each PE
            execution_times = self._calculate_execution_times(new_assignments)

            # Step 6: Check workload imbalance
            max_execution_time = max(execution_times)
            min_execution_time = min(execution_times)
            new_imbalance = max_execution_time - min_execution_time

            print(f"Iteration: {iteration}\t New Imbalance: {new_imbalance}, Current Imbalance: {cur_imbalance}")
            if new_imbalance >= cur_imbalance or cur_imbalance==0:
                print(f"Stopping with an Current Imbalance of {cur_imbalance}")
                
                break  # Terminate if workload is balanced within threshold or maximum iterations reached
            cur_imbalance = new_imbalance
            assignments = new_assignments
            
        #Step 7
        synced_tasks = self._sync(assignments, IR)
        for pe_id, assigned_tasks in enumerate(synced_tasks):
            # Step 8: Generate output code for each PE
            code = self._generate_code(assigned_tasks)

            # Step 9: Dump output code to files
            self._dump_code_to_file(code, pe_id)

    def _initial_assignment(self,tasks):
        """
        Assigns initial tasks to PEs.

        Args:
            tasks (list): The list of tasks.

        Returns:
            list: The initial task assignments to PEs.
        """
        
        assignments = [[] for _ in range(self.num_PEs)]
        task_index = 0

        for task in tasks:
            pe_id = task_index % self.num_PEs
            assignments[pe_id].append(task)
            task_index += 1

        
        return assignments

    def _calculate_execution_times(self,assignments):
        """
        Calculates the execution time for each PE.

        Args:
            assignments (list): The task assignments to PEs.

        Returns:
            list: The execution times for each PE.
        """
        execution_times = []

        for assigned_tasks in assignments:
            execution_time = 0
            for task in assigned_tasks:
                if task:
                    task_name = task[0]
                    if task_name in self.cycle_times:
                        execution_time += self.cycle_times[task_name]
            execution_times.append(execution_time)

        return execution_times

    def _rebalance_workload(self,assignments, execution_times):
        """
        Performs task migration or swapping to balance the workload.

        Args:
            assignments (list): The task assignments to PEs.
            execution_times (list): The execution times for each PE.

        Returns:
            list: The new task assignments after workload rebalancing.
        """

        new_assignments = copy.deepcopy(assignments)
        
        max_index = execution_times.index(max(execution_times))
        min_index = execution_times.index(min(execution_times))

        # Swap a task from the most loaded PE to the least loaded PE
        task_to_swap = new_assignments[max_index].pop(0)
        new_assignments[min_index].append(task_to_swap)

        return new_assignments

    def _sync(self,assignments, IR):
        """
        Synchronizes tasks across PEs.

        Args:
            assignments (list): The task assignments to PEs.
            IR (list): The list of intermediate representation (IR) tasks.

        Returns:
            list: The synchronized tasks across PEs.
        """
        sync_code = [[] for _ in range(len(assignments))]
        hash = {}
        instruction_cycle_times = [self.cycle_times[task[0]] for task in IR]
        for pos, instruc in enumerate(IR):
            hash[instruc] = pos
            

        live_time = [0 for _ in range(len(assignments)) ]
        current_instruction = ["NOP"for _ in range(len(assignments)) ]
        numerical_assignment = [[(hash[task],task[-1]) for task in tasks] for tasks in assignments ]

        instructions_done = set()
        instructions_done.add(None)
        cycle = 1
        while len(IR) != len(instructions_done)-1:

            for idx, (current, count) in enumerate(zip(current_instruction,live_time)):
                if current != "NOP":
                    if count <= 1:
                        instructions_done.add(current)
                        current_instruction[idx] = "NOP"
                    live_time[idx] -= 1

            for assignment_id, tasks in enumerate(numerical_assignment):
                
                if current_instruction[assignment_id] == "NOP":
                    for task in tasks:
                        #print(assignment_id, task, type(task[1]), task[0] not in instructions_done and task[1] in instructions_done)
                        if task[0] not in instructions_done and all(num in instructions_done for num in task[1]):
                            #print("Added ",task[0])
                            current_instruction[assignment_id] = task[0]  
                            live_time[assignment_id] = instruction_cycle_times[task[0]]
                            sync_code[assignment_id].append(IR[task[0]])
                            break

                if current_instruction[assignment_id] == "NOP" and len(IR) != len(instructions_done)-1:
                    sync_code[assignment_id].append("NOP")

            cycle += 1
        return  sync_code 
            
    def _generate_code(self,tasks):
        """
        Generates output code for a given set of tasks.

        Args:
            tasks (list): The list of tasks.

        Returns:
            str: The generated output code.
        """
        code = ""
        self.cycle_times['N'] = 1
        for task in tasks:
            if task:
                for idx in range(self.cycle_times[task[0]]):
                        task_formated = str(task[:len(task)-1]).strip("()").replace("'", "") if task != "NOP" else task
                        code += (task_formated + "\n")  if idx == 0 else "\n"

        return code

    def _dump_code_to_file(self,code, pe_id):
        """
        Dumps the generated code to a file for a specific PE.

        Args:
            code (str): The generated code.
            pe_id (int): The ID of the processing element (PE).
        """
        filename = f"{self.file_path}PE_{pe_id}_code.txt"

        with open(filename, "w") as file:
            file.write(code)

class Simulator():
    """
    A class that simulates the execution of instructions in a multi-PE environment.
    """

    def __init__(self, pes, file_path) -> None:
        """
        Initializes the Simulator.

        Args:
            pes (int): The number of processing elements (PEs).
            file_path (str): The path to the input files.
        """
        self.MEM = {}
        self.RG = {}
        self.pe_count = pes
        self.file_path = file_path
        with open(input_folder+'operation_latency.json', 'r') as f:
            self.cycle_times = json.load(f)
        self.cycle_times['NOP'] = 1
    
    def _load_files(self):
        """
        Loads the code from input files.

        Returns:
            list: The loaded code for each processing element.
        """
        code = []
        for pe in range(self.pe_count):
            file_name = f'PE_{pe}_code.txt'
            with open(self.file_path+file_name) as f:
                data = f.read()
            code.append([[j.replace(" ",'') for j in i.split(",")]for i in data.split("\n") if i])
        return code

    def run(self):
        """
        Runs the simulation.

        Returns:
            int: The total number of cycles executed.
        """
        code = self._load_files()
        instruction_running = ["NOP"]*self.pe_count
        live_cycles = [0]*self.pe_count
        instruction_pos = [0]*self.pe_count
        cycle = 1
        while all((instruction_pos[pe] < len(code[pe])) for pe in range(self.pe_count)):
            
            for pe in range(self.pe_count):

                pos = instruction_pos[pe]
                if pos >= len(code[pe]):
                    continue

                #Cycle over. Update with New instruction
                if live_cycles[pe] == 0:
                    instruction_running[pe] = code[pe][pos]
                    live_cycles[pe] = self.cycle_times[instruction_running[pe][0]]
                    instruction_pos[pe] += 1
                    self._execute(instruction_running[pe])
            
            
            message = f'Cycle:{cycle},'
            message = f'{message:<12}'
            for idx,pe in enumerate(range(self.pe_count)):
                instruction_pe = f"PE_{pe}: {', '.join(instruction_running[pe])}[{live_cycles[pe]}], "
                column_pos = 30 
                message += f"{instruction_pe:<{column_pos}}"
            print(message)

            #Update cycle times
            for pe in range(self.pe_count):
                live_cycles[pe] -= 1
            cycle += 1
        return cycle-1 if cycle-1 > 0 else 0
    
    def _execute(self, instruction):
        """
        Executes the given instruction.

        Args:
            instruction (list): The instruction to execute.
        """
        instruction_name = instruction[0]
        
        if instruction_name == "LOAD":
            if instruction[2] not in self.MEM:
                raise(ValueError(f'{instruction[2]} is not in Memory'))
            self.RG[instruction[1]] = self.MEM[instruction[2]]
            
        elif instruction_name == "STORE":
            if instruction[2] not in self.RG and not is_number(instruction[2]):
                raise(ValueError(f'{instruction[2]} is not in Register Files'))
            self.MEM[instruction[1]] = self.RG[instruction[2]] if not is_number(instruction[2]) else float(instruction[2])
        
        elif instruction_name in ["ADD","SUB", "MUL", "DIV", "SQRT"]:
            operator_map = {
                'ADD': '+',
                'SUB': '-',
                'MUL': '*',
                'DIV': '/',
            }
            x =  self.RG[instruction[2]] if instruction[2][0] == 't' else instruction[2]
            if instruction_name != 'SQRT':
                y =  self.RG[instruction[3]] if instruction[3][0] == 't' else instruction[3]
                expression =  str(x)  +  operator_map[instruction_name]  + str(y)
                self.RG[instruction[1]] = eval(expression)
            else:
                self.RG[instruction[1]] = math.sqrt(float(x))

        elif instruction_name == "NOP":
            pass

        else:
            raise(ValueError(f'Unknown Instruction: {instruction}'))
        
