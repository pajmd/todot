


def to_dot(**dico):
    def getitem(self, key):
        val = self.d[key]
        print("getting {}".format(key))
        return val

    def setitem(self, key, val):
        print("setting {} = {}".format(key, val))
        self.d[key] = val
        setattr(self, key, val)

    type_obj = type("dot", (), dico)
    type_obj.d = dico
    type_obj.__getitem__ = getitem
    type_obj.__setitem__ = setitem
    return type_obj


if __name__ == "__main__":
    model = {
        "size": "medium",
        "car": {
            "wheel": 6,
            "options": "stuff"
        }
    }

    obj_model = to_dot(**model)
    car = obj_model()
    print(car.size)
    print(car["size"])
    car["size"] = "sedan"
    print(car["size"])
    print(car.size)

