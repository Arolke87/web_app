# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file, send_from_directory
import os
import sys
import manga_downloader
from flask_security import login_required, login_user, logout_user, current_user, utils

from base_app import app, db, user_datastore, security
from models import Manga, Capitoli, Pagine, User, Ruoli, Film, Audio, Regista



APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/"))

@app.before_first_request
def set_up():
    db.create_all() #Aggiungo eventuali nuove tabelle senza dover ri-popolare tutto
    
    print "\n\nAfter first request.\n"
    
    return

@app.route('/my_login', methods=['GET','POST'])
def login():
    # username e psw non sono case-senitive
    uname = request.form['usr'].lower()
    psw = request.form['psw'].lower()
    
    user = User.query.filter_by(username=uname, active=1).first()
    
    if user:
        #check psw match
        print "\nUser exist\n"
        if utils.verify_password(psw, user.password):
            login_user(user, remember = True)
            print "\n\tCorrect Login"
            return redirect(request.args.get('next') or request.referrer or url_for('manga_main'))
        
    print "\n\nLogin Error\n"
    return redirect(url_for('manga_main'))

@app.route('/my_logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or request.referrer or url_for('manga_main'))
    

@app.route('/<path:resource>')
def serve_static(resource):
    return send_from_directory('static', resource)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
  	return render_template('contact.html')

## MANGA
@app.route("/manga", methods=['GET'])
def manga_main():
    mangas = Manga.query.all()
    return render_template("manga_main.html", mangas=mangas)
    
@app.route("/db_refresh/<numb>", methods=['GET', 'POST'])
@login_required
def db_refresh(numb=0):
    #manga_list = [
    #    ("http://www.mangahere.co/manga/lilith_s_cord/", "Lilith_s_Cord"),
    #    ("http://pignaquegna.altervista.org/series/tower_of_god/", "Tower_of_God"),
    #    ("http://www.mangaeden.com/it/it-manga/the-gamer/", "The_Gamer")
    #]
    #
    #if not this_manga:
    #    this_manga = Manga(
    #        nome=manga_list[int(numb)][1],
    #        link=manga_list[int(numb)][0]
    #    )
    #
    #    db.session.add(this_manga)
    #    db.session.commit()
        
    this_manga = Manga.query.get(int(numb))
    
    data = manga_downloader.scan_chapter_collection(this_manga.link, this_manga.nome)
    if data:
        
        print "\n\nStato di partenza:"
        for ch in this_manga.capitoli:
            print "ch:%d sub:%d %s"%(ch.numero, ch.sub_num, ch.link)
        
        for chapter in reversed(data['all_ch']):
        
            print chapter
            
            this_ch = Capitoli.query.filter_by(link=chapter['curl']).first()
            
            if not this_ch:
                this_ch = Capitoli(
                    link    = chapter['curl'],
                    volume  = chapter['vol' ],
                    numero  = chapter['num' ],
                    sub_num = chapter['sub' ],
                    valid = False
                )
                
                this_manga.capitoli.append(this_ch)
                db.session.commit()
            else:
                this_ch.capitoli = []
                db.session.commit()
                
                
            ch_data=manga_downloader.scan_pages_download(
                chapter,
                data['manga_name'],
                data['site_sets'],
                os.path.join(APP_ROOT, 'static/manga_link/'),
                imgs_flag = False,
                links_flag = False
            )
            
            for idx, url in enumerate(ch_data['imgs']):
                this_ch.pagine.append( Pagine(link=url, numero=idx) )
            
            this_ch.valid = True
            db.session.commit()
            
        print "\n\nStato finale:"
        for ch in this_manga.capitoli:
            print ch.link
        
    else:
        print "Errore con il manga " + manga_url[1]

    flash("Liste ricaricate: " + this_manga.full_name)
    return redirect(url_for('manga_main'))


@app.route("/db_update/<numb>", methods=['GET', 'POST'])
@login_required
def db_update(numb=0):
    #manga_list = [
    #    ("http://www.mangahere.co/manga/lilith_s_cord/", "Lilith_s_Cord"),
    #    ("http://pignaquegna.altervista.org/series/tower_of_god/", "Tower_of_God"),
    #    ("http://www.mangaeden.com/it/it-manga/the-gamer/", "The_Gamer")
    #]
    #    
    #if not this_manga:
    #    this_manga = Manga(
    #        nome=manga_list[int(numb)][1],
    #        link=manga_list[int(numb)][0]
    #    )
    #
    #    db.session.add(this_manga)
    #    db.session.commit()

    this_manga = Manga.query.get(int(numb))
    if this_manga:
        data = manga_downloader.scan_chapter_collection(this_manga.link, this_manga.nome)
        
    if this_manga and data:
        
        print "\n\nStato di partenza:"
        for ch in this_manga.capitoli:
            print "ch:%d sub:%d %s"%(ch.numero, ch.sub_num, ch.link)
        
        for chapter in reversed(data['all_ch']):
        
            print chapter
            
            this_ch = Capitoli.query.filter_by(link=chapter['curl']).first()
            
            if not this_ch:
                this_ch = Capitoli(
                    link    = chapter['curl'],
                    volume  = chapter['vol' ],
                    numero  = chapter['num' ],
                    sub_num = chapter['sub' ],
                    valid = False
                )
                this_manga.capitoli.append(this_ch)
                db.session.commit()
            
            if this_ch.valid==False:
                
                this_ch.pagine = []
            
                ch_data=manga_downloader.scan_pages_download(
                    chapter,
                    data['manga_name'],
                    data['site_sets'],
                    os.path.join(APP_ROOT, 'static/manga_link/'),
                    imgs_flag = False,
                    links_flag = False
                )
                
                for idx, url in enumerate(ch_data['imgs']):
                    this_ch.pagine.append( Pagine(link=url, numero=idx) )
                
                this_ch.valid = True
                db.session.commit()
            
        print "\n\nStato finale:"
        for ch in this_manga.capitoli:
            print ch.link
        
    else:
        print "Errore con il manga " + manga_url[1]

    flash("Liste aggiornate: " + this_manga.full_name)
    return redirect(url_for('manga_main'))
    
    
@app.route("/db_manga_read", methods=['GET', 'POST'])
@app.route("/db_manga_read/<manga_tag>", methods=['GET', 'POST'])
@app.route("/db_manga_read/<manga_tag>/<cap>", methods=['GET', 'POST'])
def db_views(manga_tag=None, cap=0):
    try:
        cap = int(cap)
    except:
        cap = 0
    
    main_dir_list = [ manga.nome for manga in Manga.query.all()]
    
    if request.method == 'POST' and request.form['cartella']:
        return redirect(url_for("db_views", manga_tag=request.form['cartella'], cap=0))
    
    if manga_tag == None:
        return render_template('views.html',
            main_dir_list = main_dir_list,
            img_list=[],
            cap_name = None,
            precedente = "#",
            successivo = "#"
        )
    
    
    manga = Manga.query.filter_by(nome=manga_tag).first()

    chapters = manga.capitoli[cap]
    
    img_file_path = [img.link for img in chapters.pagine ]
    
    return render_template('views.html',
        main_dir_list = main_dir_list,
        manga_name = manga.full_name,
        img_list=img_file_path,
        cap_name = chapters.unique_str(),
        precedente = url_for('db_views', manga_tag=manga_tag, cap=cap-1),
        successivo = url_for('db_views', manga_tag=manga_tag, cap=cap+1) )

## GAMES
@app.route("/snake", methods=['GET', 'POST'])
def snake():
    return render_template('my_snake.html')

    
@app.route("/tetris", methods=['GET', 'POST'])
def tetris():
    return render_template('my_tetris.html')
    

## FILM GIORDANO
@app.route("/videoteca", methods=['GET', 'POST'])
@login_required
def videoteca():
    
    films = Film.query.all()

    return render_template('videoteca.html', films = films)

    
if __name__ == "__main__":
    app.run()