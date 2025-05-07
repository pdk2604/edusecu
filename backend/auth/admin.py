from flask_login import UserMixin

# Classe représentant un utilisateur admin
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "admin"
        self.password = "admin123"  # 💡 Tu peux modifier ce mot de passe ici

    def get_id(self):
        return self.id

# Fonction pour récupérer l'utilisateur par son nom
def get_user(username):
    if username == "admin":
        return AdminUser(id="admin")
    return None
