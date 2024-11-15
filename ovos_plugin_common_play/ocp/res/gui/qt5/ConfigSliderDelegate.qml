import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft


Slider {
    id: displaySettingItemSwitchButton
    anchors.right: parent.right
    anchors.rightMargin: Mycroft.Units.gridUnit / 2
    height: parent.height - Mycroft.Units.gridUnit / 2
    width: parent.contentItemWidth
    anchors.verticalCenter: parent.verticalCenter
    from: 15
    to: 60
    stepSize: 15
    snapMode: Slider.SnapAlways
    
    property var guiEvent: null
    property var guiEventData: {}

    handle: Rectangle {
        x: displaySettingItemSwitchButton.leftPadding + displaySettingItemSwitchButton.visualPosition * (displaySettingItemSwitchButton.availableWidth - width)
        y: displaySettingItemSwitchButton.topPadding + displaySettingItemSwitchButton.availableHeight / 2 - height / 2
        implicitWidth: Mycroft.Units.gridUnit * 2
        implicitHeight: Mycroft.Units.gridUnit * 2
        radius: 13
        color: displaySettingItemSwitchButton.pressed ? Kirigami.Theme.highlightColor : Kirigami.Theme.backgroundColor
        border.color: Kirigami.Theme.textColor

        Text {
            anchors.centerIn: parent
            text: displaySettingItemSwitchButton.value
            color: Kirigami.Theme.textColor
        }
    }

    onMoved: {
        Mycroft.MycroftController.sendRequest(guiEvent, guiEventData)
    }
}