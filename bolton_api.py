
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

class Zahnbreiten(BaseModel):
    # Assuming zahnbreiten is a dictionary with specific keys and float values
    # Example: {"1.1": 8.5, "1.2": 7.0, ...}
    data: Dict[str, float]
    platzangebot_ok_rechts: float
    platzangebot_ok_links: float
    platzangebot_uk_rechts: float
    platzangebot_uk_links: float

@app.post("/submitData")
def submit_data(input_data: Zahnbreiten):
    # Process the data
    # For example, you can pass this data to your calculation functions
    # and return the results
    return {"message": "Data received successfully"}


class TonnsRelationInput(BaseModel):
    sum_upper_anterior: float
    sum_lower_anterior: float

class BoltonAnalysisInput(BaseModel):
    data: dict
    

class MoyersAnalysisInput(BaseModel):
    data: dict
    platzangebot_ok_rechts: float
    platzangebot_ok_links: float
    platzangebot_uk_rechts: float
    platzangebot_uk_links: float

# Translating the given Moyers probability table into a Python dictionary
# The dictionary will have keys that are the measurements of the SIUK (Summe der Inzisivi im Unterkiefer)
# and the values will be nested dictionaries with keys as percentages and values as the required space.

moyers_table_lower_jaw_complete = {
    19.5: {95: 21.1, 85: 20.5, 75: 20.1, 65: 19.8, 50: 19.4, 35: 19, 25: 18.7, 15: 18.4, 5: 17.7},
    20.0: {95: 21.4, 85: 20.8, 75: 20.4, 65: 20.1, 50: 19.7, 35: 19.3, 25: 19, 15: 18.7, 5: 18},
    20.5: {95: 21.7, 85: 21.1, 75: 20.7, 65: 20.4, 50: 20, 35: 19.6, 25: 19.3, 15: 19, 5: 18.3},
    21.0: {95: 22.0, 85: 21.4, 75: 21.0, 65: 20.7, 50: 20.3, 35: 19.9, 25: 19.6, 15: 19.3, 5: 18.6},
    21.5: {95: 22.3, 85: 21.7, 75: 21.3, 65: 21.0, 50: 20.6, 35: 20.2, 25: 19.9, 15: 19.6, 5: 18.9},
    22.0: {95: 22.6, 85: 22.0, 75: 21.6, 65: 21.3, 50: 20.9, 35: 20.5, 25: 20.2, 15: 19.8, 5: 19.2},
    22.5: {95: 22.9, 85: 22.3, 75: 21.9, 65: 21.6, 50: 21.2, 35: 20.8, 25: 20.5, 15: 20.1, 5: 19.5},
    23.0: {95: 23.2, 85: 22.6, 75: 22.2, 65: 21.9, 50: 21.5, 35: 21.1, 25: 20.8, 15: 20.4, 5: 19.8},
    23.5: {95: 23.5, 85: 22.9, 75: 22.5, 65: 22.2, 50: 21.8, 35: 21.4, 25: 21.1, 15: 20.7, 5: 20.1},
    24.0: {95: 23.8, 85: 23.2, 75: 22.8, 65: 22.5, 50: 22.1, 35: 21.7, 25: 21.4, 15: 21, 5: 20.4},
    24.5: {95: 24.1, 85: 23.5, 75: 23.1, 65: 22.8, 50: 22.4, 35: 22, 25: 21.7, 15: 21.3, 5: 20.7},
    25.0: {95: 24.4, 85: 23.8, 75: 23.4, 65: 23.1, 50: 22.7, 35: 22.3, 25: 22, 15: 21.6, 5: 21},
}

