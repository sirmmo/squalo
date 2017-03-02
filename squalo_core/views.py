from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import *

from pysqlite2 import dbapi2 as sqlite3
import sys, traceback
import json, csv

def index(request):
	return render(request, "index.html", {"title":"Squalo SQLite Eater", "users":User.objects.all()})
	
def profile(request):
	return HttpResponseRedirect("/data/%s" % request.user.username)

def logout(request):
	from django.contrib.auth import logout as do_logout
	do_logout(request)
	return HttpResponseRedirect("/")

@csrf_exempt
@login_required 
def add_database(request):
	if request.method=="GET":
		return render(request, "upload.html", {"title":"Upload"})
	else: 
		try:
			d = Dataspace(
				owner = request.user,
				name = request.REQUEST.get("name"),
				sqlite_file=request.FILES["sqlite"])
			d.save()

			the_file = d.sqlite_file.path
			print the_file
			con = sqlite3.connect(the_file)
			con.enable_load_extension(True)
			cursor = con.cursor()
			spatialite_tables = ["SpatialIndex","sql_statements_log","virts_geometry_columns_auth","views_geometry_columns_auth","geometry_columns_auth","geometry_columns_time","virts_geometry_columns_field_infos","views_geometry_columns_field_infos","geometry_columns_field_infos","virts_geometry_columns_statistics","views_geometry_columns_statistics","geometry_columns_statistics","virts_geometry_columns","views_geometry_columns","geometry_columns","sqlite_sequence","spatialite_history","spatial_ref_sys",]
			for table in cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';"):
				if table[0] == "spatial_ref_sys":
					con.load_extension("/usr/lib/x86_64-linux-gnu/libspatialite.so.5.1.0")
					d.geo = True
					geo_magic = con.execute("select * from geometry_columns")
					d.save()
			for table in cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';"):
				m = Model()
				m.dataspace = d
				m.name = table[0]
				m.internal = d.geo and table[0] in spatialite_tables
				m.save()


				f_cursor = con.execute("select * from "+table[0])

				for field in f_cursor.description:
					f = Field()
					f.model = m
					f.name = field[0]
					if d.geo:
						for gcol in geo_magic:
							if m.name == gcol[0] and f.name == gcol[1]:
								f.geo = True
					f.save()

			return HttpResponseRedirect("/data/%s/%s" % (request.user.username, d.name))
		except Exception, e:
			return render(request, "upload.html", {"title":"Upload", "error":str(e)})

@login_required 
def delete(request, user, db):
	the_db = Dataspace.objects.get(owner = request.user, name=db)
	the_db.delete()
	return HttpResponseRedirect("/data/%s" % user)
	
@csrf_exempt
@login_required 
def update(request, user, db):
	if request.method=="GET":
		return render(request, "upload.html", {"title":"Upload", "name":db})
	else:
		the_db = Dataspace.objects.get(owner = request.user, name=db)
		the_db.delete()
		return add_database(request)


def user(request, user):
	usr = User.objects.get(username=user)
	return render(request, "user.html", {
		"the_user": usr, 
		"title":usr.username,
		"breadcrumb":[{
			"url":"/data/"+user, 
			"name":user
		}],
		"owner":user==request.user.username,
		"icon":"user"})

def user_api(request, user):
	return HttpResponse(json.dumps([{
		"name":d.name, 
		"url":"/api/%s/%s" % (user, d.name),
		"page":"/data/%s/%s" % (user, d.name),
	} for d in User.objects.get(username=user).dataspaces.all()]))

def database(request, user, db):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	return render(request, "db_structure.html", {"db":the_db,
		"title":the_db.name,
		"breadcrumb":[{
			"url":"/data/"+user, 
			"name":user
		}, {
			"url":"/data/"+user+"/"+db, 
			"name":db
		}],
		"owner":user==request.user.username,
		"icon":"database" if not the_db.geo else "globe"
	})

def database_api(request,user,db):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	return HttpResponse(json.dumps([{
		"title":m.name, 
		"url":"/api/%s/%s/%s" % (user, db, m.name), 
		"fields":[{"name":f.name, "title":f.name, "description":f.name, "constraints":{}} for f in m.fields.all()]} for m in the_db.models.filter(internal=False)
	]))

def schema_api(request,user,db, model):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	return HttpResponse(json.dumps([{
		"title":m.name, 
		"url":"/api/%s/%s/%s" % (user, db, m.name), 
		"fields":[{"name":f.name, "title":f.name, "description":f.name, "constraints":{}} for f in m.fields.all()]} for m in the_db.models.filter(name=model, internal=False)
	][0]))

def apidoc(request, user, db):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	return render(request, "apidoc.html", {
		"title":"APIdoc - "+ the_db.name,
		"icon":"file-text",
		"db":the_db,
		"breadcrumb":[{
				"url":"/data/"+user, 
				"name":user
			}, {
				"url":"/data/"+user+"/"+db, 
				"name":db
			}, {
				"url":"/data/"+user+"/"+db+"/apidoc",
				"name":"apidoc"
			} ],})

