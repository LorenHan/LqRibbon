#ifndef LQRIBBON_H
#define LQRIBBON_H

#include <QAction>
#include <QDebug>
#include <QFrame>
#include <QGridLayout>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
#include <QMainWindow>
#include <QPaintEvent>
#include <QPointer>
#include <QResizeEvent>
#include <QStatusBar>
#include <QTabWidget>
#include <QToolButton>
#include <QVBoxLayout>
#include <QWidget>

namespace LqRibbon {

class RibbonGroup : public QFrame
{
    Q_OBJECT

public:
    explicit RibbonGroup(const QString &strTitle, QWidget *parent = nullptr);

    QAction *addAction(const QIcon &icon,
                       const QString &strText,
                       Qt::ToolButtonStyle buttonStyle);
    void addAction(QAction *action, Qt::ToolButtonStyle buttonStyle);
    void addWidget(QWidget *widget);

    QString title() const;
    void setTitle(const QString &strTitle);

private:
    QToolButton *createButton(QAction *action, Qt::ToolButtonStyle buttonStyle);
    QGridLayout *smallButtonLayout();

private:
    QLabel *m_titleLabel;
    QHBoxLayout *m_contentLayout;
    QGridLayout *m_smallButtonLayout;
    QWidget *m_smallButtonWidget;
    int m_smallButtonRow;
    int m_smallButtonColumn;
};

class RibbonPage : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonPage(const QString &strTitle, QWidget *parent = nullptr);

    RibbonGroup *addGroup(const QString &strTitle);
    QString title() const;
    void setTitle(const QString &strTitle);

signals:
    void titleChanged(const QString &strTitle);

private:
    QString m_strTitle;
    QHBoxLayout *m_groupLayout;
};

class RibbonBar : public QTabWidget
{
    Q_OBJECT

public:
    explicit RibbonBar(QWidget *parent = nullptr);

    RibbonPage *addPage(const QString &strTitle);
    RibbonPage *page(int index) const;
    RibbonPage *currentPage() const;
    QLineEdit *searchLineEdit() const;
    void setSearchVisible(bool visible);
    bool isSearchVisible() const;
    void setSearchPlaceholderText(const QString &strText);
    QString searchText() const;
    void setSearchText(const QString &strText);
    void setCurrentPageIndex(int index);
    void setFrameThemeEnabled(bool enabled);
    bool isFrameThemeEnabled() const;

signals:
    void pageChanged(int index);
    void searchTextChanged(const QString &strText);
    void searchAccepted(const QString &strText);

protected:
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    void updateSearchGeometry();
    void updateStyleSheet();

private:
    QLineEdit *m_searchEdit;
    bool m_frameThemeEnabled;
};

class RibbonMainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit RibbonMainWindow(QWidget *parent = nullptr);
    ~RibbonMainWindow() override;

    RibbonBar *ribbonBar() const;
    void setCentralWidget(QWidget *widget);

private:
    QWidget *m_rootWidget;
    QVBoxLayout *m_rootLayout;
    RibbonBar *m_ribbonBar;
    QPointer<QWidget> m_centralWidget;
};

using LqRibbonGroup = RibbonGroup;
using LqRibbonPage = RibbonPage;
using LqRibbonBar = RibbonBar;
using LqRibbonMainWindow = RibbonMainWindow;

} // namespace LqRibbon

using RibbonBar = LqRibbon::RibbonBar;
using RibbonPage = LqRibbon::RibbonPage;
using RibbonGroup = LqRibbon::RibbonGroup;
using RibbonMainWindow = LqRibbon::RibbonMainWindow;

#endif // LQRIBBON_H
