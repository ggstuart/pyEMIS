from sqlalchemy import Column, Integer, Sequence, ForeignKey
from sqlalchemy.dialects.mssql import TINYINT, SMALLINT, DECIMAL, NCHAR, DATETIME, BIT, SMALLDATETIME, NVARCHAR, VARCHAR, NTEXT, MONEY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Meter(Base):
    __tablename__ = 'Meter'
    Meter_ID = Column(Integer, Sequence('Meter_seq'), primary_key=True)
    Description = Column(NCHAR(30), nullable=False)
    Meter_Type = Column(TINYINT, nullable=False)
    Service_ID = Column(Integer, ForeignKey('Service_Type.Service_ID'), nullable=True)
    Measured_Unit_ID = Column(Integer, ForeignKey('Units.Unit_ID'), nullable=False)
    Readings_Or_Deliveries = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Readings_Or_Deliveries]  DEFAULT (0),
    Main_Or_Sub_Meter = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Main_Or_Sub_Meter]  DEFAULT (0),
    Digits = Column(TINYINT, nullable=False)
    Decimal_Digits = Column(TINYINT, nullable=False)
    Meter_Capacity = Column(DECIMAL(17, 5), nullable=False)
    Enter_Stock = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Enter_Stock]  DEFAULT (0),
    Auto_Import_Code = Column(NVARCHAR(255), nullable=True)
    Password = Column(NCHAR(12), nullable=True)
    NHS_Energy_Source = Column(TINYINT, nullable=True)
    NHS_Energy_Exported = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_NHS_Energy_Exported]  DEFAULT (0),
    NHS_Off_Site_Processes = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_NHS_Off_Site_Processes]  DEFAULT (0),
    Annual_Budget = Column(MONEY, nullable=True)
    Trend_PIN = Column(NCHAR(4), nullable=True)
    Trend_Phone = Column(NCHAR(20), nullable=True)
    Data_Collection_Frequency_Qty = Column(SMALLINT, nullable=True)
    Data_Collection_Warn_After_Qty = Column(SMALLINT, nullable=True)
    Normal_Min_Consumption = Column(DECIMAL(16, 5), nullable=True)
    Normal_Max_Consumption = Column(DECIMAL(16, 5), nullable=True)
    Critical_Min_Consumption = Column(DECIMAL(16, 5), nullable=True)
    Critical_Max_Consumption = Column(DECIMAL(16, 5), nullable=True)
    Consumption_Interval_Qty = Column(SMALLINT, nullable=True)
    Auto_Importing_Enabled = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Auto_Importing_Enabled]  DEFAULT (0),
    Main_Target_Type = Column(TINYINT, nullable=False)# [tinyint] NOT NULL CONSTRAINT [DF_Meter_Main_Target_Type]  DEFAULT (0),
    Determining_Factor_ID = Column(Integer, nullable=True)
    Degree_Day_Baseline = Column(DECIMAL(4, 2), nullable=True)
    Heating_Or_Cooling = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Heating_Or_Cooling]  DEFAULT (1),
    Applicable_Days_Calendar_ID = Column(Integer, nullable=True)
    Period_Of_Repetition_Qty = Column(SMALLINT, nullable=True)
    Minimum_Alarm_Deviation = Column(DECIMAL(16, 5), nullable=True)
    User_Defined_Formula = Column(NVARCHAR(500), nullable=True)
    Historic_Or_Theoretical = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Historic_Or_Theoretical]  DEFAULT (0),
    Pct_Of_Historic = Column(DECIMAL(6, 2), nullable=True)# CONSTRAINT [DF_Meter_Pct_Of_Historic]  DEFAULT (100),
    Alarm_Band_Width = Column(SMALLINT, nullable=True)
    Calculation_Start_Date = Column(SMALLDATETIME, nullable=True)
    Calculation_End_Date = Column(SMALLDATETIME, nullable=True)
    Baseline_Consumption = Column(DECIMAL(19, 5), nullable=True)
    Baseline_Interval_Qty = Column(SMALLINT, nullable=True)
    Baseline_Interval_Period = Column(TINYINT, nullable=True)
    Variable_Consumption = Column(DECIMAL(19, 7), nullable=True)
    Aspect_Ratio = Column(DECIMAL(10, 5), nullable=True)
    Load_Factor = Column(DECIMAL(10, 5), nullable=True)
    Walking_Route_Sequence = Column(SMALLINT, nullable=True)
    Date_Reading_Requested = Column(SMALLDATETIME, nullable=True)
    Suppress_Negative_Values = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Suppress_Negative_Values]  DEFAULT (0),
    Recycled = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Recycled]  DEFAULT (0),
    Comments = Column(NTEXT, nullable=True)
    Data_Collection_Frequency_Period = Column(TINYINT, nullable=True)
    Data_Collection_Warn_After_Period = Column(TINYINT, nullable=True)
    Consumption_Interval_Period = Column(TINYINT, nullable=True)
    Alarms_Enabled = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Alarms_Enabled]  DEFAULT (0),
    Period_Of_Repetition_Period = Column(TINYINT, nullable=True)
    Climate_Change_Levy_Var = Column(DECIMAL(11, 7), nullable=False)
    Utility_Accounting = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Utility_Accounting]  DEFAULT (0),
    Heat_On = Column(TINYINT, nullable=True)
    Heat_Off = Column(TINYINT, nullable=True)
    Manual_Meter_ID = Column(Integer, nullable=True)
    Metering_Point_ID = Column(NCHAR(16), nullable=True)
    Graphic_X = Column(Integer, nullable=True)
    Graphic_Y = Column(Integer, nullable=True)
    Graphic_File = Column(NCHAR(60), nullable=True)
    Location = Column(NVARCHAR(500), nullable=True)
    Load_Served = Column(NVARCHAR(500), nullable=True)
    Access_Issues = Column(NVARCHAR(500), nullable=True)
    Manufacturer = Column(NCHAR(40), nullable=True)
    Model_Type = Column(NCHAR(40), nullable=True)
    Serial_No = Column(NCHAR(20), nullable=True)
    Collector_Type = Column(TINYINT, nullable=True)
    Metering_Point_Ref = Column(NCHAR(30), nullable=True)
    Collector_Serial_No = Column(NCHAR(20), nullable=True)
    Via = Column(NCHAR(30), nullable=True)
    Simple_Unit_Rate = Column(DECIMAL(16, 5), nullable=False)# CONSTRAINT [DF_Meter_Simple_Unit_Rate]  DEFAULT ((0)),
    Tx_Fault = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Tx_Fault]  DEFAULT ((0)),
    Meter_Fault = Column(BIT, nullable=False)# CONSTRAINT [DF_Meter_Meter_Fault]  DEFAULT ((0)),
    Fault_Comment = Column(VARCHAR(500), nullable=True)

    Service_Type = relationship("Service_Type")
    Measured_Unit = relationship("Units")
    Readings = relationship("Meter_Reading", backref=backref('meter', remote_side=[Meter_ID]))

