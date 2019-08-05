from notify import db


class VerifiedApp(db.Model):
    __tablename__ = 'app'
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    vzid = db.Column(
        db.String(8)
    )

    appid = db.Column(
        db.String(12)
    )

    app_name = db.Column(
        db.String(500)
    )

    def __init__(
        self,
        vzid,
        appid,
        app_name
    ):
        self.vzid = vzid
        self.appid = appid
        self.app_name = app_name
