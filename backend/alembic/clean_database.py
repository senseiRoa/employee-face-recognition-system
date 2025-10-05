from sqlalchemy import create_engine, text
engine = create_engine('mysql+mysqldb://root:m634kkkd/*@host.docker.internal:3307/timeTrackerDB')

with engine.connect() as conn:
    # Listar todas las tablas
    result = conn.execute(text('SHOW TABLES'))
    tables = [row[0] for row in result]
    
    # Disable foreign key checks
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    
    # Drop todas las tablas
    for table in tables:
        try:
            conn.execute(text(f'DROP TABLE {table}'))
            print(f'Dropped table: {table}')
        except Exception as e:
            print(f'Error dropping {table}: {e}')
    
    # Re-enable foreign key checks
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
    conn.commit()

print('Database cleaned successfully')