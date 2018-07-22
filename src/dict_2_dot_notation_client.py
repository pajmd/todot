from dict_2_dot_notation import error, run_rule


def validate_dob(model):
    error(model.data.person.dob == 99999999, "Bad dob")


def derive_name(person):
    person.name = "PJMD"


def derive_company(model):
    company = model.data.person.properties[2].company
    company.employes = 300


def derive_cashflow(model):
    company = model.data.person.properties[2].company
    company.cashflow = company.employes * model.data.person.properties[2].bank_account.salary_average


if __name__ == "__main__":
    model = {
        "data": {
            "person": {
                "name": "xxx",
                "dob": 19900131,
                "properties": [
                    "car",
                    "house",
                    {
                        "company": {
                            "address": "New York",
                            "employes": 200
                        },
                        "bank_account": {
                            "bank": "chase",
                            "account_number": 12345,
                            "salary_average": 3000.00
                        }
                    }
                ]
            }
        }
    }
    log = run_rule(validate_dob, model)
    person = model["data"]["person"]
    log = run_rule(derive_name, person)
    log = run_rule(derive_company, model)
    print("update model\n{}".format(model))
    pass