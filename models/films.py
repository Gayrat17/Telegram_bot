from sqlalchemy import String, Integer, ForewignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Model


class Film(Model):
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String, nullable=True)
    release_year: Mapped[int] = mapped_column(Integer, nullable=True)

    categories: Mapped[list["Category"]] = relationship("Category", secondary='film_categories', back_populates="films")

    def __str__(self):
        return f"{self.id} | {self.title}"


class Category(Model):
    name: Mapped[str] = mapped_column(String(255))

    films: Mapped[list["Film"]] = relationship("Film", secondary='film_categories', back_populates="categories")

    def __str__(self):
        return f"{self.id} | {self.name}"


class FilmCategory(Model):
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    __table_args__ = (
        UniqueConstraint("film_id", "category_id"),
    )

    def __str__(self):
        return (self.film_id, self.category_id)
