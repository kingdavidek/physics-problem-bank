import random
from generators.shared.utils import (
    make_problem,
    format_cs_prose,
    format_cs_mcq_option,
)
from generators.shared.variant_utils import pick_named_variant

# ------------------------------------------------------------
# GCSE Python Programming – 42 exam-style questions
# Solutions use <pre><code> for proper indentation
# ------------------------------------------------------------

# ---------- FOUNDATIONAL (4) ----------
def py_found_hello():
    q = "Write a line of Python code that prints the exact text: **Hello, World!**"
    s = r"""<pre><code>print('Hello, World!')</code></pre>"""
    hint = "Use the `print()` function."
    return q, s, hint, 1

def py_found_age():
    q = "Write Python code that asks the user for their age, converts it to an integer, and then prints 'Next year you will be `x`', where `x` is the age plus one."
    s = r"""<pre><code>age = int(input('Enter your age: '))
print('Next year you will be', age + 1)</code></pre>"""
    hint = "Use `input()`, `int()`, and a comma in `print()`."
    return q, s, hint, 2

def py_found_pass():
    q = "A variable `score` holds an integer. Write an `if`/`else` statement that prints **Pass** if `score` is 50 or higher, otherwise prints **Fail**."
    s = r"""<pre><code>if score >= 50:
    print('Pass')
else:
    print('Fail')</code></pre>"""
    hint = "Use `>=` for the comparison."
    return q, s, hint, 2

def py_found_for():
    q = "Write a `for` loop that prints every integer from **1 to 10** (inclusive)."
    s = r"""<pre><code>for i in range(1, 11):
    print(i)</code></pre>"""
    hint = "`range(start, stop)` goes up to, but does not include, `stop`."
    return q, s, hint, 2

def py_found_variables():
    q = "Write Python code that creates three variables: `name` (a string), `age` (an integer), and `height` (a float). Assign any sensible values and then print all three on one line separated by spaces."
    s = r"""<pre><code>name = 'Alice'
age = 16
height = 1.65
print(name, age, height)</code></pre>"""
    hint = "Strings go in quotes; integers and floats do not. `print()` with commas adds spaces automatically."
    return q, s, hint, 1

def py_found_string_concat():
    q = "Write Python code that asks the user to enter their first name and then their last name. Print the message: **Hello, FirstName LastName!** (using the values they entered)."
    s = r"""<pre><code>first = input('First name: ')
last = input('Last name: ')
print('Hello, ' + first + ' ' + last + '!')</code></pre>"""
    hint = "Use `+` to join strings together, or put the variables directly inside an f-string."
    return q, s, hint, 2

def py_found_area():
    q = "Write Python code that asks the user for the **length** and **width** of a rectangle (both as decimal numbers), then prints the area."
    s = r"""<pre><code>length = float(input('Length: '))
width = float(input('Width: '))
print('Area:', length * width)</code></pre>"""
    hint = "Use `float()` to convert the input, then multiply."
    return q, s, hint, 2

def py_found_countdown():
    q = "Write a `while` loop that counts **down** from 10 to 1 (inclusive), printing each number, then prints **Blast off!** after the loop ends."
    s = r"""<pre><code>count = 10
while count >= 1:
    print(count)
    count = count - 1
print('Blast off!')</code></pre>"""
    hint = "Start `count` at 10, keep looping while `count >= 1`, and decrease by 1 each time."
    return q, s, hint, 2

def py_found_elif():
    q = "Write Python code that asks the user to enter a temperature as an integer. Print **Cold** if it is below 10, **Warm** if it is between 10 and 24 (inclusive), and **Hot** if it is 25 or above."
    s = r"""<pre><code>temp = int(input('Temperature: '))
if temp < 10:
    print('Cold')
elif temp < 25:
    print('Warm')
else:
    print('Hot')</code></pre>"""
    hint = "Use `if`/`elif`/`else`. The `elif` checks the next condition only if the `if` was False."
    return q, s, hint, 2

def py_found_list_build():
    q = "Write Python code that starts with an **empty list**, then appends the numbers **2, 4, 6, 8, 10** one at a time using `.append()`, and finally prints the list."
    s = r"""<pre><code>evens = []
evens.append(2)
evens.append(4)
evens.append(6)
evens.append(8)
evens.append(10)
print(evens)</code></pre>"""
    hint = "Create `[]` first, then call `.append(value)` five times."
    return q, s, hint, 2

def py_found_index():
    q = "Given the list `colours = ['red', 'green', 'blue', 'yellow', 'purple']`, write two lines of code that print the **first** element and the **last** element using index positions."
    s = r"""<pre><code>colours = ['red', 'green', 'blue', 'yellow', 'purple']
print(colours[0])
print(colours[-1])</code></pre>"""
    hint = "The first element is at index `0`; the last is at index `-1`."
    return q, s, hint, 1

