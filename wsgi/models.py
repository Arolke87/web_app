from base_app import db
from flask_security import RoleMixin, UserMixin

roles_users = db.Table(
    'ruoli_utenti', db.metadata,
    db.Column('id', db.Integer, db.ForeignKey('user.id'), nullable=True),
    db.Column('ruolo_id', db.Integer, db.ForeignKey('lista_ruoli.ID'), nullable=True),
)


class Ruoli(db.Model, RoleMixin):
    __tablename__ = 'lista_ruoli'

    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Nome', db.String(30), nullable=False)
    description = db.Column('Descrizione', db.String(255), nullable=False)

    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=1)
    roles = db.relationship('Ruoli', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    #def __init__(self, username, email):
    #    self.username = username
    #    self.email = email

    def __repr__(self):
        return '<%d User %r>' % (self.id, self.username)

    def get_id(self):
        return self.id
        
## Film di Giordano: tabelle e quant'altro
t_connect_regia = db.Table( 'connect_regia',
    db.Column('film_id', db.ForeignKey(u'film.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('regista_id', db.ForeignKey(u'regista.id'), primary_key=True, nullable=False)
)

t_connect_audio = db.Table( 'connect_audio',
    db.Column('film_id', db.ForeignKey(u'film.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('audio_id', db.ForeignKey(u'audio.id'), primary_key=True, nullable=False)
)

t_connect_sub = db.Table( 'connect_sub',
    db.Column('film_id', db.ForeignKey(u'film.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('sub_id', db.ForeignKey(u'audio.id'), primary_key=True, nullable=False)
)

class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(255), nullable=False)
    anno_a = db.Column(db.Integer)
    anno_b = db.Column(db.Integer)
    durata = db.Column(db.Integer)
    
    
    note = db.Column(db.Text)
    
    regia = db.relationship(u'Regista', secondary='connect_regia', backref=db.backref('films', lazy='dynamic'))
    audio = db.relationship(u'Audio'  , secondary='connect_audio', backref=db.backref('films_audio', lazy='dynamic'))
    sub   = db.relationship(u'Audio'  , secondary='connect_sub',   backref=db.backref('films_sub', lazy='dynamic'))
    
    def __repr__(self):
        return '<Film %r>' % (self.titolo)
        
        
class Regista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True)

class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(8), unique=True)

    
    
## Capitoli dei manga e simili
class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    full_name = db.Column(db.String(255))
    link = db.Column(db.String(255), nullable=False, unique=True)
    descrizione = db.Column(db.Text)
    locandina = db.Column(db.String(255))
    
    capitoli = db.relationship(u'Capitoli', backref=db.backref('manga'), order_by='Capitoli.volume, Capitoli.numero, Capitoli.sub_num' )
    
    def __repr__(self):
        return '<%d Manga %r>' % (self.id, self.nome)

class Capitoli(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column( db.ForeignKey(u'manga.id', ondelete='CASCADE'))
    volume = db.Column(db.Integer)
    numero = db.Column(db.Integer, nullable=False)
    sub_num = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(255))
    valid  = db.Column(db.Boolean)
    
    pagine = db.relationship(u'Pagine', backref=db.backref('capitolo'), order_by='Pagine.numero' )
    
    def unique(self):
        cod = self.volume*1000.0 if self.volume else 0.0
        cod += self.numero
        cod += self.sub_num/10.0
        
        return cod
    
    def unique_str(self):
        return ("v%02d "%self.volume if self.volume else "") + "c%03d"%self.numero + (".%d"%self.sub_num if self.sub_num else "")
        
        

class Pagine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capitolo_id = db.Column(db.ForeignKey(u'capitoli.id', ondelete='CASCADE'))
    numero = db.Column(db.Integer)
    
    link = db.Column(db.String(255))

