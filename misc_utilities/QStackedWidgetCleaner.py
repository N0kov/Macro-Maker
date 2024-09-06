from PyQt6.QtWidgets import QStackedWidget


class QStackedWidgetCleaner(QStackedWidget):
    """
    A QStackedWidget that also performs widget cleanup. Every 20 seconds it cleans up and deletes widgets
    that are no longer needed
    """
    def __init__(self, parent=None):
        """
        Initializes the widget
        """
        super().__init__(parent)

    def cleanup_widgets(self):
        """
        Clears all widgets but the base UI one
        """
        for i in reversed(range(1, self.count() - 3)):
            widget = self.widget(i)
            self.removeWidget(widget)
            widget.deleteLater()
