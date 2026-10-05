#!/usr/bin/env python3
"""
Elevator log visualiser.
Usage:  python visualize.py [elevator_log.csv]
Default log file: elevator_log.csv

Controls:
  Play/Pause button  — start and stop playback
  Scrub slider       — jump to any point in the log
  Speed buttons      — 1x / 10x / 60x / 600x simulation speed
"""

import sys
import time as wall_clock
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider

ELEVATOR_NAMES = ['A', 'B', 'C']
MAX_FLOOR = 30
SHAFT_X = {'A': 1.0, 'B': 3.0, 'C': 5.0}
SHAFT_W = 1.4
CAR_H = 0.85
SPEEDS = [1, 10, 60, 600]
DEFAULT_SPEED = 10

CAR_COLORS = {
    'door_open': '#33cc55',
    'up':        '#3399ff',
    'down':      '#ff4433',
    'still':     '#888888',
}


# ------------------------------------------------------------------ data loading

def load_log(path):
    df = pd.read_csv(path)
    data = {}
    for name in ELEVATOR_NAMES:
        sub = df[df['elevator'] == name].sort_values('t').reset_index(drop=True)
        data[name] = {
            't':         sub['t'].values,
            'floor':     sub['floor'].values,
            'event':     sub['event'].values,
            'direction': sub['direction'].values,
        }
    return data, float(df['t'].max())


def state_at(data, name, sim_t):
    """Return (floor, color_key) for elevator `name` at simulation time sim_t."""
    d = data[name]
    idx = int(np.searchsorted(d['t'], sim_t, side='right')) - 1
    if idx < 0:
        return 0, 'still'
    floor = int(d['floor'][idx])
    event = str(d['event'][idx])
    direction = str(d['direction'][idx])
    if event == 'door_open':
        return floor, 'door_open'
    return floor, direction


# ------------------------------------------------------------------ visualiser

