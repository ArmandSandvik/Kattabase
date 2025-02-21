

document.addEventListener("DOMContentLoaded", function () {

    const passordsjekk = new RegExp("^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$");
    

    const header = document.getElementById("header");
    const LoginBtn = document.createElement("div");
    LoginBtn.setAttribute("class", "LoginBtn");
    header.appendChild(LoginBtn);
    const bruker = document.createElement("div");
    bruker.setAttribute("id", "bruker");
    header.appendChild(bruker);
    Search()
    logo()
    const LoginOrReg = document.createElement("div");
    LoginOrReg.setAttribute("id", "LoginOrReg");
    LoginOrReg.innerHTML = "<p>Login or Register</p>";
    LoginBtn.appendChild(LoginOrReg);


    //Lager FormCheck slik at man kun kan han 1 registrerings/innlogginsskjema oppe samtidig.
    //Bruker samme logikk flere plasser i koden nedover.
    let FormCheck = false;
    LoginBtn.addEventListener("click", function () {

        if (FormCheck === false) {
            const UserContainer = document.querySelector("body");
            const CreateUser = document.createElement("div");
            CreateUser.setAttribute("id", "user");
            CreateUser.innerHTML = "<form id='Reguser' action=''><p>Brukernavn:</p><input type='text' id='Brukernavn'><p>Passord:</p><input type='Password' id='Passord'></form>"
            UserContainer.appendChild(CreateUser);

            const Lukknapp = document.createElement("button");
            Lukknapp.setAttribute("class", "lukk");
            Lukknapp.innerHTML = "X";
            CreateUser.appendChild(Lukknapp);

            const Registreringsknapp = document.createElement("button");
            Registreringsknapp.setAttribute("id", "Newuser");
            Registreringsknapp.innerHTML = "Har du ikke bruker? Registrer her!";
            CreateUser.appendChild(Registreringsknapp);

            LogginnKnapp = document.createElement("button");
            LogginnKnapp.innerHTML = "Logg inn!";
            CreateUser.appendChild(LogginnKnapp);

            LogginnKnapp.addEventListener("click", () => {
                //Henter passord og brukernavn fra form i CreateUser
                let Passord = document.getElementById("Passord").value;
                let Brukernavn = document.getElementById("Brukernavn").value
                fetch("/login", {
                    method: "POST",
                    body: JSON.stringify({
                        "Bruker_id": Brukernavn,
                        "Passord": Passord
                    }),
                    headers: {
                        "content-type": "application/json; charset=UTF-8"
                    }

                })
                    .then(response => response.text())
                    .then(data => {
                        if (data == Brukernavn) {
                            window.alert("Logged in")
                            bruker.innerHTML = Brukernavn
                            FormCheck = false
                            setlogincookies("Navn", Brukernavn)
                            setlogincookies("Mod", data[1])
                            setlogincookies("søk", "")
                            setlogincookies("søkevalg", "")
                            last_avatar(getcookies("Navn"));
                            AddComment(Brukernavn);
                            location.reload(true);

                        } else {
                            window.alert(data)
                        }

                    })
            });




            Registreringsknapp.addEventListener("click", () => {
                //Setter forrige create user blank og sender inn en ny med nytt skjema for registrering
                document.getElementById("user").innerHTML = "";
                CreateUser.innerHTML = "<form id='Reguser' action=''><p>Brukernavn:</p><input type='text' id='Brukernavn'><p>Passord:</p><input type='Password' id='Passord'></form>"
                CreateUser.appendChild(Lukknapp);

                SubbyKnapp = document.createElement("button");
                SubbyKnapp.innerHTML = "Registrer!";
                CreateUser.appendChild(SubbyKnapp);


                SubbyKnapp.addEventListener("click", () => {
                    //Henter igjen data fra formet i CreateUser
                    let Passord = document.getElementById("Passord").value;
                    let Brukernavn = document.getElementById("Brukernavn").value

                    if (passordsjekk.test(Passord)) {
                        fetch("/registrering", {
                            method: "POST",
                            body: JSON.stringify({
                                "Bruker_id": Brukernavn,
                                "Passord": Passord,
                                "Mod": "False"
                            }),
                            headers: {
                                "content-type": "application/json; charset=UTF-8"
                            }

                        })
                            .then(response => response.text())
                            .then(data => {
                                if (data == Brukernavn) {
                                    setlogincookies("Navn", Brukernavn)

                                    setlogincookies("søk", "")
                                    setlogincookies("søkevalg", "")
                                    last_avatar(getcookies("Navn"));

                                    FormCheck = false
                                    location.reload(true);

                                } else {
                                    window.alert(data)
                                }

                            })

                    }
                    else {

                        window.alert("Passordet oppfyller ikke kravene våre, vi trenger minst en stor bokstav, en liten bokstav, ett tall og minst 8 tegn totalt")
                    }
                });
            });


            Lukknapp.addEventListener("click", () => {
                document.getElementById("user").remove();
                FormCheck = false;
            });


            FormCheck = true;

        }
    });

    fetch("/innlogget_status")
        //Bruker denne for å sjekke om vi er logget inn eller ikke, da hva som blir vist på siden avhenger av det
        .then(response => response.json())
        .then(data => {
            if (data.innlogget) {
                document.getElementById("commentbtn").style.display = "block";

                bruker.innerHTML = "<p>" + data.username + "</p>";

                //Fjerner logg inn knappen og erstatter den med Logg ut knapp
                LoginBtn.remove();
                const LogoutBtn = document.createElement("div");
                LogoutBtn.setAttribute("class", "LoginBtn");
                LoginOrReg.innerHTML = "<p>Logg ut!</p>";
                LogoutBtn.appendChild(LoginOrReg);
                header.appendChild(LogoutBtn);

                last_avatar(getcookies("Navn"));
                AddComment(data.username);
                EndreAvatar();

                LogoutBtn.addEventListener("click", function () {
                    if(er_du_sikker()){
                    fetch("\logout", {
                        method: "POST"
                    })
                        .then(response => {
                            if (response.ok) {
                                slettcookie("Navn", data.username);
                                window.alert("Logged out successfully");
                                setlogincookies("søk", "")
                                setlogincookies("søkevalg", "")
                                location.reload(true);
                            } else {
                                window.alert("Logout failed");
                            }
                        })
                        .catch(error => {
                            console.error("Error logging out:", error);
                        });
                    }
                });
            

            } else {
                document.getElementById("commentbtn").style.display = "none";
            }
        })
        .catch(error => {
            console.error("Error checking login status:", error);
        });



});
function Last_opp(lokasjon = "video", browseknapp = "blaknapp1") {
    let opplastingsskjema = document.getElementById(lokasjon);
    let skjema = document.createElement("form1");
    skjema.setAttribute("action", "upload");
    skjema.setAttribute("enctype", "multipart/form-data");

    let blaknapp = document.createElement("input");
    blaknapp.setAttribute("class", "videouploadbutton");
    blaknapp.setAttribute("type", "file");
    blaknapp.setAttribute("id", browseknapp);

    const innsendingknapp = document.createElement("div");
    innsendingknapp.setAttribute("id", "knappy");
    innsendingknapp.innerHTML = ("Last opp")

    opplastingsskjema.appendChild(skjema);
    skjema.appendChild(blaknapp);
    skjema.appendChild(innsendingknapp);


    innsendingknapp.addEventListener("click", () => {
        let formData = new FormData
        formData.append('fil', document.getElementById(browseknapp).files[0])
        try {
            media.push(document.getElementById(browseknapp).files[0].name)
        }
        catch {
            window.alert("Ingen fil funnet")
            return
        }

        fetch("\Opplastning", {
            method: "POST",
            body: formData

        })
    
    .then(response => response.text())
    .then(data => {
            window.alert(data)
    })
    });



};





