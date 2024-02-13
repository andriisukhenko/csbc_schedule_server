import secrets
import dotenv
import typer
import shutil
from app.settings import settings
from pathlib import Path

app = typer.Typer()

@app.command()
def initenv(env: str = 'development'):
    ENV_PATH = f"{settings.app.ROOT}/.env"
    ENV_EXAMPLE_PATH = f"{settings.app.ROOT}/.env.example"
    if Path(ENV_EXAMPLE_PATH).exists():
        if not Path(ENV_PATH).exists():
            shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)
            dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(dotenv_file)
            dotenv.set_key(dotenv_file, "APP_SECRET", secrets.token_urlsafe(25))
            dotenv.set_key(dotenv_file, "APP_ENV", env)
            print("Env file sccessfuly inited")
        else:
            print("Env file already exists!")
    else:
        print('File .env.example does not existig at root folder')
    version()

@app.command()
def version():
    print(settings.app.NAME, settings.app.VERSION)

if __name__ == "__main__":
    app()