def py_found_round():
    q = "Write Python code that asks the user to enter a decimal number. Print the number **rounded to 2 decimal places** using the `round()` function."
    s = r"""<pre><code>num = float(input('Enter a decimal number: '))
print(round(num, 2))</code></pre>"""
    hint = "Use `float()` to convert the input, then `round(value, 2)` to round to 2 places."
    return q, s, hint, 2

def py_found_modulo():
    q = "Write Python code that asks the user for a whole number. If the number is exactly divisible by 3, print **Divisible by 3**, otherwise print **Not divisible by 3**."
    s = r"""<pre><code>n = int(input('Enter a number: '))
if n % 3 == 0:
    print('Divisible by 3')
else:
    print('Not divisible by 3')</code></pre>"""
    hint = "The modulo operator `%` gives the remainder. If `n % 3 == 0`, it divides exactly."
    return q, s, hint, 2

def py_found_upper_count():
    q = "Write Python code that asks the user to enter a sentence. Print the sentence in **all uppercase letters**, then on the next line print the **number of words** in the sentence."
    s = r"""<pre><code>sentence = input('Enter a sentence: ')
print(sentence.upper())
print(len(sentence.split()))</code></pre>"""
    hint = "Use `.upper()` to capitalise and `.split()` to break into words; `len()` counts them."
    return q, s, hint, 2

# ---------- INTERMEDIATE (4) ----------
def py_inter_reverse():
    q = "Write Python code that asks the user to enter a word, then prints the word **reversed** (e.g. `'hello'` prints `'olleh'`)."
    s = r"""<pre><code>word = input('Enter a word: ')
print(word[::-1])</code></pre>"""
    hint = "You can use slicing with a negative step: `[::-1]`."
    return q, s, hint, 2

def py_inter_is_even():
    q = "Write a function called `is_even(n)` that returns `True` if `n` is even, and `False` otherwise. Then write a line of code that calls the function with the number 42 and prints the result."
    s = r"""<pre><code>def is_even(n):
    return n % 2 == 0

print(is_even(42))</code></pre>"""
    hint = "Use `%` (modulo) to check for a remainder after division by 2."
    return q, s, hint, 3

def py_inter_sum_list():
    q = "A list `numbers = [5, 12, 9, 22, 7]` is given. Write code that calculates and prints the **sum** of all the numbers **without** using the built‑in `sum()` function."
    s = r"""<pre><code>numbers = [5, 12, 9, 22, 7]
total = 0
for n in numbers:
    total = total + n
print(total)</code></pre>"""
    hint = "Use a `for` loop and a running total variable."
    return q, s, hint, 3

def py_inter_password():
    q = "Write a `while` loop that keeps asking the user to enter a password. It should stop and print **Access granted.** only when the password is `secure`."
    s = r"""<pre><code>password = ''
while password != 'secure':
    password = input('Enter password: ')
print('Access granted.')</code></pre>"""
    hint = "Use `!=` to keep looping while the passwords are different."
    return q, s, hint, 3

def py_inter_fizzbuzz():
    q = "Write a program that prints the numbers **1 to 30**. For multiples of 3 print **Fizz** instead of the number, for multiples of 5 print **Buzz**, and for multiples of both 3 and 5 print **FizzBuzz**."
    s = r"""<pre><code>for i in range(1, 31):
    if i % 3 == 0 and i % 5 == 0:
        print('FizzBuzz')
    elif i % 3 == 0:
        print('Fizz')
    elif i % 5 == 0:
        print('Buzz')
    else:
        print(i)</code></pre>"""
    hint = "Check for FizzBuzz *first* (both divisible), then Fizz, then Buzz, otherwise print the number."
    return q, s, hint, 3

def py_inter_min_max():
    q = "Write a function `find_min_max(numbers)` that takes a list of integers and returns a **tuple** `(minimum, maximum)` **without** using the built-in `min()` or `max()` functions. Test it on `[4, 2, 9, 1, 7]` and print the result."
    s = r"""<pre><code>def find_min_max(numbers):
    minimum = numbers[0]
    maximum = numbers[0]
    for n in numbers:
        if n < minimum:
            minimum = n
        if n > maximum:
            maximum = n
    return (minimum, maximum)

print(find_min_max([4, 2, 9, 1, 7]))</code></pre>"""
    hint = "Start both `minimum` and `maximum` as the first element, then update them as you loop."
    return q, s, hint, 3

def py_inter_palindrome():
    q = "Write a function `is_palindrome(word)` that returns `True` if the word reads the same forwards and backwards (ignoring case), and `False` otherwise. Test it with `'Racecar'` and `'Python'` and print both results."
    s = r"""<pre><code>def is_palindrome(word):
    word = word.lower()
    return word == word[::-1]

print(is_palindrome('Racecar'))
print(is_palindrome('Python'))</code></pre>"""
    hint = "Convert to lowercase first, then compare the word with its reverse using `[::-1]`."
    return q, s, hint, 3

