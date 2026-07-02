#include "LqRibbonGallery.h"

#include <QKeyEvent>
#include <QMouseEvent>
#include <QPainter>
#include <QStyleOption>
#include <QWheelEvent>
#include <QBitmap>
#include <QtMath>

namespace {

const int defaultGalleryColumnCount = 4;
const int defaultGalleryRowCount = 2;

///
/// \brief iconFromPixmap
/// Builds an icon from a pixmap while preserving an optional transparent color.
/// \param pixmap Source pixmap.
/// \param transparentColor Color to mask out.
/// \return Icon for a gallery item.
///
QIcon iconFromPixmap(const QPixmap &pixmap, const QColor &transparentColor)
{
    if (pixmap.isNull()) {
        return QIcon();
    }

    QPixmap iconPixmap = pixmap;
    if (transparentColor.isValid()) {
        iconPixmap.setMask(iconPixmap.createMaskFromColor(transparentColor));
    }

    return QIcon(iconPixmap);
}

} // namespace

namespace LqRibbon {

RibbonGalleryItem::RibbonGalleryItem()
    : m_index(-1)
    , m_separator(false)
    , m_enabled(true)
    , m_visible(true)
{
}

RibbonGalleryItem::~RibbonGalleryItem() = default;

QIcon RibbonGalleryItem::icon() const
{
    return m_icon;
}

void RibbonGalleryItem::setIcon(const QIcon &icon)
{
    m_icon = icon;
}

QString RibbonGalleryItem::caption() const
{
    return m_strCaption;
}

void RibbonGalleryItem::setCaption(const QString &strCaption)
{
    m_strCaption = strCaption;
}

QString RibbonGalleryItem::toolTip() const
{
    return m_strToolTip;
}

void RibbonGalleryItem::setToolTip(const QString &strToolTip)
{
    m_strToolTip = strToolTip;
}

QString RibbonGalleryItem::statusTip() const
{
    return m_strStatusTip;
}

void RibbonGalleryItem::setStatusTip(const QString &strStatusTip)
{
    m_strStatusTip = strStatusTip;
}

int RibbonGalleryItem::getIndex() const
{
    return m_index;
}

bool RibbonGalleryItem::isSeparator() const
{
    return m_separator;
}

void RibbonGalleryItem::setSeparator(bool on)
{
    m_separator = on;
}

void RibbonGalleryItem::setEnabled(bool enabled)
{
    m_enabled = enabled;
}

bool RibbonGalleryItem::isEnabled() const
{
    return m_enabled;
}

void RibbonGalleryItem::setVisible(bool visible)
{
    m_visible = visible;
}

bool RibbonGalleryItem::isVisible() const
{
    return m_visible;
}

QVariant RibbonGalleryItem::data(int role) const
{
    return m_dataHash.value(role);
}

void RibbonGalleryItem::setData(int role, const QVariant &value)
{
    m_dataHash.insert(role, value);
}

void RibbonGalleryItem::draw(QPainter *painter,
                             RibbonGallery *gallery,
                             QRect itemRect,
                             bool enabled,
                             bool selected,
                             bool pressed,
                             bool checked)
{
    Q_UNUSED(gallery)

    if (isSeparator()) {
        painter->setPen(QColor(QStringLiteral("#cbd4df")));
        painter->drawLine(itemRect.left() + 4,
                          itemRect.center().y(),
                          itemRect.right() - 4,
                          itemRect.center().y());
        return;
    }

    QColor fillColor = Qt::transparent;
    QColor borderColor = Qt::transparent;
    if (checked) {
        fillColor = QColor(QStringLiteral("#d9e9fb"));
        borderColor = QColor(QStringLiteral("#6d9fd4"));
    } else if (pressed) {
        fillColor = QColor(QStringLiteral("#d3e4f6"));
        borderColor = QColor(QStringLiteral("#6d9fd4"));
    } else if (selected) {
        fillColor = QColor(QStringLiteral("#eaf2fb"));
        borderColor = QColor(QStringLiteral("#9eb7d5"));
    }

    painter->setPen(borderColor);
    painter->setBrush(fillColor);
    painter->drawRect(itemRect.adjusted(0, 0, -1, -1));

    QRect iconRect = itemRect.adjusted(6, 4, -6, -18);
    iconRect.setHeight(qMax(0, iconRect.height()));
    if (!m_icon.isNull()) {
        m_icon.paint(painter,
                     iconRect,
                     Qt::AlignCenter,
                     enabled ? QIcon::Normal : QIcon::Disabled);
    }

    painter->setPen(enabled
                    ? QColor(QStringLiteral("#2f3338"))
                    : QColor(QStringLiteral("#8a8f96")));
    painter->drawText(itemRect.adjusted(4, itemRect.height() - 18, -4, -2),
                      Qt::AlignCenter | Qt::TextSingleLine,
                      m_strCaption);
}

RibbonGalleryGroup::RibbonGalleryGroup(QObject *parent)
    : QObject(parent)
    , m_size(54, 56)
{
}

RibbonGalleryGroup::~RibbonGalleryGroup()
{
    clear();
}

RibbonGalleryItem *RibbonGalleryGroup::addItem(const QString &strCaption,
                                               const QIcon &icon)
{
    RibbonGalleryItem *newItem = new RibbonGalleryItem;
    newItem->setCaption(strCaption);
    newItem->setIcon(icon);
    appendItem(newItem);
    return newItem;
}

RibbonGalleryItem *RibbonGalleryGroup::addItem(
    const QString &strCaption,
    const QPixmap &pixmap,
    const QColor &transparentColor)
{
    return addItem(strCaption, iconFromPixmap(pixmap, transparentColor));
}

RibbonGalleryItem *RibbonGalleryGroup::addItemFromMap(
    const QString &strCaption,
    int mapIndex,
    const QPixmap &map,
    const QSize &mapSizeImage,
    const QColor &transparentColor)
{
    if (map.isNull() || mapSizeImage.isEmpty()) {
        return addItem(strCaption, QIcon());
    }

    const int columns = qMax(1, map.width() / mapSizeImage.width());
    const int x = (mapIndex % columns) * mapSizeImage.width();
    const int y = (mapIndex / columns) * mapSizeImage.height();
    QPixmap pixmap = map.copy(QRect(QPoint(x, y), mapSizeImage));
    return addItem(strCaption, iconFromPixmap(pixmap, transparentColor));
}

void RibbonGalleryGroup::appendItem(RibbonGalleryItem *item)
{
    insertItem(m_itemList.count(), item);
}

void RibbonGalleryGroup::insertItem(int index, RibbonGalleryItem *item)
{
    if (!item) {
        return;
    }

    const int boundedIndex = qBound(0, index, m_itemList.count());
    m_itemList.insert(boundedIndex, item);
    refreshItemIndexes();
    emit changed();
}

RibbonGalleryItem *RibbonGalleryGroup::addSeparator(const QString &strCaption)
{
    RibbonGalleryItem *newItem = new RibbonGalleryItem;
    newItem->setCaption(strCaption);
    newItem->setSeparator(true);
    appendItem(newItem);
    return newItem;
}

void RibbonGalleryGroup::clear()
{
    qDeleteAll(m_itemList);
    m_itemList.clear();
    emit changed();
}

void RibbonGalleryGroup::remove(int index)
{
    delete takeItem(index);
    emit changed();
}

int RibbonGalleryGroup::itemCount() const
{
    return m_itemList.count();
}

RibbonGalleryItem *RibbonGalleryGroup::item(int index) const
{
    return index >= 0 && index < m_itemList.count()
        ? m_itemList.at(index)
        : nullptr;
}

RibbonGalleryItem *RibbonGalleryGroup::takeItem(int index)
{
    if (index < 0 || index >= m_itemList.count()) {
        return nullptr;
    }

    RibbonGalleryItem *removedItem = m_itemList.takeAt(index);
    if (removedItem) {
        removedItem->m_index = -1;
    }
    refreshItemIndexes();
    emit changed();
    return removedItem;
}

QSize RibbonGalleryGroup::size() const
{
    return m_size;
}

void RibbonGalleryGroup::setSize(const QSize &size)
{
    m_size = size.expandedTo(QSize(24, 24));
    emit changed();
}

void RibbonGalleryGroup::refreshItemIndexes()
{
    for (int index = 0; index < m_itemList.count(); ++index) {
        m_itemList.at(index)->m_index = index;
    }
}

RibbonGallery::RibbonGallery(QWidget *parent)
    : QWidget(parent)
    , m_itemSize(54, 56)
    , m_itemMargins(2, 2, 2, 2)
    , m_popupAction(new QAction(this))
    , m_minimumColumnCount(1)
    , m_maximumColumnCount(8)
    , m_columnCount(defaultGalleryColumnCount)
    , m_rowCount(defaultGalleryRowCount)
    , m_selectedIndex(-1)
    , m_checkedIndex(-1)
    , m_pressedIndex(-1)
    , m_borderVisible(true)
    , m_transparent(false)
    , m_labelsVisible(true)
    , m_scrollAnimated(false)
    , m_autoWidth(true)
    , m_scrollBarPolicy(Qt::ScrollBarAsNeeded)
{
    setObjectName(QStringLiteral("lqRibbonGallery"));
    setMouseTracking(true);
    setFocusPolicy(Qt::StrongFocus);
    updateLayout();
}

RibbonGallery::~RibbonGallery() = default;

void RibbonGallery::setGalleryGroup(RibbonGalleryGroup *group)
{
    if (m_group == group) {
        return;
    }

    if (m_group) {
        disconnect(m_group.data(), nullptr, this, nullptr);
    }

    m_group = group;
    if (m_group) {
        connect(m_group.data(), &RibbonGalleryGroup::changed,
                this, &RibbonGallery::updateLayout);
        if (m_group->size().isValid()) {
            m_itemSize = m_group->size();
        }
    }

    m_selectedIndex = -1;
    m_checkedIndex = -1;
    updateLayout();
}

RibbonGalleryGroup *RibbonGallery::galleryGroup() const
{
    return m_group.data();
}

QSize RibbonGallery::itemSize() const
{
    return m_itemSize;
}

void RibbonGallery::setItemSize(const QSize &size)
{
    m_itemSize = size.expandedTo(QSize(24, 24));
    updateLayout();
}

QMargins RibbonGallery::itemMargins() const
{
    return m_itemMargins;
}

void RibbonGallery::setItemMargins(const QMargins &margins)
{
    m_itemMargins = margins;
    updateLayout();
}

bool RibbonGallery::isBorderVisible() const
{
    return m_borderVisible;
}

void RibbonGallery::setBorderVisible(bool visible)
{
    m_borderVisible = visible;
    update();
}

bool RibbonGallery::isTransparent() const
{
    return m_transparent;
}

void RibbonGallery::setTransparent(bool transparent)
{
    m_transparent = transparent;
    update();
}

bool RibbonGallery::isLabelsVisible() const
{
    return m_labelsVisible;
}

void RibbonGallery::setLabelsVisible(bool showLabels)
{
    m_labelsVisible = showLabels;
    update();
}

void RibbonGallery::setScrollBarPolicy(Qt::ScrollBarPolicy policy)
{
    m_scrollBarPolicy = policy;
}

Qt::ScrollBarPolicy RibbonGallery::scrollBarPolicy() const
{
    return m_scrollBarPolicy;
}

void RibbonGallery::ensureVisible(int index)
{
    if (index >= 0 && index < itemCount()) {
        setSelectedItem(index);
    }
}

QAction *RibbonGallery::setPopupMenu(QMenu *popupMenu)
{
    m_popupMenu = popupMenu;
    m_popupAction->setMenu(popupMenu);
    return m_popupAction;
}

QMenu *RibbonGallery::popupMenu() const
{
    return m_popupMenu.data();
}

void RibbonGallery::setMinimumColumnCount(int count)
{
    m_minimumColumnCount = qMax(1, count);
    if (m_maximumColumnCount < m_minimumColumnCount) {
        m_maximumColumnCount = m_minimumColumnCount;
    }
    updateLayout();
}

int RibbonGallery::minimumColumnCount() const
{
    return m_minimumColumnCount;
}

void RibbonGallery::setMaximumColumnCount(int count)
{
    m_maximumColumnCount = qMax(m_minimumColumnCount, count);
    updateLayout();
}

int RibbonGallery::maximumColumnCount() const
{
    return m_maximumColumnCount;
}

void RibbonGallery::setColumnCount(int count)
{
    m_columnCount = qMax(1, count);
    updateLayout();
}

int RibbonGallery::columnCount() const
{
    return normalizedColumnCount();
}

void RibbonGallery::setRowCount(int row)
{
    m_rowCount = qMax(1, row);
    updateLayout();
}

int RibbonGallery::rowCount() const
{
    return m_rowCount;
}

bool RibbonGallery::isScrollAnimated() const
{
    return m_scrollAnimated;
}

void RibbonGallery::setScrollAnimated(bool animated)
{
    m_scrollAnimated = animated;
}

int RibbonGallery::itemCount() const
{
    return m_group ? m_group->itemCount() : 0;
}

RibbonGalleryItem *RibbonGallery::item(int index) const
{
    return m_group ? m_group->item(index) : nullptr;
}

void RibbonGallery::setSelectedItem(int index)
{
    if (m_selectedIndex == index) {
        return;
    }

    RibbonGalleryItem *previousItem = item(m_selectedIndex);
    m_selectedIndex = index >= 0 && index < itemCount() ? index : -1;
    selectedItemChanged();
    emit currentItemChanged(item(m_selectedIndex), previousItem);
    emit selectionChanged(m_selectedIndex);
    update();
}

int RibbonGallery::selectedItem() const
{
    return m_selectedIndex;
}

void RibbonGallery::setCheckedIndex(int index)
{
    m_checkedIndex = index >= 0 && index < itemCount() ? index : -1;
    checkedItemChanged();
    update();
}

int RibbonGallery::checkedIndex() const
{
    return m_checkedIndex;
}

void RibbonGallery::setCheckedItem(const RibbonGalleryItem *item)
{
    setCheckedIndex(item ? item->getIndex() : -1);
}

RibbonGalleryItem *RibbonGallery::checkedItem() const
{
    return item(m_checkedIndex);
}

bool RibbonGallery::isItemSelected() const
{
    return m_selectedIndex >= 0;
}

QMargins RibbonGallery::margins() const
{
    return contentsMargins();
}

QRect RibbonGallery::getDrawItemRect(int index) const
{
    if (index < 0 || index >= itemCount()) {
        return QRect();
    }

    int visibleIndex = 0;
    for (int itemIndex = 0; itemIndex < itemCount(); ++itemIndex) {
        RibbonGalleryItem *currentItem = item(itemIndex);
        if (!currentItem || !currentItem->isVisible()) {
            continue;
        }
        if (itemIndex == index) {
            break;
        }
        ++visibleIndex;
    }

    const QRect itemsRect = getItemsRect();
    const int columns = normalizedColumnCount();
    const int row = visibleIndex / columns;
    const int column = visibleIndex % columns;
    return QRect(itemsRect.left() + (column * m_itemSize.width()),
                 itemsRect.top() + (row * m_itemSize.height()),
                 m_itemSize.width(),
                 m_itemSize.height()).adjusted(m_itemMargins.left(),
                                               m_itemMargins.top(),
                                               -m_itemMargins.right(),
                                               -m_itemMargins.bottom());
}

bool RibbonGallery::isResizable() const
{
    return false;
}

bool RibbonGallery::autoWidth() const
{
    return m_autoWidth;
}

void RibbonGallery::setAutoWidth(bool width)
{
    m_autoWidth = width;
    updateLayout();
}

int RibbonGallery::hitTestItem(QPoint point, QRect *rect) const
{
    for (int index = 0; index < itemCount(); ++index) {
        RibbonGalleryItem *galleryItem = item(index);
        if (!galleryItem || !galleryItem->isVisible()) {
            continue;
        }

        const QRect itemRect = getDrawItemRect(index);
        if (itemRect.contains(point)) {
            if (rect) {
                *rect = itemRect;
            }
            return index;
        }
    }

    return -1;
}

QRect RibbonGallery::getItemsRect() const
{
    return rect().adjusted(1, 1, -1, -1);
}

void RibbonGallery::hideSelection()
{
    setSelectedItem(-1);
}

void RibbonGallery::updateLayout()
{
    if (m_autoWidth) {
        setFixedSize(sizeHint());
    }
    updateGeometry();
    update();
}

void RibbonGallery::bestFit()
{
    const int count = qMax(1, visibleItemCount());
    const int columns = qBound(m_minimumColumnCount,
                               count,
                               m_maximumColumnCount);
    setColumnCount(columns);
}

QSize RibbonGallery::sizeHint() const
{
    const int columns = normalizedColumnCount();
    const int rows = qMax(m_rowCount,
                          qCeil(static_cast<double>(visibleItemCount())
                                / qMax(1, columns)));
    return QSize(columns * m_itemSize.width(), rows * m_itemSize.height())
        + QSize(2, 2);
}

QSize RibbonGallery::minimumSizeHint() const
{
    return QSize(m_minimumColumnCount * m_itemSize.width(),
                 m_itemSize.height()) + QSize(2, 2);
}

QSize RibbonGallery::itemSizeHint() const
{
    return m_itemSize;
}

void RibbonGallery::selectedItemChanged()
{
}

void RibbonGallery::checkedItemChanged()
{
}

bool RibbonGallery::event(QEvent *event)
{
    return QWidget::event(event);
}

void RibbonGallery::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)

    QPainter painter(this);
    if (!m_transparent) {
        painter.fillRect(rect(), QColor(QStringLiteral("#ffffff")));
    }

    if (m_borderVisible) {
        painter.setPen(QColor(QStringLiteral("#cbd4df")));
        painter.drawRect(rect().adjusted(0, 0, -1, -1));
    }

    for (int index = 0; index < itemCount(); ++index) {
        RibbonGalleryItem *galleryItem = item(index);
        if (!galleryItem || !galleryItem->isVisible()) {
            continue;
        }

        const QRect itemRect = getDrawItemRect(index);
        galleryItem->draw(&painter,
                          this,
                          itemRect,
                          isEnabled() && galleryItem->isEnabled(),
                          index == m_selectedIndex,
                          index == m_pressedIndex,
                          index == m_checkedIndex);
    }
}

