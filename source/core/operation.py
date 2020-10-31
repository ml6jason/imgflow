class ImgOperationBase:
    def __init__(self):
        self.op_ex = None
        self.op_func = None
        self.op_params = None

    def execute(self):
        raise NotImplementedError()


class ImgInputOp(ImgOperationBase):
    def __init__(self):
        super(ImgInputOp, self).__init__()

    def execute(self):
        if not (self.op_ex and self.op_func and self.op_params):
            raise ValueError("operation is not defined")
        return self.op_func(self.ex.execute(), **self.op_params)
    

class ImgTransformOp(ImgOperationBase):
    def __init__(self):
        super(ImgTransformOp, self).__init__()

    def execute(self):
        if not (self.op_func and self.op_params):
            raise ValueError("operation is not defined")
        return self.op_func(**self.op_params)
    