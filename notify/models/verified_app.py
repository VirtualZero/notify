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

    api_key = db.Column(
        db.String(1000)
    )

    refresh_api_key = db.Column(
        db.String(1000)
    )

    def __init__(
        self,
        vzid,
        appid,
        app_name,
        api_key,
        refresh_api_key
    ):
        self.vzid = vzid
        self.appid = appid
        self.app_name = app_name
        self.api_key = api_key,
        self.refresh_api_key = refresh_api_key
