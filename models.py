from ufc_api import db, ma

#Event table
class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(64),index=True)
    location = db.Column(db.String(64))
    date = db.Column(db.String(64))

    def __repr__(self):
        return '{}'.format(self.id)

#Bout Table
class Bouts(db.Model):
    ###Bout statistics
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, index=True)
    weight_class = db.Column(db.String(32))
    red_fighter = db.Column(db.String(64))
    blue_fighter = db.Column(db.String(64))
    winner = db.Column(db.String(64))
    loser = db.Column(db.String(64))
    result = db.Column(db.String(32))
    end_round = db.Column(db.Integer)
    time = db.Column(db.String(64))
    method = db.Column(db.String(32))
    ###
    ###Striking Stats
    ###

    # number of knock downs
    b_KD = db.Column(db.Integer)
    r_KD = db.Column(db.Integer)

    ### significant strikes landed vs significant strikes attempted
    # this is different than total strikes
    b_LAND_SIGSTR = db.Column(db.Integer)
    b_TTL_SIGSTR = db.Column(db.Integer)
    r_LAND_SIGSTR = db.Column(db.Integer)
    r_TTL_SIGSTR = db.Column(db.Integer)

    ### total strikes landed vs total strikes total
    ### note total strikes encompasses sig strikes
    # so total strikes is it's own stat
    b_TTL_STR = db.Column(db.Integer)
    b_LAND_STR = db.Column(db.Integer)
    r_TTL_STR = db.Column(db.Integer)
    r_LAND_STR = db.Column(db.Integer)

    ### takedowns landed vs takedowns total
    b_LAND_TD = db.Column(db.Integer)
    b_TTL_TD = db.Column(db.Integer)
    r_LAND_TD = db.Column(db.Integer)
    r_TTL_TD = db.Column(db.Integer)

    ### sub attempts
    b_SUB= db.Column(db.Integer)
    r_SUB= db.Column(db.Integer)

    ### number of reversals
    b_REV= db.Column(db.Integer)
    r_REV= db.Column(db.Integer)

    ### control time in sec format
    b_CNTRL_SEC = db.Column(db.Integer)
    r_CNTRL_SEC = db.Column(db.Integer)

class EventSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Events
    id = ma.auto_field()
    event = ma.auto_field()
    date = ma.auto_field()
    location = ma.auto_field()

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

    blue_stats = ma.Method("ser_bfighter")
    red_stats = ma.Method("ser_rfighter")

    ### parse Bout fighter stats into a dict
    def ser_bfighter(self,obj):
        stats = dict()

        stats["KD"] = obj.b_KD
        stats["SIGSTR"] = obj.b_SIGSTR
        stats["SIGSTR_PRCT"] = obj.b_SIGSTR_PRCT
        stats["TTLSTR"] = obj.b_TTLSTR
        stats["TD"] = obj.b_TD
        stats["TD_PRCT"] = obj.b_TD_PRCT
        stats["SUB"] = obj.b_SUB
        stats["PASS"] = obj.b_PASS
        return stats

    def ser_rfighter(self,obj):
        stats = dict()

        stats["KD"] = obj.r_KD
        stats["SIGSTR"] = obj.r_SIGSTR
        stats["SIGSTR_PRCT"] = obj.r_SIGSTR_PRCT
        stats["TTLSTR"] = obj.r_TTLSTR
        stats["TD"] = obj.r_TD
        stats["TD_PRCT"] = obj.r_TD_PRCT
        stats["SUB"] = obj.r_SUB
        stats["PASS"] = obj.r_PASS
        return stats