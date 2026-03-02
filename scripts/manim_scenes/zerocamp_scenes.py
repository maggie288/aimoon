"""
Manim scenes for Zero Camp episode 1–2 videos.
Render: manim -pql zerocamp_scenes.py PressureDecay ThermalBalance SolarPowerCurve
Output is copied to backend/media/videos/vid1.mp4, vid2.mp4, vid3.mp4 by render_manim_videos.py
"""
import numpy as np
from manim import *


class PressureDecay(Scene):
    """vid1: Pressure decay in closed cabin, gauge 101 kPa, time 0–6h, leak within limit."""
    def construct(self):
        title = Text("Pressure decay (leak within limit)", font_size=28).to_edge(UP)
        self.add(title)
        # Simple cabin outline
        cabin = Rectangle(width=3, height=2, color=BLUE_E, fill_opacity=0.3)
        cabin.move_to(LEFT * 2.5)
        gauge_label = Text("101 kPa", font_size=24).next_to(cabin, RIGHT, buff=0.5)
        self.add(cabin, gauge_label)
        # Time axis 0–6h（include_numbers=True 需系统安装 LaTeX；无 LaTeX 时用 False）
        axis = NumberLine(
            x_range=[0, 6, 1],
            length=4,
            include_numbers=False,
            include_ticks=True,
            label_direction=DOWN,
        ).to_edge(DOWN)
        time_label = Text("Time (h)", font_size=20).next_to(axis, DOWN)
        self.add(axis, time_label)
        self.wait(3)


class ThermalBalance(Scene):
    """vid2: Cabin with sun side (orange), space side (blue), heat flow balance."""
    def construct(self):
        title = Text("Thermal balance: sun vs deep space", font_size=28).to_edge(UP)
        self.add(title)
        cabin = Rectangle(width=3, height=2, color=GREY_BROWN, fill_opacity=0.5)
        cabin.move_to(ORIGIN)
        sun_side = Text("Sun", font_size=24, color=ORANGE).next_to(cabin, LEFT, buff=0.3)
        space_side = Text("Space", font_size=24, color=BLUE_D).next_to(cabin, RIGHT, buff=0.3)
        heat_in = Arrow(LEFT, RIGHT, color=ORANGE, max_tip_length_to_length_ratio=0.2).next_to(cabin, LEFT, buff=0.1)
        heat_out = Arrow(RIGHT, LEFT, color=BLUE_D, max_tip_length_to_length_ratio=0.2).next_to(cabin, RIGHT, buff=0.1)
        self.add(cabin, sun_side, space_side, heat_in, heat_out)
        balance = Text("Heating = Cooling", font_size=22, color=GREEN).to_edge(DOWN)
        self.add(balance)
        self.wait(3)


class SolarPowerCurve(Scene):
    """vid3: Solar array deployment and first-day power curve (design vs actual 67%)."""
    def construct(self):
        title = Text("Solar power: design vs actual (67%)", font_size=26).to_edge(UP)
        self.add(title)
        # Simple axes
        axes = Axes(
            x_range=[0, 24, 4],
            y_range=[0, 90, 30],
            x_length=5,
            y_length=3,
            axis_config={"include_numbers": False, "include_tip": True},
        ).to_edge(DOWN, buff=0.8)
        x_lab = Text("Time (h)", font_size=20).next_to(axes, DOWN)
        y_lab = Text("Power (kW)", font_size=20).next_to(axes, LEFT).rotate(PI/2)
        self.add(axes, x_lab, y_lab)
        # Design curve ~78 kW peak
        design = axes.plot(lambda x: 78 * (0.4 + 0.6 * np.sin(PI * x / 24)), x_range=[0, 24], color=GREEN)
        design_lab = Text("Design", font_size=18, color=GREEN).to_corner(UR, buff=0.5)
        # Actual curve ~67%
        actual = axes.plot(lambda x: 52 * (0.4 + 0.6 * np.sin(PI * x / 24)), x_range=[0, 24], color=YELLOW)
        actual_lab = Text("Actual 67%", font_size=18, color=YELLOW).next_to(design_lab, DOWN, buff=0.2)
        self.add(design, actual, design_lab, actual_lab)
        losses = Text("Dust · Temp · Angle", font_size=16, color=GREY_A).to_edge(DOWN, buff=0.2)
        self.add(losses)
        self.wait(4)
