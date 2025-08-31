from sqlalchemy import Table, Column, String
from database.db import metadata

users = Table(
    "users",
    metadata,
    Column("name", String(50)),
    Column("email", String(50), unique=True, nullable=False, index=True),
    Column("password", String),
    Column("role", String),
)
