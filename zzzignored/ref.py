# Ogólne metody
name = "dupa"
isinstance(name, str)  # sprawdza czy jest stringiem

# MATH OPERATORS
print(22 // 8)  # =2 integer division
print(22 / 8)  # = 2.75 division

# STRING
lotsofhellos = "hello" * 10  # hellohellohellohellohellohellohellohellohellohello

# VARIABLES
# 23_var = 'hello' #nie mozna liczb na poczatku


# konwencja wskazujaca, ze zmienna jest prywatna/internal i zeby jej nie uzywac dalej (ale w praktyce dalej publiczna)
_spam = 'Hello'
print(_spam)

# walrus operator
print(my_var := "Hello World!")  # jednoczesny assignent zmiennej
print(my_var)

# string formatting

# %s - String (or any object with a string representation, like numbers)
# %d - Integers
# %f - Floating point numbers
# %.<number of digits>f - Floating point numbers with a fixed amount of digits to the right of the dot.
# %x/%X - Integers in hex representation (lowercase/uppercase)

name = 'John'
print("Hello, %s!" % name)

age = 23

print("He's name is %s, and he's %d years old" %
      (name, age))  # kilka zmiennych

list = [1, 2, 3]
print("List: %s" % list)  # obiekty nie będące stringiem również formatujemy %s

# STRING METHODS

text = "Helo world"
print(len(text))
# na którym miejscu wystepuje o - zwroci wartosc dla pierwszego wystapienia; startuje liczenie od 0
print(text.index('o'))
print(text.count('l'))
print(text[3:7])  # zwroci indeksy 3-6 (inclusive tylko z lewej strony)
print(text[3])
print(text[-3])  # liczy od końca
print(text[3:])  # od 3go indeksu do konca
print(text[:7])  # od początku do 7
print(text[3:7:2])  # [start:stop:step]
print(text[::-1])  # reversing
print(text.upper())
print(text.lower())
# sprawdza czy string zaczyna sie na okreslone znaki
print(text.startswith("Hello"))
# sprawdza czy string konczy sie na okreslone znaki
print(text.endswith("asdfasdfasdf"))
awords = text.split(" ")  # tworzy tablice wyrazow na podstawie delimitera

# CONDITIONS
# if name == "John" and age == 23:
# if name == "John" or name == "Rick"
# if name in ["John", "Rick"]:

statement = False
another_statement = True
if statement is True:
    # do something
    # The pass statement in Python is a no-operation (no-op) placeholder. It means "do nothing."
    pass
    # All the pass statements are acting as placeholders inside the if, elif, and else blocks. These are there so Python doesn't raise a syntax error. You might use this pattern when you’re planning to fill in logic later.# elif another_statement is True: # else if
    # do something else
    pass

test = ""
if test:  # jakby if len(text) > 0 -> zwroci false m.in. dla "", None, [], (), {}, 0, 0.0
    print("Condition passed")
else:
    print("condition not passed")


x = [1, 2, 3]
y = [1, 2, 3]
print(x == y)  # Prints out True
print(x is y)  # Prints out False!!! bo inna instancja

test = "dupa"
result = test is test
print(f"Czy to ten sam objekt?: {result}")
print("Czy to ten sam objekt?: %s" % result)

print(not False)  # Prints out True
print((not False) == (False))  # Prints out False


# LISTS
even_numbers = [2, 4, 6, 8]
odd_numbers = [1, 3, 5, 7]
all_numbers = odd_numbers + even_numbers
print(all_numbers)  # [1, 3, 5, 7, 2, 4, 6, 8]

print("Alice"*5)
print([1, 2, 3] * 3)  # [1, 2, 3, 1, 2, 3, 1, 2, 3]

# LOOPS
for i, val in enumerate(["a", "b"]):
    print(i, val)

# for i in ["a", "b"]:
#     print(i, val)

# jeśli chcę poiterować 10 razy to mozna slicing
# for i in activities_timestamps_list[:10]:
#     print("Type of activity timestamp in list: %s" % type(i))

# list comprehension
# [row.timestamp for row in activities_rows_list if row.timestamp is not None]

# enumerate - mozna od razu index, oraz pozwala zaczac pozniej
# for idx, ts in enumerate(activities_timestamps_list, start=1):
#     print(f"Item {idx} has timestamp {ts}")


# zip method
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]

for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

numbers = [1, 2, 3, 4]

squared = [number**2 for number in numbers]
print(squared)
# inna opcja:
squared = list(map(lambda x: x**2, numbers))
print(squared)


_method - internal/helper function
__method - "name mangled" - private methods

__init__ in class definition - konstuktor, uruchamiany automatycznie przy tworzeniu objektu


def __init__(self, name, breed="Mixed", age=None): --self jako pierwsze w init; breed i age jako wartosci domyslne
