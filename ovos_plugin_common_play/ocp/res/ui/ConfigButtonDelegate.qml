import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Rectangle {
    id: displaySettingItemControl
    Layout.fillWidth: true
    Layout.preferredHeight: displaySettingItemLabel.implicitHeight + Mycroft.Units.gridUnit
    color: Qt.lighter(Kirigami.Theme.backgroundColor, 2)
    border.width: 1
    border.color: Qt.darker(Kirigami.Theme.textColor, 1.5)
    radius: 6
    property alias label: settingLabel.text
    property alias description: settingDescription.text
    property alias checked: displaySettingItemSwitchButton.checked
    property alias switchLabel: displaySettingItemSwitchButton.text
    property alias switchColor: displaySettingItemSwitchIcon.color
    property var guiEvent: null
    property var guiEventData: {}


    ColumnLayout {
        id: displaySettingItemLabel
        anchors.left: parent.left
        anchors.right: displaySettingItemSwitchButton.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: Mycroft.Units.gridUnit / 2

        Label {
            id: settingLabel
            font.pixelSize: 18
            fontSizeMode: Text.Fit
            minimumPixelSize: 14
            color: Kirigami.Theme.textColor
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
        }

        Label {
            id: settingDescription
            font.pixelSize: settingOneLabel.font.pixelSize / 1.5
            color: Kirigami.Theme.textColor
            wrapMode: Text.WordWrap
            elide: Text.ElideRight
            maximumLineCount: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft
        }
    }

    Button {
        id: displaySettingItemSwitchButton
        width: Mycroft.Units.gridUnit * 10
        anchors.right: parent.right
        anchors.rightMargin: Mycroft.Units.gridUnit / 2
        height: parent.height - Mycroft.Units.gridUnit / 2
        anchors.verticalCenter: parent.verticalCenter
        checkable: true
        text: displaySettingItemControl.checked ? qsTr("ON") : qsTr("OFF")

        Rectangle {
            id: displaySettingItemSwitchIcon
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 8
            height: Kirigami.Units.iconSizes.small
            width: Kirigami.Units.iconSizes.small
            radius: 1000
        }

        onClicked: {
             Mycroft.MycroftController.sendRequest(displaySettingItemControl.guiEvent, displaySettingItemControl.guiEventData)
        }
    }
}