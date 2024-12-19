class Parent:
    name = "Parent"
    def __init__(self, mystring):
        self.mystring = mystring
        

class Child(Parent):
    def __init__(self, mystring):
        super().__init__(mystring)  # Σωστή κλήση
        self.name = "Child"
        print(self.name)
        print(super().name)  # Πρόσβαση στο name της υπερκλάσης

if __name__ == "__main__":
    Child("Kitsos")