function AddComment(Brukernavn) {
    const kommenter = document.getElementById("commentbtn");

    let FormCheck = false;

    kommenter.addEventListener("click", () => {
        if (FormCheck === false) {

            LeggTilKommentar = document.getElementById("comment");
            const kommentarfelt = document.createElement("div");
            kommentarfelt.setAttribute("id", "kommentarfelt");
            LeggTilKommentar.appendChild(kommentarfelt);
            kommentarfelt.innerHTML = "<textarea id='textplass' placeholder='Leave a comment'></textarea>";

            Addbtn = document.createElement("button");
            Addbtn.innerHTML = "kommenter";
            kommentarfelt.appendChild(Addbtn);

            CancelBtn = document.createElement("button");
            CancelBtn.innerHTML = "Lukk";

            kommentarfelt.appendChild(Addbtn);
            kommentarfelt.appendChild(CancelBtn);
            FormCheck = true;
            Last_opp("kommentarfelt")
            media = []

            Addbtn.addEventListener("click", () => {
                const text_plass = document.getElementById("textplass")
                const commie = text_plass.value.trim();

                if (commie === "") {
                    window.alert("Kommentar kan ikke være tom!");
                    return;
                }

                const data = {
                    "Bruker_id": Brukernavn,
                    "Comment": commie,
                    "media": media
                };

                fetch("/kommenter", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                })
                    .then(response => response.text())
                    .then(message => {
                        hent_kommentarer();

                        text_plass.value = "";
                    })
                    .catch(error => {
                        console.error("Error adding comment:", error);
                    });

            });

            CancelBtn.addEventListener("click", () => {
                document.getElementById("comment").remove();

                const LeggTilKommentar = document.createElement("div");
                LeggTilKommentar.setAttribute("id", "comment");
                VisKommentarer.appendChild(LeggTilKommentar);

                FormCheck = false;
            });

        }

    });


};