def py_inter_letter_count():
    q = "Write Python code that asks the user for a word, then prints a **dictionary** showing how many times each letter appears (case-insensitive). For example, `'hello'` → `{'h': 1, 'e': 1, 'l': 2, 'o': 1}`."
    s = r"""<pre><code>word = input('Enter a word: ').lower()
counts = {}
for char in word:
    if char in counts:
        counts[char] = counts[char] + 1
    else:
        counts[char] = 1
print(counts)</code></pre>"""
    hint = "Use a dictionary. For each character, if it is already a key, add 1; otherwise set it to 1."
    return q, s, hint, 3

def py_inter_list_comp():
    q = "Use a **list comprehension** to create a list of the **squares** of all even numbers from 1 to 20 (inclusive). Print the resulting list."
    s = r"""<pre><code>squares = [n ** 2 for n in range(1, 21) if n % 2 == 0]
print(squares)</code></pre>"""
    hint = "A list comprehension has the form `[expression for variable in range if condition]`."
    return q, s, hint, 3

def py_inter_grade():
    q = "Write a function `get_grade(score)` that takes an integer score (0–100) and returns the grade letter: **A** (90+), **B** (80–89), **C** (70–79), **D** (60–69), **F** (below 60). Test it by printing the grade for 85."
    s = r"""<pre><code>def get_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

print(get_grade(85))</code></pre>"""
    hint = "Use a chain of `if`/`elif`/`else`. Check the highest grade first."
    return q, s, hint, 3

def py_inter_times_table():
    q = "Write Python code that uses **nested loops** to print a times table from **1 to 5**. Each row should show the products for that number, separated by tabs (`\\t`). Example first row: `1\t2\t3\t4\t5`."
    s = r"""<pre><code>for i in range(1, 6):
    row = ''
    for j in range(1, 6):
        row = row + str(i * j) + '\t'
    print(row)</code></pre>"""
    hint = "Outer loop picks the row number, inner loop picks the column. Multiply `i * j`."
    return q, s, hint, 3

def py_inter_unique():
    q = "Write a function `unique_items(lst)` that returns a **new list** containing only the unique elements from `lst`, preserving their original order, **without** using `set()`. Test it on `[3, 1, 4, 1, 5, 9, 2, 6, 5, 3]` and print the result."
    s = r"""<pre><code>def unique_items(lst):
    seen = []
    for item in lst:
        if item not in seen:
            seen.append(item)
    return seen

print(unique_items([3, 1, 4, 1, 5, 9, 2, 6, 5, 3]))</code></pre>"""
    hint = "Keep a `seen` list. Only add an item if it isn't already in `seen`."
    return q, s, hint, 3

def py_inter_replace_words():
    q = "Write Python code that asks the user for a sentence and then for a word to replace. Replace every occurrence of that word with `***` (case-sensitive) and print the result."
    s = r"""<pre><code>sentence = input('Enter a sentence: ')
word = input('Word to replace: ')
result = sentence.replace(word, '***')
print(result)</code></pre>"""
    hint = "Strings have a built-in `.replace(old, new)` method that replaces all occurrences."
    return q, s, hint, 2

def py_inter_number_stats():
    q = "Write Python code that asks the user to enter **5 numbers**, stores them in a list, then prints the **mean**, **minimum**, and **maximum** (you may use `sum()`, `min()`, and `max()` here)."
    s = r"""<pre><code>numbers = []
for i in range(5):
    n = float(input(f'Enter number {i + 1}: '))
    numbers.append(n)

print('Mean:', sum(numbers) / 5)
print('Min:', min(numbers))
print('Max:', max(numbers))</code></pre>"""
    hint = "Use a `for` loop with `range(5)` to collect input, then calculate using built-in functions."
    return q, s, hint, 3

# ---------- DIFFICULT (4) ----------
def py_diff_largest():
    q = r"""Write a Python program that repeatedly asks the user to enter a number. The user can type `done` to finish. After they enter `done`, the program should print the **largest** number that was entered.
(Assume all numbers are integers.)"""
    s = r"""<pre><code>largest = None
while True:
    value = input('Enter a number or done: ')
    if value == 'done':
        break
    num = int(value)
    if largest is None or num > largest:
        largest = num
print('Largest:', largest)</code></pre>"""
    hint = "Use a `while` loop and a variable to keep track of the maximum."
    return q, s, hint, 4

def py_diff_vowels():
    q = r"""Write a function called `count_vowels(word)` that returns the number of vowels (a, e, i, o, u) in the given string. The function should work for both uppercase and lowercase letters.
Test it with the word `Education` and print the result."""
    s = r"""<pre><code>def count_vowels(word):
    vowels = 'aeiou'
    count = 0
    for char in word.lower():
        if char in vowels:
            count = count + 1
    return count

print(count_vowels('Education'))</code></pre>"""
    hint = "Convert the word to lowercase and check each character against `'aeiou'`."
    return q, s, hint, 5

