import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os

DATA_FILE = "travel_user.json"

TEMPLATES = {
    "Пляж": {
        "Документы": ["паспорт", "страховка", "билеты"],
        "Одежда": ["купальник/плавки", "панама", "сланцы", "пляжное полотенце"],
        "Гигиена": ["солнцезащитный крем", "шампунь", "зубная щётка", "влажные салфетки"]
    },
    "Поход": {
        "Документы": ["паспорт", "разрешение", "карта маршрута"],
        "Одежда": ["треккинговые ботинки", "термобельё", "дождевик", "флиска"],
        "Гигиена": ["антисептик", "туалетная бумага", "репеллент", "аптечка"]
    },
    "Командировка": {
        "Документы": ["паспорт", "командировочное", "билеты", "бронь отеля"],
        "Одежда": ["костюм", "рубашка", "туфли", "галстук"],
        "Гигиена": ["дезодорант", "бритва", "зубная паста", "расчёска"]
    }
}

class TravelChecklist:
    def __init__(self, root):
        self.root = root
        self.root.title("TravelPack — Чек-лист для путешествий")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f5f7fa")

        self.font_header = ("Segoe UI", 16, "bold")
        self.font_title = ("Segoe UI", 12, "bold")
        self.font_item = ("Segoe UI", 11)
        self.font_button = ("Segoe UI", 10)

        self.colors = {
            "bg": "#f5f7fa",
            "header": "#2c3e50",
            "header_text": "white",
            "panel": "#ffffff",
            "button_primary": "#3498db",
            "button_secondary": "#95a5a6",
            "button_success": "#2ecc71",
            "button_danger": "#e74c3c",
            "button_warning": "#e67e22",
            "frame_bg": "#ffffff",
            "frame_border": "#dcdde1",
            "text_primary": "#2c3e50",
            "text_secondary": "#7f8c8d"
        }

        self.user_template = self.load_user_template()
        self.check_vars = {}
        self.category_frames = {}

        # Верхний колонтитул
        header = tk.Frame(root, bg=self.colors["header"], height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="Чек-лист для путешествий", font=self.font_header,
                 fg=self.colors["header_text"], bg=self.colors["header"]).pack(expand=True)

        # Панель выбора шаблона
        template_frame = tk.Frame(root, bg=self.colors["panel"], pady=10, relief="flat", bd=1)
        template_frame.pack(fill="x", padx=20, pady=(10,5))

        tk.Label(template_frame, text="Шаблон:", font=self.font_title,
                 bg=self.colors["panel"], fg=self.colors["text_primary"]).pack(side="left", padx=10)

        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var,
                                           values=["Пляж", "Поход", "Командировка", "Пользовательский"],
                                           state="readonly", width=25, font=self.font_item)
        self.template_combo.pack(side="left", padx=10)
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)
        self.template_combo.current(0)

        self.save_user_btn = tk.Button(template_frame, text="Сохранить как пользовательский",
                                       command=self.save_as_user_template,
                                       bg=self.colors["button_primary"], fg="white",
                                       font=self.font_button, padx=12, pady=4, relief="flat")
        self.save_user_btn.pack(side="left", padx=10)

        # Панель действий
        actions_frame = tk.Frame(root, bg=self.colors["panel"], pady=8)
        actions_frame.pack(fill="x", padx=20, pady=5)

        btn_style = {"font": self.font_button, "padx": 10, "pady": 4, "relief": "flat", "fg": "white"}
        tk.Button(actions_frame, text="Отметить всё", command=self.check_all,
                  bg=self.colors["button_secondary"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Снять отметки", command=self.uncheck_all,
                  bg=self.colors["button_secondary"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Добавить категорию", command=self.add_category,
                  bg=self.colors["button_success"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Удалить категорию", command=self.delete_category,
                  bg=self.colors["button_warning"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Добавить вещь", command=self.add_item,
                  bg=self.colors["button_success"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Удалить вещь", command=self.delete_item,
                  bg=self.colors["button_warning"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Сохранить список", command=self.save_current_to_file,
                  bg=self.colors["button_primary"], **btn_style).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Очистить вещи", command=self.clear_all_items,
                  bg=self.colors["button_danger"], **btn_style).pack(side="left", padx=5)

        # Область с чек-листом (прокрутка)
        list_container = tk.Frame(root, bg=self.colors["bg"])
        list_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(list_container, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg"])
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.load_template("Пляж")

    # ---------- Загрузка и сохранение ----------
    def load_user_template(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_user_template(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_as_user_template(self):
        current = self.get_current_data()
        if not current:
            messagebox.showwarning("Нет данных", "Нечего сохранять.")
            return
        self.user_template = current
        self.save_user_template(current)
        messagebox.showinfo("Сохранено", "Пользовательский шаблон сохранён.")

    def on_template_selected(self, event=None):
        name = self.template_var.get()
        if name == "Пользовательский":
            if self.user_template:
                self.load_data(self.user_template)
            else:
                self.load_data({})
        else:
            self.load_template(name)

    def load_template(self, name):
        self.load_data(TEMPLATES[name])

    def load_data(self, data):
        self.display_checklist(data)

    # ---------- Отображение ----------
    def display_checklist(self, data):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.category_frames.clear()
        self.check_vars.clear()

        if not data:
            empty_label = tk.Label(self.scrollable_frame, text="Список пуст. Добавьте категории и вещи.",
                                   font=("Segoe UI", 14), fg=self.colors["text_secondary"], bg=self.colors["bg"])
            empty_label.pack(pady=50)
            return

        for cat, items in data.items():
            cat_frame = tk.LabelFrame(self.scrollable_frame, text=cat, font=self.font_title,
                                      bg=self.colors["frame_bg"], fg=self.colors["text_primary"],
                                      padx=12, pady=8, bd=1, relief="solid")
            cat_frame.pack(fill="x", expand=False, padx=5, pady=8)
            self.category_frames[cat] = cat_frame
            for item in items:
                var = tk.BooleanVar()
                cb = tk.Checkbutton(cat_frame, text=item, variable=var, anchor="w",
                                    font=self.font_item, bg=self.colors["frame_bg"],
                                    activebackground=self.colors["frame_bg"],
                                    selectcolor=self.colors["frame_bg"])
                cb.pack(fill="x", padx=5, pady=3)
                self.check_vars[(cat, item)] = var

    def get_current_data(self):
        result = {}
        for cat, frame in self.category_frames.items():
            items = []
            for child in frame.winfo_children():
                if isinstance(child, tk.Checkbutton):
                    items.append(child.cget("text"))
            result[cat] = items
        return result

    # ---------- Операции с категориями и вещами ----------
    def add_category(self):
        new_cat = simpledialog.askstring("Новая категория", "Введите название категории:")
        if not new_cat or not new_cat.strip():
            return
        new_cat = new_cat.strip()
        if new_cat in self.category_frames:
            messagebox.showerror("Ошибка", "Такая категория уже существует.")
            return
        current = self.get_current_data()
        current[new_cat] = []
        self.display_checklist(current)

    def delete_category(self):
        cats = list(self.category_frames.keys())
        if not cats:
            messagebox.showwarning("Нет категорий", "Нечего удалять.")
            return
        cat = simpledialog.askstring("Удаление категории", 
                                     f"Введите название категории для удаления:\n{', '.join(cats)}")
        if not cat or cat not in cats:
            messagebox.showerror("Ошибка", "Категория не найдена.")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить категорию '{cat}' вместе со всеми вещами?"):
            current = self.get_current_data()
            del current[cat]
            self.display_checklist(current)

    def add_item(self):
        cats = list(self.category_frames.keys())
        if not cats:
            messagebox.showwarning("Нет категорий", "Сначала создайте хотя бы одну категорию.")
            return
        cat = simpledialog.askstring("Выбор категории", f"Введите название категории из списка:\n{', '.join(cats)}")
        if not cat or cat not in cats:
            messagebox.showerror("Ошибка", "Категория не найдена.")
            return
        item = simpledialog.askstring("Новая вещь", "Введите название вещи:")
        if not item or not item.strip():
            return
        item = item.strip()
        current = self.get_current_data()
        if item in current.get(cat, []):
            messagebox.showwarning("Уже есть", f"'{item}' уже есть в категории '{cat}'.")
            return
        current[cat].append(item)
        self.display_checklist(current)

    def delete_item(self):
        """Удаление отдельной вещи: выбор категории, затем выбор вещи"""
        cats = list(self.category_frames.keys())
        if not cats:
            messagebox.showwarning("Нет категорий", "Нечего удалять.")
            return
        # Выбор категории
        cat = simpledialog.askstring("Удаление вещи", f"Введите категорию из списка:\n{', '.join(cats)}")
        if not cat or cat not in cats:
            messagebox.showerror("Ошибка", "Категория не найдена.")
            return
        # Получаем список вещей в этой категории
        current = self.get_current_data()
        items = current.get(cat, [])
        if not items:
            messagebox.showinfo("Нет вещей", f"В категории '{cat}' нет вещей.")
            return
        # Выбор вещи
        item = simpledialog.askstring("Удаление вещи", f"Введите название вещи из списка:\n{', '.join(items)}")
        if not item or item not in items:
            messagebox.showerror("Ошибка", "Вещь не найдена.")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить вещь '{item}' из категории '{cat}'?"):
            current[cat].remove(item)
            # Если категория стала пустой, можно оставить её пустой (пользователь сам решит)
            self.display_checklist(current)

    def check_all(self):
        for var in self.check_vars.values():
            var.set(True)

    def uncheck_all(self):
        for var in self.check_vars.values():
            var.set(False)

    def save_current_to_file(self):
        data = self.get_current_data()
        with open("saved_checklist.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Сохранено", "Список сохранён в файл saved_checklist.json")

    def clear_all_items(self):
        if not messagebox.askyesno("Очистка", "Удалить все вещи из всех категорий? Категории останутся."):
            return
        current = self.get_current_data()
        for cat in current:
            current[cat] = []
        self.display_checklist(current)

if __name__ == "__main__":
    root = tk.Tk()
    app = TravelChecklist(root)
    root.mainloop()
