-----------------------------------------------------------------------------------------------------
-- Object : AIS Status, Codes and Types
-- File name : MMSI_Country_Codes.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v1 (21/09/2016)
-- SRID : NA
-- Coverage : NA
-- Volume : 281 codes
-- Period : NA
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains country codes corresponding to the first 3 digits of ship's identifier (MMSI). The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute				Data type		Description
-----------------------------------------------------------------------------------------------------
*  mmsi_country_code	integer  		Possible prefix of MMSI identifiers
*  Country 		    	text        	Name of the country (a country can have several prefixes)

** mmsi_country_code correspond to the first 3 values of an MMSI

-----------------------------------------------------------------------------------------------------
-- Object : AIS Status, Codes and Types
-- File name : ATON.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v1 (16/02/2017)
-- SRID : NA
-- Coverage : NA
-- Volume : 32 codes
-- Period : NA
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains Aid TO Navigation codes. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute		Data type		Description
-----------------------------------------------------------------------------------------------------
*  Nature		    Text			text  	    Nature of the ATON (nothing, fixed or floating)
*  Code 		    Integer			text        Unique identifier of the ATON
*  Definition 		Text			text        Gives the type of the aid to navigation

** code is linked to code field (second one) in nari_dynamic_aton.csv
** ATON = Aid TO Navigation. 


-----------------------------------------------------------------------------------------------------
-- Object : AIS Status, Codes and Types
-- File name : Navigational Status.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v1 (16/02/2017)
-- SRID : NA
-- Coverage : NA
-- Volume : 16 codes
-- Period : NA
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains text-based navigational status used by AIS dynamic data. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute		Data type		Description
-----------------------------------------------------------------------------------------------------
*  code			Integer			Unique identifier of the navigational status
*  status		Text			Detailed description of the status

** code is linked to "status" field in nari_dynamic_2017.csv


-----------------------------------------------------------------------------------------------------
-- Object : AIS Status, Codes and Types
-- File name : Ship Types List.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v1 (16/02/2017)
-- SRID : NA
-- Coverage : NA
-- Volume : 38 codes
-- Period : NA
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains text-based ship types as described in AIS specifications and used in AIS dynamic data. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute			Data type		Description
-----------------------------------------------------------------------------------------------------
*  id_shiptype		Integer			Unique identifier of the record
*  shiptype_min		Integer			min value of the given shiptype	
*  shiptype_max		Integer			max value of the given shiptype	
*  type_name 		Text			type name
*  ais_type_summary	Text			AIS summary of the given type

** id_shiptype is linked to id_shiptype field in Ship Types Detailled List.csv
** the range "shiptype_min - shiptype_max" coresponds to "shiptype" in nari_ais_static_2017.csv and in imis_ais_static_2016.csv


-----------------------------------------------------------------------------------------------------
-- Object : AIS Status, Codes and Types
-- File name : Ship Types Detailled List.csv
-- Source : Naval Academy, France (ecole-navale.fr) based on https://help.marinetraffic.com/hc/en-us/articles/205579997-What-is-the-significance-of-the-AIS-Shiptype-number-
-- Dataset version : v1 (16/02/2017)
-- SRID : NA
-- Coverage : NA
-- Volume : 233 codes
-- Period : NA
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains (detailled) text-based ship types. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute			Data type		Description
-----------------------------------------------------------------------------------------------------
*  id_detailedtype	Integer 		Unique identifier of the record
*  detailed_type	Text			Detailed description of the given type
*  id_shiptype		Integer 		coresponds to "id_shiptype" filed in Ship Types List.csv

** This table gives all the details that can corespond to the given shiptype