def py_diff_2d():
    q = "Write a program that creates a 3×3 multiplication table (numbers 1 to 3) stored as a 2D list, and then prints each row on a separate line. The output should look like:\n`[1, 2, 3]`\n`[2, 4, 6]`\n`[3, 6, 9]`"
    s = r"""<pre><code>table = []
for i in range(1, 4):
    row = []
    for j in range(1, 4):
        row.append(i * j)
    table.append(row)

for row in table:
    print(row)</code></pre>"""
    hint = "Use nested `for` loops to fill a list of lists, then loop again to print each inner list."
    return q, s, hint, 5

def py_diff_file():
    q = r"""Write a program that asks the user for a filename, then opens the file and prints its contents with line numbers (starting from 1). If the file does not exist, print **File not found.**
Example output:
`1: first line`
`2: second line`"""
    s = r"""<pre><code>filename = input('Enter filename: ')
try:
    with open(filename) as f:
        for i, line in enumerate(f, 1):
            print(f'{i}: {line}', end='')
except FileNotFoundError:
    print('File not found.')</code></pre>"""
    hint = "Use `try`/`except FileNotFoundError` and `enumerate()` with `start=1`."
    return q, s, hint, 6

def py_diff_fibonacci():
    q = "Write a function `fibonacci(n)` that returns a **list** of Fibonacci numbers up to (but not exceeding) `n`. For example, `fibonacci(50)` should return `[1, 1, 2, 3, 5, 8, 13, 21, 34]`. Test it with `n = 100` and print the result."
    s = r"""<pre><code>def fibonacci(n):
    sequence = []
    a, b = 1, 1
    while a <= n:
        sequence.append(a)
        a, b = b, a + b
    return sequence

print(fibonacci(100))</code></pre>"""
    hint = "Use two variables `a` and `b`. Each step: append `a`, then update `a, b = b, a + b`."
    return q, s, hint, 5

def py_diff_caesar():
    q = r"""Write a function `caesar(text, shift)` that applies a Caesar cipher to `text`: each **letter** is shifted forward by `shift` positions in the alphabet, wrapping around (Z → A). Non-letter characters are unchanged. Test it with `caesar('Hello, World!', 3)` and print the result."""
    s = r"""<pre><code>def caesar(text, shift):
    result = ''
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

print(caesar('Hello, World!', 3))</code></pre>"""
    hint = "Use `ord()` to get the character code, shift it, use `% 26` to wrap, then `chr()` to convert back."
    return q, s, hint, 6

def py_diff_word_freq():
    q = r"""Write a program that repeatedly asks the user to enter a line of text. Stop when they enter `STOP`. Then print the **three most common words** (case-insensitive) and how many times each appeared."""
    s = r"""<pre><code>from collections import Counter

words = []
while True:
    line = input('Enter text (or STOP): ')
    if line == 'STOP':
        break
    words.extend(line.lower().split())

counter = Counter(words)
for word, count in counter.most_common(3):
    print(word, count)</code></pre>"""
    hint = "Use `collections.Counter` and its `.most_common(3)` method, or sort a dict by value."
    return q, s, hint, 5

def py_diff_stack():
    q = r"""Write a class `Stack` that uses a list internally and supports three methods:
- `push(item)` – adds `item` to the top.
- `pop()` – removes and returns the top item (print `'Stack is empty'` if empty).
- `is_empty()` – returns `True` if the stack has no items.
Demonstrate it by pushing 3 values, then popping twice and printing each popped value."""
    s = r"""<pre><code>class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            print('Stack is empty')
            return None
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

s = Stack()
s.push(10)
s.push(20)
s.push(30)
print(s.pop())
print(s.pop())</code></pre>"""
    hint = "A stack is LIFO (last in, first out). Use a list with `.append()` for push and `.pop()` for pop."
    return q, s, hint, 6

def py_diff_binary():
    q = r"""Write a function `to_binary(n)` that converts a **positive integer** `n` to its binary representation as a **string**, **without** using `bin()` or any built-in base-conversion function. Test it with `n = 42` (expected: `'101010'`) and print the result."""
    s = r"""<pre><code>def to_binary(n):
    if n == 0:
        return '0'
    bits = ''
    while n > 0:
        bits = str(n % 2) + bits
        n = n // 2
    return bits

print(to_binary(42))</code></pre>"""
    hint = "Repeatedly divide by 2 and collect the remainders in reverse order."
    return q, s, hint, 5

