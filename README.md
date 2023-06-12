# Final Project Elen 513


## How to Run

Run the command 
'''
python3 execute.py [source code file name] [memory file name] [core count]
'''
to execute code.

### Operation Handled
|Operation Name| Instruction | IR | Description |
|----------|----------|--------------------------|----------|
|Load|t1=LOAD(x);|('LOAD','t1','x',()) |Loads value from memory address 'x' into register 't1'.|
|Store|STORE(y,t8);|('STORE','y','t8',(7,))|Stores value in register 't8' into memory address 'y'. Line 7 must be excuted first. |
|Add|t2=t1+4;|('ADD', 't2', 't1', '4', (0,))|Adds value in register t1 with 4 and stores it in register t2. Line 0 must be excuted first|
|Subtract|t4=t1-4;|('SUB', 't4', 't1', '4', (0,))|Subtracts value in register t1 with 4 and stores it in register t4. Line 0 must be excuted first|
|Multiply|t9=t5*t2;|('MUL', 't9', 't5', 't2', (1, 4))|Multiplies value in register t9 with value in register t2 and stores it in register t9. Line 1 and 4 must be excuted first.|
|Divide|t5=t1/2;|('DIV', 't5', 't1', '2', (0,)),|Divides value in register t1 with 2 and stores it in register t5. Line 0 must be excuted first.|
|Square Root|t10= ^ t9;| ('SQRT', 't10', 't9', (8,))|Takes the square root of value in register t9 and stores it in register t10. Line 8 must be excuted first.|



## Approach




### Parser Class



### CodeGen Class


### Simulator Class







