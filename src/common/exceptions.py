error_response = "🛠️ Произошла ошибка, сообщите администратору!"


class ClientNotFound(Exception):
    pass


class Conflict(Exception):
    pass


class UserForbidden(Exception):
    pass


class DatabaseErrorDataOrConstrains(Exception):
    pass


class DatabaseError(Exception):
    pass


class UpdateDatabaseError(Exception):
    pass
