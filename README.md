# Corpe
compiler for a concatenative programming language in python

# syntax
write a plain number to push an integer to the stack  
numbers can be normal integers, or they can be prefixed with `0b` or `0B` (binary numbers) or with `0x` (hexadecimal)  
to print a number from the top of the stack use the word `print`  

```
20 print
// prints 20
```

to carry mathematical operations you have to firstly push some integers on the stack they tell it what to do
```
10 5 +
print
// prints 15
```

if statements are formed with if-end blocks  
the if word will pop the first element from the stack and if that element is not zero it will execute the code
```
5 5 - if 
    10 print
end  // this prints nothing as the first element on the stack was 0
```

while loops are formed with while-do-end blocks
```
while <condition> do
    <body>
end
```
when you hit the while word it executes the code that is passed as the condition and when it hits the do word it removes
the first element from the stack and if that element is not 0 it will execute the body

```
// print from 0-100
0 while 2dup 100 < do
    print
    1 +
end
// to print 100 write print but if you want up to 99 write drop so the last element that remains in the stack will be removed
drop
```

stack operations:  
- `drop`, it removes the element that is located on top of the stack
- `drop2`,  it removes the first two elements from the top of the stack
- `dup`,  it duplicates the element on top of the stack
- `dup2`, it duplicates the element in top of the stack twice
- `swap`, it swaps the first two elements from the stack
- `clear`, it clears the whole stack

you can set constants with the const word
```
const <name> <expresion> end
```
in the name field you add the name of the constant  
the expression can be simple Corpe code that will be evaluated

```
const N 2 50 / 10 + end  // this will evaluate 35
0 while dup N < do
    dup print
    1 +
end drop
```

# memory
to allocate some memory use the mem keyword

```
mem <name> <size> end
```
the size can even be a series of intstructions
```
mem X 10 5 + end
```
to access a part of that memory use mem-get

```
mem X 15 end
// <index-of-X> mem-get <memory-block>
0 mem-get X
// the returned value is pushed into the stack
```
to set a value in a memory block use mem-set
```
mem X 15 end
// <value> <index> mem-set <memory-block>
5 0 mem-set X

// and to show that it has changed 
0 mem-get X print
```

# variables
to declare a variable use the var keyword
```
var x
```
to set the value of a variable use the set keyword
```
var x
5 set x

```
the set keyword expects one value at the stack  
to get a variable value just type the name of the variable
```
var x
5 set x
x print
```

# note 
the default stack limit is 30k