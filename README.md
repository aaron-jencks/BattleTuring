# Battle Turing
This is a project to facilitate the learning of the operation of turing machines by allowing users to implement their own
using a custom language.

## Installation

To install the program you need to install the prerequisites namely `pygame` and `pygame-menu`

```bash
pip install -r requirements.txt
```

Once you have the prereqs installed you can run the program by executing either [main.py](main.py) or [playground.py](playground.py).

```bash
python main.py
python playground.py
```

## Main

The main program has two modes, singleplayer, and multiplayer

### Singleplayer

Currently this is a copy of the playground, but will change in the future.

### Multiplayer

Coming soon.

## Playground

In [playground.py](playground.py) you can test your turing machine scripts, you can modify the initial tape, 
as well as load different scripts from text files. This is equivalent to using singleplayer in the main program (for now).

## The Language

This program uses a simple scripting language to allow for easy implementation of turing machines, with some extensions.
The language consists of a few key components:

1. Reading
2. Writing
3. Moving
4. Halting
5. Flow Control
6. Expressions
7. Functions

### Reading

Turing machines can read from the tape, this can be accomplished by using the `read` command or `^` for short.
This command by itself is not a valid statement, but can be used later on in Flow Control.

### Writing

Turing machines can write to the tape, this can be accomplished by using the `write` command for example:

```
write 'a'; # Writes the letter 'a' to the tape at the current position
```

### Moving

Turing machines can move left or right, this can be accomplished by using the `left/<<` or `right/>>` command, 
followed by a number, currently there is no default, a number must be supplied.

```
right 5; # Move right 5 spaces
left 20; # Move left 20 spaces
```

### Halting

In light of the knowledge of the halting problem, there is a `halt` command that will terminate the current program.
This is used instead of accept/reject states. If your machine halts, it's considered accepted, otherwise, 
transition to a infinite while loop.

```
halt;
```

**Note:** In multiplayer there is a time limit for execution.

### Flow Control

In addition to typical turing machine controls, simple flow control has also been implemented, 
this includes `if/else` and `while`.

#### If Else

To implement conditions in your turing machine, you can use an if statement this takes the syntax of `if(expr){...}`.

You can also have `else` statements immediately following an `if` statement.

**Example:**

```
# Simple if statement
if(!= read 'a') {
    left 1;
}

# With an else
if(= read 'a') {
    left 1;
}
else {
    right 1;
}
```

#### While Loops

For the sake of simplicity Battle Turing as also implemented while loops, similar in syntax to `if` statements

**Example:**

```
while(= read 'a') {
    right 1;
}

# Note there is no 'else' option after a while loop
```

### Expressions

Battle Turing supports most common binary equality operators, `=,<,>,<=,>=,!=`, note that `==` is symbolized as `=` here,
this is because there is no assignment operator. In addition to this, Battle Turing also supports negation using the 
`!` unary operator.

Some things to note:

- Comparisons can only be performed between like types (characters, booleans, and numerics)
- the `read` command returns a character
- The boolean constants are `true` and `false`.
- Expressions in Battle Turing use prefix notation (ie `= 5 6`)
- You can nest expressions with parenthesis.
- Comparisons between characters are done on their equivalent ascii codes (ie `'a' < 'b' < 'c'` etc...)

Some examples of valid expressions:

- `(= (> 5 6) (> 7 8))` Note that both the lhs, and rhs are both booleans
- `= read 'a'`
- `!= ^ 'a'`

Some examples of invalid expressions

- `= 5 'a'`
- `< (> 5 6) 7`
- `!= read 17`

### Functions

Battle Turing has also implemented the ability to use labels and goto's. For simplicity's sake they accept no arguments
and return nothing, the syntax is as follows:

Define a function/label:
```
foo:
{
    # Do something
}
```

Then you can call that function/label like this:

```
goto foo;
```

## Putting it all together

Below demonstrates a simple function that includes most if not all functionality in the language

```
print_name:
{
    write 'A';
    right 1;write 'a';
    right 1;write 'r';
    right 1;write 'o'; 
    right 1;write 'n';
    right 1;
}
goto print_name;
right 5;
left 20;
goto print_name;
while(= read '0') { write '1'; right 1; }
halt;
```
