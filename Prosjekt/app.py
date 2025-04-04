import sqlite3
from flask import Flask, request, jsonify, session, send_file, abort, g, current_app
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os

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
        
        with open("Data/Brukere.json", "r", encoding="UTF8") as brukere:
            #Laster filen med brukere og og sjekker for hver bruker at bruker_id og passord stemmer til det finner den rette kontoen
            innlogget = json.load(brukere)
            for user in innlogget:
                if user["Bruker_id"] == bruker_id and check_password_hash(user["Passord"],passord):
                    session["username"] = user["Bruker_id"]
                    print(session["username"])
                    return(bruker_id)
                #gir en feilmelding dersom den ikke finner brukernavn/passord
            return("Feil brukernavn eller passord!")
    #Dersom noe annet er feil gir vi en intern serverfeil
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
       bruker_id = data.get("Bruker_id")
       comment = data.get("Comment")
       media = data.get("media")

       KommentarListe = open("Data/Fildump/Kommentarer/Kommentarfil.json","r", encoding="UTF8")
       kommentarer = json.load(KommentarListe)

       session["username"] = bruker_id

       

       if kommentarer:
            forrige_id = max(int(kommentar["Id"]) for kommentar in kommentarer)
            
       
       Ny_id = forrige_id +1
        #Gir hver kommentar en unik ID
       ordbok = {'Bruker_id':bruker_id, 'Comment': comment, 'Reply': "False", 'Id': Ny_id , "media" : media} 

       kommentarer.append(ordbok)

       NyKommentar = open("Data/Fildump/Kommentarer/Kommentarfil.json","w", encoding="UTF8")
       json.dump(kommentarer,NyKommentar, indent=2)
       NyKommentar.close()
       return jsonify(message="Kommentar lagt til")
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

        with open("Data/Fildump/Kommentarer/Kommentarfil.json", "r", encoding="UTF8") as KommentarListe:
            kommentarer = json.load(KommentarListe)

        fant_kommentaren = False

        for kommentar in kommentarer:
            if (session["username"] == bruker_id or session["Mod"]) and (kommentar["Comment"] == old_comment and kommentar["Id"] == Id):
                kommentar["Comment"] = comment
                kommentar["media"] += media
                fant_kommentaren = True
                break

        if fant_kommentaren:
            with open("Data/Fildump/Kommentarer/Kommentarfil.json", "w", encoding="UTF8") as NyKommentar:
                json.dump(kommentarer, NyKommentar, indent=2)
            return jsonify(message="Kommentar ble endret!")
        else:
            #Gir unik feil dersom kommenaren ikke finnes
            return jsonify(error="Fant ikke kommentarer du prøver å endre!"), 404
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
        reply_to_comment = data.get("Reply_To_Comment")
        reply = data.get("Reply")
        media = data.get("media")

        KommentarListe = open("Data/Fildump/Kommentarer/Kommentarfil.json","r", encoding="UTF8")
        kommentarer = json.load(KommentarListe)

        fant_kommentaren = False
        if kommentarer:
            forrige_id = max(int(kommentar["Id"]) for kommentar in kommentarer)
            
        Ny_id = forrige_id +1

        for kommentar in kommentarer:
            if (session["username"] == bruker_id or session["Mod"]) and kommentar["Id"] == reply_to_comment:
                fant_kommentaren = True
                break

        if fant_kommentaren:
            ordbok = {'Bruker_id':bruker_id, 'Comment': comment, 'Reply': reply, 'Id': Ny_id, 'Reply_to_comment': reply_to_comment, 'media' : media} 

            kommentarer.append(ordbok)

            NyKommentar = open("Data/Fildump/Kommentarer/Kommentarfil.json","w", encoding="UTF8")
            json.dump(kommentarer,NyKommentar, indent=2)
            NyKommentar.close()
            return jsonify(message="Kommentar lagt til")

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
       
       with open("Data/Fildump/Kommentarer/Kommentarfil.json", "r", encoding="UTF8") as KommentarListe:
            kommentarer = json.load(KommentarListe)

       fant_kommentaren=False
       
       for kommentar in kommentarer:
            if (session["username"] == bruker_id or session["Mod"]) and (kommentar["Comment"] == comment and kommentar["Id"] == Id):
                kommentarer.remove(kommentar)
                fant_kommentaren = True
                break

       if fant_kommentaren:
            with open("Data/Fildump/Kommentarer/Kommentarfil.json", "w", encoding="UTF8") as NyKommentar:
                json.dump(kommentarer, NyKommentar, indent=2)
            return jsonify(message="Kommentar ble endret!")
       else:
            return jsonify(error="Fant ikke kommentarer du prøver å endre!"), 404

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
    
    if filextension.lower() in TILLATTE_FILTYPER:
        if filextension.lower() == ".mp4":
            filnavn = filnavn + filextension
            Opplastet_fil.save(os.path.join(Fildumpvid,filnavn))
            return("Videoen er lastet opp")
        else:
            filnavn = filnavn + filextension
            Opplastet_fil.save(os.path.join(Fildumpimg,filnavn))
            return("Bildet er lastet opp")

    else:#Dersom denne returner er filtypen feil
        return("Filtypen er feil, husk mp4 for videoer eller jpeg, gif, png, webp, jpg for bilder")

