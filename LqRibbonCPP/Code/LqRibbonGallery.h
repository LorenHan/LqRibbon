#ifndef LQRIBBON_GALLERY_H
#define LQRIBBON_GALLERY_H

#include <QHash>
#include <QIcon>
#include <QMargins>
#include <QMenu>
#include <QColor>
#include <QPainter>
#include <QPointer>
#include <QPixmap>
#include <QVariant>
#include <QVector>
#include <QWidget>

#include "LqRibbonControls.h"

namespace LqRibbon {

class RibbonGallery;

///
/// \brief The RibbonGalleryItem class stores one selectable gallery entry.
///
class RibbonGalleryItem
{
public:
    RibbonGalleryItem();
    virtual ~RibbonGalleryItem();

    QIcon icon() const;
    void setIcon(const QIcon &icon);
    QString caption() const;
    void setCaption(const QString &strCaption);
    QString toolTip() const;
    void setToolTip(const QString &strToolTip);
    QString statusTip() const;
    void setStatusTip(const QString &strStatusTip);
    int getIndex() const;
    bool isSeparator() const;
    void setSeparator(bool on);
    void setEnabled(bool enabled);
    bool isEnabled() const;
    void setVisible(bool visible);
    bool isVisible() const;
    virtual QVariant data(int role) const;
    virtual void setData(int role, const QVariant &value);
    virtual void draw(QPainter *painter,
                      RibbonGallery *gallery,
                      QRect itemRect,
                      bool enabled,
                      bool selected,
                      bool pressed,
                      bool checked);

private:
    friend class RibbonGalleryGroup;

    QIcon m_icon;
    QString m_strCaption;
    QString m_strToolTip;
    QString m_strStatusTip;
    QHash<int, QVariant> m_dataHash;
    int m_index;
    bool m_separator;
    bool m_enabled;
    bool m_visible;
};

///
/// \brief The RibbonGalleryGroup class owns gallery items and shared metrics.
///
class RibbonGalleryGroup : public QObject
{
    Q_OBJECT

public:
    explicit RibbonGalleryGroup(QObject *parent = nullptr);
    ~RibbonGalleryGroup() override;

    RibbonGalleryItem *addItem(const QString &strCaption,
                               const QIcon &icon);
    RibbonGalleryItem *addItem(const QString &strCaption,
                               const QPixmap &pixmap = QPixmap(),
                               const QColor &transparentColor = QColor());
    RibbonGalleryItem *addItemFromMap(const QString &strCaption,
                                      int mapIndex,
                                      const QPixmap &map,
                                      const QSize &mapSizeImage,
                                      const QColor &transparentColor =
                                          QColor());
    void appendItem(RibbonGalleryItem *item);
    void insertItem(int index, RibbonGalleryItem *item);
    RibbonGalleryItem *addSeparator(const QString &strCaption);
    void clear();
    void remove(int index);
    int itemCount() const;
    RibbonGalleryItem *item(int index) const;
    RibbonGalleryItem *takeItem(int index);
    QSize size() const;
    void setSize(const QSize &size);

signals:
    void changed();

private:
    void refreshItemIndexes();

private:
    QVector<RibbonGalleryItem *> m_itemList;
    QSize m_size;
};

///
/// \brief The RibbonGallery class displays selectable gallery items.
///
class RibbonGallery : public QWidget
{
    Q_OBJECT
    Q_PROPERTY(bool borderVisible READ isBorderVisible WRITE setBorderVisible)
    Q_PROPERTY(bool transparent READ isTransparent WRITE setTransparent)
    Q_PROPERTY(bool showLabels READ isLabelsVisible WRITE setLabelsVisible)
    Q_PROPERTY(int minimumColumnCount READ minimumColumnCount
               WRITE setMinimumColumnCount)
    Q_PROPERTY(int maximumColumnCount READ maximumColumnCount
               WRITE setMaximumColumnCount)
    Q_PROPERTY(Qt::ScrollBarPolicy scrollBarPolicy READ scrollBarPolicy
               WRITE setScrollBarPolicy)
    Q_PROPERTY(bool resizable READ isResizable)
    Q_PROPERTY(bool autoWidth READ autoWidth WRITE setAutoWidth)

public:
    explicit RibbonGallery(QWidget *parent = nullptr);
    ~RibbonGallery() override;

