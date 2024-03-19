from typing import List

from zk import ZK
from zk.attendance import Attendance
from zk.user import User


class ZKTeco:
    def __init__(self, host: str, port: int, timeout: int = 5, debug: bool = True):
        self.zk = ZK(ip=host, port=port, timeout=timeout)
        self.conn = None
        self.debug = debug

    def _connect(self) -> None:
        if self.debug:
            print("Connecting to device ...")

        if not self.conn:
            self.conn = self.zk.connect()

    def _disconnect(self) -> None:
        if self.debug:
            print("Disconnecting from device ...")

        if self.conn:
            self.conn.disconnect()
            self.conn = None

    def _enable_device(self) -> None:
        if self.debug:
            print("Enabling device ...")

        self.conn.enable_device()

    def _disable_device(self) -> None:
        if self.debug:
            print("Disabling device ...")

        self.conn.disable_device()

    def get_firmware(self) -> str:
        try:
            if self.debug:
                print("Getting device firmware ...")

            self._connect()
            self._disable_device()
            firmware = self.conn.get_firmware_version()
            self._enable_device()
            return firmware
        except Exception as e:
            print("Process terminate : {}".format(e))
        finally:
            self._disconnect()

    def get_users(self) -> List[User]:
        try:
            if self.debug:
                print("Getting users ...")

            self._connect()
            self._disable_device()
            users: List[User] = self.conn.get_users()
            self._enable_device()
            return users
        except Exception as e:
            print("Process terminate : {}".format(e))
            raise e
        finally:
            self._disconnect()

    def get_attendances(self) -> List[Attendance]:
        try:
            if self.debug:
                print("Getting attendances ...")
            self._connect()
            self._disable_device()
            attendances: List[Attendance] = self.conn.get_attendance()
            self._enable_device()
            return attendances
        except Exception as e:
            print("Process terminate : {}".format(e))
        finally:
            self._disconnect()
