# Create an array of numbers 
# and print only the numbers that are even
import random
import string


def print_even_numbers(numbers):
    for number in numbers:
        if number % 2 == 0:
            print(number)

# 定义一个方法，传入一个数组，打印出数组中的偶数
def print_even_numbers(numbers):
    for number in numbers:
        if number % 2 == 0:
            print(number)


# 二分查找
def binary_search(numbers, target):
    left = 0
    right = len(numbers) - 1

    while left <= right:
        middle = (left + right) // 2

        if numbers[middle] == target:
            return middle
        elif numbers[middle] > target:
            right = middle - 1
        else:
            left = middle + 1

    return -1

# 生成swift的垃圾方法，并且可以在合适的位置调用
# 1. 可以定义变量 例如 var x = 10  var str: String = "1234"
# 2. 可以定义if语句, 在if的条件中可以使用变量，可以操作变量
# 3. 可以定义while语句, 在while的条件中可以使用变量，但是不能死循环
# 4. 可以定义for语句, 在for的条件中可以使用变量，循环的次数少点
# 生成垃圾方法
def generate_garbage_method():
    method_name = "".join(random.choices(string.ascii_lowercase, k=8))
    num_lines = random.randint(5, 10)
    lines = []
    variables = set()

    for _ in range(num_lines):
        line_type = random.choice(["code", "variable", "if", "while"])

        if line_type == "code":
            line = "".join(
                random.choices(
                    string.ascii_lowercase + string.ascii_uppercase + string.digits,
                    k=20,
                )
            )
        elif line_type == "variable":
            variable_name = "".join(random.choices(string.ascii_lowercase, k=5))
            variable_value = random.randint(1, 100)
            line = f"{variable_name} = {variable_value}"
            variables.add(variable_name)
        elif line_type == "if":
            condition_variable = random.choice(list(variables))
            line = f"if {condition_variable} > 50:"
        else:  # line_type == 'while'
            condition_variable = random.choice(list(variables))
            line = f"while {condition_variable} > 0:"

        lines.append(line)

    method_body = "\n".join(lines)

    garbage_method = f"""
    func {method_name}() {{
        {method_body}
    }}
    """

    return garbage_method










if __name__=='__main__':
    x = generate_garbage_method()
    pri
    

    