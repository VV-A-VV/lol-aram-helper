import queue
import threading
import time
import tkinter as tk
from typing import Callable

from .models import AppSnapshot, ChampionRecommendation, GamePhase
from .recommendations import AugmentRank


COLORS = {
    "bg": "#1a1a2e",
    "card_bg": "#16213e",
    "card_selected": "#0f3460",
    "tier_t1": "#FFD700",
    "tier_t2": "#C0C0C0",
    "tier_t3": "#CD7F32",
    "border_selected": "#00D9FF",
    "text_primary": "#FFFFFF",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
}


def rank_style(level: str, quintile: int | None = None) -> dict[str, str]:
    quintile_colors = {
        1: COLORS["tier_t1"],
        2: "#00FF00",
        3: "#38BDF8",
        4: "#F59E0B",
        5: "#EF4444",
    }

    if level == "best":
        return {"color": quintile_colors.get(quintile, COLORS["tier_t1"]), "prefix": "★"}
    if level == "recommended":
        return {"color": quintile_colors.get(quintile, "#00FF00"), "prefix": "●"}
    if level == "situational":
        return {"color": quintile_colors.get(quintile, "#7DD3FC"), "prefix": "◆"}
    return {"color": "#FF6666", "prefix": "○"}


def format_rank_line(slot_index: int, augment_text: str, rank: AugmentRank) -> str:
    style = rank_style(rank.level, rank.quintile)
    name = augment_text or "(未识别)"
    if rank.rank is None:
        suffix = "  未收录"
    else:
        suffix = f"  总排 #{rank.rank}/{rank.total} · {rank.quintile_label}"
    return f"{style['prefix']} {slot_index}. {name}{suffix}"


def build_rank_rows(champion: ChampionRecommendation, augments: tuple[str, ...], recommendation_engine) -> list[dict]:
    rows = []
    for index, augment in enumerate(augments, 1):
        rank = recommendation_engine.rank_augment(champion, augment)
        style = rank_style(rank.level, rank.quintile)
        rows.append(
            {
                "text": format_rank_line(index, augment, rank),
                "color": style["color"],
                "level": rank.level,
            }
        )
    return rows


def build_overlay_title(champion: ChampionRecommendation, scan_id: int) -> str:
    return f"{champion.name} 海克斯推荐 #{scan_id} (F6)"


class ChampionCard(tk.Frame):
    def __init__(self, parent, champion: ChampionRecommendation, is_selected=False):
        bg = COLORS["card_selected"] if is_selected else COLORS["card_bg"]
        super().__init__(parent, bg=bg)
        self.configure(
            relief="solid",
            borderwidth=2 if is_selected else 1,
            highlightbackground=COLORS["border_selected"] if is_selected else COLORS["card_bg"],
            highlightthickness=2 if is_selected else 0,
        )

        container = tk.Frame(self, bg=bg)
        container.pack(fill="both", expand=True, padx=8, pady=6)

        self._add_top_row(container, champion, is_selected, bg)
        self._add_augments(container, champion.augments, bg)
        self._add_items(container, champion.items, bg)

    def _add_top_row(self, container, champion: ChampionRecommendation, is_selected: bool, bg: str):
        top_row = tk.Frame(container, bg=bg)
        top_row.pack(fill="x")

        if is_selected:
            indicator = tk.Label(
                top_row,
                text=">>",
                fg=COLORS["border_selected"],
                bg=bg,
                font=("Consolas", 12, "bold"),
            )
            indicator.pack(side="left", padx=(0, 4))

        name = tk.Label(
            top_row,
            text=champion.name,
            fg=COLORS["text_primary"],
            bg=bg,
            font=("Microsoft YaHei UI", 11, "bold"),
        )
        name.pack(side="left")

        tier_color = COLORS.get(f"tier_{champion.tier.lower()}", COLORS["text_secondary"])
        tier = tk.Label(
            top_row,
            text=f"[{champion.tier}]",
            fg=tier_color,
            bg=bg,
            font=("Consolas", 10, "bold"),
        )
        tier.pack(side="left", padx=(6, 4))

        winrate = tk.Label(
            top_row,
            text=champion.winrate,
            fg=COLORS["text_secondary"],
            bg=bg,
            font=("Consolas", 10),
        )
        winrate.pack(side="left")

    def _add_augments(self, container, augments: tuple[str, ...], bg: str):
        if not augments:
            return

        row = tk.Frame(container, bg=bg)
        row.pack(fill="x", pady=(4, 0))
        label = tk.Label(
            row,
            text=" / ".join(augments),
            fg=COLORS["text_muted"],
            bg=bg,
            font=("Microsoft YaHei UI", 9),
            wraplength=470,
            justify="left",
        )
        label.pack(anchor="w")

    def _add_items(self, container, items: tuple[str, ...], bg: str):
        if not items:
            return

        row = tk.Frame(container, bg=bg)
        row.pack(fill="x", pady=(2, 0))
        label = tk.Label(
            row,
            text=" > ".join(items[:6]),
            fg=COLORS["text_primary"],
            bg=bg,
            font=("Microsoft YaHei UI", 9),
            wraplength=470,
            justify="left",
        )
        label.pack(anchor="w")


