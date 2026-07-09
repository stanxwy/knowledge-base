from functools import cached_property

class Calculator:

    @cached_property
    def answer(self):
        print("Calculating answer...")
        return 101
    
if __name__ == "__main__":
    calc = Calculator()
    print(calc.answer)
    print(calc.answer)  # print 只会打印一次，之后直接从缓存中获取返回值