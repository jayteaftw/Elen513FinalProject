# Final Project Elen 513


## How to Run

Run the following command to execute code.
```
python3 execute.py [source code file name] [memory file name] [core count]
```

For example, to execute the code in "code.txt" with memory values in "mem.txt" and a core count of 3. Run....
```
python3 execute.py code.txt mem.txt 3
```
Executable text files are found and have to be in the 'input/' folder.

### Operation's Handled
|Operation Name| Instruction | IR | Description |
|----------|----------|--------------------------|----------|
|Load|t1=LOAD(x);|('LOAD','t1','x',()) |Loads value from memory address 'x' into register 't1'.|
|Store|STORE(y,t8);|('STORE','y','t8',(7,))|Stores value in register 't8' into memory address 'y'. Line 7 must be excuted first. |
|Add|t2=t1+4;|('ADD', 't2', 't1', '4', (0,))|Adds value in register t1 with 4 and stores it in register t2. Line 0 must be excuted first|
|Subtract|t4=t1-4;|('SUB', 't4', 't1', '4', (0,))|Subtracts value in register t1 with 4 and stores it in register t4. Line 0 must be excuted first|
|Multiply|t9=t5*t2;|('MUL', 't9', 't5', 't2', (1, 4))|Multiplies value in register t9 with value in register t2 and stores it in register t9. Line 1 and 4 must be excuted first.|
|Divide|t5=t1/2;|('DIV', 't5', 't1', '2', (0,)),|Divides value in register t1 with 2 and stores it in register t5. Line 0 must be excuted first.|
|Square Root|t10=^t9;| ('SQRT', 't10', 't9', (8,))|Takes the square root of value in register t9 and stores it in register t10. Line 8 must be excuted first.|



## Approach



The Main Code Loop involves 3 Classes: ```Parser()```, ```CodeGen()```, and ```Simulator()```.
```
Main Code Loop
1. Takes input code, memory, core count.
2. Generates DFG and IR from Parser() Class.
3. The CodeGen() Class then uses the IR to distributes instrutions amongst PEs and generates a multi-core and a single-core compiled code. 
4. The Simulator() Class then simulates the cycle-by-cycle insutrction execution for both compiled codes and tests to see if the outputs are correct.
```



### Parser Class

Takes code from 'input/' folder and generates an optimized IR. 

Optimization includes dead code removal, constant folding, and constant propagation. 

Main IR creation function ```parse()``` from parser class executes
```
Parser().parse()
1. Generate Instruction Set from input code
2. Tokenized Instruction Set
3. Generate Partial IR from instruction set
4. Generate IR with Dependencies from Partial IR
5. Remove dead code and generate new Partial IR
6. Regenerate IR with Dependencies from Partial IR
7. While constant_folding is True
   1. Apply Constant Folding
   2. Apply Constant Propagation
   3. Regenerate IR with Dependencies from Partial IR
8. Generate Data Flow Graph and IR
```

### CodeGen Class

```
CodeGen().generate_compiled_code()
1. Create an initial assignment instruction to PEs
2. Get initial execution times
3. Check initial wordload imbalance
4. While new imbance < Current imbalance
    1. Rebalance workload by swaping tasks between the PE with the highest cycle count time and the PE with lowest cycle time
    2. Calculate new execution times
    3. Calculate new imbalance times
5. Synchronize multi-core compiled code with NOPs so instruction excecute correctly.
6. Generate final compiled code.
```


### Simulator Class


```
Simulator().run()
1. Load Compiled Code.
2. While PEs have instructions to run
    1. For every PE, If current instruction is finished, load next instruction and execute. 
    2. Update cycle time.
```