def py_diff_prime_sieve():
    """Prime-finder using a Boolean sieve — method is explained in the question (no jargon)."""
    limit = random.choice([30, 40, 50])
    q = (
        rf"Write a program that finds **all prime numbers from 2 to {limit}** and prints them as a list.<br><br>"
        rf"Use a <strong>sieve</strong> (an efficient table method):<br>"
        rf"1. Create a list of <code>{limit + 1}</code> Boolean values; index <code>i</code> stores whether <code>i</code> is prime. Start with all <code>True</code>.<br>"
        rf"2. Set index <code>0</code> and <code>1</code> to <code>False</code> (they are not prime).<br>"
        rf"3. For each <code>i</code> from <code>2</code> up to the square root of <code>{limit}</code>, if <code>i</code> is still marked prime, "
        rf"mark every multiple of <code>i</code> (starting at <code>i × i</code>) as <code>False</code>.<br>"
        rf"4. Collect every index still <code>True</code> and print that list.<br><br>"
        rf"(Do <strong>not</strong> use a separate trial-division check on every number.)"
    )
    s = rf"""<pre><code>limit = {limit}
is_prime = [True] * (limit + 1)
is_prime[0] = False
is_prime[1] = False

for i in range(2, int(limit ** 0.5) + 1):
    if is_prime[i]:
        for j in range(i * i, limit + 1, i):
            is_prime[j] = False

primes = [i for i in range(limit + 1) if is_prime[i]]
print(primes)</code></pre>"""
    hint = (
        "You do not need to have heard of Eratosthenes — follow the steps: "
        "Boolean list, cross out multiples of each prime starting at i²."
    )
    return q, s, hint, 5

def py_diff_anagram():
    q = r"""Write a function `is_anagram(word1, word2)` that returns `True` if the two words are anagrams of each other (contain the same letters, case-insensitive), and `False` otherwise. **Do not** use `sorted()`. Test with `('listen', 'silent')` and `('hello', 'world')` and print both results."""
    s = r"""<pre><code>def is_anagram(word1, word2):
    word1 = word1.lower()
    word2 = word2.lower()
    if len(word1) != len(word2):
        return False
    counts = {}
    for ch in word1:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in word2:
        counts[ch] = counts.get(ch, 0) - 1
    return all(v == 0 for v in counts.values())

print(is_anagram('listen', 'silent'))
print(is_anagram('hello', 'world'))</code></pre>"""
    hint = "Count occurrences of each letter in word1, then subtract for word2. If all counts end at 0, they're anagrams."
    return q, s, hint, 5

def py_diff_roman():
    q = r"""Write a function `to_roman(n)` that converts an integer between **1 and 39** into its Roman numeral string. Test it with 14, 27, and 39, printing each result.
(Values to use: I=1, V=5, X=10, XX=20, XXX=30)"""
    s = r"""<pre><code>def to_roman(n):
    values = [30, 29, 28, 27, 26, 25, 24, 23, 22, 21,
              20, 19, 18, 17, 16, 15, 14, 13, 12, 11,
              10,  9,  8,  7,  6,  5,  4,  3,  2,  1]
    numerals = {30:'XXX',29:'XXIX',28:'XXVIII',27:'XXVII',26:'XXVI',
                25:'XXV',24:'XXIV',23:'XXIII',22:'XXII',21:'XXI',
                20:'XX',19:'XIX',18:'XVIII',17:'XVII',16:'XVI',
                15:'XV',14:'XIV',13:'XIII',12:'XII',11:'XI',
                10:'X',9:'IX',8:'VIII',7:'VII',6:'VI',
                5:'V',4:'IV',3:'III',2:'II',1:'I'}
    result = ''
    while n > 0:
        for v in values:
            if n >= v:
                result += numerals[v]
                n -= v
                break
    return result

for num in [14, 27, 39]:
    print(num, '->', to_roman(num))</code></pre>"""
    hint = "Use a greedy approach: always subtract the largest Roman value that fits, and add its symbol."
    return q, s, hint, 5

def py_diff_exception_handling():
    q = r"""Write a program that repeatedly asks the user to enter two numbers and prints the result of dividing the first by the second. Handle two exceptions:
- `ValueError` – if the input is not a valid number (print **Invalid input**).
- `ZeroDivisionError` – if the second number is 0 (print **Cannot divide by zero**).
The loop should stop when the user enters `q` for either number."""
    s = r"""<pre><code>while True:
    a = input('Enter first number (or q to quit): ')
    if a == 'q':
        break
    b = input('Enter second number (or q to quit): ')
    if b == 'q':
        break
    try:
        result = float(a) / float(b)
        print('Result:', result)
    except ValueError:
        print('Invalid input')
    except ZeroDivisionError:
        print('Cannot divide by zero')</code></pre>"""
    hint = "Use `try`/`except` with multiple `except` clauses to catch different error types."
    return q, s, hint, 5

def py_diff_search():
    q = r"""Write a function `binary_search(lst, target)` that performs a **binary search** on a sorted list and returns the **index** of `target`, or `-1` if it is not found. Test it on `[2, 5, 8, 12, 16, 23, 38, 56, 72, 91]` searching for `23` and for `15`."""
    s = r"""<pre><code>def binary_search(lst, target):
    low, high = 0, len(lst) - 1
    while low <= high:
        mid = (low + high) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search(data, 23))
print(binary_search(data, 15))</code></pre>"""
    hint = "Keep `low` and `high` pointers. Compare the middle element with the target and halve the search space each time."
    return q, s, hint, 6


