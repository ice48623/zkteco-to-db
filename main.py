import os
import argparse
from config import load_config
from const import AttendancePunchType
from excel_service import ExcelService
from mail_service import MailService
from model import psql_db, User, Attendance
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


def fetch_firmware(client: ZKTeco):
    print('fetching for device firmware information')
    firmware = client.get_firmware()
    print(f'device firmware: {firmware}')
    return firmware


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


def export_excel(start_date: str, end_date: str):
    service = ExcelService(start_date=start_date, end_date=end_date)
    service.export(output_path=f"รายงานการเข้างาน Amazon มศว - {start_date} - {end_date}.xlsx")


def export_and_send(start_date: str, end_date: str):
    config = load_config(filename=config_file, section="gmail")
    service = ExcelService(start_date=start_date, end_date=end_date)
    file_path = service.export(output_path=f"รายงานการเข้างาน Amazon มศว - {start_date} - {end_date}.xlsx")
    MailService.send_mail(
        to_email=config.get("to_email"),
        subject=config.get("subject"),
        message=config.get("message"),
        attachments=[file_path],
        host=config.get("host"),
        port=config.get("port"),
        from_email=config.get("from_email"),
        app_password=config.get("app_password")
    )
    if os.path.exists(file_path):
        os.remove(file_path)


def sync(client):
    users = fetch_users(client=client)
    save_users(users)

    attendances = fetch_attendances(client=client)
    save_attendances(attendances=attendances)


def init_database():
    print("Initializing database schema")
    psql_db.connect()
    psql_db.create_tables([Attendance, User])
    psql_db.close()
    print("Initializing Complete")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optional app description')
    db_config = load_config(filename=config_file, section="postgresql")
    client = connect_zkteco()

    parser.add_argument('option', type=str,
                        help='A required integer positional argument')

    parser.add_argument('start_date', type=str, nargs='?',
                        help='An optional integer positional argument')

    parser.add_argument('end_date', type=str, nargs='?',
                        help='An optional integer positional argument')
    args = parser.parse_args()

    if args.option == "sync":
        sync(client=client)

    if args.option == "test_connection":
        fetch_firmware(client=client)

    if args.option == "init_db":
        init_database()

    if args.option == "export":
        export_excel(start_date=args.start_date, end_date=args.end_date)

    if args.option == "export_and_send":
        export_and_send(start_date=args.start_date, end_date=args.end_date)
