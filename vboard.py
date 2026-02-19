from mutterboard import MutterBoard
from gi.repository import Gtk


if __name__ == "__main__":
    win = MutterBoard()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.toggle_controls()
    Gtk.main()
