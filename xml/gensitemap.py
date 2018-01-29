#!/usr/bin/env python

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.automap import automap_base
from contextlib import contextmanager
import sys
import xml.etree.ElementTree as ET
import ipdb


# Create Automap Base object
Base = automap_base()
# for engine creation, refer http://docs.sqlalchemy.org/en/latest/core/engines.html
print(sys.argv)

db_pwd = 'YFZhshAd6vZ5zRLn'
if len(sys.argv) > 1:
    db_pwd = sys.argv[1]

db_ip = '172.18.18.111'
if len(sys.argv) > 2:
    db_ip = sys.argv[2]

engine = sqlalchemy.create_engine('mysql://usroilup:' + db_pwd + '@' + db_ip + ':3306/oilup?charset=utf8mb4',
                                  echo=False, isolation_level='READ_COMMITTED')
# Using reflect for automap
Base.prepare(engine, reflect=True)

metadata = sqlalchemy.MetaData(engine)
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except (IOError, ValueError) as err:
        session.rollback()
        raise
    finally:
        pass


def control():
    # ipdb.set_trace()
    with engine.connect() as con:
        # 上架设备
        rs = con.execute(
            'SELECT g.goods_id from goods g where g.stock_state=0')
        goods = [str(row[0]) for row in rs.fetchall()]
        # print("goods id", goods)
        # 发布帖子
        rs = con.execute(
            'SELECT t.topic_id from topic t where t.is_private=0 and t.topic_state=1')
        topics = [str(row[0]) for row in rs.fetchall()]
        # print("topics id", topics)
        # 企业
        rs = con.execute(
            'SELECT org.organization_id  from organization org  where org.org_type = 8 and org.org_state= 3')
        orgs = [str(row[0]) for row in rs.fetchall()]
        # print("orgs id", orgs)
        # 用户
        rs = con.execute(
            'SELECT um.user_main_id from user_main um where um.user_main_id not in(1,2)')
        users = [str(row[0]) for row in rs.fetchall()]
        # print("users id", users)
        # parse template
        ET.register_namespace(
            '', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        tree = ET.parse('sitemap-template.xml')
        # add subelement
        root = tree.getroot()
        process(goods, root,
                'http://www.oilup.com/html/equimentdetails.html?id={0}')
        process(topics, root, 'http://www.oilup.com/html/details.html?id={0}')
        process(
            orgs, root, 'http://www.oilup.com/html/companyOilup.html?id={0}&type=2')
        process(users, root,
                'http://www.oilup.com/html/myOilup.html?id={0}&type=1')
        indent(root)
        tree.write('sitemap.xml', encoding='utf-8',
                   xml_declaration=True, method='xml')


def process(ids, root, url_prefix):
    for id in ids:
        url_element = ET.SubElement(root, 'url')
        loc = ET.SubElement(url_element, 'loc')
        loc.text = url_prefix.format(id)
        priority = ET.SubElement(url_element, 'priority')
        priority.text = '0.8'
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = ''
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = 'daily'


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return elem


if __name__ == '__main__':
    ''' do url generation
    '''
    control()
