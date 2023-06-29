import os
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from django.contrib.auth.models import BaseUserManager


class ClientCredManager(BaseUserManager):
    """
    Class for creating object manager for Client creds model.
    """

    def save_data(self, client_id, client_secret):
        """
        Method for saving data.
        """
        f = Fernet(os.getenv("ENCRYPTION_KEY"))
        encrypted_client_id = f.encrypt(str.encode(client_id)).decode()
        encrypted_client_secret = f.encrypt(str.encode(client_secret)).decode()
        client = self.model(client_id=encrypted_client_id, client_secret=encrypted_client_secret)
        client.save(using=self._db)

    def load_data(self):
        try:
            f = Fernet(os.getenv("ENCRYPTION_KEY"))
            client = self.model.objects.all().first()

            client_id = f.decrypt(str.encode(client.client_id)).decode()
            client_secret = f.decrypt(str.encode(client.client_secret)).decode()

            return client_id, client_secret
        except InvalidToken as e:
            print("exception")
            print(e)
