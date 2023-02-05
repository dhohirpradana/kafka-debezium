# TUTORIAL KAFKA DEBEZIUM MYSQL (INDONESIAN)

Debezium Repository
https://repo1.maven.org/maven2/io/debezium/

Debezium Plugins
https://debezium.io/releases/1.8/

Tutorial ini akan melakukan hands on bagaiman perubahan data di database dapat di streaming dengan mudah ke [Apache Kafka](https://kafka.apache.org/) dengan munggunakan konektor dari [Debezium](https://debezium.io).
Contoh use casenya adalah pembayaran via virtual account, dimana data akan berubah ketika ada perubahan saldo. perubahan row data ini kemudian distream ke kafka untuk diproses notifikasinya.

## 0. Instal Mysql di docker pakai sample yang sudah ada datanya & konfigurasi binlog CDC
```
> docker run -it --name mysqldbz -p 3306:3306 -e MYSQL_ROOT_PASSWORD=debezium -e MYSQL_USER=mysqluser -e MYSQL_PASSWORD=mysqlpw debezium/example-mysql:0.5

> docker exec -it mysqldbz /bin/bash

> more /etc/mysql/conf.d/mysql.cnf

log_bin           = mysql-bin
expire_logs_days  = 1
binlog_format     = row
```
> Note: bin log digunakan untuk mengambil change data capture (CDC) dari mysql. Defaultnya di disable untuk log_bin

## 1. Download kafka & extract
```
> wget https://www.apache.org/dyn/closer.cgi?path=/kafka/2.4.1/kafka_2.12-2.4.1.tgz
> tar -xzf kafka_2.12-2.4.1.tgz
```
## 2. Masuk ke folder kafka & create directory konektor
```
> cd kafka_2.12-2.4.1
> mkdir connect
> cd connect
```

## 3. Download debezium connector untuk mysql to kafka
```
> wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/0.8.3.Final/debezium-connector-mysql-0.8.3.Final-plugin.tar.gz
```

## 4. Extract debezium connector
```
> tar -xzf debezium-connector-mysql-0.8.3.Final-plugin.tar.gz
```

## 5. Copy file distributed.properties jadi debezium.properties di folder config
```
> cd ../config
> cp connect-distributed.properties debezium.properties
```

## 6. Edit file debezium.properties masukkan, tambahkan plugin.path untuk Debezium connector
```
> vim debezium.properties
        plugin.path=$KAFKA_HOME/connect
```
## 7. Start Zookeeper, Kafka, Connector REST API server
```
>cd $KAFKA_HOME
>bin/zookeeper-server-start.sh config/zookeeper.properties
>bin/kafka-server-start.sh config/server.properties
>bin/connect-distributed.sh config/debezium.properties
```
> Note: connect distributed akan membuka port 8083 untuk REST API registrasi konektor

## 8. Mendaftarkan konfigurasi debezium konektor via Rest API
POST localhost:8083/connectors
body=
```
{
  "name": "inventory-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "localhost",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.server.id": "184054",
    "database.server.name": "dbserver1",
    "database.whitelist": "inventory",
    "database.history.kafka.bootstrap.servers": "localhost:9092",
    "database.history.kafka.topic": "schema-changes.inventory"
  }
}
```
atau:
```
> curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{ "name": "inventory-connector", "config": { "connector.class": "io.debezium.connector.mysql.MySqlConnector", "tasks.max": "1", "database.hostname": "mysql", "database.port": "3306", "database.user": "debezium", "database.password": "dbz", "database.server.id": "184054", "database.server.name": "dbserver1", "database.whitelist": "inventory", "database.history.kafka.bootstrap.servers": "kafka:9092", "database.history.kafka.topic": "dbhistory.inventory" } }'

```
Cek Topik yang terbuat
```
> bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```
Result:
```
dbserver1
dbserver1.inventory.customers
dbserver1.inventory.orders
dbserver1.inventory.products
dbserver1.inventory.products_on_hand
mytopic
schema-changes.inventory

```


## 9. coba! ubah data di table inventory.customers 
```
UPDATE `inventory`.`customers`
SET
    `last_name` = 'Paijon'
WHERE
    `id` = 1003
```
result:

cek di topik = dbserver1.inventory.customers
```
....
"payload": {
		"before": {
			"id": 1003,
			"first_name": "Edward",
			"last_name": "Walker",
			"email": "ed@walker.com"
		},
		"after": {
			"id": 1003,
			"first_name": "Edward",
			"last_name": "Paijon",
			"email": "ed@walker.com"
		},
....
```