class Visualiser:
    def __init__(self, data, total_s):
        self.data = data
        self.total = total_s
        self.sim_t = 0.0
        self.playing = False
        self.speed = DEFAULT_SPEED
        self._wall_ref = None
        self._slider_busy = False

        self._build_ui()
        self._redraw()

        self._timer = self.fig.canvas.new_timer(interval=50)
        self._timer.add_callback(self._tick)
        self._timer.start()

    # ---------------------------------------------------------------- layout

    def _build_ui(self):
        self.fig = plt.figure(figsize=(10, 9), facecolor='#1a1a2e')

        # Building view
        self.ax = self.fig.add_axes([0.07, 0.20, 0.88, 0.72], facecolor='#0f0f23')
        self.ax.set_xlim(0, 6.5)
        self.ax.set_ylim(-1.2, MAX_FLOOR + 0.7)
        self.ax.set_yticks(range(0, MAX_FLOOR + 1, 5))
        self.ax.tick_params(axis='both', colors='#aaaacc', labelsize=9)
        self.ax.set_ylabel('Floor', color='#aaaacc', fontsize=10)
        for sp in self.ax.spines.values():
            sp.set_color('#2a2a4a')
        for f in range(0, MAX_FLOOR + 1):
            self.ax.axhline(f, color='#1e1e3a', linewidth=0.4, zorder=0)

        # Shaft backgrounds and elevator name labels
        for name, x in SHAFT_X.items():
            self.ax.add_patch(patches.Rectangle(
                (x - SHAFT_W / 2, -0.5), SHAFT_W, MAX_FLOOR + 1,
                facecolor='#0a0a1a', edgecolor='#2a2a5a', linewidth=1, zorder=1
            ))
            self.ax.text(x, -0.9, name, ha='center', va='center',
                         fontsize=14, fontweight='bold', color='white', zorder=5)

        # Elevator car patches — repositioned each frame, never recreated
        self._cars = {}
        self._car_labels = {}
        for name, x in SHAFT_X.items():
            car = patches.Rectangle(
                (x - SHAFT_W / 2 + 0.15, -CAR_H / 2),
                SHAFT_W - 0.3, CAR_H,
                facecolor=CAR_COLORS['still'], edgecolor='white', linewidth=1.5, zorder=3
            )
            self.ax.add_patch(car)
            lbl = self.ax.text(x, 0, '0', ha='center', va='center',
                               fontsize=9, fontweight='bold', color='white', zorder=4)
            self._cars[name] = car
            self._car_labels[name] = lbl

        self._title = self.ax.set_title(
            '', color='white', fontsize=12, pad=8, fontfamily='monospace'
        )

        # Colour legend
        legend_x = 0.72
        for i, (key, color) in enumerate(CAR_COLORS.items()):
            self.ax.add_patch(patches.Rectangle(
                (legend_x, MAX_FLOOR - 1.2 - i * 1.2), 0.3, 0.8,
                facecolor=color, edgecolor='white', linewidth=0.8, zorder=5
            ))
            self.ax.text(legend_x + 0.4, MAX_FLOOR - 0.8 - i * 1.2,
                         key.replace('_', ' '), va='center', fontsize=7,
                         color='#cccccc', zorder=5)

        # Time scrub slider
        ax_sl = self.fig.add_axes([0.10, 0.11, 0.80, 0.025], facecolor='#222244')
        self.slider = Slider(ax_sl, '', 0.0, self.total, valinit=0.0,
                             color='#3399ff', track_color='#222244')
        self.slider.valtext.set_visible(False)
        self.slider.label.set_visible(False)
        self.slider.on_changed(self._on_scrub)

        # Play/pause button
        ax_pp = self.fig.add_axes([0.10, 0.03, 0.13, 0.055])
        self._btn_play = Button(ax_pp, '▶  Play', color='#223366', hovercolor='#3355aa')
        self._btn_play.label.set_color('white')
        self._btn_play.on_clicked(self._toggle_play)

        # Speed buttons
        self._speed_btns = {}
        for i, s in enumerate(SPEEDS):
            ax_s = self.fig.add_axes([0.28 + i * 0.13, 0.03, 0.11, 0.055])
            active = (s == self.speed)
            btn = Button(ax_s, f'{s}×',
                         color='#334488' if active else '#222244',
                         hovercolor='#3355aa')
            btn.label.set_color('white')
            btn.on_clicked(lambda ev, sp=s: self._set_speed(sp))
            self._speed_btns[s] = btn

    # ---------------------------------------------------------------- update

    def _tick(self):
        if self.playing:
            now = wall_clock.monotonic()
            if self._wall_ref is not None:
                self.sim_t = min(self.sim_t + (now - self._wall_ref) * self.speed, self.total)
                if self.sim_t >= self.total:
                    self.playing = False
                    self._btn_play.label.set_text('▶  Play')
            self._wall_ref = now
        self._redraw()

    def _redraw(self):
        for name, x in SHAFT_X.items():
            floor, state = state_at(self.data, name, self.sim_t)
            color = CAR_COLORS.get(state, CAR_COLORS['still'])
            self._cars[name].set_y(floor - CAR_H / 2)
            self._cars[name].set_facecolor(color)
            self._car_labels[name].set_position((x, floor))
            self._car_labels[name].set_text(str(floor))

        h  = int(self.sim_t // 3600)
        m  = int((self.sim_t  % 3600) // 60)
        s  = int(self.sim_t  % 60)
        th = int(self.total   // 3600)
        tm = int((self.total  % 3600) // 60)
        ts = int(self.total  % 60)
        status = 'PLAYING' if self.playing else 'PAUSED '
        self._title.set_text(
            f'{status}   {h:02d}:{m:02d}:{s:02d} / {th:02d}:{tm:02d}:{ts:02d}   {self.speed}×'
        )

        self._slider_busy = True
        self.slider.set_val(self.sim_t)
        self._slider_busy = False

        self.fig.canvas.draw_idle()

    # ---------------------------------------------------------------- events

    def _toggle_play(self, _):
        self.playing = not self.playing
        if self.playing:
            self._wall_ref = wall_clock.monotonic()
            self._btn_play.label.set_text('⏸  Pause')
        else:
            self._btn_play.label.set_text('▶  Play')

    def _set_speed(self, speed):
        self.speed = speed
        for s, btn in self._speed_btns.items():
            btn.ax.set_facecolor('#334488' if s == speed else '#222244')

    def _on_scrub(self, val):
        if not self._slider_busy:
            self.sim_t = float(val)
            self._wall_ref = wall_clock.monotonic()


# ------------------------------------------------------------------ entry point

if __name__ == '__main__':
    log_path = sys.argv[1] if len(sys.argv) > 1 else 'elevator_log.csv'
    print(f'Loading {log_path} ...')
    data, total = load_log(log_path)
    n_events = sum(len(d['t']) for d in data.values())
    print(f'{n_events:,} events  |  duration {total / 3600:.2f} h')
    vis = Visualiser(data, total)
    plt.show()
