import json
import bottle
from bottle import route, run, request, abort
from bson.objectid import ObjectId
import pymongo

connection = pymongo.MongoClient()
db = connection.log


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@route('/monitors', method='GET')
def get_document():
    entity = db['mon_col'].find()
    if not entity:
        abort(404, 'No document with id %s' % id)
    final = []
    for i in entity:
    	res = JSONEncoder().encode(i)
	final.append(res)
    return final

@route('/servers', method='GET')
def get_document():
    entity = db['ser_col'].find()
    if not entity:
        abort(404, 'No document with id %s' % id)
    final = []
    for i in entity:
    	res = JSONEncoder().encode(i)
	final.append(res)
    return final

@route('/vservers', method='GET')
def get_document():
    entity = db['vser_col'].find()
    if not entity:
        abort(404, 'No document with id %s' % id)
    final = []
    for i in entity:
    	res = JSONEncoder().encode(i)
	final.append(res)
    return final

@route('/services', method='GET')
def get_document():
    entity = db['svc_col'].find()
    if not entity:
        abort(404, 'No document with id %s' % id)
    final = []
    for i in entity:
    	res = JSONEncoder().encode(i)
	final.append(res)
    return final
    
run(host='10.0.3.2', port=8081)
