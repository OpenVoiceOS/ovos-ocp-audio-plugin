import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2
        color: Kirigami.Theme.backgroundColor

        ColumnLayout {
            id: grid
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing

            LottieAnimation {
                id: statusIcon
                visible: true
                enabled: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignHCenter
                loops: Animation.Infinite
                fillMode: Image.PreserveAspectFit
                running: true
                source: Qt.resolvedUrl("animations/status-fail.json")
            }

            Label {
                id: statusLabel
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: parent.height * 0.095
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                font.family: "Noto Sans Display"
                font.styleName: "Black"
                text: "Invalid Media"
                color: Kirigami.Theme.textColor
            }
        }
    }
}