import os
import curses
import shutil

def draw_menu(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)

    current_dir = os.getcwd()
    selected_row = 0
    message = ""
    clipboard = None

    def get_icon(filename):
        if os.path.isdir(filename):
            return "📁"
        ext = filename.lower()
        if ext.endswith(".py"):
            return "💾"
        elif ext.endswith(".json"):
            return "🧾"
        elif ext.endswith(".txt"):
            return "📄"
        elif ext.endswith(".sh"):
            return "⚙️"
        elif ext.endswith(".md"):
            return "📝"
        elif ext.endswith((".zip", ".rar", ".7z")):
            return "🗜️"
        elif ext.endswith((".jpg", ".jpeg", ".png", ".gif")):
            return "🖼️"
        elif ext.endswith(".csv"):
            return "📊"
        elif ext.endswith(".pdf"):
            return "📕"
        elif ext.endswith((".html", ".htm")):
            return "🌐"
        elif ext.endswith(".js"):
            return "📜"
        elif ext.endswith(".ts"):
            return "🔷"
        elif ext.endswith(".log"):
            return "📋"
        elif ext.endswith((".mp3", ".wav")):
            return "🎵"
        elif ext.endswith((".mp4", ".mkv", ".avi")):
            return "🎞️"
        elif ext.endswith((".exe", ".bin")):
            return "💻"
        else:
            return "📦"

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        if height < 20 or width < 50:
            stdscr.addstr(0, 0, "Terminal size is too small! Resize and restart.", curses.color_pair(3))
            stdscr.refresh()
            stdscr.getch()
            return

        stdscr.addstr(1, 0, "═" * width, curses.color_pair(1))
        stdscr.addstr(2, 0, " zrfilemanager by.zamallrock ".center(width), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(3, 0, f" Current Directory: {current_dir} ".center(width), curses.color_pair(1))
        stdscr.addstr(4, 0, "═" * width, curses.color_pair(1))

        stdscr.addstr(6, 2, "Commands:", curses.color_pair(1) | curses.A_BOLD)
        commands = [
            ("'q'", "Quit"), ("'Enter'", "Open"), ("'Backspace'", "Go Back"),
            ("'c'", "Copy"), ("'v'", "Paste"), ("'d'", "Delete"),
            ("'n'", "New Folder"), ("'r'", "Rename")
        ]
        spacing = 22
        x = 4
        y = 7
        for i, (key, desc) in enumerate(commands):
            col = i % (width // spacing)
            row = i // (width // spacing)
            stdscr.addstr(y + row, x + col * spacing, f"{key:<7} {desc}", curses.color_pair(5))
        y += (len(commands) + (width // spacing) - 1) // (width // spacing) + 1

        if message:
            stdscr.addstr(y, 2, message, curses.color_pair(3 if "Error" in message else 4))
        y += 2

        try:
            items = os.listdir(current_dir)
        except PermissionError:
            items = []
        items.sort()
        items.insert(0, "..")

        max_items = height - y - 2
        start_index = max(0, selected_row - max_items + 1)
        visible_items = items[start_index:start_index + max_items]

        for idx, item in enumerate(visible_items):
            row = y + idx
            path = os.path.join(current_dir, item)
            icon = get_icon(path)
            display = f"{icon} {item}"
            if idx == selected_row - start_index:
                stdscr.addstr(row, 4, f"> {display}", curses.color_pair(2) | curses.A_REVERSE)
            else:
                stdscr.addstr(row, 4, f"  {display}", curses.color_pair(2))

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_UP and selected_row > 0:
            selected_row -= 1
        elif key == curses.KEY_DOWN and selected_row < len(items) - 1:
            selected_row += 1
        elif key in (curses.KEY_BACKSPACE, 127):
            current_dir = os.path.dirname(current_dir)
            selected_row = 0
        elif key in (ord('\n'), 10):
            selected_item = items[selected_row]
            selected_path = os.path.join(current_dir, selected_item)
            if os.path.isdir(selected_path):
                current_dir = selected_path
                selected_row = 0
            elif os.path.isfile(selected_path):
                curses.endwin()
                os.system(f"less '{selected_path}'")
                stdscr.getch()
        elif key == ord('c'):
            clipboard = os.path.join(current_dir, items[selected_row])
            message = f"Copied: {items[selected_row]}"
        elif key == ord('v') and clipboard:
            try:
                dest = os.path.join(current_dir, os.path.basename(clipboard))
                if os.path.isdir(clipboard):
                    shutil.copytree(clipboard, dest)
                else:
                    shutil.copy2(clipboard, dest)
                message = f"Pasted: {os.path.basename(clipboard)}"
            except Exception as e:
                message = f"Error: {e}"
        elif key == ord('d'):
            path = os.path.join(current_dir, items[selected_row])
            confirm = confirm_action(stdscr, items[selected_row])
            if confirm:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    message = f"Deleted: {items[selected_row]}"
                except Exception as e:
                    message = f"Error: {e}"
        elif key == ord('n'):
            name = get_input(stdscr, "Enter folder name:")
            if name:
                try:
                    os.makedirs(os.path.join(current_dir, name))
                    message = f"Folder created: {name}"
                except Exception as e:
                    message = f"Error: {e}"
        elif key == ord('r'):
            old = os.path.join(current_dir, items[selected_row])
            new = get_input(stdscr, f"Rename '{items[selected_row]}' to:")
            if new:
                try:
                    os.rename(old, os.path.join(current_dir, new))
                    message = f"Renamed to: {new}"
                except Exception as e:
                    message = f"Error: {e}"

def confirm_action(stdscr, item):
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(0, 0, f"zrfilemanager by.zamallrock".center(w), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 0, f"Delete '{item}'? (y/n): ", curses.color_pair(3))
        stdscr.refresh()
        k = stdscr.getch()
        if k == ord('y'):
            return True
        elif k == ord('n'):
            return False

def get_input(stdscr, prompt):
    curses.echo()
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, f"zrfilemanager by.zamallrock".center(w), curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 0, prompt, curses.color_pair(1))
    stdscr.refresh()
    result = stdscr.getstr(4, 0, 60).decode('utf-8')
    curses.noecho()
    return result.strip()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
