import sys

import sqlalchemy
import sqlalchemy.orm

sys.path.append(".")


def foo():
    print('bar')


def reflect_column(c: sqlalchemy.sql.schema.Column,
                   session: sqlalchemy.orm.Session):
    print('---------', c, c.foreign_keys, c.primary_key, c.default, c.index,
          c.server_default)
    print('desc=', c.desc)
    print('description=', c.description)
    print('comment=', c.comment)
    print('doc=', c.doc)
    print('expression=', c.expression)


def reflect_table(table: sqlalchemy.sql.schema.Table,
                  session: sqlalchemy.orm.Session):
    print("##########", type(table), table, session.query(table).count())
    for c in table.columns:
        reflect_column(c, session)


if __name__ == '__main__':
    engine = sqlalchemy.create_engine(
        'mysql+pymysql://root:lt7116@127.0.0.1/ittask?charset=utf8mb4',
        echo=False, isolation_level='READ_COMMITTED')
    metadata = sqlalchemy.MetaData(engine, reflect=True)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()

    # do database inspection
    for table_name in metadata.tables:
        print(type(table_name), table_name)
        table = metadata.tables[table_name]
        reflect_table(table, session)
