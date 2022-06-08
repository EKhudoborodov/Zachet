import requests, psycopg2, datetime, cv2

#URL = "http://127.0.0.1:8000"

def test_root_route():
    result = requests.get("http://127.0.0.1:8000/")
    assert result.status_code == 200

def test_server_404():
    result = requests.get("http://127.0.0.1:8000/something")
    assert result.status_code == 404
    
def database_exist():
    conn = psycopg2.connect(database="yolo_db",
                                user="postgres",
                                password="postgres",
                                host="localhost",
                                port="5432",
                                connect_timeout=5)
    conn.close()
    assert conn == None
    
def database_insert():
    conn = psycopg2.connect(dbname="yolo_db",
                                user="postgres", 
                                password="postgres", 
                                host="localhost", 
                                port="5432")
    cursor = conn.cursor()
    test_time = str(datetime.datetime.now())
    cursor.execute(f"INSERT INTO public.events (event_time, event_type, event_details, isdeleted) VALUES ('{test_time}', 'Test', 'Test done')")
    cursor.execute(f"SELECT event_time, event_type, event_details FROM public.events WHERE event_time='{test_time}' AND event_type='Test' AND event_details='Test done'")
    records = list(cursor.fetchall())
    assert records[0] == f"('{test_time}', 'Test', 'Test done')"
    
def database_stranght_insert():
    conn = psycopg2.connect(dbname="yolo_db",
                                user="postgres", 
                                password="postgres", 
                                host="localhost", 
                                port="5432")
    cursor = conn.cursor()
    test_time = str(datetime.datetime.now())
    cursor.execute(f"INSERT INTO public.events (event_time, event_type, event_details, isdeleted) VALUES ('{test_time}', 'Server test', 'Zivotnozodstvo norm tema')")
    cursor.execute(f"SELECT event_time, event_type, event_details FROM public.events WHERE event_time='{test_time}' AND event_type='Server test' AND event_details='Zivotnozodstvo norm tema'")
    records = list(cursor.fetchall())
    assert records[0] == f"('{test_time}', 'Server test', 'Zivotnozodstvo norm tema')"
    
def html_exists():
    res = os.path.exsits('templates/index.html')
    assert res == True
    
def weights_exist():
    res = os.path.exists('best_3.pt')
    assert res == True
