 
defaultStyle = \
'''
QTextEdit, QPlainTextEdit, QTableView, QHeaderView {
    font-family: Courier New, monospace;
    font-size: 10pt;
}

BaseTextEdit {
    qproperty-current_line_color : white;
    qproperty-current_line_background : blue;
    qproperty-current_line_color : white;
    qproperty-current_line_background : Fuchsia;
}

QTableView {
    selection-background-color: blue;
}

QTableView::item {
    padding-right: 10px;
    padding-left: 10px;
    padding-top: 0px;
    padding-bottom: 0px;
}
        
QHeaderView::section
{
    border: 0px;
    padding-right: 10px;
    padding-left: 10px;
    padding-top: 0px;
    padding-bottom: 0px;
    margin: 0px;
}

'''
