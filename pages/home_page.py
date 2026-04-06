import os
import sys

from PIL import Image
from PySide6.QtGui import QIcon, Qt, QGuiApplication
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QFileDialog, \
    QListWidget, QListWidgetItem, QLabel, QLineEdit, QMessageBox

from core.utils import resource_path
from core.version import get_version


class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.convert_button = None
        self.output_path_select_button = None
        self.output_path_input_field = None
        self.author_label = None
        self.list_widget = None
        self.path_select_button = None
        self.selection_anchor = None
        self.init_ui()

    # Initializing
    def init_ui(self):

        # Window settings
        self.setWindowTitle(f"LazyIconCreator {get_version()}")
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))
        self.setFixedSize(1180, 530)

        # Path select button
        self.path_select_button = QPushButton("Select Image(-s)")
        self.path_select_button.pressed.connect(self.add_images)

        # List of user added paths
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(1)
        self.list_widget.setDragEnabled(False)
        self.list_widget.itemChanged.connect(self.on_item_changed)
        self.list_widget.setStyleSheet("""
                QListWidget::item {
                    padding: 2px; /* Внутренние отступы текста */
                    border-bottom: 1px solid #333; /* Тонкая разделительная линия */
                    max-height: 12px;
                }
                QListWidget {
                    outline: none;
                }
            """)

        # Output path input field
        self.output_path_input_field = QLineEdit()
        self.output_path_input_field.setPlaceholderText("Enter path to save icon(-s)")

        # Path select button
        self.output_path_select_button = QPushButton("Select export path")
        self.output_path_select_button.pressed.connect(self.select_export_path)

        self.convert_button = QPushButton("Convert !")
        self.convert_button.pressed.connect(self.convert_images)

        # Author place :)
        self.author_label = QLabel()
        self.author_label.setText(f"Powered by\n"
                                  "RED IGLA\n"
                                  + str(get_version()))
        self.author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Path input layout
        output_path_input_layout = QHBoxLayout()
        output_path_input_layout.addWidget(self.output_path_input_field)
        output_path_input_layout.addWidget(self.output_path_select_button)


        # Main layout (vertical)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        main_layout.addWidget(self.path_select_button)
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(output_path_input_layout)
        main_layout.addWidget(self.convert_button)
        main_layout.addWidget(self.author_label)

        # Main container
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    """
    Returns a list of absolutely all images in the list.
    """
    def get_all_images(self):
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        return items

    """
    Returns a list of all selected images.
    """
    def get_checked_images(self):
        paths = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                full_path = item.data(Qt.ItemDataRole.UserRole)
                paths.append(full_path)

        return paths

    """
    Adds images that the user has selected and automatically checks them.
    """
    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select images", "", "Images (*.png *.jpg *jpeg)")

        if files:
            current_items = self.get_all_images()

            for file in files:
                # Create element
                file_name = file.split("/")[-1]

                if file_name in current_items:
                    print(f"Image {file_name} already exists.")
                    continue

                item = QListWidgetItem(file_name)
                item.setData(Qt.ItemDataRole.UserRole, file)
                # Enable check mark
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)

                self.list_widget.addItem(item)
                print(f"Added image: {file_name}")

    """
    Changes the state of check marks when shift is pressed.
    """
    def on_item_changed(self, item):
        pressed_index = self.list_widget.row(item)
        modifiers = QGuiApplication.keyboardModifiers()

        # If anchor is not None and user pressed shift
        if modifiers == Qt.KeyboardModifier.ShiftModifier and self.selection_anchor is not None:

            start = int(min(self.selection_anchor, pressed_index))
            end = int(max(self.selection_anchor, pressed_index))

            # Grab actual item state
            target_state = item.checkState()

            # Block signals, prevent from recursion
            self.list_widget.blockSignals(True)

            # Cycle baby
            for i in range(start, end + 1):
                current_item = self.list_widget.item(i)
                # Changing state, only when it different
                if current_item.checkState() != target_state:
                    current_item.setCheckState(target_state)

            # Enable signals back
            self.list_widget.blockSignals(False)

            print(f"Shift pressed: changed items from {start} to {end} to {target_state}")

        else:
            print(f"Set selection anchor on: {pressed_index}")

        # Updating anchor
        self.selection_anchor = pressed_index

    """
    Select export path for ICO's.
    """
    def select_export_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select export folder",
                                                  "",
                                                  QFileDialog.Option.ShowDirsOnly)
        if folder:
            print(f"Selected folder: {folder}")
            self.output_path_input_field.setText(folder)

    """
    Opens export folder, only if folder exists. (post converting function)
    """
    def open_export_folder(self):
        path = self.output_path_input_field.text()
        if os.path.isdir(path):
            os.startfile(path)
        else:
            QMessageBox.critical(self, "Error", "Folder not found.")

    """
    Converting images to ICO files.
    (please dont convert cappuccino assassino images in this utility...)
    """
    def convert_images(self):
        print("Converting images...")

        selected_paths = self.get_checked_images()
        export_path = self.output_path_input_field.text()

        if not selected_paths:
            QMessageBox.critical(self, "Error", "No images selected.")
            return

        if export_path == "":
            QMessageBox.critical(self, "Error", "Please enter export path.")
            return
        elif not os.path.isdir(export_path):
            QMessageBox.critical(self, "Error", "Not such a export directory. Please enter a real export path.")
            return

        try:

            for path in selected_paths:
                print(f"Processing image: {path}")

                img = Image.open(path)
                img = img.convert("RGBA")
                base_name = os.path.basename(path).split(".")[0]
                output_file = os.path.join(export_path, f"{base_name}.ico")

                width, height = img.size
                square_size = max(width, height)

                # Create new transparent image
                new_img = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
                # Paste original image into new transparent and center him
                new_img.paste(img, ((square_size - width) // 2, (square_size - height) // 2))

                original_size = img.size

                # Check, if image dont over ICO limit
                if original_size[0] > 256 or original_size[1] > 256:
                    # The thumbnail method proportionally compresses the image to 256 by the long side.
                    img.thumbnail((256, 256), Image.Resampling.LANCZOS)
                    icon_size = [img.size]  # New size
                else:
                    icon_size = [original_size]  # Skipping and just put in []

                new_img.save(output_file, format="ICO", sizes=icon_size)

                print(f"Image successfully saved: {output_file}")

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText("Images successfully converted.")

            msg.addButton("Ok", QMessageBox.ButtonRole.AcceptRole)
            btn_open_export_folder = msg.addButton("Open export folder", QMessageBox.ButtonRole.ActionRole)
            btn_exit = msg.addButton("Exit", QMessageBox.ButtonRole.RejectRole)

            btn_open_export_folder.clicked.connect(self.open_export_folder)
            btn_exit.clicked.connect(lambda: sys.exit())

            msg.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to convert images: {e}")