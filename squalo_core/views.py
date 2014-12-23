from django.shortcuts import render

from django.contrib.auth.models import User
from .models import *

import sqlite3

import json

def users(request):
	return render(request, "user.html")
	
def add_database(request):
	d = Dataspace()
	d.owner = request.user
	d.name = request.REQUEST.get("name")
	d.sqlite_file = request.FILES.get("sqlite")
	d.save()

	con = sqlite3.connect(d.sqlite_file.path)
	cursor = con.cursor()
	for table in cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
		m = Model()
		m.dataspace = d
		m.name = table[0]
		m.save()

		f_cursor = con.execute("select * from %s" % table[0])

		for field in f_cursor.description:
			f = Field()
			f.model = m
			f.name = field[0]
			f.save()

	return HttpResponse("OK")

def update_database(request, user, db):
	pass

def databases(request, user):
	return render(request, "user.html", {"user": request.user})

def database(request, user, db):
	the_db = Datapsace.objects.get(owner__username = user, name=db)
	return render(request, "db_structure.html", {"db":the_db})

def query(request, user, db):
	the_db = Datapsace.objects.get(owner__username = user, name=db)
	
	q_select = request.REQUEST.get("select", "*")
	q_select = q_select.split("|")
	q_from = request.REQUEST.get("from")
	q_where = request.REQUEST.get("where", "[]")
	q_where = json.loads(q_where)

	if the_db.models.filter(name=q_from).count() == 0:
		return HttpResponse("No Model Found")

	query = "SELECT "
	query +=",".join(q_select)
	query +=" FROM " + q_from
	query +=" WHERE "

	conds = []
	for cond in q_where:
		conds.append("%s %s %s" % (cond["field"], cond["op"], cond["val"]))

	query += " AND ".join("conds")

	print query

	the_con = sqlite3.connect(the_db.sqlite_file.path)

	ret = []
	q = the_con.execute(query)
	for row in q:
		ret.append(zip(q.description,row))

	return HttpResponse(json.dumps(ret))

