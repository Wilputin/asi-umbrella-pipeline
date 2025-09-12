# AIS Umbrella pipeline


Tämä repo demoaa merelle kulkevien laivojen ASI-viestien datan kulkemista
ETL putken läpi lopulta tietokantaan ja sen saman datan kyselyä querylla apin kautta tietokannasta.

Repon on tarkoitus antaa kosketusrajanpinta mahdolliseen arkkitehtuurin ja ratkaisuihin
eikä toimi valmiina production ready ratkaisuna.

Tarkoitus on näyttää ymmärrystä dataputkien rakentamista kokonaisvaltaisesti kuin keskittyä
yhteen palveluun.

# Miten ajaaa

projektin juuressa terminaalissa ajamalla ./deployment.sh


# Mitä tämä projekti tekee

./deployment.sh ajamalla 
1. pystytetään asi-db joka hoitaa scheman luonnin annetun metadatan mukaan sekä luo taulut streamaus datalle joka odotetaan tulevan
putkessa myöhemmin
2. sen jälkeen pystytetään kafka/zookeeper/akhq kontit topiccien luontiin ja datan streamaukseen
3. Kaikki kontit keskustelevat keskenäänin asi_network sisällä
4. sen jälkeen pipeline pyöräytetään pystyyn joka; 
    - ingestoi metadatat db:n jonka jälkeen (meta_ingestion)
    - prosessoi streamausdatan topicceihin (data_puller)
    - hakee datan topiceista ja kirjoittaa ne tauluihin (data_writer)
    - avaa portin API kutsuja varten localhost:5000 rajapinnassa (asi-api)

tämän jälkeen käyttäjä voi testata eri queryja ajamalla ./query_data.sh

pipeline/src/pipeline sisällä sijaitseva arkkitehtuuri selitettynä.

kansion juuressa sijaitsee 
    dependencies
        edustaa erilaisia kirjastoja jotka sijaitsevat imagena palvelun ulkopuolella
        base-app. Edustaa ETL putken palveluiden yhtenäistä applikaatio arkkitehtuuria
            tarjoaa esim yhtenäisen loggerin ja applikaatio ajo rakenteen
        data_process -> tarjoaisi mahdollisia yhteisiä staattisia funktioita datan processoiintiin
        decoder -> yhtenäinen logiikka kafka viestien purkamiseen
        driver - > database driver kannan kansssa keskusteluun
        models -> etl putkessa kulkevien dataputkein mallien hallinta
    pods
        edustaa erillisiä applikaatio podeja 
        asi-api -> api service UI:n ja kannan kanssa keskusteluun
        data-puller -> palvelu jonka tarkoituksena on ottaa dataa ulkoisesta lähteestä ja syöttää se sisäiseen ETL putkeen
        data-writer -> eudstaa kanta kirjoitus palvelua joka ottaa datan topicista
        meta-ingestion -> edustaa jobina ajettavaa palvelua metadatan ingestoimiseen kantaan

1. projektin juuressa syötä terminaaliin
    ./deployment.sh
    - sitä ennen jos haluat testata pienemmällä datamäärällä voit muuttaa sitä
   pipeline/configuration_compose.yaml tiedoston kautta

2. tämän pitäisi pystyttää järjestyksessä
    - database
    - kafka/zookeeper/akhq
    - pipeline
3. Akhq on exposattu localhostille portille 8080. Pääset katsomaan topicceja silloin osoitteesta
    - "http://localhost:8080"
   
3. Pipeline ajetaan singleshot moduliina paitsi. asi-api palvelu
muiden moduulien ajamisen jälkeen asi-api jää pyörimään. asi-api on exposattu localhostille portille 5000 
ja voit curlata siihen kun data on ingestattu 

4. projektin juuressa syöttämällä
./query_data.sh

5. Voit muutta haluamasi parametreja curlauksessa. Koita rikkoa se. Onnistut varmasti.


Tämä projekti koostuu seuraavista kansioista

| kansio/tiedosto | sisältö                                                                                              |
|-----------------|------------------------------------------------------------------------------------------------------|
| asi-db          | tietokannan schema.sql ja YAML-tiedosto kontin käynnistämistä varten                                 |
| docs            | ehdotettu arkkitehtuurikaavio lopulliselle tuotteelle ja parametrien kuvaukset striimaus- ja metadatalle |
| kafka_build     | docker_compose-tiedosto, jolla asennetaan kafka, zookeeper ja akhq sekä altistetaan portit 9092/29092 |
| pipeline        | putken lähdekoodi. Sisältö selitetään tarkemmin alla                                                |
| deployment.sh   | funktiot verkon/tietokannan asettamiseen ja putken suorittamiseen datan sisäänlukua varten          |
| query_data      | funktio datan hakemiseen curlilla asi-api-palvelusta (putken ajamisen jälkeen)                      |

# pipeline

kuvailen alla olevassa taulukossa hieman pipeline/ juuren kansiorakennetta

