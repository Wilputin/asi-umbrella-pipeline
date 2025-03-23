

# Purpose of this folder

this folder contains just a timestamp analysis of the dynamic data received to 
determine the frequence of the messages and do the timestamps come same time 
to multiple different vessels

this can determine little bit what we could in the pipeline

if the timestamps are similar for multiple vessels we could denormalize all 
messages corresponding with the timestamp to the same kafka messages and sent them in 
to our pipeline after datapuller

we would reduce little the needed in/out messaging.

Also the frequency is important to determine to now how much data is expected to flow
trough the system per hour for example
    - i expect a lot already
    
by the data streaming size we can determine the needed techs for the actual production
I would suspect spark is way to go if we are taking about vessel data for ALL the ships in
the world basically with 1s frequency
   - then distributed computing does really shine.

----------------------------------------------
after analytics

seems data freq is really low at least for some vessels

this coulde be done with simple kafka clients and spark feels like overkill