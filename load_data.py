import pandas as pd
from pages.models import recordData

print("Hello")
df = pd.read_csv("~/Downloads/ALLRecords.csv")
for index, entry in df.iterrows():
    print(entry)
    temp_entry = recordData(libName=entry["libName"], dayOfWeek=entry["dayOfWeek"], time=entry["time"], floorNum=entry["floorNum"], section=entry["section"], count=entry["count"])
    temp_entry.save()