def py_diff_menu_dict():
    q = (
        r"Write a program that stores a **menu** in a dictionary mapping option numbers "
        r"(as strings `'1'`, `'2'`, `'3'`) to meal names. Repeatedly ask the user to "
        r"enter a choice or `q` to quit. Print the meal name if the key exists, otherwise "
        r"print **Invalid choice**."
    )
    s = r"""<pre><code>menu = {'1': 'Pizza', '2': 'Pasta', '3': 'Salad'}

while True:
    choice = input('Choose 1-3 or q to quit: ')
    if choice == 'q':
        break
    if choice in menu:
        print(menu[choice])
    else:
        print('Invalid choice')</code></pre>"""
    hint = "Use `in` to check dictionary keys before printing the value."
    return q, s, hint, 5


def py_diff_read_scores_file():
    q = (
        r"Write a program that reads a text file called `scores.txt` where each line is "
        r"one integer score. Print the **highest** score and the **average** score "
        r"(rounded to 1 decimal place). Assume the file has at least one line."
    )
    s = r"""<pre><code>scores = []
with open('scores.txt', 'r') as f:
    for line in f:
        scores.append(int(line.strip()))

print('Highest:', max(scores))
print('Average:', round(sum(scores) / len(scores), 1))</code></pre>"""
    hint = "Read each line inside a `with open(...)` block, convert to `int`, then use `max()` and `sum()`."
    return q, s, hint, 5

# ---------- Multi-part difficult questions (a, b, c) ----------
def py_diff_multipart_scores():
    q = (
        r"A teacher stores test scores in a list. Write a program in **three parts**.<br><br>"
        r"**a)** Write a function `average(scores)` that returns the mean (average) of a "
        r"list of numbers. **Do not** use a built-in average function. [3]<br>"
        r"**b)** Write a function `highest(scores)` that returns the largest score "
        r"**without** using `max()`. [3]<br>"
        r"**c)** Using both functions, print the average and the highest score for "
        r"`scores = [55, 72, 90, 43, 68]`. [2]"
    )
    s = r"""<pre><code>def average(scores):
    total = 0
    for score in scores:
        total = total + score
    return total / len(scores)

def highest(scores):
    biggest = scores[0]
    for score in scores:
        if score > biggest:
            biggest = score
    return biggest

scores = [55, 72, 90, 43, 68]
print('Average:', average(scores))
print('Highest:', highest(scores))</code></pre>
<strong>Output:</strong><br>
<code>Average: 65.6</code><br>
<code>Highest: 90</code>"""
    hint = (
        "For (a) add the numbers with a loop then divide by `len(scores)`. "
        "For (b) keep a variable for the biggest value seen so far and update it in a loop."
    )
    return q, s, hint, 8

def py_diff_multipart_password():
    q = (
        r"A website checks the strength of passwords. Write a program in **three parts**.<br><br>"
        r"**a)** Write a function `count_digits(text)` that returns how many digits (0-9) "
        r"are in `text`. [3]<br>"
        r"**b)** Write a function `is_strong(password)` that returns `True` only if the "
        r"password is **at least 8 characters long** and contains **at least one digit** "
        r"(use your function from part a). [3]<br>"
        r"**c)** Test `is_strong` with `'password1'` and `'short'` and print each result. [2]"
    )
    s = r"""<pre><code>def count_digits(text):
    count = 0
    for char in text:
        if char.isdigit():
            count = count + 1
    return count

def is_strong(password):
    if len(password) >= 8 and count_digits(password) >= 1:
        return True
    else:
        return False

print(is_strong('password1'))
print(is_strong('short'))</code></pre>
<strong>Output:</strong><br>
<code>True</code><br>
<code>False</code>"""
    hint = (
        "For (a) loop through each character and use `.isdigit()`. "
        "For (b) combine the length check and the digit count with `and`."
    )
    return q, s, hint, 8

