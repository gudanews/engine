from processor import Processor as BaseProcessor

class GoogleProcessor(BaseProcessor):

    def process(self):
        print("Hello google")