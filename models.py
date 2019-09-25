from UFC_handler import db

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(48),index=True)

    def __reduce__(self):
        return '<Events> {}'.format(self.event)

    