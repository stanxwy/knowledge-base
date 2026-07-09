class Person:
    species = "Homo sapiens"  # 类属性
    
    def __init__(self, name):
        self.name = name      # 实例属性

if __name__ == "__main__":
    p = Person("Alice")

    # 1. 查看存储位置
    print(p.__dict__)           # {'name': 'Alice'} → 实例属性
    print(Person.__dict__)      # 包含 'species' → 类属性

    # 2. 直接判断
    print('name' in p.__dict__)         # True → 实例属性
    print('name' in Person.__dict__)    # False

    print('species' in p.__dict__)      # False
    print('species' in Person.__dict__) # True → 类属性


    print(hasattr(Person, "name"))      # False
    print(hasattr(p, "name"))           # True

    print(hasattr(Person, "species"))   # True
    print(hasattr(p, "species"))        # True

    # print(getattr(Person, "name"))    # AttributeError: type object 'Person' has no attribute 'name'
    print(getattr(p, "name"))           # Alice

    print(getattr(Person, "species"))   # Homo sapiens
    print(getattr(p, "species"))        # Homo sapiens