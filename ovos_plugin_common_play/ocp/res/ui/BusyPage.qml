import QtQuick 2.9
import QtQml.Models 2.3
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: root
    skillBackgroundColorOverlay: Kirigami.Theme.backgroundColor
    property var indicatorText: sessionData.footer_text ? sessionData.footer_text : "Loading"
    leftPadding: 0
    bottomPadding: 0
    topPadding: 0
    rightPadding: 0

    Rectangle {
        id: viewBusyOverlay
        z: 300
        anchors.fill: parent
        visible: root.visible
        enabled: visible
        color: Kirigami.Theme.backgroundColor

        BusyIndicator {
            id: viewBusyIndicator
            visible: viewBusyOverlay.visible
            anchors.centerIn: parent
            running: viewBusyOverlay.visible
            enabled: viewBusyOverlay.visible

            Label {
                id: viewBusyIndicatorLabel
                visible: viewBusyOverlay.visible
                enabled: viewBusyOverlay.visible
                anchors.top: parent.bottom
                color: Kirigami.Theme.textColor
                anchors.horizontalCenter: parent.horizontalCenter
                text: indicatorText
            }
        }
    }
}