def model(request, user, db, model):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	the_table = the_db.models.get(name=model)
	fields = [field.name for field  in the_table.fields.filter(geo=False)]
	page = request.REQUEST.get("p","1")
	page = int(page)
	offset = (page-1)*100

	q_select = ", ".join(["\""+f+"\"" for f in fields])

	if Field.objects.filter(model=the_table, model__dataspace=the_db, geo=True).count() > 0 :
		q_select = " asgeojson(%s) AS geojson, " %Field.objects.get(model=the_table, model__dataspace=the_db, geo=True).name + q_select
		fields.append("geojson")
	try:
		rows = do_query(the_db, "select "+q_select+" from %s limit 100 offset %s;" % (model, offset), geo=False)
		rows = [[row[field]  for field in fields ] for row in rows]
		return render(request, "table.html", {
			"title":the_table.dataspace.name+"."+the_table.name,
			"icon":"table",
			"breadcrumb":[{
				"url":"/data/"+user, 
				"name":user
			}, {
				"url":"/data/"+user+"/"+db, 
				"name":db
			}, {
				"url":"/data/"+user+"/"+db+"/"+model,
				"name":model
			} ],
			"table":the_table, 
			"rows":rows,
			"prev":page-1,
			"next":page+1,
			"pages":range(max(1,page-2), page+3)})
	except Exception, e:
		return render(request, "error.html", {
			"error":str(e) + "--<pre>" + traceback.format_exc() +"</pre>" + "<pre>"+q_select+"</pre>",
			"title":the_table.dataspace.name+"."+the_table.name,
			"icon":"table",
			"breadcrumb":[{
				"url":"/data/"+user, 
				"name":user
			}, {
				"url":"/data/"+user+"/"+db, 
				"name":db
			}, {
				"url":"/data/"+user+"/"+db+"/"+model,
				"name":model
			} ],
			"table":the_table, 
			"pages":range(max(1,page-2), page+3)
		})

@xframe_options_exempt
def query(request, user, db, model):
	the_db = Dataspace.objects.get(owner__username = user, name=db)

	q_from = request.REQUEST.get("from", model)
	if the_db.models.filter(name=q_from).count() == 0:
		return HttpResponse("No Model Found")


	q_select = request.REQUEST.get("select", ", ".join([f.name for f in Field.objects.filter(model__name=q_from, model__dataspace=the_db) if not f.geo]))
	q_select = q_select.split(",")
	

	q_where = request.REQUEST.get("where", "[]")
	q_where = json.loads(q_where)


	q_limit= request.REQUEST.get("limit","10")
	q_offset= request.REQUEST.get("offset","0")

	query = "SELECT "

	if Field.objects.filter(model__name=q_from, model__dataspace=the_db, geo=True).count() > 0 :
		query += "  asgeojson(%s) AS geojson, " %Field.objects.get(model__name=q_from, model__dataspace=the_db, geo=True).name
	
	query +=",".join(q_select)
	query +=" FROM " + q_from

	conds = []
	for cond in q_where:
		if cond["op"].lower() == "like":
			cond["val"] = "'%%%s%%'" % cond["val"]
		elif cond["op"].lower() == "in":
			cond["val"] = "(%s)" % ",".join([str(c) for c in cond["val"]])
		conds.append("%s %s %s" % (cond["field"], cond["op"], cond["val"]))

	if len(conds) > 0 :
		query +=" WHERE "
		query += " AND ".join(conds)


	query +=" LIMIT %s OFFSET %s" % (q_limit, q_offset)

	is_geo = Field.objects.filter(model__name=q_from, model__dataspace=the_db,geo=True).count()>0
	return HttpResponse(json.dumps({"message":"results", "query":query, "results": do_query(the_db, query,geo=is_geo)}))

def do_query(the_db, query, **kwargs):
	the_file = the_db.sqlite_file.path
	the_con = sqlite3.connect(the_file)
	the_con.enable_load_extension(True)
	the_con.load_extension("/usr/lib/x86_64-linux-gnu/libspatialite.so.5.1.0")

	ret = []
	q = the_con.execute(query)
	for row in q:
		if kwargs.get("geo",False):
			geo_el = {}
			geo_el["attributes"]= dict(zip([d[0] for d in q.description],row))
			geo_el["type"] = "Feature"
			geo_el["geometry"] = json.loads(geo_el["attributes"]["geojson"])
			del geo_el["attributes"]["geojson"]
			ret.append(geo_el)
		else:
			ret.append(dict(zip([d[0] for d in q.description],row)))

	if kwargs.get("geo",False):
		ret = {"type":"FeatureCollection", "features":ret}

	return ret

