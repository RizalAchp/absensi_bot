import asyncio
import glfw
import imgui
import OpenGL.GL as gl
import webbrowser
from imgui import *
from imgui.integrations.glfw import *

from botpresensi import CompGui, DataGui
from botpresensi.bot import Bot, aiohttp


async def GUI(_bot: Bot):
    """main."""
    component = CompGui(imgui)
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    impl.refresh_font_texture()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        component.windowsize = glfw.get_window_size(window)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.4)
        imgui.core.style_colors_dark()
        imgui.new_frame()

        if _bot.status_login:
            mainWindow(component.flags, *component.windowsize)
        else:
            loginWindow(component.flags, *component.windowsize)

        # gl.glClearColor(0.3, 0.3, 0.3, 0.3)
        gl.glClearColor(0.18, 0.18, 0.18, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def menubar():
    if imgui.begin_menu('File', True):
        imgui.menu_item('New', 'Ctrl+N', False, True)
        imgui.menu_item('Open ...', 'Ctrl+O', False, True)
        if imgui.begin_menu('Open Recent', True):
            imgui.menu_item('doc.txt', None, False, True)
            imgui.end_menu()
        imgui.end_menu()


def settingup():
    pass

def visitlink(link: str):
    webbrowser.open(link)

def tabledata():
    """tabledata."""
    _w, _h= imgui.get_window_size()
    imgui.columns(5, 'NamaList')
    imgui.separator()
    imgui.set_column_offset(1, 40)
    imgui.text_colored("ID", 0.51, 0.67, 1)
    imgui.next_column()
    imgui.text_colored("Nama", 1.0, 0.325, 0.44)
    imgui.next_column()
    imgui.text_colored("Tanggal", 0.54, 0.866, 1.0)
    imgui.next_column()
    imgui.text_colored("Link", 0.54, 0.866, 1.0)
    imgui.set_column_width(3, _w*0.45)
    imgui.next_column()
    imgui.text_colored("VisitLink", 0.54, 0.866, 1.0)
    imgui.separator()
    _ii = 0
    for i in range(_data.matkul.__len__()):
        if _data.matkul[i].data:
            imgui.next_column()
            imgui.text_colored(str(i+1), 0.51, 0.67, 1)
            imgui.next_column()
            imgui.text_colored(_data.matkul[i].name, 1.0, 0.325, 0.44)
            imgui.next_column()
            for _v, _k in _data.matkul[i].data.items():
                imgui.text_colored(_v, 1.0, 0.8, 0.42)
                imgui.next_column()
                imgui.text_colored(_k, 0.54, 0.866, 1.0)
                imgui.next_column()
                if imgui.button("link {}".format(_ii)):
                    visitlink(_k)
                imgui.next_column()
                imgui.next_column()
                imgui.next_column()
                _ii += 1
            imgui.next_column()
            imgui.next_column()
    imgui.columns(1)


def loginWindow(flags, w: int, h: int):
    """welcomeWindow."""
    imgui.set_next_window_size(w*0.5, h*0.5)
    imgui.set_next_window_position(w*0.5, h*0.5)
    imgui.begin("MainWindow", flags=flags)
    if imgui.begin_child("Isikan Data Sesuai Akun JTI Anda",
                         float(w-20), float(h-100), border=True):
        imgui.text("nim")
        _, _data.credential.nim = imgui.input_text(
            'NIM:', _data.credential.nim,
            buffer_length=10
        )
        _, _data.credential.pswd = imgui.input_text(
            'Password:', _data.credential.pswd,
            buffer_length=20,
            flags=imgui.INPUT_TEXT_PASSWORD
        )
        _, _data.idx_prodi = imgui.combo(
            "Prodi: ", 0, _data.PRODI,
            flags=imgui.COMBO_HEIGHT_LARGE
        )
        _, _data.idx_gol = imgui.combo(
            "Golongan: ", 0, _data.GOL,
            flags=imgui.COMBO_HEIGHT_LARGE
        )
        if imgui.button("select"):
            _data.set_cred()
            settingup()

        imgui.end_child()
    imgui.end()


def mainWindow(flags, w: int, h: int):
    """mainWindow."""
    data = DataGui()
    imgui.set_next_window_size(w, h)
    imgui.set_next_window_position(0, 0)
    imgui.begin("MainWindow", flags=flags | imgui.WINDOW_MENU_BAR)
    if imgui.begin_menu_bar():
        menubar()
        imgui.end_menu_bar()
    if imgui.begin_child("Child 1", w*0.2, border=True,):
        imgui.columns(3)
        imgui.text("hai "+data.credential.nim)
        imgui.end_child()

    imgui.same_line(spacing=5)

    if imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.129, 0.129, 0.129):
        imgui.begin_child(
            "Child 2", w*0.8, border=True,
        )
        tabledata()
        imgui.pop_style_color()
        imgui.end_child()
    imgui.end()


def impl_glfw_init():
    """impl_glfw_init."""
    if not glfw.init():
        print("not initialize OpenGL context")
        exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(
        int(1000), int(600), "bot-presensi", None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("not initialize Window")
        exit(1)

    return window


async def start_gui():
    """Menjalankan Bot."""
    async with aiohttp.ClientSession() as req:
        bot = Bot(req)
        await GUI(bot)

_data = DataGui()
version = "1.0.beta"
