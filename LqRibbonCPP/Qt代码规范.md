
# Qt代码规范

## 缩进
- 采用4个空格
- 尽量不要用TAB，如果用TAB, IDE中要设置一个TAB为4个空格

## 变量声明
- 每行一个变量
- 尽可能避免短的变量名(比如"a", "rbarr", "nughdeget")
- 单字符的变量只在临时变量或循环的计数中使用
- 等到真正需要使用时再定义变量

```cpp
// Wrong
int a, b;
char *c, *d;

// Correct
int height;
int width;
char *nameOfThis;
char *nameOfThat;
```

- 以小写字符开头，后续单词以大写开头
- 避免使用缩写

```cpp
// Wrong
short Cntr;
char ITEM_DELIM = '';

// Correct
short counter;
char itemDelimiter = '';
```

- 类名总是以大写开头。

## 空白
- 利用空行将语句恰当地分组
- 总是使用一个空行(不要空多行)
- 总是在每个关键字和大括号前使用一个空格
- 总是在代码结尾加一个空行

```cpp
// Wrong
if(foo){
}

// Correct
if (foo) {
}
```

- 对指针和引用，在类型和*、&之间加一个空格，但在*、&与变量之间不加空格

```cpp
char *x;
const QString &myString;
const char *const y = "hello";
```

- 二元操作符前后加空白
- 类型转换后不加空白
- 尽量避免C风格的类型转换

```cpp
// Wrong
char* blockOfMemory = (char* ) malloc(data.size());

// Correct
char *blockOfMemory = reinterpret_cast<char *>(malloc(data.size()));
```

## 大括号
- 基本原则：左大括号和语句保持在同一行：

```cpp
// Wrong
if (codec)
{
}

// Correct
if (codec) {
}
```

- 例外：函数定义和类定义中，左大括号总是单独占一行：

```cpp
static void foo(int g)
{
    qDebug("foo: %i", g);
}

class Moo
{
};
```

- 控制语句的body中只有一行时也要使用大括号

```cpp
// Wrong
if (address.isEmpty())
    return false;

for (int i = 0; i < 10; ++i)
    qDebug("%i", i);

// Correct
if (address.isEmpty()) {
    return false;
}

for (int i = 0; i < 10; ++i) {
    qDebug("%i", i);
}
```

- 如果控制语句的body为空，则使用大括号

```cpp
// Wrong
while (a);

// Correct
while (a) {}
```

## 圆括号
- 使用圆括号将表达式分组

```cpp
// Wrong
if (a && b || c)

// Correct
if ((a && b) || c)

// Wrong
a + b & c

// Correct
(a + b) & c
```

## Switch 语句
- case 和 switch 位于同一列
- 每一个case必须有一个break(或return)语句，或者用注释说明无需break

```cpp
switch (myEnum) {
    case Value1:
        doSomething();
        break;
    case Value2:
        doSomethingElse();
        // fall through
    default:
        defaultHandling();
        break;
}
```

## 断行
- 保持每行短于100 个字符，需要时进行断行
- 逗号放一行的结束，操作符放到一行的开头。如果你的编辑器太窄，一个放在行尾的操作符不容易被看到。

```cpp
// Correct
if (longExpression
    + otherLongExpression
    + otherOtherLongExpression) {
}

// Wrong
if (longExpression +
    otherLongExpression +
    otherOtherLongExpression) {
}
```

## 继承与关键字 `virtual`
- 重新实现一个虚函数时，头文件中不放置 virtual 关键字。

## 注释
- cpp文件中函数注释要 /// 然后敲回车，自动生成注释

```cpp
///
/// \brief FlatMainWindow::setActiveSubWindow
/// \param window
///
void FlatMainWindow::setActiveSubWindow(QWidget *window)
{
    
}
```
## 命名
- 成员变量命名要以m_开头, // 注释，不同变量注释尽量对齐

```cpp
    int m_typeDocCurrent;       // 当前文档类型
    QMdiArea *m_mdiArea;        // MDI区域
    qreal m_scaleFactor;        // 缩放因子
    QString m_strTitle;         // 标题
```
- 局部变量无需以m_开头

```cpp
    int studentId;
```
- 字符串命名中要包含str

```cpp
    QString strStudentName;     // 学生姓名
    QString m_strStudentName;   // 学生姓名, 成员变量命名要以m_开头
```

- 函数命名要以小写开头，小驼峰写法，名称和功能意思明确

```cpp
    void setScaleFactor(qreal scaleFactor);
```

## 其他
- 函数入参不能省略，不管是在.h文件中还是在.cpp文件中

```cpp
// Wrong
void hideStatusBar(int);

// Correct
void hideStatusBar(int state);
```
- // 注释和文字之间要有一个空格，防止汉字乱码
- 除了/// 敲回车自动生成的函数注释外，其他注释要用简体中文

- 变量命名要符合Qt原有命名规范，类名在前，名称在后。
```cpp
QString strStudentName;
QToolButton *toolButtonRead;
QLabel *labelStudentName;
QPushButton *pushButtonRead;
```