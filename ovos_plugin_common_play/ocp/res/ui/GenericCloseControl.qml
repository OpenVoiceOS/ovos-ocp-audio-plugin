import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.0
import QtMultimedia 5.12
import "code/helper.js" as HelperJS

Rectangle {
    anchors.top: parent.top
    anchors.right: parent.right
    width: Mycroft.Units.gridUnit * 4
    height: Mycroft.Units.gridUnit * 3
    color: Kirigami.Theme.highlightColor
    property bool controlVisible: false
    visible: controlVisible
    enabled: controlVisible

    function show(){
        if(hideControlTimer.running) {
            hideControlTimer.restart()
        } else {
            controlVisible = true
        }
    }

    Timer {
        id: hideControlTimer
        running: controlVisible
        interval: 6000
        onTriggered: {
            controlVisible = false
        }
    }

    Kirigami.Icon {
        id: closeIcon
        anchors.centerIn: parent
        width: Mycroft.Units.gridUnit * 1.8
        height: Mycroft.Units.gridUnit * 1.8
        source: "window-close-symbolic"

        ColorOverlay {
            anchors.fill: parent
            source: parent
            color: Kirigami.Theme.textColor
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            Mycroft.MycroftController.sendRequest("system.display.homescreen", {})
        }
    }
}
