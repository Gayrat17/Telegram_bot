from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from models.base import Model


class Region(Model):
    name: Mapped['str'] = mapped_column(String(255))

    def __str__(self):
        return str(self.name)


class District(Model):
    name: Mapped['str'] = mapped_column(String(255))
    region_id: Mapped['int'] = mapped_column(ForeignKey("regions.id"))