# Use the official PostgreSQL image
FROM postgres:13

# Install dependencies including git and pgvector build tools
RUN apt-get update && \
    apt-get install -y \
    git \
    postgresql-server-dev-13 \
    build-essential && \
    apt-get clean

# Clone and install pgvector
RUN git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git /pgvector && \
    cd /pgvector && \
    make && \
    make install

# Set environment variables (not for sensitive data)
ENV POSTGRES_PASSWORD=mysecretpassword

EXPOSE 5432
