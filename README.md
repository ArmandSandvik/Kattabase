# Kattabase

Problem analysis:
Introductory information
THis social media platform is intended as a hybrid of youtube and reddit. Its users consists of people who wish to share videos and talk through comments.
Since we are constrained to relational databases the data to be stored consist of names, id numbers, text and other data consistent with relational databases. Videos and pictures will be stored by name in the database so that they can be retrieved sepparately from the filesystem.

Entities and relationships:
The main entities are users, their (Hashed) passwords, their status, wether they are moderator or not. Additionally each user has an avatar(or a fallback if they dont upload their own), and can create a comment. the comments relation to each other comment and who created it ensures that the comment itself relates back to the user. 
Additonally each commet has a text (Which is implied by the comment ID) hence the comment text needs to be in its own table. at last, all comments may or may not have a picture or a video, Seeing as this is not a 1 to 1 relationship, as media is optional, and combining comment and media might lead to the transtive relationship comment -> media or media -> comment, best practice would dictate that these should be kept sepparate.

For the full ER-Diagram see the ER_MAP.png file

Implementation:
We will be using sqlite for this assignment, as it allows for easy coordination using github, as all the database info will be stored in a file in the project repository.
The main intention of of this project is a working tech-demo as such, the priority will be to ensure that the project runs smoothly and proper interaction between the website and the database.