function hent_kommentarer(søk = "") {
    fetch("/hent_kommentarer")
        .then(response => response.json())
        .then(data => {
            let increment = 1;
            const commentsContainer = document.getElementById("commentsContainer");

            //Må sette commentsContainer til blank slik at vi ikke lager duplikater
            commentsContainer.innerHTML = "";

            const commentsMap = {};
            data.forEach(comment => {
                commentsMap[comment.Id] = comment;
            });

            const commentElementsMap = {};

            data.forEach(comment => {
                let HeleKommentarBox;
                let media = comment.media;
                if (søk == "") {
                    HeleKommentarBox = LagKommentarBox(increment, comment, media);


                    commentElementsMap[comment.Id] = HeleKommentarBox;

                    if (comment.Reply == "False") {
                        commentsContainer.appendChild(HeleKommentarBox);
                        mediehenter(media, "mediediv" + increment, 700, 500)
                    } else {
                        const parentCommentId = comment.Reply_to_comment;
                        const parentCommentBox = commentElementsMap[parentCommentId];
                        if (parentCommentBox) {
                            const repliesContainer = parentCommentBox.querySelector("#ReplyFelt");
                            repliesContainer.appendChild(HeleKommentarBox);
                            mediehenter(media, "mediediv" + increment, 700, 500);
                        }
                    }

                } else {
                    if (comment.Comment.toLowerCase().includes(søk.toLowerCase()) || comment.Bruker_id.toLowerCase().includes(søk.toLowerCase())) {
                        HeleKommentarBox = LagKommentarBox(increment, comment, media);
                        commentsContainer.appendChild(HeleKommentarBox);
                        mediehenter(media, "mediediv" + increment, 700, 500)
                    }
                }

                increment += 1;


            });

        });
}

