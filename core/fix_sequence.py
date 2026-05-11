from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT setval(
            pg_get_serial_sequence('core_booking', 'id'),
            (SELECT MAX(id) FROM core_booking)
        );
    """)

print("Booking sequence fixed successfully!")
