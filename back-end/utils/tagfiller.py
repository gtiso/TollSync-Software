from config.db import db
from models.tag import Tag
from sqlalchemy import text

def populate_tags_from_passes():
    result = db.session.execute(text("SELECT DISTINCT(tagRef), tagHomeID FROM tollsync.pass"))
    unique_tags = result.fetchall()
    new_tags = []
    for tagRef, tagHomeID in unique_tags:
        existing_tag = Tag.query.filter_by(tagRef=tagRef).first()
        if not existing_tag:
            new_tag = Tag(tagRef=tagRef, tagHomeID=tagHomeID, balance=50.0) 
            new_tags.append(new_tag)

    if new_tags:
        db.session.bulk_save_objects(new_tags)
        db.session.commit()
        print(f"{len(new_tags)} new tags inserted successfully.")