function LagKommentarBox(increment, comment) {
    const HeleKommentarBox = document.createElement("div");
    HeleKommentarBox.setAttribute("id", "KomBox" + increment);

    const BrukerBox = document.createElement("div");
    BrukerBox.setAttribute("id", "BrukerNavn" + increment);
    BrukerBox.innerHTML = comment.Bruker_id;

    const IdBox = document.createElement("div");
    IdBox.setAttribute("id", "IdBox");
    if (comment.Reply == "False") {
        IdBox.innerHTML = comment.Id;
        BrukerBox.appendChild(IdBox);
    } else {
        IdBox.innerHTML = comment.Id + " reply to " + comment.Reply_to_comment;
        BrukerBox.appendChild(IdBox);
    }


    HeleKommentarBox.appendChild(BrukerBox);

    const KommentarText = document.createElement("div");
    KommentarText.setAttribute("id", "KommentarText");
    KommentarText.textContent = comment.Comment;
    HeleKommentarBox.appendChild(KommentarText);

    const mediediv = document.createElement("div");
    mediediv.setAttribute("id", "mediediv" + increment);
    HeleKommentarBox.appendChild(mediediv);

    const KnappContainer = document.createElement("div");
    KnappContainer.setAttribute("class", "KnappContainer");
    HeleKommentarBox.appendChild(KnappContainer);

    const EditBtn = document.createElement("div");
    EditBtn.setAttribute("id", "EditBtn");
    EditBtn.innerHTML = "Edit Comment";
    EditBtn.style.display = "none";
    KnappContainer.appendChild(EditBtn);

    const ReplyBtn = document.createElement("div");
    ReplyBtn.setAttribute("id", "ReplyBtn");
    ReplyBtn.innerHTML = "Reply";
    ReplyBtn.style.display = "none";
    KnappContainer.appendChild(ReplyBtn);

    const DeleteBtn = document.createElement("div");
    DeleteBtn.setAttribute("id", "DeleteBtn");
    DeleteBtn.innerHTML = "Delete";
    DeleteBtn.style.display = "none";
    KnappContainer.appendChild(DeleteBtn);

    const SkrivReply = document.createElement("div");
    SkrivReply.setAttribute("id", "SkrivReply" + increment);
    HeleKommentarBox.appendChild(SkrivReply)

    const SkrivEdit = document.createElement("div");
    SkrivEdit.setAttribute("id", "SkrivEdit" + increment);
    HeleKommentarBox.appendChild(SkrivEdit);

    const ReplyFelt = document.createElement("div");
    ReplyFelt.setAttribute("id", "ReplyFelt");
    HeleKommentarBox.appendChild(ReplyFelt);



    last_avatar(comment.Bruker_id, "BrukerNavn" + increment)

    fetch("/innlogget_status")
        .then(response => response.json())
        .then(data => {
            if (data.innlogget) {
                let FormCheck = false;
                ReplyBtn.style.display = "block";
                ReplyBtn.addEventListener("click", () => {
                    if (FormCheck === false) {
                        ReplyCommentBtn(comment, increment);

                        FormCheck = true

                        CancelReplyBtn = document.createElement("div");
                        CancelReplyBtn.setAttribute("class", "CancelBtn");
                        replyfelt = document.getElementById("SvarKommentar" + increment);
                        CancelReplyBtn.innerHTML = "Cancel!"
                        ReplyKnappContainer = document.getElementById("ReplyKC")
                        ReplyKnappContainer.appendChild(CancelReplyBtn);

                        CancelReplyBtn.addEventListener("click", () => {
                            replyfelt.remove()
                            FormCheck = false;
                        })

                    }

                });
            }
        })


    fetch("/mod_status")
        .then(response => response.json())
        .then(data => {
            let FormCheck = false;
            if (comment.Bruker_id == data.username || data.mod == "True") {
                EditBtn.style.display = "block";


                EditBtn.addEventListener("click", () => {
                    if (FormCheck === false) {
                        FormCheck = true
                        EditCommentBtn(comment, increment);

                        CancelEditBtn = document.createElement("div");
                        CancelEditBtn.setAttribute("class", "CancelBtn");

                        editfelt = document.getElementById("editfelt" + increment);
                        CancelEditBtn.innerHTML = "Cancel!"
                        EditKnappContainer = document.getElementById("EditKC")
                        EditKnappContainer.appendChild(CancelEditBtn);

                        CancelEditBtn.addEventListener("click", () => {
                            editfelt.remove()
                            FormCheck = false;
                        })

                    }
                });

                DeleteBtn.style.display = "block";
                DeleteBtn.addEventListener("click", () => {
                    if(er_du_sikker()){
                    DeleteCommentBtn(comment);
                    }
                });


            }
        })
        .catch(error => {
            console.error("Error fetching comments:", error);
        });

    return HeleKommentarBox;
}



