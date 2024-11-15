import QtMultimedia 5.12
import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import QtQuick.Templates 2.12 as Templates
import QtGraphicalEffects 1.0
import "../code/helper.js" as HelperJS
import Mycroft 1.0 as Mycroft

Controls.Button {
    id: videoPlayerControlButton
    Layout.preferredWidth: parent.width > 600 ? Kirigami.Units.iconSizes.large : Kirigami.Units.iconSizes.medium
    Layout.preferredHeight: Layout.preferredWidth
    z: 1000
    property var controlIcon
    property color controlBackgroundColor: Kirigami.Theme.backgroundColor

    background: Rectangle {
        id: videoPlayerControlButtonBackground
        color: videoPlayerControlButton.controlBackgroundColor
        radius: 5
        border.width: 1.25
        border.color: videoPlayerControlButton.activeFocus ? Kirigami.Theme.highlightColor : Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.25)
    }

    contentItem: Item {
        Kirigami.Icon {
            height: parent.height - (Mycroft.Units.gridUnit / 2)
            width: height
            anchors.centerIn: parent
            source: videoPlayerControlButton.controlIcon

            ColorOverlay {
                source: parent
                anchors.fill: parent
                color: Kirigami.Theme.textColor
            }
        }
    }

    SequentialAnimation {
        id: videoPlayerControlButtonAnimation

        PropertyAnimation {
            target: videoPlayerControlButtonBackground
            property: "color"
            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.darker(Kirigami.Theme.backgroundColor, 1.5) : Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
            duration: 200
        }

        PropertyAnimation {
            target: videoPlayerControlButtonBackground
            property: "color"
            to: videoPlayerControlButton.controlBackgroundColor
            duration: 200
        }
    }

    onPressed: {
        videoPlayerControlButtonAnimation.running = true;
    }

    onFocusChanged: {
        hideTimer.restart();
    }
}
