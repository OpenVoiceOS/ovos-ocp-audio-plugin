import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

ComboBox {
    id: combobox
    anchors.right: parent.right
    anchors.rightMargin: Mycroft.Units.gridUnit / 2
    height: parent.height - Mycroft.Units.gridUnit / 2
    width: parent.contentItemWidth
    anchors.verticalCenter: parent.verticalCenter
    property var guiEvent: null
    property var guiEventData: {}
}