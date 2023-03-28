from models import db, Role
from app import create_app

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    db.session.add_all([Role(id=1, role='House administrator'), Role(id=2, role='Street administrator'),
                        Role(id=3, role='City administrator'), Role(id=4, role='Super admin')])

    db.session.commit()

