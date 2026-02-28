from datetime import datetime

from sqlalchemy import Integer, create_engine, select as sqlalchemy_select, \
    update as sqlalchemy_update, delete as sqlalchemy_delete, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker, declared_attr
from sqlalchemy.sql.functions import now

from config import settings


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, sort_order=-1)

    @declared_attr
    def __tablename__(cls):
        name = cls.__name__[0].lower()

        for i in cls.__name__[1:]:
            if i.isupper():
                name += '_' + i.lower()
            else:
                name += i

        if name.endswith('y'):
            name = name[:-1] + 'ie'
        return name.lower() + 's'


class Database:

    def __init__(self):
        self._engine = None
        self._session = None

    def init(self):
        self._engine = create_engine(settings.postgresql_url)
        self._session = sessionmaker(self._engine, expire_on_commit=False)()

    def __getattr__(self, item):
        return getattr(self._session, item)

    def create_all(self):
        Base.metadata.create_all(self._engine)

    def drop_all(self):
        Base.metadata.drop_all(self._engine)


db = Database()
db.init()


class AbstractClass:
    @classmethod
    def commit(cls):
        try:
            db.commit()
        except Exception:
            db.rollback()

    @classmethod
    def create(cls, **kwargs):
        _obj = cls(**kwargs)
        db.add(_obj)
        cls.commit()
        return _obj

    @classmethod
    def bulk_create(cls, items: list):
        obj_list = []
        for item in items:
            obj_list.append(cls(**item))
        db.add_all(obj_list)
        cls.commit()

    @classmethod
    def get_all(cls):
        query = sqlalchemy_select(cls).order_by(cls.id.desc())
        db.expire_all()
        results = db.execute(query)
        return results.scalars()

    @classmethod
    def first(cls):
        query = sqlalchemy_select(cls).order_by(cls.id.desc())
        db.expire_all()
        results = db.execute(query)
        return results.scalar()

    @classmethod
    def get(cls, _id):
        query = sqlalchemy_select(cls).where(cls.id == _id)
        db.expire_all()
        results = db.execute(query)
        return results.scalar()

    @classmethod
    def update(cls, _id, **kwargs):
        query = sqlalchemy_update(cls).where(cls.id == _id).values(**kwargs).returning(cls)
        new_obj = db.execute(query)
        cls.commit()
        db.expire_all()
        return new_obj.scalar()

    @classmethod
    def delete(cls, _id):
        query = sqlalchemy_delete(cls).where(cls.id == _id).returning(cls)
        new_obj = db.execute(query)
        cls.commit()
        db.expire_all()
        return new_obj.scalar()

    @classmethod
    def truncate(cls):
        query = sqlalchemy_delete(cls).returning(cls)
        new_obj = db.execute(query)
        cls.commit()
        return new_obj.scalars()

    @classmethod
    def filter(cls, *conditions, **kwargs):
        """
        Filter records by conditions or keyword arguments.
        Example:
            User.filter(User.age > 21, is_active=True)

            # Get all active users
            users = User.filter(is_active=True)

            # Get users older than 30
            users = User.filter(User.age > 30)

            # Combine both
            users = User.filter(User.age > 30, is_active=True)
        """
        query = sqlalchemy_select(cls)

        # Handle explicit conditions (like User.age > 21)
        if conditions:
            for cond in conditions:
                query = query.where(cond)

        # Handle keyword filters (like is_active=True)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.where(getattr(cls, key) == value)

        db.expire_all()
        results = db.execute(query)
        return results.scalars()


class Model(AbstractClass, Base):
    __abstract__ = True


class CreatedBaseModel(Model):
    __abstract__ = True
    updated_at: Mapped[datetime] = mapped_column(DateTime, insert_default=now(), server_onupdate=now(), sort_order=99)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=now(), sort_order=100)
