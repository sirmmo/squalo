from django.core.management.base import BaseCommand, CommandError

from squalo_core.models import *

import sqlite3

import json

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        #print args
        for d in Dataspace.objects.all():
            con = sqlite3.connect(d.sqlite_file.name)
            cursor = con.cursor()
            for table in cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';"):
                m = Model()
                m.dataspace = d
                m.name = table[0]
                m.save()

                f_cursor = con.execute("select * from " + table[0])

                for field in f_cursor.description:
                    f = Field()
                    f.model = m
                    f.name = field[0]
                    f.save()