/*
 please refer to /docs
 for original data parameters
 */


/*
  first we create metadata tables that are not planned to be updated constantly but their
  contained information should be migrated on start of the pipeline.

  below this markings contains the metadata tables
  /////////////////////////////////////////////////////////////////////////////////////////////

  This table maps navigation status and their description.
  source -> Navigational Status.csv
  
  description from parameters.txt

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


*/
CREATE TABLE navigational_status(status INT PRIMARY KEY ,description TEXT NOT NULL);



/*
  This table maps ship type their description.
  this combines information from two different sources since they seemed nice to be normalized for single
  table
  source -> Ship Types Detailed List.csv + Ship Types List.csv
  
  description from parameters.txt
  
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
*/

CREATE TABLE ship_types(id_shiptype INT PRIMARY KEY,shiptype_max INTEGER NOT NULL, shiptype_min INTEGER NOT NULL, type_name TEXT, ais_type_summary TEXT);



/*
  This table maps detailed ship types.

  source -> Ship Types Detailed List.csv 
  
     example/ ship type detailed 
    id_detailedtype,detailed_type,id_shiptype
    1,Wing In Ground Effect Vessel,2
    
    description from parameters.txt
    
    
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
*/
CREATE TABLE ship_types_detailed(id_detailedtype INT PRIMARY KEY , detailed_type TEXT, id_shiptype INT REFERENCES ship_types(id_shiptype) ON UPDATE CASCADE);

/*s
  This table maps aton code number to their nature and defintion
    nature and definion can be null
  source -> ATON.csv
  
  description from the parameters.txt

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


*/
CREATE TABLE aton_type(code INT PRIMARY KEY,nature TEXT,definition TEXT);

/*
   This table maps mmsi code and their respective country
   MMSI Codes are usually 9(? not sure) digits long and first three numbers
   represent the origin country code
   source -> MMSI Country Codes.csv
 */

CREATE TABLE mmsi_codes(mmsi_prefix INT PRIMARY KEY,country TEXT NOT NULL);


/*
here ends metadata tables
--------------------------------------------------------------------------------------------------------------------------------------------
below we create normalized tables for each message type. Data to these tables
should writen in realtime

*/

/*
   This table represents incoming dynamic vessel data
   source -> dynamic_vessel_data.csv

   primary keys for this data is the timestamp -> converted to utc ISO datetime
   AND the MMSI code for the message (the country prefix is removed from the mmsi)

   note: country prefix is disected by the pipeline and inserted in to its own column country_codes
   this is repeated for

   dynamic_aton_data
   dynamic_sar_data

   otherwise we would need to disect it upon query to get the origin country of the message
   (if i have understood the documentation correctly)

 */
 
CREATE TABLE dynamic_vessel(timestamp TIMESTAMP NOT NULL,mmsi INTEGER,navigational_status INT REFERENCES navigational_status(status) ON UPDATE CASCADE , rateofturn FLOAT, speedoverground FLOAT, courseoverground FLOAT, trueheading FLOAT, lon FLOAT, lat FLOAT,country_code INT, PRIMARY KEY (timestamp, mmsi));
 
 
 
/*

	this data represeent dynamic aton data received as streaming data from the ETL pipeline
   example/

   sourcemmsi,typeofaid,aidsname,virtual,lon,lat,t
992271015,6,FEU MILLIER,f,-4.4656634,48.098763,1443650415


description from the parameters



 */
 
 
CREATE TABLE dynamic_aton(timestamp TIMESTAMP NOT NULL,mmsi INTEGER NOT NULL,typeofaid INT REFERENCES aton_type(code) ON UPDATE CASCADE ,aids_name TEXT,virtual TEXT, lon FLOAT, lat FLOAT, country_code INT);


/*

	this data represeent dynamic aton data received as streaming data from the ETL pipeline
   example/

sourcemmsi,altitude,speedoverground,courseoverground,lon,lat,ts
2115,943,222,281.8,-3.0043533,46.860394,1443688426

 */

CREATE TABLE dynamic_sar(timestamp TIMESTAMP NOT NULL,mmsi INTEGER NOT NULL,altidute INT NOT NULL, speedoverground FLOAT, courseoverground FLOAT,lon FLOAT, lat FLOAT, country_code INT);



/*

	this data represeent dynamic aton data received as streaming data from the ETL pipeline
   example/

sourcemmsi,altitude,speedoverground,courseoverground,lon,lat,ts
2115,943,222,281.8,-3.0043533,46.860394,1443688426



-----------------------------------------------------------------------------------------------------
-- Object : AIS Static Data (version 2)
-- File name : nari_ais_static.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v2 (31/05/2017)
-- SRID : NA 
-- Coverage : Longitude between -10.00 and 0.00 and Latitude between 45.00 and 51.00
-- Volume : 1.032.187 decoded static messages
-- Period : 6 months (2015-10-01 00:00:00 UTC to 2016-03-31 23:59:59 UTC)
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains static and voyage-related information collected by Naval Academy receiver. The file combines message types ITU 5, ITU 19, ITU 24. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute	Data type		Description
-----------------------------------------------------------------------------------------------------
*  sourcemmsi 	  integer         	MMSI identifier for vessel
*  imo 			  integer         	IMO ship identification number (7 digits); 
*  callsign 	  text            	International radio call sign (max 7 characters), assigned to the vessel by its country of registry
*  shipname 	  text            	Name of the vessel (max 20 characters)
*  shiptype 	  integer           Code for the type of the vessel (see enumeration)
*  to_bow 	  	  integer          	Distance (meters) to Bow
*  to_stern 	  integer         	Distance (meters) to Stern --> to_bow + to_stern = LENGTH of the vessel
*  to_starboard   integer      		Distance (meters) to Starboard, i.e., right side of the vessel --> to_port + to_starboard = BEAM at the vessel's nominal waterline
*  to_port 		  integer           Distance (meters) to Port, i.e., left side of the vessel (meters)  
*  eta 			  text            	ETA (estimated time of arrival) in format dd-mm hh:mm (day, month, hour, minute) – UTC time zone
*  draught 		  double precision  Allowed values: 0.1-25.5 meters
*  destination 	  text            	Destination of this trip (manually entered)
*  mothershipmmsi integer			Dimensions of ship in metres and reference point for reported position
*  t 			  bigint          	timestamp in UNIX epochs

** shiptype linked to the range shiptype_min to shiptype_max in "Ship Types List.csv"
** country name can be obtained through MMSI prefix which is linked to "MMSI Country Codes.csv"
*** callsign can be linked with IRCS in EU fleet register (EuropeanVesselRegister.csv )



 */
 
 CREATE TABLE dynamic_voyage(timestamp TIMESTAMP NOT NULL, mmsi INTEGER NOT NULL, country_code INT NOT NULL, imo INT, callsign TEXT, shipname TEXT,shiptype INT, to_bow INT, to_stern INT, to_starboard INT, to_port INT, eta TEXT, draught FLOAT, destination TEXT, mothershipmmsi INT);
