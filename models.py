from UFC_handler import db

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(48),index=True)

    def __repr__(self):
        return '{}'.format(self.id)


class Bouts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, index=True)
    weight_class = db.Column(db.String(32), index=True)
    red_fighter = db.Column(db.String(64), index=True)
    blue_fighter = db.Column(db.String(64), index=True)
    winner = db.Column(db.String(64), index=True)
    loser = db.Column(db.String(64), index=True)
    result = db.Column(db.String(32), index=True)
    end_round = db.Column(db.Integer, index=True)
    time = db.Column(db.String(64), index=True)
    method = db.Column(db.String(32), index=True)

    