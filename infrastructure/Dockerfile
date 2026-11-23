FROM apache/iceberg-rest-fixture:1.10.1

ADD --chmod=644 https://jdbc.postgresql.org/download/postgresql-42.7.14.jar /usr/lib/iceberg-rest/postgresql.jar

CMD ["java", "-cp", "iceberg-rest-adapter.jar:postgresql.jar", "org.apache.iceberg.rest.RESTCatalogServer"]