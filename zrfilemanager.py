import os
import curses
import shutil


def draw_menu(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Header
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # File/Folder list
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # Error message
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success message
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Highlighted keys
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Border

    current_dir = os.getcwd()
    selected_row = 0
    message = ""
    clipboard = None

    while True:
        stdscr.clear()

        # Periksa ukuran terminal
        height, width = stdscr.getmaxyx()
        if height < 20 or width < 50:
            stdscr.addstr(0, 0, "Terminal size is too small! Resize and restart.", curses.color_pair(3))
            stdscr.refresh()
            stdscr.getch()
            return

        # Header
        stdscr.addstr(1, 0, "═" * width, curses.color_pair(1))
        stdscr.addstr(2, 0, " zrfilemanager by.zamallrock ".center(width, " "), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(3, 0, f" Current Directory: {current_dir} ".center(width, " "), curses.color_pair(1))
        stdscr.addstr(4, 0, "═" * width, curses.color_pair(1))

        # Command instructions
        stdscr.addstr(6, 2, "Commands:", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(6, 14, "'q'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(6, 18, "Quit", curses.color_pair(1))
        stdscr.addstr(6, 26, "'Enter'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(6, 34, "Open", curses.color_pair(1))
        stdscr.addstr(6, 42, "'Backspace'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(6, 54, "Go Back", curses.color_pair(1))

        stdscr.addstr(7, 14, "'c'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(7, 18, "Copy", curses.color_pair(1))
        stdscr.addstr(7, 26, "'v'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(7, 30, "Paste", curses.color_pair(1))
        stdscr.addstr(7, 38, "'d'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(7, 42, "Delete", curses.color_pair(1))
        stdscr.addstr(7, 50, "'n'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(7, 54, "New Folder", curses.color_pair(1))
        stdscr.addstr(7, 62, "'r'", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(7, 66, "Rename", curses.color_pair(1))

        # Pesan status
        if message:
            stdscr.addstr(9, 2, f"{message}", curses.color_pair(3 if "Error" in message else 4))
        else:
            stdscr.addstr(9, 2, " " * (width - 4))

        # Dapatkan daftar file dan direktori
        try:
            items = os.listdir(current_dir)
        except PermissionError:
            items = []
        items.sort()
        items.insert(0, "..")  # Tambahkan opsi untuk kembali

        # Tampilkan daftar file dan direktori
        max_items = height - 12  # Batas maksimal item yang ditampilkan
        start_index = max(0, selected_row - max_items + 1)
        visible_items = items[start_index:start_index + max_items]

        for idx, item in enumerate(visible_items):
            row_pos = 11 + idx
            if idx == selected_row - start_index:
                stdscr.addstr(row_pos, 4, f"> {item}", curses.color_pair(2) | curses.A_REVERSE)
            else:
                stdscr.addstr(row_pos, 4, f"  {item}", curses.color_pair(2))

        stdscr.refresh()

        # Ambil input pengguna
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_UP and selected_row > 0:
            selected_row -= 1
        elif key == curses.KEY_DOWN and selected_row < len(items) - 1:
            selected_row += 1
        elif key == curses.KEY_BACKSPACE or key == 127:
            # Kembali ke direktori sebelumnya
            current_dir = os.path.dirname(current_dir)
            selected_row = 0
        elif key == ord('\n'):
            # Buka file atau navigasi direktori
            selected_item = items[selected_row]
            selected_path = os.path.join(current_dir, selected_item)

            if os.path.isdir(selected_path):
                current_dir = selected_path
                selected_row = 0
            elif os.path.isfile(selected_path):
                curses.endwin()
                os.system(f"less {selected_path}")
                stdscr.getch()  # Tunggu input setelah keluar dari "less"
        elif key == ord('c'):
            # Copy file atau folder
            selected_item = items[selected_row]
            clipboard = os.path.join(current_dir, selected_item)
            message = f"Copied: {selected_item}"
        elif key == ord('v') and clipboard:
            # Paste file atau folder
            destination = os.path.join(current_dir, os.path.basename(clipboard))
            try:
                if os.path.isdir(clipboard):
                    shutil.copytree(clipboard, destination)
                else:
                    shutil.copy2(clipboard, destination)
                message = f"Pasted: {os.path.basename(clipboard)}"
            except Exception as e:
                message = f"Error: {str(e)}"
        elif key == ord('d'):
            # Delete file atau folder
            selected_item = items[selected_row]
            selected_path = os.path.join(current_dir, selected_item)
            confirm_delete = confirm_action(stdscr, selected_item)
            if confirm_delete:
                try:
                    if os.path.isdir(selected_path):
                        shutil.rmtree(selected_path)
                    else:
                        os.remove(selected_path)
                    message = f"Deleted: {selected_item}"
                except Exception as e:
                    message = f"Error: {str(e)}"
            else:
                message = "Deletion canceled."
        elif key == ord('n'):
            folder_name = get_input(stdscr, "Enter folder name:")
            if folder_name:
                new_folder_path = os.path.join(current_dir, folder_name)
                try:
                    os.makedirs(new_folder_path)
                    message = f"Folder created: {folder_name}"
                except Exception as e:
                    message = f"Error: {str(e)}"
        elif key == ord('r'):
            # Rename file atau folder
            selected_item = items[selected_row]
            selected_path = os.path.join(current_dir, selected_item)
            new_name = get_input(stdscr, f"Rename '{selected_item}' to:")
            if new_name:
                new_path = os.path.join(current_dir, new_name)
                try:
                    os.rename(selected_path, new_path)
                    message = f"Renamed: {selected_item} to {new_name}"
                except Exception as e:
                    message = f"Error: {str(e)}"


def confirm_action(stdscr, item):
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"zrfilemanager by.zamallrock".center(curses.COLS), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 0, f"Are you sure you want to delete '{item}'? (y/n)", curses.color_pair(3))
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('y'):
            return True
        elif key == ord('n'):
            return False


def get_input(stdscr, prompt):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, f"zrfilemanager by.zamallrock".center(curses.COLS), curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(2, 0, prompt, curses.color_pair(1))
    stdscr.refresh()
    input_str = stdscr.getstr(4, 0, 60).decode('utf-8')
    curses.noecho()
    return input_str.strip()


def main():
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()