state = 'inactive'

def my_function():
    global state  # 声明使用全局变量
    print(state)
    state = 'active'

my_function()
print(state)  # 现在 state 是 'active'
