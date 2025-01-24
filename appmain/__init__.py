from flask import Flask

app = Flask(__name__)

app.config["SECRET_KEY"] = 'a6490c591739b89066e3331993faeb78'

from appmain.routes import main
app.register_blueprint(main)

from appmain.user.routes import user
app.register_blueprint(user)

from appmain.article.routes import article
app.register_blueprint(article)

from appmain.reply.routes import reply
app.register_blueprint(reply)

from appmain.recommend.routes import recommend
app.register_blueprint(recommend)
