import sqlite3
from flask import Flask, request, jsonify, session, send_file, abort, g, current_app
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

app=Flask(__name__)

app.secret_key = 'Secretkeythatshouldntbeshared36872931'



#Returnerer en indexfil, Dette er den eneste filen vi bruker
@app.route("/")
def index():
    db = get_db()
    print(db)
    db_setup(db)
    return app.send_static_file("index.html")



#Login
@app.route("/login", methods=['POST'])
def login():
    try:
        #Prøver å hente bruker id og passord fra ajax request
        data = request.json
        bruker_id = data.get("Bruker_id")
        passord = data.get("Passord")

        if db_sjekk("Brukere", "Bruker_id", bruker_id) and db_sjekk_passord("Brukere", "Bruker_id", bruker_id, passord, "Passord"):
            session["username"] = bruker_id
            print(session["username"])
            return(bruker_id)
        else:
            return ("Feil brukernavn eller passord")
            

       
    except:
        abort(500)



#Registrering
@app.route("/registrering", methods=['POST'])
def registrer():
    try:
        #Henter data fra AJAX request
        data = request.json
        bruker_id = data.get("Bruker_id")
        passord = data.get("Passord")
        Mod = data.get("Mod")
        db = get_db

        if db_sjekk("Brukere", "bruker_id", bruker_id):
            return ("Brukernavnet er tatt")
        if re.search(r'[^a-zA-Z0-9]', bruker_id):
            return("Navn kan bare være tall og/eller nummer")

        if len(bruker_id) <= 3:
            return("Brukernabnet er for kort")
        if len(bruker_id) > 12:
            return("Brukernavnet er for langt")
        
        Passord = generate_password_hash(passord)

        db_write("Brukere", "bruker_id", bruker_id, "Passord",Passord, "Mod", "False")
        session["username"] = bruker_id
           
        
        
        #newUser = open("Data/Brukere.json","w", encoding="UTF8")
        #json.dump(users,newUser, indent=2)
        session["username"] = bruker_id

        #newUser.close()
        return(bruker_id)
    #Returner bruker id dersom alt er greit
            
    except:
        #Ved feil gir vi en servererror feil
        return abort(500)
    

#Håndterer kommentarer
@app.route("/kommenter", methods=['POST'])
def Lag_kommentar():
    try:
       #Henter data fra AJAX
       data = request.json
       print("før id")

       
       bruker_id = data.get("Bruker_id")
       print("Før komment")
       comment = data.get("Comment")
       print("før id")
       id = db_sjekk_kommentar("Kommentarer", "Id")
       #media = data.get("media")

       try:
           print("Krasjer denne?")
           reply = data.get("Reply_To_Comment")
           print("Vi fikk denne replyen", reply)
       except:
           reply = 0
           print("Dette er etter except:", reply)
       

       db_write_comment("Kommentarer", "Bruker_id", bruker_id, "Reply", reply, "Id", id)
       db_write_comment_ny("Kommentarer_tekst", "Comment", comment, "Id", id)
       print("Dette er etter db_write_comment funksjonen")



       #KommentarListe = open("Data/Fildump/Kommentarer/Kommentarfil.json","r", encoding="UTF8")
       #kommentarer = json.load(KommentarListe)

       session["username"] = bruker_id
       return jsonify(message="Kommentar og evt. media lagret!")

       

       #if kommentarer:
        #    forrige_id = max(int(kommentar["Id"]) for kommentar in kommentarer)
            
       
       #Ny_id = forrige_id +1
        #Gir hver kommentar en unik ID
       #ordbok = {'Bruker_id':bruker_id, 'Comment': comment, 'Reply': "False", 'Id': Ny_id , "media" : media} 

       #kommentarer.append(ordbok)

       #NyKommentar = open("Data/Fildump/Kommentarer/Kommentarfil.json","w", encoding="UTF8")
       #json.dump(kommentarer,NyKommentar, indent=2)
       #NyKommentar.close()
       #return jsonify(message="Kommentar lagt til")
    except:
        abort(500)
   
   #Redigere kommentar
@app.route("/edit_kommentar", methods=['POST'])
def edit_kommentar():
    try:
        data = request.json
        bruker_id = data.get("Bruker_id")
        comment = data.get("Comment")
        old_comment = data.get("old_comment")
        Id = data.get("Id")
        media = data.get("media")

        db_edit_kommentar("Kommentarer_tekst", Id, comment)
        return jsonify(message="Kommentar ble endret!")

        #with open("Data/Fildump/Kommentarer/Kommentarfil.json", "r", encoding="UTF8") as KommentarListe:
         #   kommentarer = json.load(KommentarListe)

        #fant_kommentaren = False

        #for kommentar in kommentarer:
         #   if (session["username"] == bruker_id or session["Mod"]) and (kommentar["Comment"] == old_comment and kommentar["Id"] == Id):
          #      kommentar["Comment"] = comment
           #     kommentar["media"] += media
            #    fant_kommentaren = True
             #   break

        #if fant_kommentaren:
         #   with open("Data/Fildump/Kommentarer/Kommentarfil.json", "w", encoding="UTF8") as NyKommentar:
          #      json.dump(kommentarer, NyKommentar, indent=2)
           # 
        #else:
            #Gir unik feil dersom kommenaren ikke finnes
            #return jsonify(error="Fant ikke kommentarer du prøver å endre!"), 404
    #GIr feilen dersom serveren gjør feil
    except Exception as e:
        return jsonify(error="Crashhh"), 500
    


#Svare til kommentarer
@app.route("/reply_kommentar", methods=['POST'])
def reply_kommentar():
    try:
        data = request.json
        bruker_id = data.get("Bruker_id")
        comment = data.get("Comment")
        id = db_sjekk_kommentar("Kommentarer", "Id")
        #reply_to_comment = data.get("Reply_To_Comment")
        reply = data.get("Reply_To_Comment")
        print("Her kommer reply:", reply)
        #media = data.get("media")

        #KommentarListe = open("Data/Fildump/Kommentarer/Kommentarfil.json","r", encoding="UTF8")
        #kommentarer = json.load(KommentarListe)

        db_write_comment("Kommentarer", "Bruker_id", bruker_id, "Comment", comment, "Reply", reply, "Id", id)

        #fant_kommentaren = False
        #if kommentarer:
         #   forrige_id = max(int(kommentar["Id"]) for kommentar in kommentarer)
            
        #Ny_id = forrige_id +1

        #for kommentar in kommentarer:
         #   if (session["username"] == bruker_id or session["Mod"]) and kommentar["Id"] == reply_to_comment:
          #      fant_kommentaren = True
           #     break

        #if fant_kommentaren:
            #ordbok = {'Bruker_id':bruker_id, 'Comment': comment, 'Reply': reply, 'Id': Ny_id, 'Reply_to_comment': reply_to_comment, 'media' : media} 
            #kommentarer.append(ordbok)

            #NyKommentar = open("Data/Fildump/Kommentarer/Kommentarfil.json","w", encoding="UTF8")
            #json.dump(kommentarer,NyKommentar, indent=2)
            #NyKommentar.close()
            #return jsonify(message="Kommentar lagt til")

    except:
        abort(500)
            
#Slettkommentar
@app.route("/slett_kommentar", methods=['POST'])
def slett_kommentar():
    try:
       data = request.json
       bruker_id = data.get("Bruker_id")
       comment = data.get("Comment")
       Id = data.get("Id")

       db_slett_kommentar("Kommentarer", Id)
       db_slett_kommentar("Kommentarer_tekst", Id)
       return jsonify(message="Kommentar ble endret!")


       
       #with open("Data/Fildump/Kommentarer/Kommentarfil.json", "r", encoding="UTF8") as KommentarListe:
        #    kommentarer = json.load(KommentarListe)

       #fant_kommentaren=False
       
       #for kommentar in kommentarer:
        #    if (session["username"] == bruker_id or session["Mod"]) and (kommentar["Comment"] == comment and kommentar["Id"] == Id):
        #        kommentarer.remove(kommentar)
        #        fant_kommentaren = True
        #        break

       #if fant_kommentaren:
        #    with open("Data/Fildump/Kommentarer/Kommentarfil.json", "w", encoding="UTF8") as NyKommentar:
        #        json.dump(kommentarer, NyKommentar, indent=2)
        
       #else:
       #     return jsonify(error="Fant ikke kommentarer du prøver å endre!"), 404

    except Exception as e:
        print("Error:", e)
        return jsonify(error="Crashhh"), 500
    

                