moyers_table_upper_jaw_complete = {
    19.5: {95: 21.6, 85: 21, 75: 20.6, 65: 20.4, 50: 20, 35: 19.6, 25: 19.4, 15: 19, 5: 18.5},
    20.0: {95: 21.8, 85: 21.3, 75: 20.9, 65: 20.6, 50: 20.3, 35: 19.9, 25: 19.7, 15: 19.3, 5: 18.8},
    20.5: {95: 22.1, 85: 21.5, 75: 21.2, 65: 20.9, 50: 20.6, 35: 20.2, 25: 19.9, 15: 19.6, 5: 19},
    21.0: {95: 22.4, 85: 21.8, 75: 21.5, 65: 21.2, 50: 20.8, 35: 20.5, 25: 20.2, 15: 19.9, 5: 19.3},
    21.5: {95: 22.7, 85: 22.1, 75: 21.8, 65: 21.5, 50: 21.1, 35: 20.8, 25: 20.5, 15: 20.2, 5: 19.6},
    22.0: {95: 22.9, 85: 22.4, 75: 22, 65: 21.8, 50: 21.4, 35: 21, 25: 20.8, 15: 20.4, 5: 19.9},
    22.5: {95: 23.2, 85: 22.6, 75: 22.3, 65: 22, 50: 21.7, 35: 21.3, 25: 21, 15: 20.7, 5: 20.1},
    23.0: {95: 23.5, 85: 22.9, 75: 22.6, 65: 22.3, 50: 21.9, 35: 21.6, 25: 21.3, 15: 21, 5: 20.4},
    23.5: {95: 23.8, 85: 23.2, 75: 22.9, 65: 22.6, 50: 22.2, 35: 21.9, 25: 21.6, 15: 21.3, 5: 20.7},
    24.0: {95: 24, 85: 23.5, 75: 23.1, 65: 22.8, 50: 22.5, 35: 22.1, 25: 21.9, 15: 21.5, 5: 21},
    24.5: {95: 24.3, 85: 23.7, 75: 23.4, 65: 23.1, 50: 22.8, 35: 22.4, 25: 22.1, 15: 21.8, 5: 21.2},
    25.0: {95: 24.6, 85: 24, 75: 23.7, 65: 23.4, 50: 23, 35: 22.7, 25: 22.4, 15: 22.1, 5: 21.5},
}

