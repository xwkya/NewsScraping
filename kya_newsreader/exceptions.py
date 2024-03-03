class HTMLValidationException(Exception):
    def __init__(self, *args):
        super().__init__(args)
    
class HTMLDownloadException(Exception):
    def __init__(self, *args):
        super().__init__(args)