void RibbonGallery::mousePressEvent(QMouseEvent *event)
{
    m_pressedIndex = hitTestItem(event->pos());
    if (m_pressedIndex >= 0) {
        RibbonGalleryItem *pressedItem = item(m_pressedIndex);
        if (pressedItem && pressedItem->isEnabled()) {
            setSelectedItem(m_pressedIndex);
            emit itemPressed(pressedItem);
        }
    }
    update();
}

void RibbonGallery::mouseReleaseEvent(QMouseEvent *event)
{
    const int releasedIndex = hitTestItem(event->pos());
    RibbonGalleryItem *releasedItem = item(releasedIndex);
    if (releasedIndex == m_pressedIndex && releasedItem
        && releasedItem->isEnabled()) {
        bool handled = false;
        emit itemClicking(releasedItem, handled);
        if (!handled) {
            setCheckedIndex(releasedIndex);
            emit itemClicked(releasedItem);
        }
    }

    m_pressedIndex = -1;
    update();
}

void RibbonGallery::mouseMoveEvent(QMouseEvent *event)
{
    const int hoveredIndex = hitTestItem(event->pos());
    if (hoveredIndex != m_selectedIndex) {
        setSelectedItem(hoveredIndex);
    }
}

void RibbonGallery::wheelEvent(QWheelEvent *event)
{
    const int delta = event->angleDelta().y();
    if (delta > 0) {
        setSelectedItem(qMax(0, m_selectedIndex - normalizedColumnCount()));
    } else if (delta < 0) {
        setSelectedItem(qMin(itemCount() - 1,
                             m_selectedIndex + normalizedColumnCount()));
    }
}

