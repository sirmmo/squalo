from django.core.management.base import BaseCommand, CommandError


import sqlite3

import json

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        #print args
        query = args[1]

        the_con = sqlite3.connect(args[0])

        ret = []
        q = the_con.execute(query)
        for row in q:
            ret.append(dict(zip([d[0] for d in q.description],row)))

        print json.dumps(ret)