#Laster opp bilder og filer til serveren
@app.route("/Opplastning", methods=['POST'])
def Last_opp():
    #Sjekker at det faktisk blir lastet opp en fil
    if 'fil' not in request.files:
        return("Ingen fil funnet")
    Opplastet_fil = request.files['fil']
    #Definerere sepparate fildumper etter filtype
    Fildumpvid = ("Data/Fildump/Videoer")
    Fildumpimg = ("Data/Fildump/Bilder")
    TILLATTE_FILTYPER = [".mp4",".jpeg",".gif", ".png", ".webp", ".jpg"]
    filnavn,filextension = os.path.splitext(Opplastet_fil.filename)
    id = db_sjekk_kommentar("Kommentarer", "Id")
    
    if filextension.lower() in TILLATTE_FILTYPER:
        if filextension.lower() == ".mp4":
            filnavn = filnavn + filextension
            Opplastet_fil.save(os.path.join(Fildumpvid,filnavn))
            db_write_comment_ny("Media", "media", filnavn, "Id", id)
            return("Videoen er lastet opp")
        else:
            filnavn = filnavn + filextension
            Opplastet_fil.save(os.path.join(Fildumpimg,filnavn))
            db_write_comment_ny("Media", "media", filnavn, "Id", id)
            return("Bildet er lastet opp")

    else:#Dersom denne returner er filtypen feil
        return("Filtypen er feil, husk mp4 for videoer eller jpeg, gif, png, webp, jpg for bilder")

#Henter kommentarene
@app.route("/hent_kommentarer", methods=['GET'])
def hent_kommentar():

    Kommentarer = db_get("Kommentarer","Kommentarer_tekst", "Media")

    for kommentar in Kommentarer:
        if kommentar["Reply"] == None:
            kommentar["Reply"] = "False"

    print("Her er kommentarer tablet etter for løkken:", Kommentarer)


    #KommentarListe = open("Data/Fildump/Kommentarer/Kommentarfil.json","r", encoding="UTF8")
    #kommentarer = json.load(KommentarListe)
    return jsonify(Kommentarer)
    

#Brukes i mod status, returnerer en liste av brukere
#def read_users_file():
 #   with open('Data/Brukere.json', 'r') as file:
  #      return json.load(file)

    #Sjekker om brukere er mods
@app.route("/mod_status", methods=['GET'])
def mod_status():
    response = {"innlogget": False}

    if "username" in session:
        username = session["username"]
        response["innlogget"] = True
        response["username"] = username
        response["mod"] = db_sjekk_mod("Brukere", session["username"])
        session["Mod"] = db_sjekk_mod("Brukere", session["username"])
    return jsonify(response)


#Skaffer innlogingsstatusen når noen lander på siden
@app.route("/innlogget_status", methods=['GET'])
def innlogget_status():
    if "username" in session:
        return jsonify(innlogget = True, username=session["username"])
    else:
        return jsonify(innlogget= False)
        
    #Logger brukere ut
@app.route("/logout", methods = ['POST'])
def logout():
    session.pop("username", None)
    return("Du har logget ut")


#Henter alle videoene som er lagret i videofildumpen
@app.route("/videoliste")
def videoliste():
    videoliste= db_finn_videoer()
    print(videoliste)

    return (jsonify(videoliste))

#Returnerer en blobstrem som lar oss spille av videoer
@app.route("/spill_av_video", methods=['POST'])
def spill_av_video():
    data = request.json
    videonavn = data["videonavn"]
    return (send_file("Data/Fildump/Videoer/" + videonavn, mimetype='video/mp4'))


#Henter avatarene til brukerne
@app.route("/Avatar", methods=['POST'])
def Avatar():
    data = request.json
    avatar = data["navn"]
    Fildump = ("Data/Fildump/Avatar")
    for fil in os.listdir(Fildump):

        if avatar in fil:
            TILLATTE_FILTYPER = [".jpeg",".gif", ".png", ".webp", ".jpg"]
            for extension in TILLATTE_FILTYPER:

                avatartry = avatar + extension
                

                try:
            
                    return (send_file("Data/Fildump/Avatar/" + avatartry, mimetype='image/*'))
                except:
                    continue
            

        
                
    return (send_file("Data/Fildump/Avatar" + "/averageuser.WEBP", mimetype='image/webp'))