# ---------- MCQ (27 questions) ----------
def py_mcq():
    import random
    questions = [
        {
            "q": "What will `print(2 + 3)` output?",
            "opts": ["A  5", "B  23", "C  2 + 3", "D  6"],
            "ans": "A",
            "hint": "The `+` operator adds numbers."
        },
        {
            "q": "Which of these is a valid variable name in Python?",
            "opts": ["A  2things", "B  my‑name", "C  my_name", "D  class"],
            "ans": "C",
            "hint": "Variable names can contain underscores, but not start with a number or contain hyphens."
        },
        {
            "q": "What type is the value `3.14`?",
            "opts": ["A  int", "B  float", "C  str", "D  bool"],
            "ans": "B",
            "hint": "Numbers with a decimal point are floats."
        },
        {
            "q": "How do you get user input in Python?",
            "opts": ["A  get()", "B  input()", "C  read()", "D  ask()"],
            "ans": "B",
            "hint": "The built‑in function for reading a line of text from the user is `input()`."
        },
        {
            "q": "What does `input()` always return?",
            "opts": ["A  an integer", "B  a string", "C  a float", "D  a boolean"],
            "ans": "B",
            "hint": "Whatever the user types comes back as a string."
        },
        {
            "q": "Which operator checks if two values are equal?",
            "opts": ["A  =", "B  ==", "C  !=", "D  eq"],
            "ans": "B",
            "hint": "Double equals `==` compares values; single `=` assigns."
        },
        {
            "q": "What is the result of `10 // 3`?",
            "opts": ["A  3.333...", "B  1", "C  3", "D  4"],
            "ans": "C",
            "hint": "`//` performs integer (floor) division, discarding the remainder."
        },
        {
            "q": "What will `if 5 > 3:` do?",
            "opts": ["A  cause an error", "B  run the indented code", "C  skip the indented code", "D  print 'True'"],
            "ans": "B",
            "hint": "The condition `5 > 3` is `True`, so the indented block runs."
        },
        {
            "q": "What is the purpose of `else` in an `if` statement?",
            "opts": ["A  to add another condition", "B  to handle the case when the condition is False", "C  to repeat the code", "D  to end the program"],
            "ans": "B",
            "hint": "`else` catches everything the `if` (and `elif`) didn't match."
        },
        {
            "q": "How many times will `for i in range(5):` loop?",
            "opts": ["A  4", "B  5", "C  6", "D  0"],
            "ans": "B",
            "hint": "`range(5)` gives 0,1,2,3,4 – five numbers."
        },
        {
            "q": "What will `while count < 3:` do if `count` never changes?",
            "opts": ["A  loop forever", "B  loop three times", "C  cause an error immediately", "D  not loop at all"],
            "ans": "A",
            "hint": "If the condition never becomes `False`, you get an infinite loop."
        },
        {
            "q": "Which method removes whitespace from the beginning and end of a string?",
            "opts": ["A  .trim()", "B  .strip()", "C  .remove()", "D  .clean()"],
            "ans": "B",
            "hint": "`.strip()` removes leading and trailing spaces (and other whitespace)."
        },
        {
            "q": "How do you get the length of a list `my_list`?",
            "opts": ["A  my_list.length()", "B  len(my_list)", "C  length(my_list)", "D  count(my_list)"],
            "ans": "B",
            "hint": "The built‑in `len()` function works on lists, strings, and many other collections."
        },
        {
            "q": "If `fruits = ['apple','banana']`, what does `fruits[0]` give?",
            "opts": ["A  'banana'", "B  'apple'", "C  'apple','banana'", "D  an error"],
            "ans": "B",
            "hint": "Indexes start at 0, so `[0]` is the first item."
        },
        {
            "q": "Which statement correctly defines a function?",
            "opts": ["A  function my_func():", "B  def my_func():", "C  define my_func():", "D  func my_func():"],
            "ans": "B",
            "hint": "The `def` keyword is used to define functions."
        },
        {
            "q": "What does `return` do in a function?",
            "opts": ["A  prints a value", "B  exits the program", "C  sends a value back to the caller", "D  starts the function again"],
            "ans": "C",
            "hint": "`return` gives a result back to the code that called the function."
        },
        {
            "q": "Which of these opens a file for writing?",
            "opts": ["A  open('f.txt','r')", "B  open('f.txt','w')", "C  open('f.txt','a')", "D  open('f.txt','x')"],
            "ans": "B",
            "hint": "`'w'` mode writes (and overwrites) the file."
        },
        {
            "q": "What is a variable declared inside a function called?",
            "opts": ["A  global variable", "B  local variable", "C  constant variable", "D  external variable"],
            "ans": "B",
            "hint": "Variables created inside functions are local to that function."
        },
        {
            "q": "What will `print(2 == '2')` output?",
            "opts": ["A  True", "B  False", "C  2", "D  an error"],
            "ans": "B",
            "hint": "An integer and a string are never equal, even if they look similar."
        },
        {
            "q": "Which keyword skips the rest of the current iteration in a loop?",
            "opts": ["A  break", "B  skip", "C  continue", "D  pass"],
            "ans": "C",
            "hint": "`continue` jumps back to the top of the loop without finishing the current iteration."
        },
        {
            "q": "What is the output of `len([10, 20, 30, 40])`?",
            "opts": ["A  3", "B  4", "C  40", "D  10"],
            "ans": "B",
            "hint": "`len()` counts the number of items in the list. There are 4 elements."
        },
        {
            "q": "Which data structure stores data as **key-value pairs**?",
            "opts": ["A  list", "B  tuple", "C  dictionary", "D  set"],
            "ans": "C",
            "hint": "Dictionaries (`{}`) map keys to values, e.g. `{'name': 'Alice', 'age': 16}`."
        },
        {
            "q": "What does `range(2, 10, 2)` produce?",
            "opts": ["A  [2, 4, 6, 8, 10]", "B  [2, 4, 6, 8]", "C  [0, 2, 4, 6, 8]", "D  [2, 3, 4, 5, 6, 7, 8, 9]"],
            "ans": "B",
            "hint": "`range(start, stop, step)` goes from 2, stepping by 2, stopping before 10: 2, 4, 6, 8."
        },
        {
            "q": "What is the result of `'hello'[1:4]`?",
            "opts": ["A  'hel'", "B  'ell'", "C  'ello'", "D  'hell'"],
            "ans": "B",
            "hint": "Slicing `[1:4]` takes characters at indices 1, 2, 3 (not 4): 'e', 'l', 'l' → 'ell'."
        },
        {
            "q": "Which exception is raised when you divide by zero in Python?",
            "opts": ["A  ValueError", "B  TypeError", "C  ZeroDivisionError", "D  ArithmeticError"],
            "ans": "C",
            "hint": "Python raises `ZeroDivisionError` specifically when the divisor is 0."
        },
        {
            "q": "What does `my_list.append([4, 5])` do?",
            "opts": ["A  Adds 4 and 5 as separate items", "B  Adds the list [4, 5] as one item",
                     "C  Removes items 4 and 5", "D  Sorts the list"],
            "ans": "B",
            "hint": "`append` adds its argument as a **single** element."
        },
        {
            "q": "What is the result of `[10, 20, 30, 40][1:3]`?",
            "opts": ["A  [10, 20]", "B  [20, 30]", "C  [20, 30, 40]", "D  [30, 40]"],
            "ans": "B",
            "hint": "Slice `[1:3]` takes indices 1 and 2 only."
        },
        {
            "q": "What will `print(type(True))` output?",
            "opts": ["A  <class 'str'>", "B  <class 'bool'>", "C  <class 'int'>", "D  True"],
            "ans": "B",
            "hint": "`True` and `False` are boolean values."
        },
        {
            "q": "Which statement correctly converts the string `'42'` to an integer?",
            "opts": ["A  integer('42')", "B  int('42')", "C  str(42)", "D  float('42')"],
            "ans": "B",
            "hint": "Use `int()` to convert a numeric string to an integer."
        },
        {
            "q": "What does `elif` do in Python?",
            "opts": ["A  Ends the program", "B  Checks another condition if previous ones were False",
                     "C  Repeats code forever", "D  Defines a function"],
            "ans": "B",
            "hint": "`elif` is short for ‘else if’ — another branch in a selection structure."
        },
        {
            "q": "What is the output of `print('Hi' * 3)`?",
            "opts": ["A  Hi3", "B  HiHiHi", "C  Hi Hi Hi", "D  an error"],
            "ans": "B",
            "hint": "Multiplying a string by an integer repeats the string."
        },
        {
            "q": "Which operator gives the remainder after division?",
            "opts": ["A  /", "B  //", "C  %", "D  **"],
            "ans": "C",
            "hint": "The modulo operator `%` returns the remainder."
        },
    ]
    chosen = random.choice(questions)
    return (
        chosen["q"],
        f"Answer: {chosen['ans']}\n\n{chosen['hint']}",
        chosen["hint"],
        1,
        chosen["opts"],
        chosen["ans"]
    )

