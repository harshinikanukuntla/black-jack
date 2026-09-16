
input =  {
    "policy_id" : 555,
    "vehicle1_make": "Honda",
    "vehicle1_model": "civic",
    "vehicle2_make": "Ford",
    "vehicle2_model": "F150",
    "vehicle3_make": "BMW",
    "vehicle3_model": "X5",
}

output = {
    "policy_id": 555,
    "vehicle": [
        {"make": "Honda", "model": "civic"},
        {"make": "Ford", "model": "F150"},
        {"make": "BMW", "model": "X5"},
    ]
}

