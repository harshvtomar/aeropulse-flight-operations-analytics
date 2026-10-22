"""All generated rows in tests are synthetic, never business-analysis inputs."""
import pandas as pd
import pytest
from src.validate import FIELDS

@pytest.fixture
def rows():
    row=dict.fromkeys(FIELDS,None)
    row.update(FlightDate='2025-01-01',Year=2025,Month=1,DayOfWeek=3,Reporting_Airline='AA',
      DOT_ID_Reporting_Airline=19805,Flight_Number_Reporting_Airline=1,OriginAirportID=12478,DestAirportID=12892,
      Origin='JFK',Dest='LAX',CRSDepTime=900,CRSArrTime=1200,DepTime=900,ArrTime=1200,
      DepDelay=0,ArrDelay=-5,ArrDel15=0,Cancelled=0,Diverted=0,Distance=2475,
      CarrierDelay=0,WeatherDelay=0,NASDelay=0,SecurityDelay=0,LateAircraftDelay=0)
    return pd.DataFrame([row])