    void setGalleryGroup(RibbonGalleryGroup *group);
    RibbonGalleryGroup *galleryGroup() const;
    QSize itemSize() const;
    void setItemSize(const QSize &size);
    QMargins itemMargins() const;
    void setItemMargins(const QMargins &margins);
    bool isBorderVisible() const;
    void setBorderVisible(bool visible);
    bool isTransparent() const;
    void setTransparent(bool transparent = true);
    bool isLabelsVisible() const;
    void setLabelsVisible(bool showLabels);
    void setScrollBarPolicy(Qt::ScrollBarPolicy policy);
    Qt::ScrollBarPolicy scrollBarPolicy() const;
    void ensureVisible(int index);
    QAction *setPopupMenu(QMenu *popupMenu);
    QMenu *popupMenu() const;
    void setMinimumColumnCount(int count);
    int minimumColumnCount() const;
    void setMaximumColumnCount(int count);
    int maximumColumnCount() const;
    void setColumnCount(int count);
    int columnCount() const;
    void setRowCount(int row);
    int rowCount() const;
    bool isScrollAnimated() const;
    void setScrollAnimated(bool animated);
    int itemCount() const;
    RibbonGalleryItem *item(int index) const;
    void setSelectedItem(int index);
    int selectedItem() const;
    void setCheckedIndex(int index);
    int checkedIndex() const;
    void setCheckedItem(const RibbonGalleryItem *item);
    RibbonGalleryItem *checkedItem() const;
    bool isItemSelected() const;
    virtual QMargins margins() const;
    QRect getDrawItemRect(int index) const;
    bool isResizable() const;
    bool autoWidth() const;
    void setAutoWidth(bool width);
    int hitTestItem(QPoint point, QRect *rect = nullptr) const;
    QRect getItemsRect() const;
    void hideSelection();
    void updateLayout();
    void bestFit();
    QSize sizeHint() const override;
    QSize minimumSizeHint() const override;
    QSize itemSizeHint() const;

signals:
    void itemPressed(RibbonGalleryItem *item);
    void itemClicking(RibbonGalleryItem *item, bool &handled);
    void itemClicked(RibbonGalleryItem *item);
    void currentItemChanged(RibbonGalleryItem *current,
                            RibbonGalleryItem *previous);
    void selectionChanged(int index);

public:
    virtual void selectedItemChanged();
    virtual void checkedItemChanged();

protected:
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void wheelEvent(QWheelEvent *event) override;
    void leaveEvent(QEvent *event) override;
    void focusOutEvent(QFocusEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;

private:
    int normalizedColumnCount() const;
    int visibleItemCount() const;
    int visibleIndexToItemIndex(int visibleIndex) const;

private:
    QPointer<RibbonGalleryGroup> m_group;
    QSize m_itemSize;
    QMargins m_itemMargins;
    QPointer<QMenu> m_popupMenu;
    QAction *m_popupAction;
    int m_minimumColumnCount;
    int m_maximumColumnCount;
    int m_columnCount;
    int m_rowCount;
    int m_selectedIndex;
    int m_checkedIndex;
    int m_pressedIndex;
    bool m_borderVisible;
    bool m_transparent;
    bool m_labelsVisible;
    bool m_scrollAnimated;
    bool m_autoWidth;
    Qt::ScrollBarPolicy m_scrollBarPolicy;
};

///
/// \brief The RibbonGalleryControl class embeds a gallery in a Ribbon group.
///
class RibbonGalleryControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonGalleryControl(RibbonGroup *parent = nullptr,
                                  RibbonGallery *gallery = nullptr);
    ~RibbonGalleryControl() override;

    RibbonGallery *widget() const;
    void setContentsMargins(int top, int bottom);
    QSize sizeHint() const override;
    bool adjustCurrentSize(bool expand) override;
    void sizeChanged(RibbonControlSizeDefinition::GroupSize size) override;

protected:
    void resizeEvent(QResizeEvent *event) override;
};

} // namespace LqRibbon

#endif // LQRIBBON_GALLERY_H
