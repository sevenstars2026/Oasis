class OasisError(Exception):
    """基础异常"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PlayerNotFoundError(OasisError):
    def __init__(self, player_id: int):
        super().__init__("PLAYER_NOT_FOUND", f"Player {player_id} not found", 404)


class EmailAlreadyExistsError(OasisError):
    def __init__(self, email: str):
        super().__init__("EMAIL_EXISTS", f"Email {email} already registered", 409)


class UsernameAlreadyExistsError(OasisError):
    def __init__(self, username: str):
        super().__init__("USERNAME_EXISTS", f"Username {username} already taken", 409)


class InvalidCredentialsError(OasisError):
    def __init__(self):
        super().__init__("INVALID_CREDENTIALS", "Invalid email or password", 401)


class InsufficientGoldError(OasisError):
    def __init__(self, required: int, current: int):
        super().__init__(
            "INSUFFICIENT_GOLD",
            f"Need {required} gold but only have {current}",
            400
        )


class InvalidJobTypeError(OasisError):
    def __init__(self, job_type: str):
        super().__init__("INVALID_JOB", f"Invalid job type: {job_type}", 400)


class GameException(OasisError):
    """通用游戏异常 - 用于任务、交易等业务逻辑"""
    def __init__(self, code: int = 400, message: str = "Game error"):
        # 为了兼容性，保存code和message为公开属性
        self.code = code
        self.message = message
        super().__init__(str(code), message, code)
