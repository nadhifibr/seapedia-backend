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

# Kumpulkan file statis (Whitenoise)
RUN python manage.py collectstatic --noinput

# --- HUGGING FACE SPACES CONFIGURATION ---
# Hugging Face mengharuskan port 7860
EXPOSE 7860

# Hugging Face menjalankan container sebagai non-root user (UID 1000)
# Jadi kita harus memberikan akses penuh ke folder /app
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

USER user

# Jalankan server Gunicorn di port 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "core.wsgi:application"]
