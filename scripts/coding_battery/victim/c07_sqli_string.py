def find_user(conn, username):
    q = "SELECT * FROM users WHERE name = '%s'" % username
    return conn.execute(q).fetchall()

def delete_by_id(conn, table, row_id):
    conn.execute("DELETE FROM %s WHERE id = %s" % (table, row_id))