| kansio/tiedosto            | sisältö                                                                                                                                                      |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| data                       | streamaava data, joka pusketaan pipelinen alussa kafka topicciin ja syötetään lopussa DB:sen                                                                 |
| metadata                   | metadata, joka syötetään DB:en pipelinen alussa (meta-ingestion hoitaa)                                                                                      |
| src                        | pipelinen source koodi                                                                                                                                       |
| tests                      | sisältää yhden huikean testin queryn toteuttamiseen lokaalisti. Ei ajeta image buildissa. Olettaa että DB on pystyssä ja dataa on sisällä                    |
| configuration.yaml         | testaus konfiguraatio lokaaliin ajoon. Asettaa mitkä moduulit ovat aktiivisia ja käytätkö yhteyksissä localhost vai compose networkkia                       |
| configuration_compose.yaml | pipeline kontin pystytyksessä annetaan volumiina kontille nimellä -> configuration.yaml (sisältää saman periaatteen kuin juuressa oleva saman niminen .yaml) |
| docker-compose.yaml        | docker-compose                                                                                                                                               |
| Dockerfile                 | hoitaa imagen luonnin multi-stage buildina. Käytin tätä periaatetta kun ensimmäistä API-applikaatiota tein imagen koon minimoimiseen                         |
| lint.sh                    | ajaa linttaus moduulit poetryn kautta. Olettaa että olet ajanut jo lokaalisti poetry lock + poetry install                                                   |

tämä pipeline on rakennettu monoliitti kansiona devauksen helpottamiseksi mutta todellinen ratkaisu
tuskin sellainen olisi vaan jokainen moduuli/podi olisi oma imagensa

sitä yritin hakea src/ kansion alla olevasta kansiorakenteesta joka pitäisi kuvastaa hieman tätä ajatusta

src/pipeline/pods kansion alla pitäisi löytyä kaikki palvelut jotka ajattelin olla omia podejaan

src/pipeline/dependencies kansion alla pitäisi löytyä kaikki moduulit jotka ajattelin olla riippuvuksia jo
määrityille podeille


# Dependencies
Ajattelin tässä että kaikki dependencien sisällä ovat ulkoisia imageja ja podin riippuvat niiden tuomista malleista/rajapinnoista
esimerkiksi näin DbDriver olisi saatavilla keskitetysti monelle eri podille (asi-api + meta_ingestion esimerkiksi)

# Dependencies.base_app

Sisältää perusappi logikaan ja abstraktoidut kutsut jota kaikki pipelinen podit käyttävät
jos ETL pipeline tehdään olisi mielestäni loogista että kaikki toimivat aika samalla tavalla
vaikka nyt minun esimerkkini ei ole hirveän sivistynyt kaipa siitä perusidean saa haltuun

perusappi myös sisältäisi yhteisen loggerin. Eli devaaja ei siitä tarvitsisi miettiä vaan loggeri olisi
valmiiksi jo saatavilla

# Dependencies.decoder

Ajattelin että messge_decoder
olisi hyvä olla dependencynä kaikille ETL putken podeille ja ne decodaisivat ja handlaisivat kafka messageja samalla tavalla

Seuraavana on message_map joka mappaa viestityypin (onko se aton, sar,voyage, vessel etc) oikeaan
datamalliin (validointia varten) ja oikeaan DB taulun inserttiä varten.
Tämä itseasiassa pitäisi olla mielestäni data_writer podin sisällä

# Dependencies.driver

varmaan tärkein dependency ainakin tehtävän annon perusteella
db_driver.py:

    Sisältää driverin joka init vaiheessa ottaa Asyncconnectionpoolin itseensä ja pyyntöjen
    tullessa ottavat kutsut vapaista olevista connectioneista itselleen käyttöön ja käyttävät
    niitä statementtien toteuttamiseen

    sisältää kolme päämethodia

    async def insert_meta_data()
    async def insert_streaming_data()
    async def query_data()

query_builder.py:

    Sisältää SQL statementtien rakennus logiikan. Mahdollistaa helpon query rakennuksen ja mahdollisuuden
    helpon rajapinnan tarjoamiseen api-palvuille querien käyttöön

    sisältää query validoinnin ennen toteuttamista
table_info.py:

       Sisältää taulujen metatieto infoa query builderia varten. Sekä sisältää suoria insert 
        komentoja db_writerin kirjoittamis funktioita varten
# Dependencies.models

Tämä kansio sisältää pipelinen yleisesti käytössä olevat data mallit ja niiden keskitetyn Pydantic mallien validointi logiikan
jos kaikki ei ole järkevästi keskitetty Pydantic mallien validaatioon niin vakuutan että se oli tarkoitus

meta_models.py

        sisältää meta taulujen datamallit ja niiden validoinnin ennen insertoimista
wire_models.py
        
        sisältää streaming/dynamic taulujen datamallit ja niiden validoinnin ennen insertoimista
# Pods.Meta_ingestion
Tämä repo on nopea asennus tarjotun meta datan sisäänlukemiseen
ja kirjoittamiseen DB:hen

Mitä se tekee:

    1. CSV-tiedostot liitetään konttiin volyymin kautta
    3. CSV:t muunnetaan dataframeiksi.
    4. Dataframen rivit validoidaan pydantic mallien kautta ennen insertoimista DB:hen

# Pods.Data_puller
Tämä repo on nopea asennus tarjotun datan sisäänlukemiseen
data/-kansiosta Kafka-topiceihin. 


