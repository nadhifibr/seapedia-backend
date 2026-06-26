# Gunakan image Python versi ringan
FROM python:3.11-slim

# Set environment variables agar output log Python langsung muncul
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Buat dan pindah ke direktori kerja di dalam container
WORKDIR /app

# Install dependensi sistem yang dibutuhkan untuk database PostgreSQL (psycopg2)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements.txt
COPY requirements.txt /app/

# Install library python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file aplikasi ke dalam container
COPY . /app/

# (Opsional) Kumpulkan file statis (Whitenoise)
# RUN python manage.py collectstatic --noinput

# Beri tahu Docker bahwa aplikasi jalan di port 8000
EXPOSE 8000

# Perintah untuk menyalakan server menggunakan Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
