import copy
import math
from itertools import accumulate

from .collection import ImgCollection


class OpBase:
    op_id = 0

    def __init__(self, *args, **kwargs):
        self.op_name = str(self.__class__.op_id) + "_" + self.__class__.__name__
        OpBase.op_id += 1

        self.op_ex = None
        self.op_func = self.process
        self.op_params = (args, kwargs)

        self.process_all = False

        self.initialized()

    def __call__(self, ex):
        raise NotImplementedError

    def initialized(self):
        pass

    def execute(self):
        raise NotImplementedError

    def run(self):
        for _ in self.execute():
            pass

    def process(self, *args, **kwargs):
        raise NotImplementedError

    def op_ex_check(self):
        if not self.op_ex:
            raise AttributeError(f"op_ex is not defined for {self.op_name}")

    def op_func_check(self):
        if not self.op_func:
            raise AttributeError(f"op_func is not defined for {self.op_name}")

    def op_params_check(self):
        if not self.op_params:
            raise AttributeError(f"op_params is not defined for {self.op_name}")

    def data_collection_check(self, data):
        if not isinstance(data, ImgCollection):
            raise TypeError(f"{self.op_name} expects the input type ImgCollection, but got {type(data)} from {self.op_ex.op_name}")


def op_execution_profile(execute):
    def wrapper(self):
        ret = execute(self)
        print(f"executing operation {self.op_name}")
        return ret
    return wrapper


class OpInput(OpBase):
    def __call__(self, ex):
        raise TypeError(f"OpInput does not accept any inputs")

    @op_execution_profile
    def execute(self):
        self.op_func_check()

        for new_imgelem in self.op_func(*self.op_params[0], **self.op_params[1]):
            yield new_imgelem

        #return self.op_func(*self.op_params[0], **self.op_params[1])


class OpOneToOne(OpBase):
    def __call__(self, ex):
        self.op_ex = ex
        return self

    @op_execution_profile
    def execute(self):
        self.op_ex_check()
        self.op_func_check()

        collection = self.op_ex.execute()
        #self.data_collection_check(collection)

        if self.process_all:
            collection = self.op_ex.execute()
            new_collection = self.op_func(collection, *self.op_params[0], **self.op_params[1])
            for imgelem in new_collection:
                yield imgelem
        else:
            # TODO: can be paralleled here
            for imgelem in collection:
                for new_imgelem in self.op_func(imgelem, *self.op_params[0], **self.op_params[1]):
                    yield new_imgelem


class OpDispatch(OpBase):
    def __init__(self, percents):
        super(OpDispatch, self).__init__(percents)
        counts = [int(p * 100.0) for p in percents]
        assert sum(counts) == 100, "the percents must sum up to 1.0"

        gcd = self.gcd_many(counts)
        counts = [c // gcd for c in counts]
        self.cumsum = dict.fromkeys(accumulate(counts), 1)
        self.total = sum(counts)

    def gcd_many(self, s):
        g = s[0]
        for x in s[1:]:
            g = math.gcd(g, x)
        return g

    def __call__(self, ex):
        self.op_ex = ex
        return self

    @op_execution_profile
    def execute(self):
        self.op_ex_check()

        collection = self.op_ex.execute()

        for i, imgelem in enumerate(collection):
            if (i % self.total in self.cumsum) or (i == self.total):
                raise StopIteration
            yield imgelem
