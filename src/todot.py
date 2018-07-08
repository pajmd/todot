import copy


def traverse(model):
    model_obj = to_dot(**model)
    for att in model_obj.__dict__:
        if isinstance(getattr(model_obj, att), dict):
            setattr(model_obj, att, traverse(getattr(model_obj, att)))
        if isinstance(getattr(model_obj, att), list):
            setattr(model_obj, att, copy.deepcopy(model_obj.__dict__[att]))
            for i, item in enumerate(model_obj.__dict__[att]):
                if isinstance(item, dict):
                    model_obj.__dict__[att][i] =  traverse(item)
    return model_obj

def to_dot(**dico):
    type_obj = type("dot", (), dico)
    return type_obj


if __name__ == "__main__":
    model = {
        "size": "medium",
        "car": {
            "wheel": 6,
            "options": [
                "AC", "SATANAV", "Airbags",
                {
                    "drive": 4,
                    "differential": "autoblock"
                }
            ]
        }
    }

    dot_model = traverse(model)

    print(dot_model.size)
    print(dot_model.car)
    print(dot_model.car.wheel)
    print(dot_model.car.options)
    print(dot_model.car.options[2])
    print(dot_model.car.options[3].differential)
    print("Instance:")
    inst = dot_model()
    print(inst.size)
    print(inst.car)
    print(inst.car.wheel)

