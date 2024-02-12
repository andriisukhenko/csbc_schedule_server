from sqlalchemy.orm import Session
from libgravatar import Gravatar
from users.models import User
from users import schemas
from app.services.auth import auth

class UserController:
    UserModel = User

    async def get_user_by_email(self, email: str, db: Session) -> UserModel | None:
        return db.query(self.UserModel).filter(self.UserModel.email == email).first()

    async def create(self, body: schemas.UserCreationModel, db: Session) -> UserModel:
        avatart = None
        try:
            g = Gravatar(body.email)
            avatart = g.get_image()
        except Exception as e:
            print("Avatar creation exception:", e)
        body.password = auth.password.hash(body.password)
        user = self.UserModel(**body.model_dump(), avatart=avatart)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user