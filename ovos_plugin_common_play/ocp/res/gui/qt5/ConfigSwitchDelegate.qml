import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft


Button {
    id: displaySettingItemSwitchButton
    anchors.right: parent.right
    anchors.rightMargin: Mycroft.Units.gridUnit / 2
    height: parent.height - Mycroft.Units.gridUnit / 2
    width: parent.contentItemWidth
    anchors.verticalCenter: parent.verticalCenter
    checkable: true

    property var guiEvent: null
    property var guiEventData: {}

    Rectangle {
        id: displaySettingItemSwitchIcon
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 8
        height: Kirigami.Units.iconSizes.small
        width: Kirigami.Units.iconSizes.small
        radius: 1000
        color: displaySettingItemSwitchButton.checked ? "green" : "red"
    }

    onClicked: {
        Mycroft.MycroftController.sendRequest(guiEvent, guiEventData)
    }
}