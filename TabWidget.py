from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class TabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        url = QUrl("https://google.com")
        self.view = HtmlView(self)
        self.view.load(url)
        self.view.loadFinished.connect(lambda x: self.addTab(self.view, self.view.page().title()))
        #ix = self.addTab(self.view, "loading ...")


    def load(self, url):
        url = QUrl(url)
        self.view.load(url)



class HtmlView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        QWebEngineView.__init__(self, *args, **kwargs)
        self.tab = self.parent()

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            webView = HtmlView(self.tab)
            webView.loadFinished.connect(lambda x: self.tab.setCurrentIndex(self.tab.addTab(webView, webView.page().title())))
            # ix = self.tab.addTab(webView, "loading ...")
            # self.tab.setCurrentIndex(ix)

            return webView

        return QWebEngineView.createWindow(self, windowType)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main = TabWidget()
    main.show()
    sys.exit(app.exec_())