function DeleteCommentBtn(comment) {
    window.alert("Kommentar fjernet.")
    const data = {
        "Bruker_id": comment.Bruker_id,
        "Comment": comment.Comment,
        "Id": comment.Id
    };

    fetch("/slett_kommentar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(response => response.text())
        .then(message => {
            console.log(message);
            hent_kommentarer();

        })
        .catch(error => {
            console.error("Error adding comment:", error);
        });
}

function EditCommentBtn(comment, increment) {
    const editFelt = document.createElement("div");
    editFelt.setAttribute("id", "editfelt" + increment);
    const SkrivEdit = document.getElementById("SkrivEdit" + increment)
    SkrivEdit.appendChild(editFelt);
    editFelt.innerHTML = "<textarea id='editText' placeholder='Edit comment'></textarea>";

    Last_opp("editfelt" + increment, "ReplyBrowse")

    const EditKnappContainer = document.createElement("div");
    EditKnappContainer.setAttribute("class", "KnappContainer");
    EditKnappContainer.setAttribute("id", "EditKC")
    editFelt.appendChild(EditKnappContainer);

    ConfirmEditBtn = document.createElement("div");
    ConfirmEditBtn.setAttribute("class", "ConfirmBtn");
    ConfirmEditBtn.innerHTML = "Confrim!"
    EditKnappContainer.appendChild(ConfirmEditBtn);


    media = []

    ConfirmEditBtn.addEventListener("click", () => {

        const edit_text = document.getElementById("editText")
        const eddie = edit_text.value.trim();

        if (eddie === "") {
            window.alert("Kommentar kan ikke være tom!");
            return;
        }
        const data = {
            "Bruker_id": comment.Bruker_id,
            "Comment": eddie,
            "old_comment": comment.Comment,
            "Id": comment.Id,
            "media": media
        };

        fetch("/edit_kommentar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
            .then(response => response.text())
            .then(message => {
                console.log(message);

                hent_kommentarer();

                edit_text.value = "";
            })
            .catch(error => {
                console.error("Error adding comment:", error);
            });
    })

}

function EndreAvatar() {
    const Nav = document.getElementById("navigation")
    dropdown = document.createElement("div")
    dropdown.setAttribute("id", "dropdown")
    dropdown.innerHTML = "<p>Endre avatar</p>"
    Nav.prepend(dropdown)
    let FormCheck = false;

    dropdown.addEventListener("click", () => {
        if (FormCheck === false) {
            FormCheck = true;
            const EndreAvDivContainer = document.querySelector("body")
            const EndreAvDiv = document.createElement("div");
            EndreAvDiv.setAttribute("id", "EndreAvDiv");
            EndreAvDivContainer.appendChild(EndreAvDiv)


            last_opp_avatar("EndreAvDiv")
            Lukknapp = document.createElement("button")
            Lukknapp.setAttribute("class", "lukk")
            Lukknapp.innerHTML = "x"
            EndreAvDiv.appendChild(Lukknapp)
            Lukknapp.addEventListener("click", () => {
                EndreAvDiv.remove();
                FormCheck = false;
            })
        }
    });
}


function ReplyCommentBtn(comment, increment) {
    const SvarKommentar = document.createElement("div");
    SvarKommentar.setAttribute("id", "SvarKommentar" + increment);
    const Skrivreply = document.getElementById("SkrivReply" + increment)
    Skrivreply.appendChild(SvarKommentar);
    SvarKommentar.innerHTML = "<textarea id='replyText' placeholder='Leave a comment'></textarea>";

    Last_opp("SvarKommentar" + increment, "ReplyBrowse")

    const ConfirmReplyBtn = document.createElement("div");
    ConfirmReplyBtn.setAttribute("class", "ConfirmBtn");
    ConfirmReplyBtn.innerHTML = "Confrim!"

    const ReplyKnappContainer = document.createElement("div");
    ReplyKnappContainer.setAttribute("class", "KnappContainer");
    ReplyKnappContainer.setAttribute("id", "ReplyKC")
    SvarKommentar.appendChild(ReplyKnappContainer);
    ReplyKnappContainer.appendChild(ConfirmReplyBtn);

    media = []

    ConfirmReplyBtn.addEventListener("click", () => {
        const reply_text = document.getElementById("replyText")
        const reppie = reply_text.value.trim();


        if (reppie === "") {
            window.alert("Kommentar kan ikke være tom!");
            return;
        }

        const data = {
            "Bruker_id": getcookies("Navn"),
            "Comment": reppie,
            "Reply_To_Comment": comment.Id,
            "Reply": "True",
            "media": media
        };

        fetch("/reply_kommentar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
            .then(response => response.text())
            .then(message => {
                console.log(message);
                reply_text.value = "";
                hent_kommentarer();

            })
            .catch(error => {
                console.error("Error adding comment:", error);
            });

    })
}

function setlogincookies(navn, id, utgår = 2592000000) {
    let dato = new Date();
    dato.setTime(dato.getTime() + utgår);
    let utgåelsesdato = "utgår" + dato.toUTCString();
    document.cookie = navn + "=" + id + ";" + utgåelsesdato + "; path=/;SameSite=Lax";

}
function getcookies(Navn) {
    let navn = Navn + "="
    let avkodetcookie = decodeURIComponent(document.cookie)
    let kjeksbit = avkodetcookie.split(";");
    for (let i = 0; i < kjeksbit.length; i++) {
        let bit = kjeksbit[i];
        while (bit.charAt(0) == " ") {
            bit = bit.substring(1)
        }
        if (bit.indexOf(navn) == 0) {
            return bit.substring(navn.length)
        }


    }
}


function slettcookie(navn, navnverdi) {
    let dato = new Date();
    dato.setTime(0);
    let utgåelsesdato = "utgår" + dato.toUTCString();
    document.cookie = navn + "=" + navnverdi + ";" + utgåelsesdato + "; path=/";
}




function List_opp_videoer(søk = "") {
    document.getElementById("commentsContainer").innerHTML = ""
    fetch("/videoliste")
        .then(response => response.json())
        .then(data => {


            for (i = 0; i < data.length; i++) {
                let videofil = data[i]

                let videofillowwercase = videofil.toLowerCase()
                if (søk == "") {
                    if (videofil.includes(".mp4")) {
                        let video = document.createElement("p")
                        video.setAttribute("id", videofil)
                        video.innerHTML = videofil;
                        document.getElementById("commentsContainer").appendChild(video)

                        video.addEventListener("click", () => {
                            spill_av_video(videofil)


                        })


                    }
                }
                else

                    if (videofillowwercase.includes(søk.toLowerCase())) {
                        if (videofillowwercase.includes(".mp4")) {

                            let video = document.createElement("p")
                            video.setAttribute("id", videofil)
                            video.innerHTML = videofil;
                            document.getElementById("commentsContainer").appendChild(video)

                            video.addEventListener("click", () => {
                                spill_av_video(videofil)

                            })


                        }
                    }
            }
        })


}
function last_avatar(Navn = "avguser", plass = "bruker") {
    fetch("/Avatar", {
        method: "POST",
        headers: {
            "content-type": "application/json"
        },
        body: JSON.stringify({
            "navn": Navn
        })

    })
        .then(response => response.blob())
        .then(blob => {
            bildeplass = document.getElementById(plass)
            avatar = document.createElement("img")
            avatar.setAttribute("src", URL.createObjectURL(blob))
            avatar.setAttribute("id", "avatar")
            bildeplass.appendChild(avatar)
        })

}
function last_opp_avatar(lokasjon = "navigation") {

    let opplastingsskjema = document.getElementById(lokasjon);

    let skjema = document.createElement("form");
    skjema.setAttribute("action", "upload");
    skjema.setAttribute("enctype", "multipart/form-data");

    let blaknapp = document.createElement("input");
    blaknapp.setAttribute("class", "avatarupload");
    blaknapp.setAttribute("type", "file");
    blaknapp.setAttribute("id", "blaknapp");

    const innsendingknapp = document.createElement("div");
    innsendingknapp.setAttribute("id", "knappy")
    innsendingknapp.innerHTML = "Last opp avatar"
    opplastingsskjema.appendChild(skjema);

    skjema.appendChild(blaknapp);
    skjema.appendChild(innsendingknapp);


    innsendingknapp.addEventListener("click", () => {
        let formData = new FormData
        formData.append('fil', document.getElementById("blaknapp").files[0])

        fetch("\Avatarupload", {
            method: "POST",
            body: formData

        })

            .then(response => response.text())
            .then(data => {

                window.alert(data)
                if (data === "Suksess") {
                    location.reload(true);
                }

            })
    });
}

function List_opp_bilde(bilde, lokasjon = "") {
    fetch("/vis_bilde", {
        method: "POST",
        headers: {
            "content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify({
            "bildenavn": bilde
        })

    })

        .then(response => response.blob())
        .then(data => {
            
            bildeplass = document.getElementById(lokasjon)
            bilde = document.createElement("img")
            bilde.setAttribute("src", URL.createObjectURL(data))

            document.getElementById(lokasjon).appendChild(bilde);
        })
}

function mediehenter(medieliste, lokasjon) {
    let tillatte_bildetyper = [".gif", ".png", ".jpg"];
    let tillatte_bildetyper2 = [".jpeg", ".webp"]
    for (medie in medieliste) {
        if (medieliste[medie].slice(-4).toLowerCase() == ".mp4") {
            spill_av_video(medieliste[medie], lokasjon)
        }
        else if (tillatte_bildetyper.includes(medieliste[medie].slice(-4).toLowerCase()) || tillatte_bildetyper2.includes(medieliste[medie].slice(-5).toLowerCase())) {
            List_opp_bilde(medieliste[medie], lokasjon)
        }
        else {
            console.log("Media: " + medieliste[medie] + ", Kan ikke lastes korrekt")
        }
    }
}

function spill_av_video(video, lokasjon = video) {

    fetch("/spill_av_video", {
        method: "POST",
        headers: {
            "content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify({
            "videonavn": video
        })

    })
        .then(response => response.blob())
        .then(blob => {
            let videodiv = document.getElementById(lokasjon)
            Avspilling = document.createElement("video")
            Avspilling.setAttribute("type", "video/mp4")
            Avspilling.setAttribute("Content-Type", "video/mp4")
            Avspilling.setAttribute("src", URL.createObjectURL(blob))
            tittel = document.createElement("p")
            tittel.innerHTML = video
            Avspilling.controls = true;
            if (video == lokasjon) {
                videodiv.innerHTML = ''
            }
            videodiv.appendChild(Avspilling)
            videodiv.appendChild(tittel)

        });


}


function Search() {
    søkeform = document.createElement("form")
    søkeform.setAttribute("id", "søkeform")

    søketema = document.createElement("label")

    søkevalg = document.createElement("select")

    bilde = document.createElement("option")
    bilde.setAttribute("value", "bilde")
    bilde.innerHTML = "video"

    kommentar = document.createElement("option")
    kommentar.setAttribute("value", "kommentar")
    kommentar.innerHTML = "kommentar"

    søkevalg.appendChild(kommentar)
    søkevalg.appendChild(bilde)
    søketema.appendChild(søkevalg)
    søkeform.appendChild(søketema)

    søkeinput = document.createElement("input")
    søkeinput.setAttribute("type", "text")
    søkeinput.value = getcookies("søk")

    søkevalg.value = getcookies("søkevalg")
    søkeform.appendChild(søkeinput)

    søkeknapp = document.createElement("input")
    søkeknapp.setAttribute("id", "submit")
    søkeknapp.setAttribute("type", "submit")
    søkeknapp.value = "Søk"

    søkeform.appendChild(søkeknapp)
    document.getElementById("navigation").prepend(søkeform)
    hent_kommentarer()

    søkeform.addEventListener("submit", function () {
        event.preventDefault()
        if (søkevalg.value == "bilde") {
            List_opp_videoer(søkeinput.value)
            setlogincookies("søk", søkeinput.value)
            setlogincookies("søkevalg", søkevalg.value)
        }
        else {
            hent_kommentarer(søkeinput.value)
            setlogincookies("søk", søkeinput.value)
            setlogincookies("søkevalg", søkevalg.value)
        }

    })



}

function logo() {
    fetch("/logo")
        .then(response => response.blob())
        .then(blob => {
            bildeplass = document.getElementById("header")
            logoen = document.createElement("img")
            logoen.setAttribute("src", URL.createObjectURL(blob))
            logoen.setAttribute("id", "logo")
            bildeplass.appendChild(logoen)
        })

}


function er_du_sikker(){
    if (confirm("Er du sikker på at du vil gå videre")) {
        return true;
      } else {
        return false;
      } 
}