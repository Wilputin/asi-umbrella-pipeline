# AIS Umbrella pipeline



Päätin nyt laittaa dokumentaation suomeksi. Hyvää harjoitusta kun aikamonta vuotta ollut työkieli englantina
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

Äsken mainitetut pipeline podit (mainittiin nimeltä sujuissa) on myös mainittu ehdotuksessa
lopullisen tuotteen arkkitehtuurista (joka on hieman keskeneräinen). Arkkitehtuuri löytyy 

kansion docs/ sisältä tämän projektin juuresta


# Alkusanat

en ole varma menikö tämä projekti nyt yli tai ali. Teinköhän asiat mitä pyydettiin. Toivottavasti tein.
Innostuin ehkä liikaa yrittää seurata mahdollista "todellista arkkitehtuuria" että olisin voinut tehdä
tuosta querybuilderista hieman siistimmä/kyvykkäämän. Noh ensi kerralla sitten...

Tarkoituksenani oli aluksi tehdä tämä software engineerin tehtävä. Jota aloitinkin. Tein kansiorakenteet. routerin
Dockerfilet yms. Sain boilerprate projektin toimimaan kivasti. Mutta 19.3 sain vain ajatuksen että ehkä minun kannattaisi tehdä tämä pipeline projekti ja liittää
tämä Api applikaatio siihen. En kyllä saisi Api-applikaatiosta valmista, mutta tähtäisin siisteyteen ja maintabilityyn
koko projektin sisällä. Niin toivottavasti se riittäisi vaikka en pääsisi ihan täydellistä softa arkkitehtuuria tekemään.

halusin vain hieman näyttää MYÖS kokemustani pipelinen rakentamisessa. Koin että "pelkästään" (en tarkoita että olisi super helppo) API-applikaation tekeminen
ei näyttäisi ihan kaikkea.

Tähtäsin tässä siisteyteen. hyvään kansiorakenteeseen. Maintanabilityyn ja että joku muukin voisi
tajuta miten esimerkiksi DbDriverin kyvykkyyksiä laajennetaan helposti. Noh katsotaan mitä mieltä olette

# Miten testata tätä

ENSIKSI: Koska github tappelee filukokojen kanssa valitettavasti tajusin tämän liian myöhään niin en nyt saanut tähän hienostuneempaa ratkaisua
pahoittelut

jos katsotte kansiota polussa

/pipeline/data/add_files_here.txt

annetaan kuvaus mitkä tiedostot millä nimellä tarvitaan tähän kansioon että pipeline toimii

toivotaan että tästä ei tule "it works on my machine"

1. projektin juuressa syötä terminaaliin
    ./deployment.sh
    - sitä ennen jos haluat testata pienemmällä datamäärällä voit muuttaa sitä
   pipeline/configuration_compose.yaml tiedoston kautta
   

        #MUUTA messa_size kenttää haluaamaasi suuntaan muuttakseksi kafka topicciehin työnnettämän datan määrää
        - name: data_puller
          active: True
          config:
            connection_config:
              message_size: 0.2 # 1.0 means 100% of data -> 0.5 is 50% etc. relevant only for kafka
              localhost: False
              compose: True
              use_kafka: True

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
| data_analytics  | perusanalyysit striimausdatan frekvensseistä                                                         |
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


Mitä se tekee:

    1. CSV-tiedostot liitetään konttiin volyymin kautta
    2. Kafka-topicit luodaan CSV-tiedostojen nimien perusteella
    3. CSV:t muunnetaan dataframeiksi. Niiden viestityyppi liitetään mukaan payloadiin
    4. MMSI:n perusteella haetaan maan tunnus ja lisätään payloadiin
    5. Käännetään nan arvot noneiksi
    5. Dataframe muunnetaan JSON-muotoon ja lähetetään Kafkaan asynkronisina tehtävinä
    6. Jos use_kafka flagi = False niin data tallennetaan src/kafka_data/topic_nimi.json tiedostopolkuun 

Laajentaminen:

pääasiallinen prosessointi tapahtuu tässä funktiossa. Toiminallisuuksien lisääminen 
tähän lisää prosseointia:

        async def processing_pipeline(self, data: str) -> pd.DataFrame:
        filepath = self.data_source / f"{data}.csv"
        df = pd.read_csv(filepath)
        if "ts" in df.columns:
            df.rename(columns={"ts": "t"}, inplace=True)
        df.sort_values(by="t", inplace=True, ascending=True)
        processed_df = self.divide_mmsi_and_country_code(df)
        message_type = self.message_map.get_message_key_by_table(data)
        processed_df["message_type"] = [message_type for _ in range(len(processed_df))]
        processed_df.reset_index(inplace=True, drop=True)
        return processed_df

# Things to do

dataa pitäisi hieman ymmärtää lisää että mitkä olisivat kaikista järkevimpiä primary keytä 
taualuhin. Ainakin voyage datassa tulee paljon unique key violationeita. en ole siihen perehtynyt hirveän
orjallisesti nyt

Voluumien hoito/sijainti. Imagessa taitaa nyt olla sisällä leivottu hieman metadataa yms. Ei hyvä pitäisi ne korjata

Kafka configuraatioiden saaminen configuration.yamliin että niiden kanssa voisi vähän optimoida putken suoritusta

Poistin viimeisinä tekoinan dynamic_voyage taulun primary keyn koska ärsytti ainaiset duplicate hälytykset. En ymmärrä datasta tarpeeksi että kannattaisiko tällä
olla edes primary keytä. Eli tuleeko samalla sekunnilla samalle vesselille useita voyage viestejä.

 
# Kohti valmista tuotetta


Olen hieman biased teknologia valinnoissani sillä näillä nyt olen työskennellyt.

Konttien orkestrointi → Kubernetes
Docker → konttien luomiseen ja ajamiseen (konttienhallinta, ei orkestrointi)
Kubernetes → konttien orkestrointiin ja käyttöönottoon (deployment)

src code kielet
Pipeline konttien valittu src kieli voisi olla Forecastingia ja anomaly detectionia tekevissä podeissa
Python. Mielestäni paras kieli tälläiseen työhön.
Muussa tapauksessa voitaisiin harkita Java/Scala kieliä jotka pelaavat vahvasti Kafkan kanssa

Muut palvelut:
    Tech stackeissänne mainittiin Spark. Mutta kokisin ettää perustuen data_analytics/
    tuloksiin data määrän olevan turhan pieni että olisi oikeutettu käyttämään Sparkkia. Voin olla
    toki väärässä datamäärä olettamastani. jos olen tehnyt kohtalokkaan virhen koodissani.
    Muussa tapauksessa mielestäni pärjäisi hyvin omalla kafka työkaluilla