"""
FOREIGN KEY([Applicable_Days_Calendar_ID]) REFERENCES [dbo].[Applicable_Day_Calendar_Name] ([Calendar_ID])
FOREIGN KEY([Manual_Meter_ID]) REFERENCES [dbo].[Meter] ([Meter_ID])
FOREIGN KEY([Determining_Factor_ID]) REFERENCES [dbo].[Meter] ([Meter_ID])
FOREIGN KEY([Service_ID]) REFERENCES [dbo].[Service_Type] ([Service_ID])
FOREIGN KEY([Measured_Unit_ID]) REFERENCES [dbo].[Units] ([Unit_ID])
CHECK  (([Heat_Off] >= 1 and [Heat_Off] <= 12))
CHECK  (([Heat_On] >= 1 and [Heat_On] <= 12))
"""




class Meter_Reading(Base):
    __tablename__ = 'Meter_Reading'
    Meter_ID = Column(Integer, ForeignKey("Meter.Meter_ID"), nullable=False)
    Reading_DateTime = Column(DATETIME, nullable=False)
    Reading_Type = Column(TINYINT, nullable=False)
    Reading_Or_Total = Column(DECIMAL(16, 5), nullable=False)
    Delivered_Or_Movement = Column(DECIMAL(16, 5), nullable=False)
    Suspect_Reading = Column(BIT, nullable=False)
    Meter_Reading_ID = Column(Integer, Sequence('Meter_Reading_seq', -2147483647, 1), primary_key=True)


