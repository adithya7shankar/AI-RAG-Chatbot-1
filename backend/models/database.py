from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.PickleType, nullable=True)  # Store embeddings as binary data
    created_at = db.Column(db.Integer, default=lambda: int(datetime.datetime.now().timestamp()), nullable=False)

    def __repr__(self):
        return f"<Document id={self.id}, title={self.title}>"

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
