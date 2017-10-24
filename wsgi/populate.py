from base_app import db, APP_ROOT, app
from models import User, Film, Manga, Regista, Audio
from flask_security import utils
import io

def recreate_db():
    db.drop_all()
    db.create_all()

def populate_user():

    print 'User'
    
    with app.app_context():

        def_user   = User(username='admin', password=utils.encrypt_password('299792458'))
        guess_user = User(username='guess', password=utils.encrypt_password('123456789'))
        
        db.session.add(def_user)
        db.session.add(guess_user)
        db.session.commit()
    
        print User.query.all()
    
def populate_film():
    print 'Archivio Film'
    
    with io.open(APP_ROOT + 'db_csv/films.csv', 'r', encoding='utf-16') as films_file:
        films = films_file.read().split('\n')[1:]
        
        for film in films:
           
            film_spl = film.split('\t')
            if len(film_spl) > 1:
                
                
                print film_spl
                print film_spl[1]
                
                date = film_spl[1].split('-')
                data_a = None
                data_b = None
                
                if len(date) == 2:
                    date_a = int(date[0])
                    date_b = int(date[1])
                elif len(date) == 1:
                    data_a = int(date[0])
                
                new_el = Film(
                    titolo = film_spl[0],
                    anno_a = data_a,
                    anno_b = data_b,
                    durata = int(film_spl[3]),
                )
                
                #REGIA
                registi = film_spl[2].split(', ') if film_spl[2]!='' else []
                for regista in registi:
                    regista = regista.strip()
                    new_regista=Regista.query.filter_by(nome=regista).first()
                    if not new_regista:
                        new_regista = Regista(nome=regista)
                        db.session.add(new_regista)
                        #db.session.commit()
                    
                    new_el.regia.append(new_regista)
                    
                #AUDIO
                audii = film_spl[5].split('/') if film_spl[5]!='' else []
                for audio in audii:
                    audio = audio.strip()
                    new_audio=Audio.query.filter_by(nome=audio).first()
                    if not new_audio:
                        new_audio = Audio(nome=audio)
                        db.session.add(new_audio)
                        #db.session.commit()
                    
                    new_el.audio.append(new_audio)
                    
                #SUB
                subs = film_spl[4].split('/') if film_spl[4]!='' else []
                for sub in subs:
                    sub = sub.strip()
                    new_sub=Audio.query.filter_by(nome=sub).first()
                    if not new_sub:
                        new_sub = Audio(nome=sub)
                        db.session.add(new_sub)
                        #db.session.commit()
                    
                    new_el.sub.append(new_sub)
                
                db.session.add(new_el)
            
    db.session.commit()
    
    print User.query.all()
    
def populate_manga():
    print "Populate Manga list"
    
    this_manga = Manga(
        nome = "Lilith_s_Cord",
        full_name = "Lilith's Cord",
        link = 'http://www.mangahere.co/manga/lilith_s_cord/',
        locandina = 'lilith_s_cord.jpg'
    )
    db.session.add(this_manga)
    
    this_manga = Manga(
        nome = "Tower_of_God",
        full_name = "Tower of God",
        link = 'http://pignaquegna.altervista.org/series/tower_of_god/',
        locandina = 'tower_of_god.jpg'
    )
    db.session.add(this_manga)
    
    this_manga = Manga(
        nome = "The_Gamer",
        full_name = "the Gamer",
        link = 'http://www.mangaeden.com/it/it-manga/the-gamer/',
        locandina = 'the_gamer.png'
    )
    db.session.add(this_manga)
    
    db.session.commit()
    
    print Manga.query.all()
    
    
if __name__ == "__main__":
    
    recreate_db()
    populate_user()
    populate_film()
    populate_manga()