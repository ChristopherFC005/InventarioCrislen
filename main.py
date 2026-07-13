from app.database import init_database
from app.ui import CrislenApp

if __name__ == "__main__":
    init_database()
    CrislenApp().mainloop()
