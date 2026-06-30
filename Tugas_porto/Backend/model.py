import os
import sqlite3
import time
import logging
from typing import Optional

from Backend.config import Config
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _pool = None
    _pool_error = None
    _engine = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None and self._pool_error is None:
            if Config.DB_TYPE == 'mysql':
                try:
                    import mysql.connector
                    from mysql.connector import pooling

                    self._engine = 'mysql'
                    self._pool = pooling.MySQLConnectionPool(
                        pool_name='portfolio_pool',
                        pool_size=5,
                        pool_reset_session=True,
                        **Config.MYSQL_CONFIG
                    )
                    self._initialize_mysql()
                except Exception as exc:
                    self._pool_error = str(exc)
                    logger.warning('MySQL unavailable. %s', exc)
                    if Config.DB_FALLBACK_TO_SQLITE:
                        self._engine = None
                    else:
                        self._engine = None
            if self._engine is None:
                self._engine = 'sqlite'
                os.makedirs(os.path.dirname(Config.DB_PATH) or '.', exist_ok=True)
                self._initialize_sqlite()

    def _initialize_mysql(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL UNIQUE,
                    nama_lengkap VARCHAR(255) NULL,
                    nama_panggilan VARCHAR(255) NULL,
                    tempat_lahir VARCHAR(255) NULL,
                    tanggal_lahir DATE NULL,
                    email VARCHAR(255) NULL,
                    telepon VARCHAR(50) NULL,
                    universitas VARCHAR(255) NULL,
                    fakultas VARCHAR(255) NULL,
                    prodi VARCHAR(255) NULL,
                    semester VARCHAR(50) NULL,
                    alamat TEXT NULL,
                    foto_url VARCHAR(500) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    posisi VARCHAR(255) NOT NULL,
                    perusahaan VARCHAR(255) NOT NULL,
                    durasi VARCHAR(100) NOT NULL,
                    deskripsi TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT fk_experiences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    judul VARCHAR(255) NOT NULL,
                    deskripsi TEXT NOT NULL,
                    gambar_url VARCHAR(500) NULL,
                    link_project VARCHAR(500) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    nama_skill VARCHAR(255) NOT NULL,
                    icon_class VARCHAR(255) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT fk_skills_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute(
                'INSERT IGNORE INTO users (username, password_hash, role) VALUES (%s, %s, %s)',
                ('admin', generate_password_hash('password123'), 'admin')
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()

    def _initialize_sqlite(self):
        conn = self._get_sqlite_connection()
        try:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    nama_lengkap TEXT,
                    nama_panggilan TEXT,
                    tempat_lahir TEXT,
                    tanggal_lahir TEXT,
                    email TEXT,
                    telepon TEXT,
                    universitas TEXT,
                    fakultas TEXT,
                    prodi TEXT,
                    semester TEXT,
                    alamat TEXT,
                    foto_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    posisi TEXT NOT NULL,
                    perusahaan TEXT NOT NULL,
                    durasi TEXT NOT NULL,
                    deskripsi TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    judul TEXT NOT NULL,
                    deskripsi TEXT NOT NULL,
                    gambar_url TEXT,
                    link_project TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nama_skill TEXT NOT NULL,
                    icon_class TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            ''')
            conn.execute(
                'INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                ('admin', generate_password_hash('password123'), 'admin')
            )
            conn.commit()
        finally:
            conn.close()

    def _get_sqlite_connection(self):
        conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def get_connection(self):
        if self._engine == 'sqlite':
            return self._get_sqlite_connection()
        if self._pool is None:
            raise ConnectionError(
                f'Database connection is unavailable. Check your MySQL/TiDB server and config. Details: {self._pool_error or "unknown error"}'
            )
        return self._pool.get_connection()

    def execute_query(self, query, params=None, fetch=False):
        start_time = time.time()
        conn = self.get_connection()
        try:
            if self._engine == 'sqlite':
                normalized_query = query.replace('%s', '?')
                cursor = conn.execute(normalized_query, params or ())
                if fetch:
                    result = [dict(row) for row in cursor.fetchall()]
                else:
                    conn.commit()
                    result = cursor.lastrowid if cursor.lastrowid else True
            else:
                cursor = conn.cursor(dictionary=True)
                if params is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = cursor.lastrowid if cursor.lastrowid else True
            elapsed = time.time() - start_time
            logger.debug('Query executed in %.3fs: %s...', elapsed, query[:50])
            return result
        except Exception as e:
            if self._engine == 'sqlite':
                conn.rollback()
            else:
                conn.rollback()
            raise e
        finally:
            if self._engine == 'sqlite':
                conn.close()
            else:
                cursor.close()
                conn.close()
