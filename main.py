from config import load_config
from const import AttendancePunchType
from model import User, Attendance
from zkteco import ZKTeco
from zkteco import Attendance as ZKAttendance
from zkteco import User as ZKUser

config_file = "config.ini"


def connect_zkteco():
    zkteco_config = load_config(filename=config_file, section="zkteco")

    client = ZKTeco(
        host=zkteco_config["host"],
        port=int(zkteco_config["port"]),
        timeout=int(zkteco_config["timeout"]),
        debug=bool(zkteco_config["debug"])
    )

    return client


def fetch_attendances(client: ZKTeco):
    attendances = client.get_attendances()
    return attendances


def fetch_users(client: ZKTeco):
    users = client.get_users()
    return users


def save_users(users: list[ZKUser]):
    print(f'Receive {len(users)} users')
    new_users = []
    for user in users:
        if User.get_or_none(uid=user.uid) is None:
            new_user = User(
                uid=user.uid,
                name=user.name,
                privilege=user.privilege,
                password=user.password,
                group_id=user.group_id,
                user_id=user.user_id,
                card=user.card
            )
            new_user.save()
            new_users.append(new_user)
    print(f"Successfully save {len(new_users)} users")


def save_attendances(attendances: list[ZKAttendance]):
    print(f'Receive {len(attendances)} attendance records')
    new_atts = []
    for att in attendances:
        try:
            if Attendance.get_or_none(uid=att.uid) is None:
                new_att = Attendance(
                    uid=att.uid,
                    user_id=User.get(User.user_id == att.user_id),
                    timestamp=att.timestamp,
                    status=att.status,
                    punch=att.punch,
                    punch_type=AttendancePunchType(att.punch).name
                )
                new_att.save()
                new_atts.append(new_att)
        except Exception as e:
            print(e)
    print(f"Successfully save {len(new_atts)} attendance records")


if __name__ == '__main__':
    db_config = load_config(filename=config_file, section="postgresql")
    client = connect_zkteco()

    users = fetch_users(client=client)
    save_users(users)

    attendances = fetch_attendances(client=client)
    save_attendances(attendances=attendances)