class Site(Base):
    __tablename__ = 'Site'
    Site_ID = Column(Integer, Sequence('Site_seq'), primary_key=True)
    Title = Column(NCHAR(20), nullable=True)
    Initials_Or_First_Name = Column(NCHAR(20), nullable=True)
    Surname = Column(NCHAR(30), nullable=True)
    Position = Column(NCHAR(30), nullable=True)
    Name = Column(NCHAR(30), nullable=False)
    Address_Line_1 = Column(NCHAR(40), nullable=True)
    Address_Line_2 = Column(NCHAR(40), nullable=True)
    Address_Line_3 = Column(NCHAR(40), nullable=True)
    Address_Line_4 = Column(NCHAR(40), nullable=True)
    Postcode = Column(NCHAR(12), nullable=True)
    Phone_Number = Column(NCHAR(30), nullable=True)
    Fax_Number = Column(NCHAR(30), nullable=True)
    Email_Address = Column(NCHAR(50), nullable=True)
    Buildings_Occupied = Column(SMALLINT, nullable=True)
    Buildings_In_Watermark = Column(SMALLINT, nullable=True)
    Financial_Year_Start = Column(SMALLDATETIME, nullable=True)
    Financial_Year_End = Column(SMALLDATETIME, nullable=True)
    Receives_Reports = Column(BIT, nullable=False)
    Receives_Bills = Column(BIT, nullable=False)
    Validation = Column(BIT, nullable=False)
    Redirection = Column(BIT, nullable=False)
    DFEE_No = Column(Integer, nullable=True)
    Date_Registered = Column(SMALLDATETIME, nullable=True)
    Date_Approved = Column(SMALLDATETIME, nullable=True)
    Degree_Day_Region_ID = Column(Integer, nullable=False)
    NHS_Site_Type = Column(TINYINT, nullable=False)
    Country = Column(NCHAR(20), nullable=True)
    URL = Column(NCHAR(60), nullable=True)
    Password = Column(NCHAR(20), nullable=True)

"""
FOREIGN KEY([Degree_Day_Region_ID]) REFERENCES [dbo].[Degree_Day_Region] ([Region_ID])
"""

class Tree(Base):
    __tablename__ = 'Tree'
    Node_ID = Column(Integer, Sequence('Tree_seq'), primary_key=True)
    Object_ID = Column(Integer, nullable=False)
    Parent_Node_ID = Column(Integer, ForeignKey('Tree.Node_ID'), nullable=False)
    Object_Type = Column(TINYINT, nullable=False)
    Virtual_Meter_Factor = Column(DECIMAL(8, 6), nullable=True)
    Object_Subtype = Column(TINYINT, nullable=True)
    Object_Description = Column(NCHAR(30), nullable=False)
    Sign = Column(NCHAR(1), nullable=True)
    
    children = relationship("Tree", backref=backref('parent', remote_side=[Node_ID]))


class Units(Base):
    __tablename__ = u'Units'
    Unit_ID = Column(Integer, Sequence('Unit_ID_seq'), primary_key=True)
    Unit_Description = Column(NCHAR(30), nullable=False)
    Unit_Type = Column(TINYINT, nullable=False)
    Units_Per_GJ = Column(DECIMAL(12, 4), nullable=True)
    Units_Per_Cubic_Metre = Column(DECIMAL(12, 4), nullable=True)
    Abbreviation = Column(NCHAR(10), nullable=False)


class Service_Type(Base):
    __tablename__ = 'Service_Type'
    Service_ID = Column(Integer, Sequence('Service_ID_seq'), primary_key=True)
    Service_Description = Column(NCHAR(20), nullable=False)
    Utility = Column(TINYINT, nullable=False)
    Normal_Unit_ID = Column(Integer, nullable=False)
    Climate_Change_Levy = Column(DECIMAL(16, 5), nullable=False)
    Colour = Column(NCHAR(10), nullable=True)
    Climate_Change_Levy_De_Minimis = Column(DECIMAL(8, 2), nullable=True)

    
"""
FOREIGN KEY([Normal_Unit_ID]) REFERENCES [dbo].[Units] ([Unit_ID])
"""

