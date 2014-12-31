from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File

from .models import *

import sqlite3

import json

def index(request):
	return render(request, "index.html", {"title":"Squalo SQLite Eater"})
	
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
			cursor = con.cursor()
			for table in cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';"):
				m = Model()
				m.dataspace = d
				m.name = table[0]
				m.save()

				f_cursor = con.execute("select * from "+table[0])

				for field in f_cursor.description:
					f = Field()
					f.model = m
					f.name = field[0]
					f.save()

			return HttpResponseRedirect("/data/%s/%s" % (request.user.username, d.name))
		except Exception, e:
			return render(request, "upload.html", {"title":"Upload", "error":str(e)})


def update(request, user, db):
	if request.method=="GET":
		return render(request, "upload.html", {"title":"Upload", "name":db})

def user(request, user):
	usr = User.objects.get(username=user)
	return render(request, "user.html", {
		"user": usr, 
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
		"icon":"database"
	})

def database_api(request,user,db):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	return HttpResponse(json.dumps([{
		"name":m.name, 
		"url":"/api/%s/%s/%s" % (user, db, m.name), 
		"fields":[f.name for f in m.fields.all()]} for m in the_db.models.all()
	]))

def model(request, user, db, model):
	the_db = Dataspace.objects.get(owner__username = user, name=db)
	the_table = the_db.models.get(name=model)
	fields = [field.name for field  in the_table.fields.all()]
	page = request.REQUEST.get("p","1")
	page = int(page)
	offset = (page-1)*100
	rows = do_query(the_db, "select * from %s limit 100 offset %s;" % (model, offset))
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

def query(request, user, db, model):
	the_db = Dataspace.objects.get(owner__username = user, name=db)

	q_select = request.REQUEST.get("select", "*")
	q_select = q_select.split(",")
	
	q_from = request.REQUEST.get("from", model)

	q_where = request.REQUEST.get("where", "[]")
	q_where = json.loads(q_where)

	if the_db.models.filter(name=q_from).count() == 0:
		return HttpResponse("No Model Found")

	query = "SELECT "
	query +=",".join(q_select)
	query +=" FROM " + q_from

	conds = []
	for cond in q_where:
		if cond["op"].lower() == "like":
			cond["val"] = "'%%%s%%'" % cond["val"]
		conds.append("%s %s %s" % (cond["field"], cond["op"], cond["val"]))

	if len(conds) > 0 :
		query +=" WHERE "
		query += " AND ".join(conds)

	return HttpResponse(json.dumps({"message":"results", "query":query, "results": do_query(the_db, query)}))

def do_query(the_db, query):
	the_file = the_db.sqlite_file.path
	the_con = sqlite3.connect(the_file)

	ret = []
	q = the_con.execute(query)
	for row in q:
		ret.append(dict(zip([d[0] for d in q.description],row)))
	return ret

