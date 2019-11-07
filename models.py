from ufc_api import db

#Event table
class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(48),index=True)

    def __repr__(self):
        return '{}'.format(self.id)

#Bout Table
class Bouts(db.Model):
    ###Bout statistics
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
    ###
    ###Striking Stats
    ###
    b_KD = db.Column(db.Integer, index=True)
    r_KD = db.Column(db.Integer, index=True)
    b_SIGSTR = db.Column(db.String(12), index=True)
    r_SIGSTR = db.Column(db.String(12), index=True)
    b_SIGSTR_PRCT = db.Column(db.String(12),index=True)
    r_SIGSTR_PRCT = db.Column(db.String(12),index=True)
    b_TTLSTR = db.Column(db.String(12), index=True)
    r_TTLSTR = db.Column(db.String(12), index=True)
    b_TD= db.Column(db.Integer, index=True)
    r_TD= db.Column(db.Integer, index=True)
    b_TD_PRCT = db.Column(db.String(12),index=True)
    r_TD_PRCT = db.Column(db.String(12),index=True)
    b_SUB= db.Column(db.Integer, index=True)
    r_SUB= db.Column(db.Integer, index=True)
    b_PASS= db.Column(db.Integer, index=True)
    r_PASS= db.Column(db.Integer, index=True)

    