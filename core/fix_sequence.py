from django.http import HttpResponse
from django.db import connection

def fix_sequence(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('core_booking', 'id'),
                COALESCE((SELECT MAX(id) FROM core_booking), 1),
                true
            );
        """)

    return HttpResponse("Booking sequence fixed!")
