import asyncio,logging
import aiomysql

#创建连接池
@asyncio.coroutine
def create_pool(loop,**kw):
	logging.info('create database connection pool...')
	global __pool
	__pool=yield from aiomysql.create_pool(
		host=kw.get('host','localhost'),
		port=kw.get('port',3306),
		user=kw['user'],
		password=kw['password'],
		db=kw['db'],
		charset=kw.get('charset','utf-8'),
		autocommit=kw.get('autocommit',True),
		maxsize=kw.get('maxsize',10),
		minsize=kw.get('minsize',1),
		loop=loop
		)
#Select 要执行Select语句，我们用select函数执行，需要传入SQL语句和SQL参数
@asyncio.coroutine
def select(sql,args,size=None):
	log(sql,args)
	global __pool
	with (yield from __pool) as connection:
		cur=yield from conn.corsor(aiomysql.DictCursor)
		yield from cur.execute(sql.replace('?','%s'),args or())
		if size:
			rs=yield from cur.fetchmany(size)
		else:
			rs=yield from cur.fetchall()
		yield from cur.close()
		logging.info('rows returned:%s' % len(rs))
		return rs
#Insert、Update、Delete语句，统称execute()函数
@asyncio.coroutine
def execute(sql,args):
	log(sql)
	with(yield from __pool) as conn:
		try:
			cur=yield from conn.cursor()
			yield from cur.execute(sql.replace('?','%s'),args)
			affected=cur.rowcount
			yield from cur.close()
		except BaseException as e:
			raise
		return affected

#ORM
from ORM import Model,StringField,IntegerField

class User(Model):
	__table__='users'

	id=IntegerField(primary_key=True)
	name=StringField()

#创建实例：
user=User(id=123,name='Michael')
#存入数据库后：
user.insert()
#查询所有User对象：
users=User.findAll()
