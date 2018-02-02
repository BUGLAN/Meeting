from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager
from run import app
from app.main.models import Meet, User, db, ChatMessage, Role


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)


@manager.shell
def manager_shell_context():
    return dict(db=db, app=app, User=User, Meet=Meet, ChatMessage=ChatMessage, Role=Role)


if __name__ == '__main__':
    manager.run()
