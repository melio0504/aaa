from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List, Optional, Tuple

import tkinter as tk
from tkinter import filedialog

import pygame
import pygame_gui
import pygame_widgets
from pygame_widgets.slider import Slider

from canvas import Canvas, CanvasConfig
from tools import ToolState, update_position_from_keys, update_position_from_mouse, DEFAULT_COLORS
from ui import Button, draw_overlay, get_color_swatch_rect


WINDOW_SIZE = (1180, 820)
SIDEBAR_WIDTH = 240
PADDING = 20
GRID_SIZE = 80
FPS = 60
CANVAS_BACKGROUND = (255, 255, 255, 255)
CANVAS_BORDER = (228, 130, 1, 255)
SLIDER_VALUE_COLOR = (253, 211, 127)
SIDEBAR_BORDER_WIDTH = 4
APP_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(APP_DIR, "assets")
SAVE_DIR = os.path.join(ASSETS_DIR, "saved")
FONT_PATH = os.path.join(ASSETS_DIR, "font", "Stardew Valley ALL CAPS.ttf")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.jpeg")
LOGO_MAX_WIDTH = SIDEBAR_WIDTH


def load_font(path: str, size: int) -> pygame.font.Font:
    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.SysFont("DejaVu Sans", size)


def init_pygame() -> Tuple[pygame.Surface, pygame.time.Clock, pygame.font.Font, pygame.font.Font]:
    pygame.init()
    pygame.display.set_caption("Ateliera - Drawing and Painting App")
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("DejaVu Sans", 16)
    title_font = load_font(FONT_PATH, 56)
    return screen, clock, font, title_font