class AramHelperApp:
    def __init__(
        self,
        root,
        data_store,
        state_service,
        recommendation_engine,
        ocr_service_factory=None,
        update_data: Callable[[], object] | None = None,
        hotkey_service=None,
        scan_hotkey: str = "f6",
    ):
        self.root = root
        self.data_store = data_store
        self.state_service = state_service
        self.recommendation_engine = recommendation_engine
        self.ocr_service_factory = ocr_service_factory
        self.update_data = update_data
        self.hotkey_service = hotkey_service
        self.scan_hotkey = scan_hotkey
        self.ocr_overlay = None
        self.scan_id = 0
        self.scan_in_progress = False
        self.events = queue.Queue()
        self.cards = []
        self.ocr_panel = None
        self.ocr_result_labels = []
        self.current_snapshot: AppSnapshot | None = None
        self.last_render_key = None
        self.running = True

        self._build_ui()
        self._register_hotkey()

    def start(self):
        threading.Thread(target=self._poll_loop, daemon=True).start()
        self.root.after(100, self._drain_events)
        self.root.mainloop()

    def close(self):
        self.running = False
        if self.hotkey_service:
            self.hotkey_service.close()
        if self.ocr_overlay:
            self.ocr_overlay.destroy()
        self.root.destroy()

    def _register_hotkey(self):
        if not self.hotkey_service:
            return

        status = self.hotkey_service.register(
            self.scan_hotkey,
            lambda: self.events.put(("trigger_ocr", None)),
        )
        self.root.after(250, lambda: self.update_status(status.message))

    def _build_ui(self):
        self.root.title("LOL ARAM Helper")
        self.root.attributes("-topmost", True)
        self.root.geometry("520x650+50+50")
        self.root.configure(bg=COLORS["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        status_bar = tk.Frame(self.root, bg=COLORS["card_bg"], height=35)
        status_bar.pack(fill="x", padx=5, pady=(5, 0))
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar,
            text="状态: 连接中...",
            fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"],
            font=("Microsoft YaHei UI", 9),
        )
        self.status_label.pack(side="left", padx=10, pady=8)

        self.update_btn = tk.Button(
            status_bar,
            text="更新数据",
            command=self.on_update_clicked,
            bg=COLORS["card_selected"],
            fg=COLORS["text_primary"],
            font=("Microsoft YaHei UI", 9),
            relief="flat",
            cursor="hand2",
            padx=10,
        )
        self.update_btn.pack(side="right", padx=10, pady=6)

        canvas_frame = tk.Frame(self.root, bg=COLORS["bg"])
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.window_id, width=event.width),
        )

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

    def _poll_loop(self):
        while self.running:
            self.events.put(("snapshot", self.state_service.poll()))
            time.sleep(2)

    def _drain_events(self):
        while not self.events.empty():
            event_type, payload = self.events.get()
            if event_type == "snapshot":
                self._render_snapshot(payload)
            elif event_type == "ocr_result":
                scan_id, augments = payload
                self._handle_ocr_result(scan_id, augments)
            elif event_type == "ocr_error":
                self.scan_in_progress = False
                self.update_status(f"识别失败: {payload}")
                self.show_message_overlay("海克斯识别失败", str(payload), "#FF6666")
            elif event_type == "data_error":
                self._handle_data_error(payload)
            elif event_type == "data_updated":
                self._handle_data_updated(payload)
            elif event_type == "trigger_ocr":
                self.on_recognize_hextech()

        if self.running:
            self.root.after(100, self._drain_events)

    def _render_snapshot(self, snapshot: AppSnapshot):
        self.current_snapshot = snapshot
        status = snapshot.status
        if snapshot.phase == GamePhase.CHAMP_SELECT and snapshot.champion_ids:
            status = f"{snapshot.status} | {self.data_store.champion_count} 英雄"
        self.update_status(status)

        render_key = (snapshot.phase, snapshot.champion_ids, snapshot.selected_champion_id)
        if render_key == self.last_render_key:
            return

        self.last_render_key = render_key
        self.clear_content()

        if snapshot.phase in {GamePhase.DISCONNECTED, GamePhase.OTHER}:
            return

        for champion_id in snapshot.champion_ids:
            champion = self.data_store.get_champion(champion_id)
            card = ChampionCard(
                self.scrollable_frame,
                champion,
                is_selected=champion_id == snapshot.selected_champion_id,
            )
            card.pack(fill="x", pady=3)
            self.cards.append(card)

        if snapshot.phase == GamePhase.IN_PROGRESS and snapshot.selected_champion_id:
            self.create_ocr_panel()

    def clear_content(self):
        for card in self.cards:
            card.destroy()
        self.cards = []

        if self.ocr_panel:
            self.ocr_panel.destroy()
            self.ocr_panel = None
            self.ocr_result_labels = []

    def update_status(self, text: str):
        self.status_label.config(text=text)

    def create_ocr_panel(self):
        if self.ocr_panel:
            return

        self.ocr_panel = tk.Frame(self.scrollable_frame, bg=COLORS["card_bg"], relief="solid", borderwidth=1)
        self.ocr_panel.pack(fill="x", pady=(10, 3), padx=3)

        header = tk.Frame(self.ocr_panel, bg=COLORS["card_bg"])
        header.pack(fill="x", padx=10, pady=8)

        title = tk.Label(
            header,
            text="海克斯识别",
            fg=COLORS["text_primary"],
            bg=COLORS["card_bg"],
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        title.pack(side="left")

        button = tk.Button(
            header,
            text="识别",
            command=self.on_recognize_hextech,
            bg=COLORS["tier_t1"],
            fg="#000000",
            font=("Microsoft YaHei UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=3,
        )
        button.pack(side="right")

        self.ocr_result_frame = tk.Frame(self.ocr_panel, bg=COLORS["card_bg"])
        self.ocr_result_frame.pack(fill="x", padx=10, pady=(0, 8))

    def on_recognize_hextech(self):
        if self.scan_in_progress:
            self.show_message_overlay("海克斯识别中", "上一轮识别还没结束，请稍等。", COLORS["tier_t1"])
            return

        if not self.current_snapshot or not self.current_snapshot.selected_champion_id:
            self.update_status("错误: 未检测到当前英雄")
            self.show_message_overlay("无法识别海克斯", "未检测到当前英雄。请确认已进入对局，或从选人阶段启动助手。", "#FF6666")
            return
        if not self.ocr_service_factory:
            self.update_status("错误: OCR 模块未配置")
            self.show_message_overlay("无法识别海克斯", "OCR 模块未配置。", "#FF6666")
            return

        self.scan_id += 1
        scan_id = self.scan_id
        self.scan_in_progress = True
        self.update_status(f"识别中 #{scan_id}...")
        self.show_message_overlay("海克斯识别中", f"正在进行第 {scan_id} 次识别...", COLORS["tier_t1"])
        threading.Thread(target=self._ocr_worker, args=(scan_id,), daemon=True).start()

    def _ocr_worker(self, scan_id: int):
        try:
            ocr_service = self.ocr_service_factory()
            self.events.put(("ocr_result", (scan_id, ocr_service.recognize_augments())))
        except Exception as exc:
            self.events.put(("ocr_error", str(exc)))

    def _handle_ocr_result(self, scan_id: int, augments: tuple[str, ...]):
        self.scan_in_progress = False
        if not self.current_snapshot or not self.current_snapshot.selected_champion_id:
            return

        champion = self.data_store.get_champion(self.current_snapshot.selected_champion_id)
        rows = build_rank_rows(champion, tuple(augments), self.recommendation_engine)
        for label in self.ocr_result_labels:
            label.destroy()
        self.ocr_result_labels = []

        for row in rows:
            label = tk.Label(
                self.ocr_result_frame,
                text=row["text"],
                fg=row["color"],
                bg=COLORS["card_bg"],
                font=("Microsoft YaHei UI", 9, "bold"),
                anchor="w",
                wraplength=470,
                justify="left",
            )
            label.pack(fill="x", pady=2)
            self.ocr_result_labels.append(label)

        self.show_ocr_overlay(champion, rows, scan_id)
        self.update_status(f"识别完成 #{scan_id}")

    def show_message_overlay(self, title_text: str, message: str, color: str):
        if self.ocr_overlay:
            try:
                self.ocr_overlay.destroy()
            except Exception:
                pass

        overlay = tk.Toplevel(self.root)
        self.ocr_overlay = overlay
        overlay.title(title_text)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.9)
        overlay.configure(bg="#000000")
        overlay.overrideredirect(True)

        width = 620
        height = 130
        x = max((overlay.winfo_screenwidth() - width) // 2, 0)
        overlay.geometry(f"{width}x{height}+{x}+120")

        title = tk.Label(
            overlay,
            text=title_text,
            fg=color,
            bg="#000000",
            font=("Microsoft YaHei UI", 11, "bold"),
        )
        title.pack(pady=(16, 8))

        body = tk.Label(
            overlay,
            text=message,
            fg=COLORS["text_primary"],
            bg="#000000",
            font=("Microsoft YaHei UI", 9),
            wraplength=560,
            justify="left",
        )
        body.pack(padx=24)
        overlay.after(4000, self._destroy_ocr_overlay)

    def show_ocr_overlay(self, champion: ChampionRecommendation, rows: list[dict], scan_id: int):
        if self.ocr_overlay:
            try:
                self.ocr_overlay.destroy()
            except Exception:
                pass

        overlay = tk.Toplevel(self.root)
        self.ocr_overlay = overlay
        overlay.title("海克斯推荐")
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.9)
        overlay.configure(bg="#000000")
        overlay.overrideredirect(True)

        width = 620
        height = 190
        x = max((overlay.winfo_screenwidth() - width) // 2, 0)
        overlay.geometry(f"{width}x{height}+{x}+120")

        title = tk.Label(
            overlay,
            text=build_overlay_title(champion, scan_id),
            fg=COLORS["tier_t1"],
            bg="#000000",
            font=("Microsoft YaHei UI", 11, "bold"),
        )
        title.pack(pady=(12, 8))

        for row in rows:
            label = tk.Label(
                overlay,
                text=row["text"],
                fg=row["color"],
                bg="#000000",
                font=("Microsoft YaHei UI", 10, "bold"),
                wraplength=580,
                justify="left",
            )
            label.pack(anchor="w", padx=24, pady=2)

        hint = tk.Label(
            overlay,
            text="4 秒后自动关闭",
            fg="#888888",
            bg="#000000",
            font=("Microsoft YaHei UI", 8),
        )
        hint.pack(pady=(8, 0))
        overlay.after(4000, self._destroy_ocr_overlay)

    def _destroy_ocr_overlay(self):
        if not self.ocr_overlay:
            return
        try:
            self.ocr_overlay.destroy()
        finally:
            self.ocr_overlay = None

    def on_update_clicked(self):
        if not self.update_data:
            self.update_status("错误: 更新功能未配置")
            return

        self.update_btn.config(state="disabled", text="更新中...")
        threading.Thread(target=self._update_data_worker, daemon=True).start()

    def _update_data_worker(self):
        try:
            self.events.put(("data_updated", self.update_data()))
        except Exception as exc:
            self.events.put(("data_error", str(exc)))

    def _handle_data_updated(self, result):
        if result.ok:
            self.data_store.reload()
            self.last_render_key = None
            if self.current_snapshot:
                self._render_snapshot(self.current_snapshot)
            self.update_btn.config(text="更新成功", bg="#10b981")
            self.update_status(f"更新成功: {result.champion_count} 英雄")
        else:
            self.update_btn.config(text="更新失败", bg="#ef4444")
            self.update_status(f"更新失败: {result.message}")

        self.root.after(
            2000,
            lambda: self.update_btn.config(
                state="normal",
                text="更新数据",
                bg=COLORS["card_selected"],
            ),
        )

    def _handle_data_error(self, message: str):
        self.update_status(f"更新失败: {message}")
        self.update_btn.config(text="更新失败", bg="#ef4444")
        self.root.after(
            2000,
            lambda: self.update_btn.config(
                state="normal",
                text="更新数据",
                bg=COLORS["card_selected"],
            ),
        )
