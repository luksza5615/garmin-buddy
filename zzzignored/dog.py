# from zzzignored.animal import Animal

class Animal():
    def bark(self):
        print("Animal bark")


class Dog(Animal):
    def __init__(self, name: str = None, breed=None):
        self.name = name
        self.breed = breed

    def bark(self):
        print("Dog bark")

    def test():
        print("do nothing")


class Cat(Animal):
    def bark(self):
        print("I cannot bark")


dog = Dog()
dog.bark()

dog1 = Dog(2, "Golden")
print(dog1.name, dog1.breed)
