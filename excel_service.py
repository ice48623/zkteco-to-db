from collections import defaultdict

import pandas as pd
from datetime import datetime, date, timedelta

from pandas import DataFrame

from model import psql_db, User, Attendance


class ExcelService:
    def __init__(self, start_date: str = None, end_date: str = None, working_hour: int = 9):
        start_date_str = start_date if start_date else self.get_default_start_date_string()
        end_date_str = end_date if end_date else self.get_default_end_date_string()
        self.start_date = self.parse_date_from_string(start_date_str)
        self.end_date = self.parse_date_from_string(end_date_str)
        self.working_hour = timedelta(hours=working_hour)

    def get_default_start_date_string(self) -> str:
        today = datetime.now()
        month = today.month - 1
        year = today.year
        return f'26-{month}-{year}'

    def get_default_end_date_string(self) -> str:
        today = datetime.now()
        month = today.month
        year = today.year
        return f'10-{month}-{year}'

    def parse_date_from_string(self, date_str: str) -> date:
        # Date pattern = '04-12-2024'
        return datetime.strptime(date_str, '%d-%m-%Y').date()

    def load_data(self, start_date: date, end_date: date):
        end_date = end_date + timedelta(days=1) # offset for end_date not inclusive
        records = (Attendance
                   .select(Attendance, User)
                   .join(User)
                   .where(Attendance.timestamp.between(start_date, end_date))
                   .order_by(User.name, Attendance.timestamp.asc())
                   )
        return records

    def calculate_actual_working_hours(self, start_time: timedelta, end_time: timedelta):
        working_hours = end_time - start_time
        hours, remainder = divmod(working_hours.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return '{:02d}'.format(hours), '{:02d}'.format(minutes)

    def calculate_ot(self, start_time: timedelta, end_time: timedelta):
        actual_working_hours = end_time - start_time
        if actual_working_hours <= self.working_hour:
            return '{:02d}'.format(0), '{:02d}'.format(0)
        ot = actual_working_hours - self.working_hour
        hours, remainder = divmod(ot.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return '{:02d}'.format(hours), '{:02d}'.format(minutes)

    def prepare_data(self, data):
        columns = ['ชื่อ', 'วันที่', 'เวลาเข้า', 'เวลาออก', 'เวลาทำงาน', 'ล่วงเวลา (OT)']
        # Group by name and date
        grouped = defaultdict(lambda: defaultdict(list))

        for record in data:
            name = record.user_id.name
            timestamp = pd.to_datetime(record.timestamp)
            date = timestamp.date()
            grouped[name][date].append(timestamp)

        # Process data into rows
        rows = []

        for name, dates in grouped.items():
            for date, times in dates.items():
                times.sort()
                check_in = times[0]
                check_out = times[-1]
                wh_hours, wh_minutes = self.calculate_actual_working_hours(start_time=check_in, end_time=check_out)
                actual_working_hours = f"{wh_hours}:{wh_minutes}"
                ot_hours, ot_minutes = self.calculate_ot(check_in, check_out)
                overtime = f"{ot_hours}:{ot_minutes}"
                rows.append({
                    'ชื่อ': name,
                    'วันที่': date,
                    'เวลาเข้า': check_in.time(),
                    'เวลาออก': check_out.time(),
                    'เวลาทำงาน': actual_working_hours,
                    'ล่วงเวลา (OT)': overtime
                })
        return rows, columns

    def generate_excel(self, data: list, columns: list, output_path: str, sheet_name: str):
        df = DataFrame(data=data, columns=columns)
        writer = pd.ExcelWriter(output_path)
        df.to_excel(writer, sheet_name=sheet_name, index=False, na_rep='NaN')

        # Set auto column width
        for column in df:
            column_length = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)

        writer.close()

    def prepare_raw_data(self, records):
        columns = ['ชื่อ', 'เวลาเข้า']
        data = []
        for record in records:
            data.append([record.user_id.name, record.timestamp])
        return data, columns

    def export(self, output_path: str = 'output.xlsx'):
        records = self.load_data(start_date=self.start_date, end_date=self.end_date)
        data, columns = self.prepare_data(data=records)
        self.generate_excel(data=data, columns=columns, output_path=output_path, sheet_name='attendance')
        # raw_data, raw_columns = self.prepare_raw_data(records=records)
        # self.generate_excel(data=raw_data, columns=raw_columns, output_path="test.xlsx", sheet_name='attendance')
        return output_path
