from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StringType, LongType, IntegerType, DoubleType


spark = (
    SparkSession.builder.appName("KafkaEventsStreaming").getOrCreate()
)

events = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "broker-kafka:9092")
    .option("subscribe", "gridflow.telemetry.meters.v1")
    .option("startingOffsets", "earliest")
    .load()
)

schema = (
    StructType()
    .add("event_id", StringType())
    .add("schema_version", IntegerType())
    .add("device_id", LongType())
    .add("event_time", StringType())
    .add("ingest_time", StringType())
    .add("interval_kwh", DoubleType())
    .add("voltage_v", DoubleType())
    .add("current_a", DoubleType())
    .add("frequency_hz", DoubleType())
)

parsed = (
    events.select(from_json(col("value").cast("string"), schema).alias("data"))
    .select("data.*")
    .withColumn("event_time", to_timestamp(col("event_time"), "yyyy-MM-dd'T'HH:mm:ssXXX"))
    .withColumn("ingest_time", to_timestamp(col("ingest_time"), "yyyy-MM-dd'T'HH:mm:ssXXX"))
)

query = (parsed.writeStream
    .format("iceberg")
    .outputMode("append")
    .trigger(processingTime="15 seconds")
    .option("fanout-enabled", "true")
    .option("checkpointLocation", "s3a://gridflow/checkpoints/bronze_meter_readings")
    .toTable("bronze.meter_readings")
)

query.awaitTermination()
