import os
import platform
import dbm.dumb as dbm


class DatasourceManager:
    def __init__(self, db_name="datasource"):
        home_dir = os.path.expanduser("~")
        if platform.system() in ["Darwin", "Linux"]:
            self.base_path = os.path.join(home_dir, ".datasource")
        elif platform.system() == "Windows":
            self.base_path = os.path.join(home_dir, "AppData", "Local", "datasource")
        else:
            raise Exception("Unsupported operating system")

        os.makedirs(self.base_path, exist_ok=True)
        self.db_path = os.path.join(self.base_path, f"newsletter_scraper_{db_name}.db")

    def clear(self):
        with dbm.open(self.db_path) as db:
            db.clear()

    def get(self, *keys):
        with dbm.open(self.db_path) as db:
            return tuple([db.get(key, b"").decode('utf-8') for key in keys])

    def set(self, **kwargs):
        with dbm.open(self.db_path) as db:
            for key, value in kwargs.items():
                db[key] = value


class CredentialManager(DatasourceManager):
    def __init__(self, db_name="credentials"):
        super().__init__(db_name)

    def get_username_and_password(self):
        return self.get("username", "password")

    def set_username_and_password(self, username, password):
        self.set(username=username, password=password)

    def get_product_dcm(self):
        return self.get(
            "product_dcm_session", "product_dcm_member_id", "product_dcm_use"
        )

    def set_product_dcm(self, session, member_id, use):
        return self.set(
            product_dcm_session=session,
            product_dcm_member_id=member_id,
            product_dcm_use=use,
        )
