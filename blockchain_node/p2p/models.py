from p2p import db

class MiningNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True, nullable=False)
    port = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.Float, nullable=False)