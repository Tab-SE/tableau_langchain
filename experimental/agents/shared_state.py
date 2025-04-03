# shared_state.py
current_datasource_luid = None

def set_datasource_luid(luid: str):
    global current_datasource_luid
    current_datasource_luid = luid

def get_datasource_luid():
    return current_datasource_luid
