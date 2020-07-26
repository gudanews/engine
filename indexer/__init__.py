class Processor:
    def test(self):
        pass

    def process(self):
        raise NotImplementedError("Subclass needs to implemente this method.")

def main():
    import os
    from util import find_modules, find_public_classes
    from indexer import Processor
    modules = find_modules(os.path.dirname(__file__))
    for module in modules:
        classes = find_public_classes(module)
        for _,cls in classes.items():
            if issubclass(cls, Processor) and not issubclass(Processor, cls):
                obj = cls()
                obj.process()

    
if __name__ == "__main__":
    main()
