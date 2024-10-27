from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtCore import Qt, QRegularExpression

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        # Настройка форматов
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("blue"))
        self.keyword_format.setFontWeight(QFont.Bold)

        # Формат для строк
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("darkred"))

        # Формат для комментариев
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("green"))
        
        # Определение паттернов для ключевых слов
        self.keyword_patterns = [
            "\\bdef\\b", "\\bclass\\b", "\\bimport\\b", "\\bfrom\\b",
            "\\breturn\\b", "\\bif\\b", "\\belse\\b", "\\belif\\b", "\\bfor\\b",
            "\\bwhile\\b", "\\btry\\b", "\\bexcept\\b", "\\bpass\\b", 
            "\\bTrue\\b", "\\bFalse\\b", "\\bNone\\b", "\\bwith\\b", "\\bas\\b"
        ]
        
        # Хранение правил подсветки
        self.highlighting_rules = [(QRegularExpression(pattern), self.keyword_format) for pattern in self.keyword_patterns]
        self.highlighting_rules.append((QRegularExpression("\".*?\""), self.string_format))
        self.highlighting_rules.append((QRegularExpression("\'.*?\'"), self.string_format))
        self.highlighting_rules.append((QRegularExpression("#.*"), self.comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match = expression.globalMatch(text)
            while match.hasNext():
                match_obj = match.next()
                self.setFormat(match_obj.capturedStart(), match_obj.capturedLength(), fmt)

        # Устанавливаем форматирование для строк
        self.setCurrentBlockState(0)
