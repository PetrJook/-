import psycopg2
from config import host, user, password, db_name

conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)
cursor = conn.cursor()
#
# base_date = '06-12-21'  # this has to be any past monday of the upper week
#
# cursor.execute(f"""
# SELECT name, full_name, day, room_numb, start_time
# FROM timetable
# INNER JOIN subject on subject.subject_id = timetable.fk_subject_id
# INNER JOIN teachers on teachers.teacher_id = subject.fk_teacher_id
# WHERE
# CASE WHEN (current_date - date '{base_date}') % 14 < 7
#     THEN day < 7
#     ELSE day > 7
# END
# ORDER BY day ASC, start_time ASC
# """)
# records = cursor.fetchall()
# print(records)

# d = {"name":
#      1}
# print(d['name'])
# try:
#     cursor.execute("""
#     INSERT INTO teacher VALUES (13, 'Олег Олегович')
#     """)
#     conn.commit()
# except:
#     print('Pizdec')
cursor.execute("""
            SELECT MAX(timetable_id) FROM timetable
            """)
new_id = list(cursor.fetchall())
new_id[0] += 1
print(new_id)