OK_nach_UK_dict = {
    'OK12': [85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    'UK12': [77.6, 78.5, 79.4, 80.3, 81.3, 82.2, 83.1, 84.0, 84.9, 85.8, 86.7, 87.6, 88.6, 89.5, 90.4, 91.3, 92.2, 93.1, 94.0, 95.0, 95.9, 96.8, 97.7, 98.6, 99.5, 100.4]
    }

UK_nach_OK_dict = {
    'UK12': [77.6, 78.5, 79.4, 80.3, 81.3, 82.2, 83.1, 84.0, 84.9, 85.8, 86.7, 87.6, 88.6, 89.5, 90.4, 91.3, 92.2, 93.1, 94.0, 95.0, 95.9, 96.8, 97.7, 98.6, 99.5, 100.4],
    'OK12': [85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
    }

# Function to find the corresponding value
def find_corresponding_value_OK(lower_sum_6_6, uk_to_ok_dict):
    # First, round lower_sum_6_6 to the closest value in the UK12 list
    closest_value = min(uk_to_ok_dict['UK12'], key=lambda x: abs(x - lower_sum_6_6))
    
    # Find the index of this value
    index = uk_to_ok_dict['UK12'].index(closest_value)
    
    # Return the corresponding OK12 value
    return uk_to_ok_dict['OK12'][index]

# Function to find the corresponding value
def find_corresponding_value_UK(upper_sum_6_6, ok_to_uk_dict):
    # First, round lower_sum_6_6 to the closest value in the UK12 list
    closest_value = min(ok_to_uk_dict['OK12'], key=lambda x: abs(x - upper_sum_6_6))
    
    # Find the index of this value
    index = ok_to_uk_dict['OK12'].index(closest_value)
    
    # Return the corresponding OK12 value
    return ok_to_uk_dict['UK12'][index]

# Function to calculate Tonns Relation
def calculate_tonns_relation(sum_upper_anterior, sum_lower_anterior):
    
    # Tonnschen Index berechnen
    try:
        tonns_ratio = round(((sum_lower_anterior / sum_upper_anterior) * 100),1)
    except ZeroDivisionError:
        tonns_ratio = 0

    # Überschuss bestimmen
    if tonns_ratio > 74:
        surplus = 'Überschuss im Unterkiefer (UK)'
    elif tonns_ratio < 74:
        surplus = 'Überschuss im Oberkiefer (OK)'
    else:
        surplus = 'Ausgeglichenes Verhältnis'

    result = f"Tonn Index: {tonns_ratio},\n{surplus}"

    return result, tonns_ratio, surplus

@app.post("/calculateTonnsRelation")
def api_calculate_tonns_relation(input_data: TonnsRelationInput):
    try:
        result, tonns_ratio, surplus = calculate_tonns_relation(input_data.sum_upper_anterior, input_data.sum_lower_anterior)
        return {"result": result, "tonns_ratio": tonns_ratio, "surplus": surplus}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function to check decimal - if they end in .5 or .0 no rounding
def check_decimal(value):
    # Extract the decimal part of the number
    decimal_part = value % 1
    
    # Check if the decimal part is 0.5 or 0
    if decimal_part == 0.5 or decimal_part == 0:
        # If condition is met, do something
        return True
    else:
        # If condition is not met, do nothing
        return False

# round to next half number
def round_up_to_nearest_half(number):
    result = int(number*2+1)/2
    return result

# Anzeige der Zahnbreiten
def anzeige_zaehne(zahnbreiten):
    upper_teeth_3_3 = [zahnbreiten.get(f"{i}.{j}", 0) for i in range(1, 3) for j in range(1, 4)]
    upper_sum_3_3 = round(sum(upper_teeth_3_3),1)
    lower_teeth_3_3 = [zahnbreiten.get(f"{i}.{j}", 0) for i in range(3, 5) for j in range(1, 4)]
    lower_sum_3_3 = round(sum(lower_teeth_3_3),1)
    upper_teeth_6_6 = [zahnbreiten.get(f"{i}.{j}", 0) for i in range(1, 3) for j in range(1, 7)]
    upper_sum_6_6 = round(sum(upper_teeth_6_6),1)
    lower_teeth_6_6 = [zahnbreiten.get(f"{i}.{j}", 0) for i in range(3, 5) for j in range(1, 7)]
    lower_sum_6_6 = round(sum(lower_teeth_6_6),1)
    
    # Werte für alle Zähne im Ober- und Unterkiefer extrahieren
    upper_teeth = [zahnbreiten.get(f"{i}.{j}", 0) for i in range(1, 3) for j in range(1, 7)]
    upper_sum = sum(upper_teeth)
    lower_teeth = [zahnbreiten.get(f"{i}.{j}", 0) for i in range(3, 5) for j in range(1, 7)]
    lower_sum = sum(lower_teeth)

    return lower_sum, upper_sum, upper_sum_3_3, lower_sum_3_3, upper_sum_6_6, lower_sum_6_6
    
# calculate anterior teeth width
def Frontzahnbreiten(zahnbreiten, anzahl_frontzähne):
    upper_anterior_teeth = [zahnbreiten.get(f"1.{i}", 0) for i in range(1, anzahl_frontzähne+1)] + \
                        [zahnbreiten.get(f"2.{i}", 0) for i in range(1, anzahl_frontzähne+1)]
    upper_anterior_sum = sum(upper_anterior_teeth)
    lower_anterior_teeth = [zahnbreiten.get(f"3.{i}", 0) for i in range(1, anzahl_frontzähne+1)] + \
                        [zahnbreiten.get(f"4.{i}", 0) for i in range(1, anzahl_frontzähne+1)]
    lower_anterior_sum = sum(lower_anterior_teeth)


    return upper_anterior_sum, lower_anterior_sum

def calculate_bolton_analysis(zahnbreiten):
    lower_sum, upper_sum, upper_sum_3_3, lower_sum_3_3, upper_sum_6_6, lower_sum_6_6 = anzeige_zaehne(zahnbreiten)
    try:
        ttsr = round(((lower_sum / upper_sum) * 100), 2)
        upper_anterior_sum, lower_anterior_sum = Frontzahnbreiten(zahnbreiten, 3)
        atsr = round(((lower_anterior_sum / upper_anterior_sum) * 100), 2)
        ratio = round(((upper_sum / lower_sum) * 100), 2)
        print(ttsr)
    except ZeroDivisionError:
        ttsr = 0
        atsr = 0
        ratio = 0

    if ttsr < 91.3:
        text_ttsr = "OK-Zahnmaterial relativ zu groß"
        corresponding_value = find_corresponding_value_OK(lower_sum, UK_nach_OK_dict)
        text_korrektur = f"Im OK muss auf {corresponding_value} mm reduziert werden."
    elif ttsr > 91.3:
        text_ttsr = "UK-Zahnmaterial relativ zu groß"
        corresponding_value = find_corresponding_value_UK(upper_sum, OK_nach_UK_dict)
        text_korrektur = f"Im UK muss auf {corresponding_value} mm reduziert werden."
    else:
        text_ttsr = "Balanced"
        text_korrektur = "Keine Korrektur erforderlich"

    if atsr < 77.2:
        text_atsr = "OK-Zahnmaterial relativ zu groß"
    elif atsr > 77.2:
        text_atsr = "UK-Zahnmaterial relativ zu groß"
    else:
        text_atsr = "Balanced"

    return {
        "Overall Ratio": ttsr,
        "Overall Ratio Interpretation": text_ttsr,
        "Correction Suggestion": text_korrektur,
        "Anterior Ratio": atsr,
        "Anterior Ratio Interpretation": text_atsr,
        "Upper Sum 6-6": upper_sum,
        "Lower Sum 6-6": lower_sum,
        "Upper Sum 3-3": upper_anterior_sum,
        "Lower Sum 3-3": lower_anterior_sum
    }
@app.post("/calculateBoltonAnalysis")
def api_calculate_bolton_analysis(input_data: BoltonAnalysisInput):
    result = calculate_bolton_analysis(input_data.data)
    return result

def calculate_moyers_analysis(zahnbreiten, platzangebot_ok_rechts, platzangebot_ok_links, platzangebot_uk_rechts, platzangebot_uk_links):
    upper_anterior_sum, lower_anterior_sum_orig = Frontzahnbreiten(zahnbreiten, 2)
    
    if not check_decimal(lower_anterior_sum_orig):
        lower_anterior_sum = round_up_to_nearest_half(lower_anterior_sum_orig)
    else:
        lower_anterior_sum = lower_anterior_sum_orig

    try:
        required_space_upper_jaw = moyers_table_upper_jaw_complete[lower_anterior_sum][75]
        required_space_lower_jaw = moyers_table_lower_jaw_complete[lower_anterior_sum][75]
        diff_OK_rechts = round((platzangebot_ok_rechts - required_space_upper_jaw), 1)
        diff_OK_links = round((platzangebot_ok_links - required_space_upper_jaw), 1)
        diff_UK_rechts = round((platzangebot_uk_rechts - required_space_lower_jaw), 1)
        diff_UK_links = round((platzangebot_uk_links - required_space_lower_jaw), 1)
    except KeyError:
        print('Achtung: Der SIUK-Wert liegt außerhalb der Tabelle.')
        return {
            "Summe Schneidezahnbreite Oberkiefer (SIOK)": upper_anterior_sum,
            "Summe Schneidezahnbreiten Unterkiefer (SIUK)": lower_anterior_sum_orig,
            "Gerundete SIUK": lower_anterior_sum,
            "Platzbedarf OK": 0,
            "Platzbedarf UK": 0,
            "Differenz Platzangebot - Platzbedarf OK rechts": 0,
            "Differenz Platzangebot - Platzbedarf OK links": 0,
            "Differenz Platzangebot - Platzbedarf UK rechts": 0,
            "Differenz Platzangebot - Platzbedarf UK links": 0
        }

    return {
        "Summe Schneidezahnbreite Oberkiefer (SIOK)": upper_anterior_sum,
        "Summe Schneidezahnbreiten Unterkiefer (SIUK)": lower_anterior_sum_orig,
        "Gerundete SIUK": lower_anterior_sum,
        "Platzbedarf OK": required_space_upper_jaw,
        "Platzbedarf UK": required_space_lower_jaw,
        "Differenz Platzangebot - Platzbedarf OK rechts": diff_OK_rechts,
        "Differenz Platzangebot - Platzbedarf OK links": diff_OK_links,
        "Differenz Platzangebot - Platzbedarf UK rechts": diff_UK_rechts,
        "Differenz Platzangebot - Platzbedarf UK links": diff_UK_links
    }

@app.post("/calculateMoyersAnalysis")
def api_calculate_moyers_analysis(input_data: MoyersAnalysisInput):
    result = calculate_moyers_analysis(
        input_data.data, 
        input_data.platzangebot_ok_rechts, 
        input_data.platzangebot_ok_links, 
        input_data.platzangebot_uk_rechts, 
        input_data.platzangebot_uk_links
    )
    return result


def main():
    #----------- Dateneingabe-----------------------------
    
    # ------- Auswertungen -------------------------------


    moyers_result = calculate_moyers_analysis(zahnbreiten, platzangebot_ok_rechts, platzangebot_ok_links, platzangebot_uk_rechts, platzangebot_uk_links)

    # Access the values from the result dictionary using the correct keys
    upper_anterior_sum = moyers_result["Summe Schneidezahnbreite Oberkiefer (SIOK)"]
    lower_anterior_sum_orig = moyers_result["Summe Schneidezahnbreiten Unterkiefer (SIUK)"]
    lower_anterior_sum = moyers_result["Gerundete SIUK"]
    required_space_upper_jaw = moyers_result["Platzbedarf OK"]
    required_space_lower_jaw = moyers_result["Platzbedarf UK"]
    diff_OK_rechts = moyers_result["Differenz Platzangebot - Platzbedarf OK rechts"]
    diff_OK_links = moyers_result["Differenz Platzangebot - Platzbedarf OK links"]
    diff_UK_rechts = moyers_result["Differenz Platzangebot - Platzbedarf UK rechts"]
    diff_UK_links = moyers_result["Differenz Platzangebot - Platzbedarf UK links"]

    #--Auswertung Tonn Index -------------------

    tonns_result, tonns_ratio, surplus = calculate_tonns_relation(upper_anterior_sum, lower_anterior_sum)

    #--Auswertung Breitenrelation nach Bolton ---------

    print('Breitenrelation nach Bolton ')
    print(f'Summe der Breiten aller permanenten Zähne (6-6) im Unterkiefer geteilt durch Summe aller permanenten Zähne (6-6) im Oberkiefer.')

    bolton_result = calculate_bolton_analysis(zahnbreiten)


    # Access the values from the bolton_result dictionary using the correct keys
    ttsr = bolton_result["Overall Ratio"]
    text_ttsr = bolton_result["Overall Ratio Interpretation"]
    text_korrektur = bolton_result["Correction Suggestion"]
    atsr = bolton_result["Anterior Ratio"]
    text_atsr = bolton_result["Anterior Ratio Interpretation"]
    upper_sum_6_6 = bolton_result["Upper Sum 6-6"]
    lower_sum_6_6 = bolton_result["Lower Sum 6-6"]
    upper_sum_3_3 = bolton_result["Upper Sum 3-3"]
    lower_sum_3_3 = bolton_result["Lower Sum 3-3"]



if __name__ == "__main__":
    main()