#Lar brukerene laste opp avatarer
@app.route("/Avatarupload", methods=['POST'])
def Avatarupload():
    if 'fil' not in request.files:
        return("Ingen fil funnet")
    Opplastet_fil = request.files['fil']
    Fildump = ("Data/Fildump/Avatar")
    TILLATTE_FILTYPER = [".jpeg",".gif", ".png", ".webp", ".jpg"]
    filnavn,filextension = os.path.splitext(Opplastet_fil.filename)


    filnavn = Opplastet_fil.name
    print(filnavn)
    
    db_write_comment_ny("Avatarer", "Avataren", filnavn, "Bruker_id", session["username"])
    
    if filextension.lower() in TILLATTE_FILTYPER:
        for filtype in TILLATTE_FILTYPER:
            if os.path.exists("Data/Fildump/Avatar/" + filnavn):
                os.remove("Data/Fildump/Avatar/" + filnavn)
        
        
        Opplastet_fil.save(os.path.join(Fildump,filnavn))
        return("Suksess")
    else:
        return("Filtypen er feil, den må være jpeg, gif, png eller webp")
            

#Returnerer en blobstrem som viser bildene som blir requested
@app.route("/vis_bilde", methods = ['POST'])
def vis_bilde():
    bilde = request.json["bildenavn"]
    id = request.json["Id"]
    print("Blir bildenavn kalt riktig?", bilde)
    print("Her er iden vi får fra magic:", id )
    fil = db_finn_media("Media", "Id", id)
    print(fil)
    #Fildump = ("Data/Fildump/Bilder")
    #for fil in os.listdir(Fildump):
     #   if bilde == fil:
    return (send_file("Data/Fildump/Bilder/" + fil, mimetype='image/*'))
        
    #abort(404)

#Henter Detektiv Kot
@app.route("/logo")
def logo():
    try:
        return send_file("static/Logo/OIG2.jpeg", mimetype = 'image/jpeg')
    except Exception as e:
        abort(500)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('static/Database.db'
        )
        g.db.row_factory = sqlite3.Row
        if g.db is None:
            print("Error", g.db)
        if g.db is not None:
            print(g.db , "succsessfull connection")

    return g.db

