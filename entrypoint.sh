set -e

echo "⏳ Waiting for PostgreSQL..."
until python -c "
import os, psycopg2
psycopg2.connect(
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    port=os.environ.get('DB_PORT', '5432'),
)
" 2>/dev/null; do
  sleep 1
done
echo "✅ PostgreSQL is ready"

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting server..."
exec python manage.py runserver 0.0.0.0:8000