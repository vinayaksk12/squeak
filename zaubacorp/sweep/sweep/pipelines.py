# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from hashlib import md5
import json
from twisted.enterprise import adbapi
from scrapy import log
from scrapy.utils.project import get_project_settings

from sweep.utils import get_string, EMAIL_REGEX, URL_REGEX


settings = get_project_settings()


class SweepPipeline(object):
    """A pipeline to store the item in a json format
    """
    def __init__(self):
        self.file = open('items.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class CleanPipeline(object):
    """A pipeline to clean item
    """
    def __init__(self):
        pass

    def process_item(self, item, spider):
        for key, value in dict(item).iteritems():
            if key == "email":
                item[key] = get_string(value).strip() if EMAIL_REGEX.match(value) else ''
            elif key == "website":
                item[key] = get_string(value).strip() if URL_REGEX.match(value) else ''
            else:
                item[key] = get_string(value).strip().replace('_', ' ') if value and len(value) > 1 else ''
        return item


class MySQLPipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """
    insert_query = "INSERT IGNORE INTO company (%s) values (%s)"
    update_query = "UPDATE company SET %s WHERE cin='%s'"

    def __init__(self):
        dbargs = settings.get('DB_CONNECT')
        db_server = settings.get('DB_SERVER')
        dbpool = adbapi.ConnectionPool(db_server, **dbargs)
        self.dbpool = dbpool

    def __del__(self):
        self.dbpool.close()

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM company WHERE cin = %s
        )""", (item["cin"],))
        ret = conn.fetchone()[0]

        if ret:
            self._update_data(item, self.update_query)
            spider.log("Item updated in db: %s %r" % (item["cin"], item))
        else:
            self._insert_data(item, self.insert_query)
            spider.log("Item stored in db: %s %r" % (item["cin"], item))
        return item

    def _insert_data(self, item, insert):
            keys = item.fields.keys()
            fields = u','.join(keys)
            qm = u','.join([u'%s'] * len(keys))
            sql = insert % (fields, qm)
            data = [item[k] for k in keys]
            return self.dbpool.runOperation(sql, data)

    def _update_data(self, item, update):
        keys = item.fields.keys()
        fields = u','.join(["{}=%s".format(key) for key in keys if key != "cin"])
        sql = update % (fields, item["cin"])
        data = [item[k] for k in keys if k != "cin"]
        return self.dbpool.runOperation(sql, data)

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        log.err(failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return md5(item['url']).hexdigest()