void RibbonGallery::leaveEvent(QEvent *event)
{
    QWidget::leaveEvent(event);
    hideSelection();
}

void RibbonGallery::focusOutEvent(QFocusEvent *event)
{
    QWidget::focusOutEvent(event);
    m_pressedIndex = -1;
    update();
}

void RibbonGallery::resizeEvent(QResizeEvent *event)
{
    QWidget::resizeEvent(event);
}

void RibbonGallery::keyPressEvent(QKeyEvent *event)
{
    int nextIndex = m_selectedIndex < 0 ? 0 : m_selectedIndex;
    switch (event->key()) {
    case Qt::Key_Left:
        --nextIndex;
        break;
    case Qt::Key_Right:
        ++nextIndex;
        break;
    case Qt::Key_Up:
        nextIndex -= normalizedColumnCount();
        break;
    case Qt::Key_Down:
        nextIndex += normalizedColumnCount();
        break;
    case Qt::Key_Return:
    case Qt::Key_Enter:
    case Qt::Key_Space:
        if (RibbonGalleryItem *currentItem = item(m_selectedIndex)) {
            setCheckedIndex(m_selectedIndex);
            emit itemClicked(currentItem);
        }
        return;
    default:
        QWidget::keyPressEvent(event);
        return;
    }

    setSelectedItem(qBound(0, nextIndex, itemCount() - 1));
}

