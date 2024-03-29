# -*- coding: utf-8 -*-

import MySQLdb
import csv, codecs, cStringIO

from sweep.settings import DB_CONNECT, DB_TABLE


class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        '''writerow(unicode) -> None
        This function takes a Unicode string and encodes it to the output.
        '''
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.writerow(data.replace('"', '').split(','))
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


db = MySQLdb.connect(**DB_CONNECT)

cursor = db.cursor()

cursor.execute("SELECT distinct(batch) FROM {} order by batch asc".format(DB_TABLE))

db.commit()

categories = cursor.fetchall()
categories = [x for cat in categories for x in cat]

for category in categories:
    cursor.execute("SELECT batch, name, email, gender, type, url FROM {} WHERE batch like '{}'".format(DB_TABLE, category))
    csv_writer = csv.writer(open("csvs/{}.csv".format(category), "wt"))
    csv_writer.writerow([i[0] for i in cursor.description])
    writer = UnicodeWriter(csv_writer, quoting=csv.QUOTE_ALL)
    writer.writerows(cursor)
    del csv_writer

cursor.close()
db.close()
