
import pandas as pd
import base64
import requests
import pandas as pd
import io
from io import StringIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}



if __name__ == "__main__":
    main()
