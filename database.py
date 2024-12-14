from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util import inject_docstring_text

#Database info for PostgreSQL
user = 'postgres'
password = 'Sqlroot'
host = 'localhost'
port = '5432'
database = 'todo_list'

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    tid = Column("tid", Integer, primary_key=True)
    title = Column("title", String)
    content = Column("content", String)
    status = Column(Integer, ForeignKey("status.sid"))

    def __init__(self, tid, title, content, status):
        self.tid = tid
        self.title = title
        self.content = content
        self.status = status

    def __repr__ (self):
        return f"({self.tid}) {self.title} {self.content} {self.status}"

class Status(Base):
    __tablename__ = "status"

    sid = Column("sid", Integer, primary_key=True)
    state = Column("state", String)

    def __init__(self, sid, state):
        self.sid = sid
        self.state = state

    def __repr__(self):
        return f"({self.sid}) {self.state}"

connection_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_str, echo = True)
#create all class into tables
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

ttrue = Status(1, "True")
ffalse = Status(2, "False")

task01 = Task(69, "py proyect", "Make the python TODO list proyect", 2)

session.add(ttrue)
session.add(ffalse)
session.add(task01)
session.commit()