#Henter kommentarene
@app.route("/hent_kommentarer", methods=['GET'])
def hent_kommentar():
    KommentarListe = open("Data/Fildump/Kommentarer/Kommentarfil.json","r", encoding="UTF8")
    kommentarer = json.load(KommentarListe)
    return jsonify(kommentarer)
    

#Brukes i mod status, returnerer en liste av brukere
def read_users_file():
    with open('Data/Brukere.json', 'r') as file:
        return json.load(file)

    #Sjekker om brukere er mods
@app.route("/mod_status", methods=['GET'])
def mod_status():
    response = {"innlogget": False}
    if "username" in session:
        username = session["username"]
        users = read_users_file()
        user = next((user for user in users if user["Bruker_id"] == username), None)
        if user:
            response["innlogget"] = True
            response["username"] = username
            response["mod"] = user["Mod"]
            session["Mod"] = user["Mod"]
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
    Fildump = ("Data/Fildump/Videoer")
    videoliste=[]
    for video in os.listdir(Fildump):
        videoliste.append(video)

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


    filnavn = session["username"] + filextension
    
    if filextension.lower() in TILLATTE_FILTYPER:
        for filtype in TILLATTE_FILTYPER:
            if os.path.exists("Data/Fildump/Avatar/" + session["username"] + filtype):
                os.remove("Data/Fildump/Avatar/" + session["username"] + filtype)
        
        
        Opplastet_fil.save(os.path.join(Fildump,filnavn))
        return("Suksess")
    else:
        return("Filtypen er feil, den må være jpeg, gif, png eller webp")
            

#Returnerer en blobstrem som viser bildene som blir requested
@app.route("/vis_bilde", methods = ['POST'])
def vis_bilde():
    bilde = request.json["bildenavn"]
    Fildump = ("Data/Fildump/Bilder")
    for fil in os.listdir(Fildump):
        if bilde == fil:
            return (send_file("Data/Fildump/Bilder/" + fil, mimetype='image/*'))
        
    abort(404)

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
                   Mod boolean);""")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print("Table:", table['name'])
    
    cursor.execute("PRAGMA table_info(Brukere);")
    columns = cursor.fetchall()

    for column in columns:
        print(dict(column))

def db_get(db, tabble):
    conn = sqlite3.connect('static/Database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        if table['name'] == tabble:
            print("table:",table['name'])
            return table
        
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


 

#starter Serveren, Ligger sist for å la a
if __name__ == "__main__":
    app.run(host='0.0.0.0')