int RibbonGallery::normalizedColumnCount() const
{
    return qBound(m_minimumColumnCount,
                  m_columnCount,
                  m_maximumColumnCount);
}

int RibbonGallery::visibleItemCount() const
{
    int count = 0;
    for (int index = 0; index < itemCount(); ++index) {
        RibbonGalleryItem *galleryItem = item(index);
        if (galleryItem && galleryItem->isVisible()) {
            ++count;
        }
    }
    return count;
}

int RibbonGallery::visibleIndexToItemIndex(int visibleIndex) const
{
    int currentVisibleIndex = 0;
    for (int index = 0; index < itemCount(); ++index) {
        RibbonGalleryItem *galleryItem = item(index);
        if (!galleryItem || !galleryItem->isVisible()) {
            continue;
        }
        if (currentVisibleIndex == visibleIndex) {
            return index;
        }
        ++currentVisibleIndex;
    }
    return -1;
}

RibbonGalleryControl::RibbonGalleryControl(RibbonGroup *parent,
                                           RibbonGallery *gallery)
    : RibbonWidgetControl(parent, true)
{
    setContentWidget(gallery ? gallery : new RibbonGallery(this));
}

RibbonGalleryControl::~RibbonGalleryControl() = default;

RibbonGallery *RibbonGalleryControl::widget() const
{
    return qobject_cast<RibbonGallery *>(contentWidget());
}

void RibbonGalleryControl::setContentsMargins(int top, int bottom)
{
    RibbonWidgetControl::setMargins(0, top, 0, bottom);
}

QSize RibbonGalleryControl::sizeHint() const
{
    return RibbonWidgetControl::sizeHint();
}

bool RibbonGalleryControl::adjustCurrentSize(bool expand)
{
    return RibbonWidgetControl::adjustCurrentSize(expand);
}

void RibbonGalleryControl::sizeChanged(
    RibbonControlSizeDefinition::GroupSize size)
{
    RibbonWidgetControl::sizeChanged(size);
}

void RibbonGalleryControl::resizeEvent(QResizeEvent *event)
{
    RibbonWidgetControl::resizeEvent(event);
}

} // namespace LqRibbon
