"""
this file hold statements used to insert dynamic data into databased and keyd by their respective table


key(table_name): value(SQL statement for insertion)
"""

table_meta_info = {
    "vessel": {
        "name": "dynamic_vessel",
        # (timestamp TIMESTAMP NOT NULL PRIMARY KEY,mmsi INTEGER NOT NULL,navigational_status INT NOT NULL, rateofturn FLOAT NOT NULL, speedoverground FLOAT NOT NULL, courseoverground FLOAT NOT NULL, trueheading FLOAT NOT NULL, lon FLOAT NOT NULL, lat NOT NULL);
        "columns": [
            "timestamp",
            "mmsi",
            "navigational_status",
            "rateofturn",
            "speedoverground",
            "courseoverground",
            "trueheading",
            "lon",
            "lat",
            "country_code",
        ],
    },
    "voyage": {
        "name": "dynamic_voyage",
        # dynamic_voyage(timestamp TIMESTAMP NOT NULL, mmsi INTEGER NOT NULL, country_code INT NOT NULL, imo INT, callsign TEXT, shipname TEXT,shiptype INT, to_bow INT, to_stern INT, to_starboard INT, to_port INT, eta TEXT, draught FLOAT, destination TEXT, mothershipmmsi INT, PRIMARY KEY (timestamp, mmsi));
        "columns": [
            "timestamp",
            "mmsi",
            "country_code",
            "imo",
            "callsign",
            "shipname",
            "shiptype",
            "to_bow",
            "to_stern",
            "to_starboard",
            "to_port",
            "eta",
            "draught",
            "destination",
            "mothershipmmsi",
        ],
    },
}


dynamic_data_statements = {
    "dynamic_vessel": "INSERT INTO dynamic_vessel(timestamp, mmsi,navigational_status,rateofturn,speedoverground,courseoverground,trueheading,lon,lat,country_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    "dynamic_aton": "INSERT INTO dynamic_aton(timestamp, mmsi,typeofaid,aids_name,virtual,lon,lat,country_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
    "dynamic_sar": "INSERT INTO dynamic_sar(timestamp, mmsi,altidute,speedoverground,courseoverground,lon,lat,country_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
    "dynamic_voyage": "INSERT INTO dynamic_voyage(timestamp,mmsi,country_code,imo,callsign,shipname,shiptype,to_bow,to_stern,to_starboard,to_port,eta,draught,destination,mothershipmmsi)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
}

meta_data_statements = {
    "ship_types_detailed": "INSERT INTO ship_types_detailed(id_detailedtype, detailed_type,id_shiptype) VALUES (%s,%s,%s)",
    "navigational_status": "INSERT INTO navigational_status(status, description) VALUES (%s,%s)",
    "mmsi_codes": "INSERT INTO mmsi_codes(mmsi_prefix, country) VALUES (%s,%s)",
    "aton_type": "INSERT INTO aton_type(code,nature,definition) VALUES (%s,%s,%s)",
    "ship_types": "INSERT INTO ship_types(id_shiptype,shiptype_max,shiptype_min,type_name,ais_type_summary) VALUES (%s,%s,%s,%s,%s)",
}
