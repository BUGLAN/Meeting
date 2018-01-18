from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager
from app import create_app
from app.main.models import Meet, User, db


app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)


@manager.shell
def manager_shell_context():
    return dict(app=app, User=User, Meet=Meet, db=db)


if __name__ == '__main__':
    manager.run()
