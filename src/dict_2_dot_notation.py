import threading
import traceback
from enum import Enum

STATUS = Enum('STATUS', 'ValidationOK ValidationFail DervationOK DerivationFail')
LOCAL_TRHEAD_OBJ = threading.local()
LOCAL_TRHEAD_OBJ.logs = []
PRIMITIVE = (int, str, bool, float, )


def isprimitive(var):
    return isinstance(var, PRIMITIVE)


class traceit(object):  # orig not from object

    def __init__(self, store , pointer, enable=True):
        self.tracelist = store
        self.pointer = pointer.__name__
        self.enable = enable

    def __call__(self, obj):
        def wrap(*args, **kwargs):
            def get_current_rule_trace_object(rule_name):
                try:
                    return next(it for it in self.tracelist if rule_name in it)
                except StopIteration:
                    pass

            def update_trace_obj(rule_name, trace_obj, info):
                trace_obj[rule_name].append(info)

            def get_rule_name(stack):
                try:
                    rule_name = next(
                        iter(
                            [frame.name for frame in stack][[frame.name for frame in stack].index(self.pointer)+1:]
                        )
                    )
                    if rule_name != "__init__":
                        return rule_name
                except StopIteration:
                    pass

            if self.enable:
                current_rule = get_rule_name(traceback.extract_stack())
                if current_rule:
                    trace_obj = get_current_rule_trace_object(current_rule)
                    if trace_obj:
                        update_trace_obj(
                            current_rule,
                            trace_obj,
                            {
                                "{}".format(args[1]
                                            if obj.__name__ == "__getitem__"
                                            else "{} = {}".format(args[1], args[2])): traceback.extract_stack()
                            }
                        )
            res = obj(*args, **kwargs)
            return res
        return wrap


class Context(object):

    def __init__(self, model, pointer):
        self.set = []
        self.get = []
        self.pointer = pointer
        self.enable = True

        class My(dict):

            def __init__(self, model):
                for k in model:
                    if isinstance(model[k], dict):
                        self[k] = My(model[k])
                    elif isprimitive(model[k]):
                        self[k] =  model[k]
                    elif isinstance(model[k], list):
                        self[k] = model[k]
                        self._traverse(model[k])

            def _traverse(self, lst):
                for k, it in enumerate(lst):
                    if isinstance(lst[k], dict):
                        lst[k] = My(lst[k])
                    elif isprimitive(lst[k]):
                        lst[k] = lst[k]
                    elif isinstance(lst[k], list):
                        self._traverse(lst[k])

            def __setattr__(self, key, value):
                self.__setitem__(key, value)

            def __getattr__(self, key):
                return self.__getitem__(key)

            @traceit(self.set, self.pointer, self.enable)
            def __setitem__(self, key, value):
                super(My, self).__setitem__(key, value)

            @traceit(self.get, self.pointer, self.enable)
            def __getitem__(self, key):
                return super(My, self).__getitem__(key)

        self.model = My(model)

    def get_log(self):
        return {
            "validation": self.get,
            "derivation": self.set
        }

    def fail(self, rule, msg):
        self.get.append({rule.__name__: STATUS.ValidationFail, "error": msg})

    def success(self, rule):
        self.get.append({rule.__name__: STATUS.ValidationOK})

    def initialize(self, rule):
        self.get.append({rule.__name__: []})
        self.set.append({rule.__name__: []})

    def get_path_key(self, k, d):
        path = "[{}]".format(k)
        if isinstance(d[k], dict):
            return self.get_path_key(d[k])
        else:
            return  path

    def get_path(self, path, d):
        for k in d:
            path = "{}[{}]".format(path, k)
            if isinstance(d[k], dict):
                return self.get_path(d[k])
            else:
                return path

    def to_dict(self, orig):
        for k in orig:
            if isinstance(orig[k], dict):
                orig[k] = dict(orig[k])
                self.to_dict(orig[k])

    def to_json(self, orig):
        self.enable = False
        orig.update(self.model)
        self.to_dict(orig)



def run_rule(rule, model):
    ctx = Context(model, run_rule)
    ctx.set.clear()
    ctx.get.clear()
    ctx.initialize(rule)
    rc = rule(ctx.model)
    if rc:
        ctx.fail(rule, rc)
    else:
        ctx.success(rule)
    LOCAL_TRHEAD_OBJ.logs.append(ctx.get_log())
    ctx.to_json(model)
    return LOCAL_TRHEAD_OBJ.logs


def error(expr, message):
    if expr:
        return message




