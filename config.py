class Config:
    APP_NAME = "Сласти от всех напастей"
    APP_DESC = "Интернет-магазин по доставке конфет"

    URL = "0.0.0.0"
    PORT = 8080

    POSTGRES = {
        "user": "postgres",
        "pw": "password",
        "db": "db",
        "host": "localhost",
        "port": "5432",
    }

    SQLALCHEMY_DATABASE_URI = "postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES
