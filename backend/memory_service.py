from backend.database import get_connection

def create_user():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users DEFAULT VALUES
    """)

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return user_id


def create_memory(user_id, object_name, location_name):
    connection = get_connection()
    cursor = connection.cursor()

    # 1. Find the object for this user
    cursor.execute(
        """
        SELECT id
        FROM objects
        WHERE user_id = ? AND name = ?
        """,
        (user_id, object_name)
    )

    object_row = cursor.fetchone()

    # 2. Create the object if it doesn't exist
    if object_row is None:
        cursor.execute(
            """
            INSERT INTO objects (user_id, name)
            VALUES (?, ?)
            """,
            (user_id, object_name)
        )

        object_id = cursor.lastrowid
    else:
        object_id = object_row["id"]

    # 3. Find the location for this user
    cursor.execute(
        """
        SELECT id
        FROM locations
        WHERE user_id = ? AND name = ?
        """,
        (user_id, location_name)
    )

    location_row = cursor.fetchone()

    # 4. Create the location if it doesn't exist
    if location_row is None:
        cursor.execute(
            """
            INSERT INTO locations (user_id, name)
            VALUES (?, ?)
            """,
            (user_id, location_name)
        )

        location_id = cursor.lastrowid
    else:
        location_id = location_row["id"]

    # 5. Create the memory event
    cursor.execute(
        """
        INSERT INTO memory_events
        (user_id, object_id, location_id, action, confidence, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, object_id, location_id, "placed", 1.0, "confirmed")
    )

    memory_id = cursor.lastrowid

    connection.commit()

    # 6. Retrieve the saved memory
    cursor.execute(
        """
        SELECT
            memory_events.id,
            objects.name AS object_name,
            locations.name AS location_name,
            memory_events.action,
            memory_events.confidence,
            memory_events.status,
            memory_events.created_at
        FROM memory_events
        JOIN objects ON memory_events.object_id = objects.id
        JOIN locations ON memory_events.location_id = locations.id
        WHERE memory_events.id = ?
        """,
        (memory_id,)
    )

    memory = cursor.fetchone()

    connection.close()

    return memory