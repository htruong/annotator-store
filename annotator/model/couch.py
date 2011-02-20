from datetime import datetime

import couchdb
import couchdb.design
from couchdb.mapping import Document
from couchdb.mapping import TextField, IntegerField, DateField, DictField
from couchdb.mapping import ListField, DateTimeField


class Metadata(object):
    SERVER = None
    DB = None

def init_model(config):
    Metadata.SERVER = couchdb.Server(config['COUCHDB_HOST'])
    Metadata.DB = setup_db(config['COUCHDB_DATABASE'])

def setup_db(dbname):
    if dbname in Metadata.SERVER:
        return Metadata.SERVER[dbname]
    else:
        db = Metadata.SERVER.create(dbname)
        setup_views(db)
        return db

def rebuild_db(dbname):
    if dbname in Metadata.SERVER:
        del Metadata.SERVER[dbname]
    return setup_db(dbname)


class DomainObject(Document):
    def save(self):
        self.store(Metadata.DB)

    @classmethod
    def get(cls, id):
        return cls.load(Metadata.DB, id)

    def to_dict(self):
        return dict(self.items())

    @classmethod
    def from_dict(self, dict_):
        if 'id' in dict_:
            ann = Annotation(dict_['id'])
            del dict_['id']
        else:
            ann = Annotation()
        for k,v in dict_.items():
            ann[k] = v
        return ann

class Annotation(DomainObject):
    user = TextField()
    text = TextField()
    created = DateTimeField(default=datetime.now)
    ranges = ListField(DictField())

# Required views
# query by document
# query by user
# query by document and user
# query 
# TODO: general, change from all_fields to include_docs=True ?
# Remove offset ....?
# limit the same
# results format is different: {'total_rows': 3, 'offset':', 'rows': ..
# as opposed to {'total': ,'results': ...}
# could sort this out with a list function ...
def setup_views(db):
    design_doc = 'annotator'
    view = couchdb.design.ViewDefinition(design_doc, 'all', '''
function(doc) {
    emit(doc._id, null);
}
'''
    )
    view.get_doc(db)
    view.sync(db)

    view = couchdb.design.ViewDefinition(design_doc, 'byuri', '''
function(doc) {
    if(doc.uri) {
        emit(doc.uri, null);
    }
}
'''
    )
    view.get_doc(db)
    view.sync(db)

