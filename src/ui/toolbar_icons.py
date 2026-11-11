"""Small theme-aware vector icons used by compact toolbar buttons."""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def _canvas():
    pixmap = QPixmap(48, 48)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    return pixmap, painter


def _finish(pixmap, painter) -> QIcon:
    painter.end()
    return QIcon(pixmap)


def memo_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    page = QPainterPath(QPointF(5.0, 2.8))
    page.lineTo(15.8, 2.8)
    page.lineTo(20.0, 7.0)
    page.lineTo(20.0, 21.0)
    page.lineTo(5.0, 21.0)
    page.closeSubpath()
    painter.setPen(QPen(accent, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(panel)
    painter.drawPath(page)
    painter.drawLine(QPointF(15.8, 3.1), QPointF(15.8, 7.0))
    painter.drawLine(QPointF(15.8, 7.0), QPointF(19.7, 7.0))
    painter.setPen(QPen(dark, 1.5, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(8.0, 10.0), QPointF(16.8, 10.0))
    painter.drawLine(QPointF(8.0, 14.0), QPointF(16.8, 14.0))
    painter.drawLine(QPointF(8.0, 18.0), QPointF(14.0, 18.0))
    return _finish(pixmap, painter)


def image_manager_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    painter.setPen(QPen(accent.darker(150), 1.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(dark)
    painter.drawRoundedRect(2.8, 3.2, 15.5, 14.5, 2.0, 2.0)
    painter.setPen(QPen(accent, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(panel)
    painter.drawRoundedRect(5.5, 6.0, 15.5, 14.5, 2.0, 2.0)
    painter.setBrush(accent)
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(16.4, 10.4), 1.7, 1.7)
    mountain = QPainterPath(QPointF(7.4, 18.4))
    mountain.lineTo(11.5, 13.2)
    mountain.lineTo(14.2, 16.1)
    mountain.lineTo(16.1, 14.3)
    mountain.lineTo(19.2, 18.4)
    mountain.closeSubpath()
    painter.setBrush(accent.darker(115))
    painter.drawPath(mountain)
    return _finish(pixmap, painter)


def _draw_gear(painter, accent, panel, dark):
    center, radius, tooth = QPointF(12.0, 12.0), 5.5, 2.4
    cx, cy = center.x(), center.y()
    painter.setPen(QPen(accent, 2.6, Qt.SolidLine, Qt.RoundCap))
    diagonal = tooth * 0.72
    for start, end in (
        ((cx, cy - radius - tooth), (cx, cy - radius)),
        ((cx, cy + radius), (cx, cy + radius + tooth)),
        ((cx - radius - tooth, cy), (cx - radius, cy)),
        ((cx + radius, cy), (cx + radius + tooth, cy)),
        ((cx - radius - diagonal, cy - radius - diagonal), (cx - radius * .72, cy - radius * .72)),
        ((cx + radius * .72, cy + radius * .72), (cx + radius + diagonal, cy + radius + diagonal)),
        ((cx - radius - diagonal, cy + radius + diagonal), (cx - radius * .72, cy + radius * .72)),
        ((cx + radius * .72, cy - radius * .72), (cx + radius + diagonal, cy - radius - diagonal)),
    ):
        painter.drawLine(QPointF(*start), QPointF(*end))
    painter.setPen(QPen(accent, 1.2))
    painter.setBrush(panel)
    painter.drawEllipse(center, radius, radius)
    painter.setBrush(dark)
    painter.drawEllipse(center, radius * .36, radius * .36)


def settings_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    _draw_gear(painter, QColor(accent_color), QColor(panel_color), QColor(dark_color))
    return _finish(pixmap, painter)


def vendor_presets_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    painter.setPen(QPen(accent, 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(panel)
    painter.drawRoundedRect(3.0, 8.0, 16.0, 12.5, 1.8, 1.8)
    painter.setBrush(accent)
    painter.drawRect(2.5, 5.0, 17.0, 4.0)
    painter.setPen(QPen(dark, 1.2))
    for x in (6.8, 11.0, 15.2):
        painter.drawLine(QPointF(x, 5.3), QPointF(x, 8.7))
    painter.setPen(QPen(accent, 1.2))
    painter.setBrush(dark)
    painter.drawRoundedRect(5.0, 11.2, 5.0, 9.3, 1.0, 1.0)
    painter.setPen(QPen(dark, 1.5, Qt.SolidLine, Qt.RoundCap))
    painter.setBrush(accent)
    painter.drawRoundedRect(12.0, 11.0, 10.0, 10.0, 1.7, 1.7)
    painter.setPen(QPen(dark, 1.3, Qt.SolidLine, Qt.RoundCap))
    for y in (14.0, 17.0):
        painter.drawLine(QPointF(14.4, y), QPointF(19.6, y))
    return _finish(pixmap, painter)


def _stroke(painter, color, width=1.6):
    painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))


def home_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.6)
    painter.setBrush(panel)
    roof = QPainterPath(QPointF(12.0, 2.6))
    roof.lineTo(21.2, 10.2)
    roof.lineTo(2.8, 10.2)
    roof.closeSubpath()
    painter.drawPath(roof)
    painter.setBrush(dark)
    painter.drawRoundedRect(5.2, 10.0, 13.6, 10.2, 1.2, 1.2)
    painter.setBrush(accent)
    painter.drawRoundedRect(10.2, 14.2, 3.6, 6.0, 0.6, 0.6)
    return _finish(pixmap, painter)


def guide_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.5)
    painter.setBrush(panel)
    painter.drawRoundedRect(3.2, 2.8, 14.2, 18.4, 1.6, 1.6)
    painter.setPen(QPen(dark, 1.3, Qt.SolidLine, Qt.RoundCap))
    for y in (7.0, 10.4, 13.8):
        painter.drawLine(QPointF(5.6, y), QPointF(14.6, y))
    painter.setPen(Qt.NoPen)
    painter.setBrush(accent)
    painter.drawEllipse(QPointF(17.6, 16.2), 3.4, 3.4)
    painter.setBrush(dark)
    painter.drawEllipse(QPointF(17.6, 16.2), 1.3, 1.3)
    return _finish(pixmap, painter)


def timer_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.6)
    painter.setBrush(panel)
    painter.drawEllipse(QPointF(12.0, 13.0), 8.0, 8.0)
    painter.setBrush(dark)
    painter.drawEllipse(QPointF(12.0, 13.0), 1.1, 1.1)
    painter.setPen(QPen(accent, 1.6, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(12.0, 13.0), QPointF(12.0, 8.2))
    painter.drawLine(QPointF(12.0, 13.0), QPointF(15.6, 15.0))
    painter.drawLine(QPointF(8.4, 3.2), QPointF(15.6, 3.2))
    return _finish(pixmap, painter)


def map_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.5)
    painter.setBrush(panel)
    painter.drawRoundedRect(2.6, 4.0, 18.8, 15.6, 1.8, 1.8)
    painter.setPen(QPen(accent, 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    path = QPainterPath(QPointF(5.0, 15.6))
    path.cubicTo(QPointF(8.0, 11.0), QPointF(10.2, 14.8), QPointF(13.0, 10.2))
    path.cubicTo(QPointF(15.2, 6.8), QPointF(16.8, 8.4), QPointF(19.0, 6.4))
    painter.drawPath(path)
    painter.setPen(Qt.NoPen)
    painter.setBrush(dark)
    painter.drawEllipse(QPointF(13.0, 10.2), 1.5, 1.5)
    return _finish(pixmap, painter)


def gem_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.5)
    painter.setBrush(panel)
    gem = QPainterPath(QPointF(12.0, 2.4))
    gem.lineTo(20.2, 8.6)
    gem.lineTo(12.0, 21.6)
    gem.lineTo(3.8, 8.6)
    gem.closeSubpath()
    painter.drawPath(gem)
    painter.setPen(QPen(dark, 1.2, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(3.8, 8.6), QPointF(20.2, 8.6))
    painter.drawLine(QPointF(12.0, 2.4), QPointF(12.0, 21.6))
    painter.setPen(Qt.NoPen)
    painter.setBrush(accent)
    painter.drawEllipse(QPointF(12.0, 8.6), 1.3, 1.3)
    return _finish(pixmap, painter)


def mini_navi_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent.darker(130), 1.3)
    painter.setBrush(dark)
    painter.drawRoundedRect(2.4, 4.6, 13.4, 10.4, 1.6, 1.6)
    _stroke(painter, accent, 1.6)
    painter.setBrush(panel)
    painter.drawRoundedRect(7.2, 8.4, 14.2, 11.2, 1.8, 1.8)
    painter.setPen(QPen(accent, 1.3, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(9.6, 12.2), QPointF(18.6, 12.2))
    painter.drawLine(QPointF(9.6, 15.4), QPointF(15.4, 15.4))
    return _finish(pixmap, painter)


def info_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, _dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.6)
    painter.setBrush(panel)
    painter.drawEllipse(QPointF(12.0, 12.0), 8.6, 8.6)
    painter.setPen(QPen(accent, 1.8, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(12.0, 10.6), QPointF(12.0, 16.8))
    painter.setPen(Qt.NoPen)
    painter.setBrush(accent)
    painter.drawEllipse(QPointF(12.0, 7.6), 1.15, 1.15)
    return _finish(pixmap, painter)


def poetore_icon(accent_color, panel_color, dark_color) -> QIcon:
    pixmap, painter = _canvas()
    accent, panel, dark = map(QColor, (accent_color, panel_color, dark_color))
    _stroke(painter, accent, 1.5)
    painter.setBrush(panel)
    tag = QPainterPath(QPointF(3.2, 8.2))
    tag.lineTo(12.4, 8.2)
    tag.lineTo(21.0, 13.2)
    tag.lineTo(12.4, 18.2)
    tag.lineTo(3.2, 18.2)
    tag.closeSubpath()
    painter.drawPath(tag)
    painter.setPen(Qt.NoPen)
    painter.setBrush(dark)
    painter.drawEllipse(QPointF(8.0, 13.2), 1.5, 1.5)
    painter.setBrush(accent)
    painter.drawEllipse(QPointF(8.0, 13.2), 0.6, 0.6)
    return _finish(pixmap, painter)