# ---------- VARIANTS FUNCTION ----------
def gcse_python_variants(difficulty, mode):
    if mode == 'mcq':
        return [py_mcq] * 10

    found_pool = [
        py_found_hello, py_found_age, py_found_pass, py_found_for,
        py_found_variables, py_found_string_concat, py_found_area,
        py_found_countdown, py_found_elif, py_found_list_build,
        py_found_index, py_found_round, py_found_modulo, py_found_upper_count,
    ]
    inter_pool = [
        py_inter_reverse, py_inter_is_even, py_inter_sum_list, py_inter_password,
        py_inter_fizzbuzz, py_inter_min_max, py_inter_palindrome, py_inter_letter_count,
        py_inter_list_comp, py_inter_grade, py_inter_times_table, py_inter_unique,
        py_inter_replace_words, py_inter_number_stats,
    ]
    diff_pool = [
        py_diff_largest, py_diff_vowels, py_diff_2d, py_diff_file,
        py_diff_fibonacci, py_diff_caesar, py_diff_word_freq, py_diff_stack,
        py_diff_binary, py_diff_prime_sieve, py_diff_anagram, py_diff_roman,
        py_diff_exception_handling, py_diff_search, py_diff_menu_dict,
        py_diff_read_scores_file, py_diff_multipart_scores, py_diff_multipart_password,
    ]

    if difficulty == 'foundational':
        pool = found_pool
    elif difficulty == 'intermediate':
        pool = inter_pool
    elif difficulty == 'difficult':
        pool = diff_pool
    else:
        pool = found_pool + inter_pool + diff_pool

    return random.sample(pool, min(len(pool), 10))

# ---------- MAIN GENERATOR ----------
def gcse_python_programming(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = py_mcq()
        return make_problem(
            format_cs_prose(q_mcq),
            format_cs_prose(s_mcq),
            format_cs_prose(hint_mcq),
            difficulty, marks_mcq,
            'gcse', 'cs', 'python_programming',
            options=[format_cs_mcq_option(opt) for opt in opts_mcq],
            correct_answer=correct_mcq,
        )

    variants = gcse_python_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    q, s, hint, marks = variant()
    return make_problem(
        format_cs_prose(q),
        s,
        format_cs_prose(hint),
        difficulty, marks,
        'gcse', 'cs', 'python_programming',
    )