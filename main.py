from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from datetime import datetime

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Alternatively, restrict to specific origins
# CORS(app, origins=["http://localhost:3000", "http://example.com"])

# PostgreSQL Connection Pool
DB_POOL = pool.SimpleConnectionPool(
    1,
    10,  # 최소 1, 최대 10개의 연결 유지
    dbname="mydb",
    user="myuser",
    password="mypassword",
    host="localhost",
    port=5432,
)


@app.route("/search_hospitals", methods=["GET", "OPTIONS"])
def search_hospitals():
    try:
        # 요청 파라미터 가져오기
        latitude = float(request.args.get("latitude"))
        longitude = float(request.args.get("longitude"))
        radius = float(request.args.get("radius"))  # 반경 (미터 단위)
        max_results = int(request.args.get("max_results", 30))  # Default to 30 results
        keyword = request.args.get("keyword", "").strip()

        # PostgreSQL 연결 가져오기
        conn = DB_POOL.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if not keyword:
            # PostGIS ST_DWithin을 사용하여 검색 반경 내 병원 검색
            query = """
            SELECT
                address,
                zipcode,
                name,
                TO_CHAR(last_modified_date, 'YYYY-MM-DD') AS last_modified_date,
                TO_CHAR(updated_date, 'YYYY-MM-DD') AS updated_date,
                department_content,
                ST_AsGeoJSON(geom) AS location
            FROM medical_institutions
            WHERE ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326),
                %s
            )
            LIMIT %s;
            """
            cursor.execute(query, (longitude, latitude, radius, max_results))
        else:
            # 키워드 제공됨: 위치 & 유사도 기반 검색
            query = """
            SELECT
                address,
                zipcode,
                name,
                last_modified_date,
                updated_date,
                department_content,
                ST_AsGeoJSON(geom) AS location,
                similarity(COALESCE(name, '') || ' ' || COALESCE(address, '') || ' ' || COALESCE(department_content, ''), %s) AS similarity_score
            FROM medical_institutions
            WHERE ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326),
                %s
            )
            ORDER BY similarity_score DESC
            LIMIT %s;
            """
            cursor.execute(query, (keyword, longitude, latitude, radius, max_results))

        results = cursor.fetchall()

        # 결과를 JSON 형태로 변환
        hospitals = []
        for row in results:
            # Null 값 제거
            hospital = {k: v for k, v in row.items() if v is not None}
            hospitals.append(hospital)

        # PostgreSQL 연결 반납
        cursor.close()
        DB_POOL.putconn(conn)

        # 결과 반환
        return jsonify({"status": "success", "data": hospitals}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/search_by_keyword", methods=["GET", "OPTIONS"])
def search_by_keyword():
    try:
        # 요청 파라미터 가져오기
        keyword = request.args.get("keyword", "").strip()
        max_results = int(request.args.get("max_results", 30))  # 최대 반환 개수

        if not keyword:
            return (
                jsonify(
                    {"status": "error", "message": "Keyword parameter is required"}
                ),
                400,
            )

        # PostgreSQL 연결
        conn = DB_POOL.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 유사도 검색 쿼리 (tsvector와 pg_trgm 활용)
        query = """
        SELECT
            address,
            zipcode,
            name,
            last_modified_date,
            updated_date,
            department_content,
            ST_AsGeoJSON(geom) AS location,
            similarity(COALESCE(name, '') || ' ' || COALESCE(address, '') || ' ' || COALESCE(department_content, ''), %s) AS similarity_score
        FROM medical_institutions
        ORDER BY similarity_score DESC
        LIMIT %s;
        """
        cursor.execute(query, (keyword, max_results))
        results = cursor.fetchall()

        # 결과를 JSON 형태로 변환
        hospitals = []
        for row in results:
            # Null 값 제거
            hospital = {k: v for k, v in row.items() if v is not None}
            hospitals.append(hospital)

        # PostgreSQL 연결 반납
        cursor.close()
        DB_POOL.putconn(conn)

        # 결과 반환
        return jsonify({"status": "success", "data": hospitals}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
