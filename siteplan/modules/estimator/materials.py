# pycal/materials.py

class Water:
    watername:str = 'H2O'
    water_property:dict = {
        "_id": "water_properties",
         "form": 'fluid',
        "vol": 1,
        "unit": "gal",
        "ppg": 8.34,
        "kgpg": 3.785,
        "ltr": 3.785,
        "temp": {
            "unit": "deg",
             "boil": {
                 "F": 212,
                 "C": 100
                },
             "freeze": {
                 "F": 32,
                 "C": 0
                 }
            },
        "unit_convention": """
                ppg:pound per gallon,
                kgpg: kilograms per gallon,
                ltr: liter,
                tmp: room temperature
                """  ,
         "generalnnote": """Cold water is more dense than ice
        or than warm water or liquid just above freezing.
        This is an unusual property of the substance,
        resulting from hydrogen bonding.
         So, a gallon of warm water would weigh slightly less
         than a gallon of cold water.
        """


    }
    water_consumption:dict = {
      "_id": "portable_water_requirements",
      "title": "Ministry Of Health Environmental Healt Unit Portable Water Requirements",
      "residential_development": {
        "title": "Nominal Residential Water Consumption",
        "desciption": "The nominal water consumption for residential developments is assumed to be 230 Liters per person per day.",
        "system_capacity": {
          "studio": {
            "accupancy": 2,
            "consumption": 460,
            "unit": "litre"
          },
          "single_bedroom": {
            "accupancy": 3,
            "consumption": 690,
            "unit": "litre"
          },
          "two_bedrooms": {
            "accupancy": 2,
            "consumption": 920,
            "unit": "litre"
          }
        }
      },
      "water_devices": {
        "title": "Water Saving Devices Usage Per Fixture",
        "description": "Plumbing Devices minimum water consumption rates per fixture per day.",
        "device": {
          "bath_tub": {
            "consumption": {
              "litre": 30,
              "us_gal": 8
            }
          },
          "faucet": {
            "consumption": {
              "litre": 35,
              "us_gal": 9.2
            }
          },
          "shower": {
            "consumption": {
              "litre": 60,
              "us_gal": 16
            }
          },
          "toilet": {
            "consumption": {
              "litre": 25,
              "us_gal": 6.6
            }
          },
          "urinal": {
            "consumption": {
              "litre": 15,
              "us_gal": 4
            }
          }
        }
      }
    }
    wastewater:dict = {
      "_id": "treated_wastewater_quality_standards",
      "title": "Typical Medium Strength Domestic Sewage",
      "description": "NEPA Standard for liquid waste water discharge.",
      "notice": "None value represent Not Applicable Values (N/A)",
      "domestic_waste_water": {
        "title": "Water Quality Criteria",
        "description": "NRCA Sewage Effluent Regulations (2004)",
        "tss": {
          "title": "Total Suspended Solids",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 20,
              "unit": "mg/L"
            },
            "irrigation": {
              "value": 15,
              "unit": "mg/L"
            }
          }
        },
        "cod": {
          "title": "Chemical Oxygen Demand",
          "description": "Chemical Oxygen Demand",
          "design_value": {
            "direct_discharge": {
              "value": 100,
              "unit": "mg/L"
            },
            "irrigation": {
              "value": 99,
              "unit": "mg/L"
            }
          }
        },
        "bod": {
          "title": "Biochemical Oxygen Demand",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 20,
              "unit": "mg/L"
            },
            "irrigation": {
              "value": 15,
              "unit": "mg/L"
            }
          }
        },
        "n": {
          "title": "Total Nitrogen",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 10,
              "unit": "mg/L"
            },
            "irrigation": {
              "value": None,
              "unit": "mg/L"
            }
          }
        },
        "p": {
          "title": "Total Phosphates",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 4,
              "unit": "mg/L"
            },
            "irrigation": {
              "value": None,
              "unit": "mg/L"
            }
          }
        },
        "ph": {
          "title": "Power of Hydrogen",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 6,
              "unit": ""
            },
            "irrigation": {
              "value": None,
              "unit": ""
            }
          }
        },
        "fc": {
          "title": "Faecal Coliform Bacteria",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 200,
              "unit": "MPN/100ml"
            },
            "irrigation": {
              "value": 12,
              "unit": "MPN/100ml"
            }
          }
        },
        "residual_chlorine": {
          "title": "Residual Chlorine",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": 1.5,
              "unit": "mg/L"
            },
            "irrigation": {
              "value": 0.5,
              "unit": "mg/L"
            }
          }
        },
        "oil_grease": {
          "title": "Oil and Grease",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": None,
              "unit": ""
            },
            "irrigation": {
              "value": 10,
              "unit": "mg/L"
            }
          }
        },
        "giardia_cyst": {
          "title": "Giardia Cyst",
          "description": "",
          "design_value": {
            "direct_discharge": {
              "value": None,
              "unit": ""
            },
            "irrigation": {
              "value": 0.99,
              "unit": "#/ 100 ml"
            }
          }
        }
      }
    }
    sewage_strength:dict = {
      "_id": "sewage_strength_composition",
      "title": "Typical Medium Strength Domestic Sewage",
      "description": "Medium strength raw sewage and composition arriving at a treatment plant standard as provided by The MOH EHU.",
      "domestic_sewage": {
        "tss": {
          "title": "Total Suspended Solids",
          "description": "",
          "design_value": {
            "value": 220,
            "unit": "mg/L"
          }
        },
        "cod": {
          "title": "Chemical Oxygen Demand",
          "description": "Chemical Oxygen Demand",
          "design_value": {
            "value": 500,
            "unit": "mg/L"
          }
        },
        "bod": {
          "title": "Biochemical Oxygen Demand",
          "description": "",
          "design_value": {
            "value": 250,
            "unit": "mg/L"
          }
        },
        "n": {
          "title": "Total Nitrogen",
          "description": "",
          "design_value": {
            "value": 40,
            "unit": "mg/L"
          }
        },
        "p": {
          "title": "Total Phosphorus",
          "description": "",
          "design_value": {
            "value": 8,
            "unit": "mg/L"
          }
        },
        "cb": {
          "title": "Total Coliform Bacteria",
          "description": "",
          "design_value": {
            "value": {
              "min": 100000000,
              "max": 1000000000
            },
            "unit": "MPN/100ml"
          }
        }
      }
    }
    sewage_treatment:dict = {
      "_id": "system_proximity_location",
      "title": "Soil Absorption System Proximity & Location",
      "description": "Soil Absorption System - Proximity Location Allowances",
      "component": {
        "septic_tank": {
          "distance": {
            "unit": "m",
            "from": {
              "building_foundation": 1.5,
              "property_line": 1.5,
              "tile_field": 6
            },
            "to": {}
          }
        },
        "tile_field": {
          "distance": {
            "unit": "m",
            "notes": "Distance measured for pits are 3 X Pit Diameter",
            "from": {
              "building_foundation": 6,
              "property_line": 3,
              "septic_tank": 0.5,
              "cased_well": 7.5,
              "uncased_well": 30,
              "river_stream": 45,
              "high_water_mark": 45,
              "fractured_rock": 3,
              "neighbouring_pit": 3
            },
            "to": {}
          }
        }
      },
      "treatment_category": {
          "_id": "treatment_category",
          "title": "The Ministry Of Health Environmental Health Unit Categories of Treatment",
          "description": "The EHU at the Ministry of Health makes recommendations on wastewater treatment systems and treatment quality.",
          "treatment_category": {
            "primary": {
              "definition": "Physical treatment",
              "requirements": "Treatment prior to final disposal",
              "specifications": {}
            },
            "secondary": {
              "definition": "The removal of organic load (COD , and BOD)",
              "requirements": "Physical treatment and biological treatment prior to final disposal",
              "specifications": {}
            },
            "tertiary": {
              "definition": "The removal of nutrient.",
              "notes": "This type of system is usually required where developments are located within environmentally sensitive areas or areas of public health concern",
              "requirements": "Requires physical and advanced biological treatment, sometimes in combination with chemical treatment",
              "specifications": {}
            }
          }
        }
    }

    def water(self, name:str=None):
        ''' H2O  A Clear Fluid Substance  composting of Hydrogen and Oxygen.'''
        if name:
            self.watername = name
        return self.watername

    def waterppg( self , gals:float=None):
        """ Pound per gallon returns the weight in pounds of 1 usgallon of water"""
        if gals:
            return f"{gals * self.water_property['ppg']} lbs"
        return f"{self.water_property['ppg']} lb"

    def waterkpg( self , kilos:float=None):
        """ Kilograms  per gallon returns the weight in kilograms of 1 usgallon of water"""
        if kilos:
            return f"{kilos * self.water_property['kgpg']} Kg"
        return f"{self.water_property['kgpg']} Kg"

    def waterlpg( self , liters:float=None):
        """ Liters  per gallon returns the Metric Volume in liters of 1 usgallon of water"""
        if liters:
            return f"{liters * self.water_property['ltr']} liters"
        return f"{self.water_property['ltr']} liter"