def db_setup(db):
    print("Db_setup kjores")
    g.db = sqlite3.connect('static/Database.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Brukere(
                   Bruker_id varchar(60), 
                   Passord varchar(124), 
                   Mod boolean,
                   Primary key(Bruker_id));""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS Kommentarer(
                   Bruker_id varchar(60),
                   Reply int, 
                   Id int,
                   Primary key(Id),
                   Foreign key(Bruker_id) REFERENCES Brukere(Bruker_id));""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS Kommentarer_tekst( 
                   Comment varchar(500),
                   Id int,
                   Primary key(Id),
                   Foreign key(Id) REFERENCES Kommentarer(Id));""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS Media(
                   media TEXT, 
                   Id int,
                   Primary Key(media),
                   Foreign key(Id) REFERENCES Kommentarer(Id));""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS Avatarer(
                   Avataren TEXT, 
                   Bruker_id varchar(60),
                   Primary Key(Avataren),
                   Foreign key(Bruker_id) REFERENCES Brukere(Bruker_id));""")
    
    #cursor.execute("""ALTER TABLE Media RENAME COLUMN Mediet TO media """)
    #db.commit()
    #cursor.execute("""DROP TABLE IF EXISTS Avatarer; """)
    #db.commit()
    #cursor.execute("""ALTER TABLE Kommentarer DROP COLUMN Comment;""")
    #db.commit()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print("Table:", table['name'])
    
    cursor.execute("PRAGMA table_info(Brukere);")
    columns = cursor.fetchall()

    for column in columns:
        print(dict(column))

def db_get(tabble, tabble2, tabble3):
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"""SELECT * FROM {tabble} JOIN {tabble2} ON {tabble}.Id = {tabble2}.Id
                    LEFT JOIN {tabble3} ON {tabble}.Id = {tabble3}.Id""")
    tables = cursor.fetchall()

    resultat = [dict(row) for row in tables]
    print(resultat)
    return resultat


            
        
def db_sjekk(table, column, navn):
    conn = sqlite3.connect('static/Database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column} FROM {table};")
    res = cursor.fetchall()
    print("Jeg kom så langt")
    for index in res:
        if index[0] == navn:
            print("Hello, this is true")
            return True
    print("hello, i evalute false")
    
    return False

def db_sjekk_mod(table, Bruker_id):
    conn = sqlite3.connect('static/Database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT Mod FROM {table} WHERE Bruker_id = ?", (Bruker_id,))
    res = cursor.fetchone()
    if res[0]:
        return True
    return False

def db_sjekk_kommentar(table, column):
    conn = sqlite3.connect('static/Database.db')
    cursor = conn.cursor()
    print("DEtte er før vi lager ID")
    try:
        cursor.execute(f"SELECT MAX({column}) AS highest_value FROM {table};")
        res = cursor.fetchone()
        highest = res[0] if res[0] is not None else 0
        print("Her sjekker jeg etter høyesete id:", highest)
    except:
        highest=0
        print("Dette er hvis vi ikke fikk Id tidligere:", highest)
    print("Jeg kom så langt")
    
    print("hello, i evalute false")
    
    return highest + 1


def db_slett_kommentar(table, id):
    conn = sqlite3.connect('static/Database.db')
    cursor = conn.cursor()
    print("Etter å laget cursor")
    print("Her er iden vi får:", id)

    cursor.execute(f"DELETE FROM {table} WHERE Id = ?", (id,))
    print("i teorien etter delete funksjonen")
    conn.commit()
    print("etter commit")



def db_edit_kommentar(table, id, ny_kommentar):
    conn = sqlite3.connect('static/Database.db')
    cursor = conn.cursor()
    print("Etter å laget cursor")
    print("Her er iden vi får:", id)

    cursor.execute(f"UPDATE {table} SET COMMENT = ? WHERE Id = ?", (ny_kommentar, id,))
    print("i teorien etter delete funksjonen")
    conn.commit()
    print("etter commit")

def db_sjekk_passord(table, column, navn, passord, column2):
    conn = sqlite3.connect('static/Database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column}, {column2} FROM {table};")
    res = cursor.fetchall()
    print("Jeg kom så langt")
    for index in res:
        print("index 0", index[0])
        print("index 1", index[1])
        if index[0] == navn:
            if check_password_hash(index[1], passord):
                return True
            
    print("hello, i evalute false")
    
    return False

def db_write_comment(tabel, column1, info1, column3, info3, column4, info4):
    print("Attempting to establish connections")
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("Connextion establisehd")
    query = f"INSERT INTO {tabel} ({column1}, {column3}, {column4}) VALUES (?,?,?);"
    cursor.execute(query,(info1, info3, info4))
    conn.commit()
    conn.close()

def db_write_comment_ny(tabel, column1, info1, column3, info3):
    print("Attempting to establish connections")
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("Connextion establisehd")
    query = f"INSERT INTO {tabel} ({column1}, {column3}) VALUES (?,?);"
    cursor.execute(query,(info1, info3))
    conn.commit()
    conn.close()

def db_finn_media(tabel, column1, info1):
    print("Attempting to establish connections")
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("Connextion establisehd")
    query = f"SELECT media FROM {tabel} WHERE {column1} = ?;"
    cursor.execute(query,(info1,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result["media"]
    else:
        return None
    
def db_finn_videoer():
    print("Attempting to establish connections")
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("Connextion establisehd")
    query = f"SELECT * FROM Media WHERE media LIKE '%.mp4';"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return [row["media"] for row in result]


def db_write(tabel, column1, info1, column2, info2, column3, info3):
    print("Attempting to establish connections")
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("Connextion establisehd")
    query = f"INSERT INTO {tabel} ({column1}, {column2}, {column3}) VALUES (?,?,?);"
    cursor.execute(query,(info1, info2, info3))
    conn.commit()
    conn.close()

 

#starter Serveren, Ligger sist for å la a
if __name__ == "__main__":
    app.run(host='0.0.0.0')