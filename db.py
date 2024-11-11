import shelve


def get_username_and_password():
    with shelve.open("credentials") as db:
        username = db.get("username", "")
        password = db.get("password", "")
    return username, password


def set_username_and_password(username, password):
    with shelve.open("credentials") as db:
        db["username"] = username
        db["password"] = password


def get_product_dcm():
    with shelve.open("credentials") as db:
        product_dcm_session = db.get("product_dcm_session", "")
        product_dcm_member_id = db.get("product_dcm_member_id", "")
        product_dcm_use = db.get("product_dcm_use", "")

    return product_dcm_session, product_dcm_member_id, product_dcm_use


def set_product_dcm(session, member_id, use):
    with shelve.open("credentials") as db:
        db["product_dcm_session"] = session
        db["product_dcm_member_id"] = member_id
        db["product_dcm_use"] = use
