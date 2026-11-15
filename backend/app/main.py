import os
from typing import Annotated, Literal
from fastapi import FastAPI, Path, HTTPException, status
import psycopg
from pydantic import BaseModel, Field


app = FastAPI()

connection_params = {
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD")
}


class Location(BaseModel):
    name: str = Field(title="The title of the location", max_length=255)


class Substation(BaseModel):
    location_id: int
    name: str = Field(title="The title of the substation", max_length=255)


class Device(BaseModel):
    substation_id: int
    name: str = Field(title="The title of the device", max_length=255)
    type: Literal["meter"] = Field(
        default="meter", title="The type of the device", description="Now available only 'meter'"
    )
    status: Literal["active", "inactive"]


@app.get("/health")
def backend_health():
    return {"backend-service": "Success"}


@app.get("/health/db")
def check_database_health():
    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT current_database()""")
            database_info = cur.fetchone()

    return {"database": database_info[0]}


@app.post("/locations", status_code=status.HTTP_201_CREATED)
def create_location(location: Location):
    query = """
        INSERT INTO locations (name)
        VALUES (%s)
        RETURNING id
    """
    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, (location.name,))
                row = cur.fetchone()
            except psycopg.errors.CheckViolation:
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid values have been entered."
                )

            return {"id": row[0]}


@app.post("/substations", status_code=status.HTTP_201_CREATED)
def create_substation(substation: Substation):
    query = """
        INSERT INTO substations (location_id, name)
        VALUES (%s, %s)
        RETURNING id
    """
    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, (substation.location_id, substation.name,))
                row = cur.fetchone()
            except psycopg.errors.ForeignKeyViolation:
                raise HTTPException (
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The specified location_id does not exist."
                )
            except psycopg.errors.CheckViolation:
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid values have been entered."
                )

            return {"id": row[0]}


@app.post("/devices", status_code=status.HTTP_201_CREATED)
def create_device(device: Device):
    query = """
        INSERT INTO devices (substation_id, name, type, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, (
                        device.substation_id,
                        device.name,
                        device.type,
                        device.status,
                    )
                )
                row = cur.fetchone()
            except psycopg.errors.ForeignKeyViolation:
                raise HTTPException (
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The specified substation_id does not exist."
                )
            except psycopg.errors.CheckViolation:
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid values have been entered."
                )

            return {"id": row[0]}


@app.get("/devices/{device_id}")
def get_device(device_id: Annotated[int, Path(title="The ID of the device to get")]):
    query = """
        SELECT substation_id, name, type, status
        FROM devices
        WHERE id = %s
    """
    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (device_id,))
            row = cur.fetchone()

            if row is None:
                raise HTTPException (
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Device not found."
                )

            return {"substation_id": row[0], "name": row[1], "type": row[2], "status": row[3]}
