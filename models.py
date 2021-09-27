from ufc_api import db, ma
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

class EventSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Events
    id = ma.auto_field()
    event = ma.auto_field()

class BoutSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Bouts
    event_id = ma.auto_field()
    weight_class = ma.auto_field()
    red_fighter = ma.auto_field()
    blue_fighter = ma.auto_field()
    winner = ma.auto_field() 
    loser =  ma.auto_field()
    result = ma.auto_field() 
    end_round = ma.auto_field() 
    time = ma.auto_field()
    method = ma.auto_field()

    b_KD = ma.auto_field()
    r_KD = ma.auto_field()
    b_SIGSTR = ma.auto_field()
    r_SIGSTR = ma.auto_field()
    b_SIGSTR_PRCT = ma.auto_field()
    r_SIGSTR_PRCT = ma.auto_field()
    b_TTLSTR = ma.auto_field()
    r_TTLSTR = ma.auto_field()
    b_TD= ma.Str()
    r_TD= ma.Str()
    b_TD_PRCT = ma.auto_field()
    r_TD_PRCT = ma.auto_field()
    b_SUB= ma.Str()
    r_SUB= ma.Str()
    b_PASS= ma.Str()
    r_PASS= ma.Str()