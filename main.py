from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from nabiji_scrapper import search_product_nabiji, filtered_results_nabiji
from spar_scrapper import search_product_spar, filtered_results_spar

app = FastAPI()

class InputModel(BaseModel):
    param: str

@app.post("/process")
def process(input: InputModel):
    raw_nabiji = search_product_nabiji(input.param)
    nabiji_filtered, store_name_nabiji = filtered_results_nabiji(raw_nabiji, input.param)
    raw_spar = search_product_spar(input.param)
    spar_filtered, store_name_spar = filtered_results_spar(raw_spar, input.param)
    output = nabiji_filtered + spar_filtered

    output.sort(key=lambda p: float(p["price now"] or 0))

    input_words = input.param.lower().split()

    return [
        {
            "name": p["name"], 
            "price_now": p["price now"],
            "old_price": p["old price"],
            "store": store_name_nabiji if p in nabiji_filtered else store_name_spar,
        }
        for p in output
        if all(word in p["name"].lower() for word in input_words)
        and p["name"].lower().split("/")[0].strip().startswith(input_words[0])
    ]