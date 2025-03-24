# Things to do

pods:
    - parempi applikaatioiden kafka handlaus logiikka

kafka:
 - Kafka configuraatioiden saaminen configuration.yamliin että niiden kanssa voisi vähän optimoida putken suoritusta

pipeline.dependencies.driver.db_driver.py
    - Parempi error handlaus
    - koodiduplikaatioita
    - retry logiikka decoratorilla tai jollain muulla jos on DB:n kanssa ongelmia
    - kaikki queryt ja insertiot menisi query_builder.SQLQueryBuilder:in kautta
    - connection poolin parempi hallinta. milloin sulkea yms.
    - yksi testi tethy mutta parempi testaus rajapinta

data:
  - dataa pitäisi hieman ymmärtää lisää että mitkä olisivat kaikista järkevimpiä primary keytä 
    taualuhin. Ainakin voyage datassa tulee paljon unique key violationeita. en ole siihen perehtynyt hirveän
    orjallisesti nyt
