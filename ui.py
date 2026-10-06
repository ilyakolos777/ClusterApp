import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSlider, QFrame, QTabWidget, QTextBrowser
)
from PyQt6.QtCore import Qt

from data_provider import get_dataset
from kmeans import KMeansClustering
from maximin import MaximinClustering


class ClusterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кластерный анализ: Экспертная система")
        self.resize(1350, 800)

        self.COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        self.dataset = get_dataset()

        self.kmeans = KMeansClustering(k=3)
        self.kmeans.fit(self.dataset)

        self.maximin = MaximinClustering(alpha=0.4)
        self.maximin.fit(self.dataset)

        self._setup_styles()
        self._build_ui()
        self._update_plots()

    def _setup_styles(self):
        pg.setConfigOption('background', '#0f0f11')
        pg.setConfigOption('foreground', '#a1a1aa')
        pg.setConfigOptions(antialias=True)
        self.setStyleSheet("""
            QMainWindow { background-color: #09090b; }
            QLabel { color: #e4e4e7; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QLabel#title { font-size: 16px; font-weight: bold; color: #60a5fa; margin-bottom: 5px; }
            QFrame#card { background-color: #18181b; border-radius: 8px; border: 1px solid #27272a; padding: 10px; }
            QComboBox { background-color: #0f0f11; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 6px; }
            QTabWidget::pane { border: 1px solid #27272a; background: #18181b; border-radius: 6px; }
            QTabBar::tab { background: #0f0f11; color: #a1a1aa; padding: 10px 20px; font-weight: bold; }
            QTabBar::tab:selected { background: #18181b; color: #60a5fa; border-bottom: 2px solid #3b82f6; }
            QTextBrowser { background-color: #0f0f11; color: #e4e4e7; border: 1px solid #27272a; padding: 15px; border-radius: 6px; }
        """)

    def _create_slider_group(self, label_text, min_val, max_val, default_val):
        layout = QVBoxLayout()
        header = QHBoxLayout()
        lbl_title = QLabel(label_text)
        lbl_val = QLabel(str(default_val))
        lbl_val.setStyleSheet("color: #3b82f6; font-weight: bold;")
        header.addWidget(lbl_title)
        header.addStretch()
        header.addWidget(lbl_val)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(int(min_val * 10), int(max_val * 10))
        slider.setValue(int(default_val * 10))

        slider.valueChanged.connect(lambda v: lbl_val.setText(str(v / 10.0)))
        slider.valueChanged.connect(self._update_plots)

        layout.addLayout(header)
        layout.addWidget(slider)
        return layout, slider

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        left_frame = QFrame()
        left_frame.setObjectName("card")
        left_frame.setFixedWidth(320)
        left_layout = QVBoxLayout(left_frame)

        lbl_inst = QLabel("ЧТО У ВАС ЗДЕСЬ ПРОИСХОДИТ???")
        lbl_inst.setObjectName("title")
        left_layout.addWidget(lbl_inst)

        instruction = QLabel(
            "Программа разделяет базу автомобилей на группы "
            "(кластеры) на основе их скрытых закономерностей.\n\n"
            "Ваша задача:\n"
            "1. Изменяйте параметры новой машины ползунками ниже.\n"
            "2. Выбирайте оси для просмотра графика.\n"
            "3. Смотрите на панель справа: система автоматически "
            "объяснит, к какому типу относится машина."
        )
        instruction.setWordWrap(True)
        instruction.setStyleSheet("color: #a1a1aa; margin-bottom: 15px;")
        left_layout.addWidget(instruction)

        lbl_axes = QLabel("1. ПРОЕКЦИЯ ГРАФИКА")
        lbl_axes.setObjectName("title")
        left_layout.addWidget(lbl_axes)

        self.cb_x = QComboBox()
        self.cb_y = QComboBox()
        axes = ["X1: Мощность (л.с.)", "X2: Расход (л/100км)", "X3: Разгон (с)"]
        self.cb_x.addItems(axes)
        self.cb_y.addItems(axes)
        self.cb_y.setCurrentIndex(1)
        self.cb_x.currentIndexChanged.connect(self._update_plots)
        self.cb_y.currentIndexChanged.connect(self._update_plots)
        left_layout.addWidget(self.cb_x)
        left_layout.addWidget(self.cb_y)
        left_layout.addSpacing(15)

        lbl_test = QLabel("2. ПАРАМЕТРЫ НОВОЙ МАШИНЫ")
        lbl_test.setObjectName("title")
        left_layout.addWidget(lbl_test)

        l1, self.sl_power = self._create_slider_group("Мощность (л.с.):", 50, 800, 250)
        l2, self.sl_cons = self._create_slider_group("Расход (л):", 4, 30, 10.5)
        l3, self.sl_accel = self._create_slider_group("Разгон (с):", 2, 16, 6.5)

        left_layout.addLayout(l1)
        left_layout.addLayout(l2)
        left_layout.addLayout(l3)
        left_layout.addStretch()
        main_layout.addWidget(left_frame)

        center_frame = QFrame()
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        self.plot_kmeans = pg.PlotWidget()
        self.plot_kmeans.showGrid(x=True, y=True, alpha=0.15)
        self.plot_kmeans.addLegend(offset=(15, 15))
        self.tabs.addTab(self.plot_kmeans, "Алгоритм K-Средних")

        self.plot_maximin = pg.PlotWidget()
        self.plot_maximin.showGrid(x=True, y=True, alpha=0.15)
        self.plot_maximin.addLegend(offset=(15, 15))
        self.tabs.addTab(self.plot_maximin, "Алгоритм Максимина")

        self.tabs.currentChanged.connect(self._update_plots)
        center_layout.addWidget(self.tabs)
        main_layout.addWidget(center_frame, stretch=1)

        right_frame = QFrame()
        right_frame.setObjectName("card")
        right_frame.setFixedWidth(350)
        right_layout = QVBoxLayout(right_frame)

        lbl_verdict = QLabel("ЖИВАЯ АНАЛИТИКА")
        lbl_verdict.setObjectName("title")
        right_layout.addWidget(lbl_verdict)

        self.txt_verdict = QTextBrowser()
        self.txt_verdict.setOpenExternalLinks(True)
        right_layout.addWidget(self.txt_verdict)
        main_layout.addWidget(right_frame)

    def _get_cluster_semantic_name(self, centroid):
        if centroid[0] > 350:
            return "Спорткары (Высокая мощность)"
        elif centroid[0] < 150:
            return "Городские авто (Экономичные)"
        else:
            return "Средний класс (Универсальные)"

    def _generate_verdict(self, model, pred_idx, distance):
        method_name = "K-Средних" if self.tabs.currentIndex() == 0 else "Максимина"
        c_name = self._get_cluster_semantic_name(model.centroids[pred_idx])
        pred_color = self.COLORS[pred_idx % len(self.COLORS)]

        if distance < 50:
            conf_text = "ВЫСОКАЯ (Ядро кластера)"
            conf_color = "#10b981"
        elif distance < 150:
            conf_text = "СРЕДНЯЯ (Периферия)"
            conf_color = "#f59e0b"
        else:
            conf_text = "НИЗКАЯ (Аномалия)"
            conf_color = "#ef4444"

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; color: #e4e4e7;">
            <div style="color: #71717a; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;">Активный алгоритм</div>
            <div style="color: #60a5fa; font-size: 18px; font-weight: bold;">{method_name}</div>

            <hr style="border: none; border-bottom: 1px solid #27272a; margin: 15px 0;">

            <div style="color: #71717a; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Вердикт экспертной системы</div>

            <div style="background-color: #09090b; padding: 12px; border-left: 5px solid {pred_color}; margin-bottom: 15px;">
                <span style="font-size: 15px; font-weight: bold; color: {pred_color};">{c_name}</span>
            </div>

            <table style="width: 100%; font-size: 13px; margin-bottom: 15px;">
                <tr>
                    <td style="color: #a1a1aa; padding-bottom: 6px;">Дистанция до центра:</td>
                    <td style="text-align: right; font-weight: bold; color: #e4e4e7; padding-bottom: 6px;">{distance:.1f} ед.</td>
                </tr>
                <tr>
                    <td style="color: #a1a1aa;">Уверенность:</td>
                    <td style="text-align: right; font-weight: bold; color: {conf_color};">{conf_text}</td>
                </tr>
            </table>

            <hr style="border: none; border-bottom: 1px solid #27272a; margin: 15px 0;">
            <div style="color: #71717a; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Профиль кластеров ({len(model.centroids)})</div>
        """

        for i, c in enumerate(model.centroids):
            name = self._get_cluster_semantic_name(c)
            items = len(model.clusters[i])
            color = self.COLORS[i % len(self.COLORS)]
            html += f"""
            <div style="margin-bottom: 12px; background-color: #09090b; padding: 10px;">
                <div style="font-weight: bold; color: {color}; font-size: 13px; margin-bottom: 4px;">Кластер {i + 1}: {name}</div>
                <div style="font-size: 12px; color: #a1a1aa; line-height: 1.4;">
                    • Объем группы: <b>{items} шт.</b><br>
                    • Центр масс: {c[0]:.0f} л.с. | {c[1]:.1f} л. | {c[2]:.1f} сек.
                </div>
            </div>
            """

        html += "</div>"
        self.txt_verdict.setHtml(html)

    def _draw_plot(self, plot_widget, model):
        if not hasattr(plot_widget, 'custom_items'):
            plot_widget.custom_items = []
        for item in plot_widget.custom_items:
            plot_widget.removeItem(item)
        plot_widget.custom_items.clear()

        if plot_widget.plotItem.legend:
            plot_widget.plotItem.legend.clear()

        idx_x = self.cb_x.currentIndex()
        idx_y = self.cb_y.currentIndex()

        plot_widget.setLabel('bottom', self.cb_x.currentText())
        plot_widget.setLabel('left', self.cb_y.currentText())

        for c_idx, items in model.clusters.items():
            color = self.COLORS[c_idx % len(self.COLORS)]
            points = [(item.power, item.consumption, item.acceleration) for item in items]

            x_vals = [pt[idx_x] for pt in points]
            y_vals = [pt[idx_y] for pt in points]

            scatter = plot_widget.plot(
                x_vals, y_vals, pen=None, symbol='o', symbolSize=14,
                symbolBrush=color, name=f"Кластер {c_idx + 1}"
            )
            plot_widget.custom_items.append(scatter)

            cx = model.centroids[c_idx][idx_x]
            cy = model.centroids[c_idx][idx_y]
            cross = plot_widget.plot(
                [cx], [cy], pen=None, symbol='+', symbolSize=22,
                symbolPen=pg.mkPen(color, width=3)
            )
            plot_widget.custom_items.append(cross)

        test_pt = (self.sl_power.value() / 10.0, self.sl_cons.value() / 10.0, self.sl_accel.value() / 10.0)
        pred_idx, distance = model.predict(test_pt)
        pred_color = self.COLORS[pred_idx % len(self.COLORS)]

        star = plot_widget.plot(
            [test_pt[idx_x]], [test_pt[idx_y]],
            pen=None, symbol='star', symbolSize=24,
            symbolBrush='#ffffff', symbolPen=pg.mkPen(pred_color, width=2),
            name="Новая машина"
        )
        plot_widget.custom_items.append(star)

        if model.centroids:
            cx = model.centroids[pred_idx][idx_x]
            cy = model.centroids[pred_idx][idx_y]
            line = plot_widget.plot(
                [test_pt[idx_x], cx], [test_pt[idx_y], cy],
                pen=pg.mkPen('#71717a', width=1.5, style=Qt.PenStyle.DashLine)
            )
            plot_widget.custom_items.append(line)

        return pred_idx, distance

    def _update_plots(self):
        k_idx, k_dist = self._draw_plot(self.plot_kmeans, self.kmeans)
        m_idx, m_dist = self._draw_plot(self.plot_maximin, self.maximin)

        if self.tabs.currentIndex() == 0:
            self._generate_verdict(self.kmeans, k_idx, k_dist)
        else:
            self._generate_verdict(self.maximin, m_idx, m_dist)