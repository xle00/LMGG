import sqlite3

connector = sqlite3.connect('data\\config.db')
cursor = connector.cursor()


def rename_member(new_name, old_name):
    with connector:
        cursor.execute('update members set name = ? where name = ?', (new_name, old_name))
        cursor.execute('update members set r4_super = ? where r4_super = ?', (new_name, old_name))


def create_members_table():
    with connector:
        cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                       name TEXT,
                       is_r4 INTEGER,
                       r4_super TEXT
                       )
                        ''')


def create_config_table():
    with connector:
        cursor.execute('''CREATE TABLE IF NOT EXISTS config (
                       option TEXT,
                       value TEXT
                       )
                        ''')


def create_dates_table():
    with connector:
        cursor.execute('''CREATE TABLE IF NOT EXISTS dates(
                       date TEXT
                       )
                        ''')


def write_event_date(date):
    create_dates_table()
    dates = get_event_dates()
    if date not in dates:
        with connector:
            cursor.execute('insert into dates values (?)', (date,))


def get_event_dates():
    create_dates_table()
    result = cursor.execute('select date from dates order by date').fetchall()
    return [r[0] for r in result]


def remove_event_dates(dates_list: iter):
    dates = f"({','.join(['?'] * len(dates_list))})"
    with connector:
        cursor.execute(f'delete from dates where date in {dates}', dates_list)


def write_members(members: iter):
    create_members_table()
    existing_members = set(get_members_name())
    members_to_add = set(members)
    actual_members_to_add = members_to_add - existing_members
    with connector:
        for member in actual_members_to_add:
            query = 'insert into members values (?, ?, ?)'
            cursor.execute(query, (member, 0, ''))


'''def get_members_names():
    result = cursor.execute('select name from members').fetchall()
    return tuple(member[0] for member in result)'''


def get_admins():
    result = cursor.execute('select name from members where is_r4 = 1 order by name').fetchall()
    return tuple(name[0] for name in result)


def get_members(name_list=None):
    if not name_list:
        result = cursor.execute('select * from members where name is not null order by name').fetchall()
    else:
        names = [f'%{name}%' for name in name_list]
        result = []
        for name in names:
            members = cursor.execute('select * from members where name like ? order by name', (name,)).fetchall()
            result += list(set(members))
        result = list(set(result))
    return result


def get_members_name(name_list=None):
    return [member[0] for member in get_members(name_list)]


def update_member(name, is_r4, r4_super):
    with connector:
        cursor.execute('update members set is_r4 = ?, r4_super = ? where name = ?', (is_r4, r4_super, name))


def del_member(name):
    with connector:
        cursor.execute('update members set r4_super = "" where r4_super = ?', (name,))
        cursor.execute('delete from members where name = ?', (name,))


def get_configs():
    result = cursor.execute('select * from config').fetchall()
    result.sort(key=lambda i: i[0])
    return dict(option for option in result)


def get_config(name):
    return cursor.execute('select value from config where option = ?', (name,)).fetchone()[0]


def write_configs(name, value):
    with connector:
        cursor.execute('update config set value = ? where option = ?', (value, name))


def get_members_by_admin(admin):
    result = cursor.execute('select name from members where r4_super = ? order by name', (admin,)).fetchall()

    return [r[0] for r in result]


def get_monster_values():
    values = {}
    for i in range(1, 6):
        v = get_config(f'valor_lv_{i}',)
        values.update({i: int(v)})
    return values
