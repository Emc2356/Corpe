# Corpe
compiler for a concatenative programming language in python

# syntax
write a plain number, either a normal, hex or bin to push it to the data stack  
```
50
100
0b110001
0x55F995
```

# arithmetical operations
| name | signature | description |
|:----:|:---------:|:-----------:|
| `+` | `[a: int] [b: int] -- [a + b: int]` | sums two numbers from the top of the stack |
| `-` | `[a: int] [b: int] -- [a - b: int]` | subtracts two numbers from the top of the stack |
| `/` | `[a: int] [b: int] -- [a / b: int]` | divides two numbers from the top of the stack |
| `%` | `[a: int] [b: int] -- [a % b: int]` | divides two numbers from the top of the stack and returns the remainder |
| `*` | `[a: int] [b: int] -- [a * b: int]` | multiplies two numbers from the top of the stack |
| `**` | `[a: int] [b: int] -- [a ** b: int]` | raises one number to the power of another number |

# bitwise operators
| name | signature | description |
|:----:|:---------:|:-----------:|
| `&` | `[a: int] [b: int] -- [a & b: int]` | it performs bitwise and |
| <code>&#124;</code> | <code>[a: int] [b: int] -- [a &#124; b: int]</code> | it performs bitwise or |
| `~` | `[a: int] -- [~a: int]` | it performs bitwise not |
| `^` | `[a: int] [b: int] -- [a ^ b: int]` | it performs bitwise xor |
| `>>` | `[a: int] [b: int] -- [a >> b: int]` | it performs a bitwise right shift |
| `<<` | `[a: int] [b: int] -- [a << b: int]` | it performs a bitwise left shift |

# comparisons
| name | signature | description |
|:----:|:---------:|:-----------:|
| `<` | `[a: int] [b: int] -- [a< b: int]` | it checks if one number is less than the other number | 
| `<=` | `[a: int] [b: int] -- [a <= b: int]` | it checks if one number is less than or equal to another number | 
| `==` | `[a: int] [b: int] -- [a == b: int]` | it checks if two numbers are equal | 
| `!=` | `[a: int] [b: int] -- [a != b: int]` | it checks if two numbers are not equal | 
| `>=` | `[a: int] [b: int] -- [a >= b: int]` | it checks if one number is great than or equal to another number | 
| `>` | `[a: int] [b: int] -- [a> b: int]` | it checks if one number is greater than the other number | 

- `print`, print the number on top of the stack
```
a = pop()
print(a)
```
- `putc`, interpreters the number on top of the stack as a character and prints it
```
putc(a)
```
- `drop`, it removes the top element
```
a = pop()
```
- `2drop`, it removes the top 2 elements from the stack
```
a = pop()
b = pop()
```
- `dup`, duplicates the element on top of the stack
```
a = pop()
push(a)
push(a)
```
- `2dup`, duplicates the top 2 elements on the stop
```
a = pop()
b = pop()
push(b)
push(a)
push(b)
push(a)
```
- `swap`, it swaps the first two elements in the stack
```
a = pop()
b = pop()
push(a)
push(b)
```
- `clear`, it clears the data stack
```
stack.clear()
```

# type checking
corpe is a statically typed language  
some functions can only accept integers or only pointers or a mix  
to go from one type to the other use the `cast(int)` and `cast(ptr)`  

# memory system
to declare a chunk of memory use the `memory` keyword:
```
memory <name> <body> end
```
the name will be the identifier  
the body can be a simple number  
or a series of corpe code to be evaluated
```
memory x 8 end
```
the above code reserved an 8 byte block of memory  
to access this memory block you will use the store and load operators

| name | signature | description |
|:----:|:---------:|:-----------:|
| `!8`  | `[value: int] [location: ptr] --` | store the given number as a 1 byte number |
| `@8`  | `[location: ptr] -- [value: int]` | reads the pointer as a 1 byte number |
| `!16` | `[value: int] [location: ptr] --` | store the given number as a 2 byte number |
| `@16` | `[location: ptr] -- [value: int]` | reads the pointer as a 2 byte number |
| `!32` | `[value: int] [location: ptr] --` | store the given number as a 4 byte number |
| `@32` | `[location: ptr] -- [value: int]` | reads the pointer as a 4 byte number |
| `!64` | `[value: int] [location: ptr] --` | store the given number as a 8 byte number |
| `@64` | `[location: ptr] -- [value: int]` | reads the pointer as a 8 byte number |

```
memory x 4 end
100 memory !32
x @32 print // prints 100
```

# constants
to declare a constant use the `const` keyword
```
const <name> <body> end
```
the body will be evaluated at compile time 
```
const x 10 50 * end
x print
```

# loops
to create a loop use the 3 keyword loop, `while` `do` `end`
```
while <cond> do
    <body>
end
```
the while-do and the do-end are allowed to change the state of the stack but at the end it needs to be the same  
print the first 100 numbers with while loops
```
0 while dup 100 < do
    dup print
    1 +
end 0
```