def init_background_music(assets_dir: str) -> None:
    music_path = os.path.join(assets_dir, "music", "bg.mp3")
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def compute_layout(window_size: Tuple[int, int]) -> Tuple[int, Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    available_size = (
        max(1, window_size[0] - SIDEBAR_WIDTH - 2 * PADDING),
        max(1, window_size[1] - 2 * PADDING),
    )
    pixel_scale = max(1, min(
        available_size[0] // GRID_SIZE,
        available_size[1] // GRID_SIZE,
    ))
    canvas_size = (GRID_SIZE * pixel_scale, GRID_SIZE * pixel_scale)
    canvas_offset = (
        SIDEBAR_WIDTH + PADDING + (available_size[0] - canvas_size[0]) // 2,
        PADDING + (available_size[1] - canvas_size[1]) // 2,
    )
    return pixel_scale, canvas_size, canvas_offset, available_size


def sanitize_filename(name: str) -> str:
    safe = "".join(ch for ch in name if ch.isalnum()
                   or ch in ("-", "_", " ")).strip()
    return safe.replace(" ", "_")


def prompt_filename(
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        font: pygame.font.Font,
        initial_text: str,
        hide_cursor_after: bool,
) -> Optional[str]:
    text = initial_text
    caret_index = len(text)
    active = True
    previous_repeat = pygame.key.get_repeat()
    pygame.key.set_repeat(250, 25)
    pygame.mouse.set_visible(True)
    pygame.key.start_text_input()
    try:
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.TEXTINPUT:
                    text = text[:caret_index] + event.text + text[caret_index:]
                    caret_index += len(event.text)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_RETURN:
                        cleaned = sanitize_filename(text)
                        if cleaned:
                            return cleaned
                        return None
                    if event.key == pygame.K_BACKSPACE:
                        if caret_index > 0:
                            text = text[:caret_index - 1] + text[caret_index:]
                            caret_index -= 1
                    elif event.key == pygame.K_LEFT:
                        caret_index = max(0, caret_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        caret_index = min(len(text), caret_index + 1)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    input_rect = pygame.Rect(244, 378, 692, 42)
                    if input_rect.collidepoint(event.pos):
                        rel_x = event.pos[0] - (input_rect.x + 12)
                        caret_index = len(text)
                        for i in range(len(text) + 1):
                            segment_width = font.size(text[:i])[0]
                            if segment_width >= rel_x:
                                caret_index = i
                                break

            screen.fill((250, 250, 252))
            prompt_rect = pygame.Rect(220, 300, 740, 180)
            pygame.draw.rect(screen, (255, 255, 255),
                             prompt_rect, border_radius=14)
            pygame.draw.rect(screen, (90, 90, 100),
                             prompt_rect, 2, border_radius=14)

            title_surface = font.render("Save drawing as", True, (40, 40, 45))
            help_surface = font.render(
                "Type a name and press Enter. Esc cancels.", True, (80, 80, 90))
            input_rect = pygame.Rect(
                prompt_rect.x + 24, prompt_rect.y + 78, prompt_rect.width - 48, 42)
            pygame.draw.rect(screen, (245, 245, 248),
                             input_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 120, 130),
                             input_rect, 2, border_radius=8)

            text_surface = font.render(text or " ", True, (40, 40, 45))
            screen.blit(title_surface,
                        (prompt_rect.x + 24, prompt_rect.y + 22))
            screen.blit(help_surface, (prompt_rect.x + 24, prompt_rect.y + 48))
            screen.blit(text_surface, (input_rect.x + 12, input_rect.y + 10))
            if not text:
                placeholder_surface = font.render(
                    "Type a file name...", True, (140, 140, 150))
                screen.blit(placeholder_surface,
                            (input_rect.x + 12, input_rect.y + 10))
            caret_x = input_rect.x + 12 + font.size(text[:caret_index])[0]
            caret_y = input_rect.y + 8
            pygame.draw.line(screen, (40, 40, 45),
                             (caret_x, caret_y), (caret_x, caret_y + 24), 2)

            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.key.stop_text_input()
        pygame.key.set_repeat(*previous_repeat)
        pygame.mouse.set_visible(not hide_cursor_after)


def main() -> None:
    screen, clock, font, title_font = init_pygame()
    large_font = pygame.font.SysFont("DejaVu Sans", 24)
    window_size = WINDOW_SIZE
    pixel_scale, canvas_size, canvas_offset, _ = compute_layout(window_size)
    canvas = Canvas(CanvasConfig(GRID_SIZE, GRID_SIZE,
                    CANVAS_BACKGROUND, canvas_size))
    tool_state = ToolState(background=canvas.config.background)
    manager = pygame_gui.UIManager(window_size)
    tk_root = tk.Tk()
    tk_root.withdraw()
    tk_root.attributes("-topmost", True)
    tk_root.update_idletasks()

    # Load UI assets (brush cursor)
    assets_dir = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "assets"))
    init_background_music(assets_dir)
    bg_path = os.path.join(assets_dir, "bg.jpeg")
    brush_path = os.path.join(assets_dir, "brushes", "paintbrush.png")
    logo_path = LOGO_PATH
    try:
        bg_source = pygame.image.load(bg_path).convert()
        bg_image = pygame.transform.smoothscale(bg_source, window_size)
    except Exception:
        bg_source = None
        bg_image = None
    canva_source = None
    canva_image = None
    try:
        brush_image = pygame.image.load(brush_path).convert_alpha()
        brush_image = pygame.transform.smoothscale(brush_image, (32, 32))
        pygame.mouse.set_visible(False)
    except Exception:
        brush_image = None
    try:
        logo_source = pygame.image.load(logo_path).convert()
        source_width, source_height = logo_source.get_size()
        scale_width = max(1, LOGO_MAX_WIDTH)
        scale_height = max(1, int(scale_width * (source_height / source_width)))
        logo_image = pygame.transform.smoothscale(
            logo_source, (scale_width, scale_height))
    except Exception:
        logo_image = None

    pen_pos = (GRID_SIZE // 2, GRID_SIZE // 2)
    shake_frames = 0
    shake_offsets: List[Tuple[int, int]] = []
    undo_history: List[pygame.Surface] = []
    drawing_session_active = False
    save_status_text: Optional[str] = None
    save_status_frames = 0
    color_picker_dialog: Optional[pygame_gui.windows.UIColourPickerDialog] = None
    gui_cursor_active = False
    brush_slider: Optional[Slider] = None
    brush_slider_rect = pygame.Rect(0, 0, 0, 0)
    brush_label_y = 0
    last_slider_value = tool_state.thickness
    swatch_size = 56

    def start_shake() -> None:
        nonlocal shake_frames, shake_offsets
        shake_frames = 18
        shake_offsets = [(6, -6), (-6, 6), (4, -4), (-4, 4)] * 5

    def reset_canvas() -> None:
        canvas.clear()

    def push_undo_state() -> None:
        if len(undo_history) >= 20:
            undo_history.pop(0)
        undo_history.append(canvas.surface.copy())

    def undo_last_action() -> None:
        nonlocal drawing_session_active, mouse_was_down
        if not undo_history:
            return
        canvas.surface.blit(undo_history.pop(), (0, 0))
        drawing_session_active = False
        mouse_was_down = False

    def open_color_picker() -> None:
        nonlocal color_picker_dialog, gui_cursor_active
        if color_picker_dialog is not None and color_picker_dialog.alive():
            return
        color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(
            rect=pygame.Rect((160, 50), (420, 400)),
            manager=manager,
            window_title="Choose Color",
        )
        if brush_image is not None:
            pygame.mouse.set_visible(True)
            gui_cursor_active = True

    last_saved_path: Optional[str] = None

    def save_canvas() -> None:
        nonlocal last_saved_path, save_status_text, save_status_frames
        name = prompt_filename(screen, clock, font, "",
                               hide_cursor_after=brush_image is not None)
        if not name:
            return
        os.makedirs(SAVE_DIR, exist_ok=True)
        path = os.path.join(SAVE_DIR, f"{name}.png")
        canvas.save(path)
        last_saved_path = path
        save_status_text = "Image successfully saved"
        save_status_frames = FPS * 2

    def load_canvas() -> None:
        nonlocal last_saved_path, save_status_text, save_status_frames
        os.makedirs(SAVE_DIR, exist_ok=True)
        tk_root.update()
        path = filedialog.askopenfilename(
            parent=tk_root,
            initialdir=SAVE_DIR,
            title="Load a saved drawing",
            filetypes=[("PNG images", "*.png"), ("All files", "*.*")],
        )
        if not path:
            return
        push_undo_state()
        if canvas.load(path):
            last_saved_path = path
            save_status_text = "Image successfully loaded"
            save_status_frames = FPS * 2
        else:
            undo_history.pop()

    def set_brush_mode() -> None:
        tool_state.eraser = False

    def build_sidebar_controls() -> None:
        nonlocal brush_slider, brush_slider_rect, brush_label_y, last_slider_value
        slider_rect = pygame.Rect(
            26, controls_top + 304, SIDEBAR_WIDTH - 52, 14)
        brush_slider_rect = slider_rect
        brush_label_y = controls_top + 270
        if brush_slider is None:
            brush_slider = Slider(
                screen,
                slider_rect.x,
                slider_rect.y,
                slider_rect.width,
                slider_rect.height,
                min=1,
                max=32,
                step=1,
                valueColour=SLIDER_VALUE_COLOR,
            )
            brush_slider.setValue(tool_state.thickness)
            last_slider_value = tool_state.thickness
        else:
            brush_slider.win = screen
            brush_slider.x = slider_rect.x
            brush_slider.y = slider_rect.y
            brush_slider.width = slider_rect.width
            brush_slider.height = slider_rect.height
            brush_slider.rect = pygame.Rect(
                slider_rect.x,
                slider_rect.y,
                slider_rect.width,
                slider_rect.height,
            )
            brush_slider.valueColour = SLIDER_VALUE_COLOR

    def sync_brush_slider() -> None:
        nonlocal last_slider_value
        if brush_slider is None:
            return
        current_value = int(brush_slider.getValue())
        if current_value != last_slider_value:
            tool_state.thickness = current_value
            last_slider_value = current_value

    button_width = SIDEBAR_WIDTH - 40
    controls_top = 148
    buttons = [
        Button(pygame.Rect(20, controls_top, button_width, 32),
               "Shake", "R", start_shake),
        Button(pygame.Rect(20, controls_top + 38, button_width, 32),
               "Save", "P", save_canvas),
        Button(pygame.Rect(20, controls_top + 76, button_width, 32),
               "Load", "L", load_canvas),
        Button(
            pygame.Rect(20, controls_top + 114, button_width, 32),
            "Brush",
            "B",
            set_brush_mode,
            is_active=lambda: not getattr(tool_state, "eraser", False),
        ),
        Button(
            pygame.Rect(20, controls_top + 152, button_width, 32),
            "Eraser",
            "X",
            lambda: tool_state.toggle_eraser(),
            is_active=lambda: getattr(tool_state, "eraser", False),
        ),
        Button(
            pygame.Rect(20, controls_top + 190, button_width, 32),
            "Color Picker",
            "C",
            open_color_picker,
        ),
    ]
    build_sidebar_controls()

    knobs = []

    running = True
    mouse_was_down = False
    canvas_rect = pygame.Rect(canvas_offset, canvas_size)

    def screen_to_grid(point: Tuple[int, int]) -> Tuple[int, int]:
        offset_x, offset_y = canvas_offset
        x, y = point
        return (x - offset_x) // pixel_scale, (y - offset_y) // pixel_scale
    while running:
        delta = clock.tick(FPS)
        time_delta = delta / 1000.0
        overlay_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, window_size[1])
        color_swatch_rect = get_color_swatch_rect(overlay_rect, swatch_size)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.VIDEORESIZE:
                min_width = SIDEBAR_WIDTH + 2 * PADDING + GRID_SIZE
                min_height = 2 * PADDING + GRID_SIZE
                window_size = (
                    max(min_width, event.w),
                    max(min_height, event.h),
                )
                screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                manager.set_window_resolution(window_size)
                manager.clear_and_reset()
                build_sidebar_controls()
                pixel_scale, canvas_size, canvas_offset, _ = compute_layout(
                    window_size)
                canvas.display_size = canvas_size
                canvas_rect = pygame.Rect(canvas_offset, canvas_size)
                if bg_source is not None:
                    bg_image = pygame.transform.smoothscale(
                        bg_source, window_size)
                if canva_source is not None:
                    canva_image = pygame.transform.smoothscale(
                        canva_source, canvas_size)
            manager.process_events(event)
            if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                selected = event.colour
                DEFAULT_COLORS.append(
                    (int(selected.r), int(selected.g), int(selected.b)))
                tool_state.color_index = len(DEFAULT_COLORS) - 1
            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if color_picker_dialog is not None and event.ui_element == color_picker_dialog:
                    color_picker_dialog = None
                    if brush_image is not None and gui_cursor_active:
                        pygame.mouse.set_visible(False)
                        gui_cursor_active = False
            for button in buttons:
                if button.handle_event(event):
                    break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if color_swatch_rect.collidepoint(event.pos):
                    open_color_picker()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_z and event.mod & pygame.KMOD_CTRL:
                    undo_last_action()
                    continue
                if event.key == pygame.K_r:
                    start_shake()
                if event.key == pygame.K_p:
                    save_canvas()
                if event.key == pygame.K_l:
                    load_canvas()
                if event.key == pygame.K_x:
                    # toggle eraser mode
                    tool_state.toggle_eraser()
                if event.key == pygame.K_c:
                    open_color_picker()
                if event.key == pygame.K_b:
                    set_brush_mode()
                if event.key == pygame.K_LEFTBRACKET:
                    step = 4 if event.mod & pygame.KMOD_SHIFT else 1
                    tool_state.adjust_thickness(-step)
                    if brush_slider is not None:
                        brush_slider.setValue(tool_state.thickness)
                        last_slider_value = tool_state.thickness
                if event.key == pygame.K_RIGHTBRACKET:
                    step = 4 if event.mod & pygame.KMOD_SHIFT else 1
                    tool_state.adjust_thickness(step)
                    if brush_slider is not None:
                        brush_slider.setValue(tool_state.thickness)
                        last_slider_value = tool_state.thickness
            if event.type == pygame.MOUSEWHEEL:
                # If the mouse is over a knob, let the knob handle the wheel (rotate + action)
                mx, my = pygame.mouse.get_pos()
                handled = False
                for knob in knobs:
                    if knob.is_point_over((mx, my)):
                        handled = True
                        # rotate knob for feedback
                        knob.angle = (knob.angle - event.y * 15) % 360
                        if knob.label == "Size":
                            # change thickness
                            tool_state.adjust_thickness(event.y)
                        break
                if not handled:
                    tool_state.adjust_thickness(event.y)
                    if brush_slider is not None:
                        brush_slider.setValue(tool_state.thickness)
                        last_slider_value = tool_state.thickness
        if brush_slider is not None:
            brush_slider.win = screen
            brush_slider.x = brush_slider_rect.x
            brush_slider.y = brush_slider_rect.y
            brush_slider.width = brush_slider_rect.width
            brush_slider.height = brush_slider_rect.height
            brush_slider.rect = pygame.Rect(
                brush_slider_rect.x,
                brush_slider_rect.y,
                brush_slider_rect.width,
                brush_slider_rect.height,
            )
        sync_brush_slider()

        keys = pygame.key.get_pressed()
        next_pos, moved = update_position_from_keys(
            pen_pos, keys, (GRID_SIZE, GRID_SIZE), tool_state.speed)
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        left_down = mouse_buttons[0]
        right_down = mouse_buttons[2]
        mouse_down = left_down or right_down
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_in_canvas = canvas_rect.collidepoint(mouse_screen_pos)
        mouse_pos = screen_to_grid(mouse_screen_pos)
        mouse_moved = False
        drawing_input_active = moved or (mouse_down and mouse_in_canvas)
        if drawing_input_active and not drawing_session_active:
            push_undo_state()
            drawing_session_active = True
        # If right button is held, treat as erasing regardless of toggle
        active_eraser = tool_state.eraser or right_down
        if mouse_down and mouse_in_canvas:
            if not mouse_was_down:
                pen_pos = mouse_pos
                draw_color = canvas.config.background if active_eraser else tool_state.color()
                canvas.draw_line(pen_pos, pen_pos, draw_color,
                                 tool_state.thickness)
            else:
                mouse_pos, mouse_moved = update_position_from_mouse(
                    pen_pos,
                    mouse_pos,
                    mouse_down,
                    (GRID_SIZE, GRID_SIZE),
                )
                if mouse_moved:
                    next_pos = mouse_pos
                    moved = True
        elif not drawing_input_active:
            drawing_session_active = False
        mouse_was_down = mouse_down

        if moved:
            draw_color = canvas.config.background if (
                tool_state.eraser) else tool_state.color()
            canvas.draw_line(pen_pos, next_pos, draw_color,
                             tool_state.thickness)
            pen_pos = next_pos

        if shake_frames > 0:
            shake_frames -= 1
            if shake_offsets:
                offset = shake_offsets.pop(0)
            else:
                offset = (0, 0)
            if shake_frames == 0:
                push_undo_state()
                reset_canvas()
        else:
            offset = (0, 0)

        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((250, 250, 252))
        pygame.draw.rect(screen, CANVAS_BACKGROUND[:3], pygame.Rect(
            0, 0, SIDEBAR_WIDTH, window_size[1]))
        pygame.draw.line(
            screen,
            CANVAS_BORDER[:3],
            (SIDEBAR_WIDTH, 0),
            (SIDEBAR_WIDTH, window_size[1]),
            SIDEBAR_BORDER_WIDTH,
        )
        canvas_pos = (canvas_offset[0] + offset[0],
                      canvas_offset[1] + offset[1])
        pygame.draw.rect(
            screen,
            CANVAS_BACKGROUND[:3],
            pygame.Rect(canvas_pos, canvas_size),
            border_radius=0,
        )
        canvas.blit_to(screen, canvas_pos)
        pygame.draw.rect(
            screen,
            CANVAS_BORDER[:3],
            pygame.Rect(canvas_pos, canvas_size),
            6,
            border_radius=0,
        )

        mode_label = "Erasure" if tool_state.eraser else "Drawing"
        info = [
            f"Mode: {mode_label}",
            f"Last save: {os.path.basename(
                last_saved_path) if last_saved_path else 'None'}",
        ]
        draw_overlay(
            screen,
            font,
            title_font,
            tool_state,
            buttons,
            knobs,
            info,
            overlay_rect,
            None,
        )

        if logo_image:
            logo_rect = logo_image.get_rect(topleft=(0, 0))
            screen.blit(logo_image, logo_rect)

        brush_label = f"Brush Size: {tool_state.thickness}"
        label_surface = large_font.render(brush_label, True, (0, 0, 0))
        label_rect = label_surface.get_rect(
            midtop=(overlay_rect.centerx, brush_label_y))
        screen.blit(label_surface, label_rect)

        if save_status_frames > 0 and save_status_text:
            status_surface = large_font.render(
                save_status_text, True, (25, 95, 45))
            status_bg = status_surface.get_rect(
                center=(SIDEBAR_WIDTH + (window_size[0] - SIDEBAR_WIDTH) // 2, 52))
            status_bg.inflate_ip(28, 18)
            pygame.draw.rect(screen, (235, 250, 238),
                             status_bg, border_radius=12)
            pygame.draw.rect(screen, (25, 95, 45),
                             status_bg, 2, border_radius=12)
            screen.blit(status_surface, status_surface.get_rect(
                center=status_bg.center))
            save_status_frames -= 1

        pygame_widgets.update(events)
        manager.update(time_delta)
        manager.draw_ui(screen)

        if color_picker_dialog is not None and not color_picker_dialog.alive():
            color_picker_dialog = None
            if brush_image is not None and gui_cursor_active:
                pygame.mouse.set_visible(False)
                gui_cursor_active = False

        # draw custom brush cursor if available and not using GUI cursor
        if brush_image and not gui_cursor_active:
            mx, my = pygame.mouse.get_pos()
            rect = brush_image.get_rect()
            pos = (mx - rect.width // 2, my - rect.height // 2)
            screen.blit(brush_image, pos)

        pygame.display.flip()

    if tk_root.winfo_exists():
        tk_root.destroy()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
