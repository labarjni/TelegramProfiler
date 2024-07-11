import configparser
import getpass
import logging
import time

import flet as ft
import tkinter as tk

import os
import subprocess

dropdown = None

config = configparser.ConfigParser()

telegram_path = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'Telegram.exe')

if os.path.exists('config.ini'):
    config.read('config.ini')
    if os.path.exists(telegram_path) and config.getboolean("Settings", "OpenTelegramOnRun"):
        os.startfile(telegram_path)

    if config.getboolean("Settings", "DebugLogs"):
        logging.basicConfig(filename="debug.log", level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
else:
    config['Settings'] = {
        'OpenTelegramOnRun': str(False),
        'DebugLogs': str(False)
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def main(page: ft.Page):
    global telegram_path

    page.title = "Telegram Profiler"
    page.padding = 50
    page.window.height = 400
    page.window.width = 400
    page.window.resizable = False
    page.bgcolor = "#18191d"

    def openTelegramOnRun_change(e):
        config['Settings']['OpenTelegramOnRun'] = str(OpenTelegramOnRun.value)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def debugLogs_change(e):
        config['Settings']['DebugLogs'] = str(DebugLogs.value)
        if DebugLogs.value:
            logging.basicConfig(filename="debug.log", level=logging.DEBUG,
                                format='%(asctime)s - %(levelname)s - %(message)s')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def select_tdata_folder(event):

        subprocess.run(["taskkill", "/f", "/im", "Telegram.exe"])

        selected_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Telegram Desktop\\" + event.control.value
        current_tdata_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Telegram Desktop\\tdata"
        if os.path.isdir(current_tdata_folder):
            name = get_folder_name(current_tdata_folder)
            if name == "tdata":
                name = get_unique_name(current_tdata_folder)
            save_name_to_file(current_tdata_folder, name)
            os.rename(current_tdata_folder,
                      f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Telegram Desktop\\{name}")
        time.sleep(1)
        os.rename(selected_folder, current_tdata_folder)
        subprocess.Popen(telegram_path)
        if os.path.exists('config.ini'):
            if config.getboolean("Settings", "DebugLogs"):
                logging.debug("Telegram Desktop profile changed to %s", selected_folder)
        event.control.update()

        update_folder_dropdown()

    def get_unique_name(folder_path):
        name_file = folder_path + "\\name.txt"
        if os.path.isfile(name_file):
            with open(name_file, "r") as f:
                names = f.readlines()
                if names:
                    name = names[0].strip()
                    with open(name_file, "w") as f:
                        f.writelines(names[1:])
                    return name

    def save_name_to_file(folder_path, name):
        with open(os.path.join(folder_path, "name.txt"), "w") as f:
            f.write(name)

    def get_folder_name(folder_path):
        return os.path.basename(folder_path)

    def update_folder_dropdown():
        global dropdown

        folders = [
            folder
            for folder in os.listdir(
                f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Telegram Desktop"
            )
            if "@" in folder
        ]

        dropdown_options = [
            ft.dropdown.Option(folder)
            for folder in folders
        ]

        if dropdown is not None:
            dropdown.options = dropdown_options
            dropdown.update()
            return

        newDropdown = ft.Dropdown(
            options=dropdown_options,
            label="Profile",
            on_change=select_tdata_folder,
            width=200,
            height=40,
            color="#e9e8e8",
            bgcolor="#282e33"
        )

        dropdown = newDropdown
        page.add(ft.Container(content=newDropdown, padding=20, alignment=ft.alignment.center))

    def add_profile(e):
        def save_profile():
            profile_name = entry.get()
            new_profile_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Telegram Desktop\\tdata@{profile_name}"
            if not os.path.exists(new_profile_folder):

                os.makedirs(new_profile_folder)
                save_name_to_file(new_profile_folder, f"tdata@{profile_name}")

                if os.path.exists('config.ini'):
                    if config.getboolean("Settings", "DebugLogs"):
                        logging.debug("Added new Telegram Desktop profile: %s", f"tdata@{profile_name}")

                update_folder_dropdown()
                window.destroy()
            else:
                error_label.config(text="Profile already exists!")

        window = tk.Tk()
        window.title("New profile")
        window.geometry("300x100")

        label = tk.Label(window, text="Enter profile name:")
        label.pack()

        entry = tk.Entry(window)
        entry.pack()

        button = tk.Button(window, text="Create", command=save_profile)
        button.pack()

        error_label = tk.Label(window, text="", fg="red")
        error_label.pack()

        window.mainloop()

    add_profile_button = ft.ElevatedButton(
        text="Add profile",
        on_click=add_profile,
        width=210,
        height=40,
        color="#e9e8e8",
        bgcolor="#282e33",
        icon=ft.icons.ADD
    )

    OpenTelegramOnRun = ft.Checkbox(
        label="Open Telegram Desktop on run",
        on_change=openTelegramOnRun_change
    )
    DebugLogs = ft.Checkbox(
        label="Enable debug logs",
        on_change=debugLogs_change
    )

    update_folder_dropdown()
    page.add(ft.Container(content=OpenTelegramOnRun, alignment=ft.alignment.center))
    page.add(ft.Container(content=DebugLogs, alignment=ft.alignment.center))
    page.add(ft.Container(content=add_profile_button, padding=20, alignment=ft.alignment.center))


ft.app(target=main)
