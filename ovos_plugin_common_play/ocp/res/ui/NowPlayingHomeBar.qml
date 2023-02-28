import QtQuick.Layouts 1.15
import QtQuick 2.15
import QtQuick.Controls 2.15 as Controls
import org.kde.kirigami 2.19 as Kirigami
import QtQuick.Window 2.15
import Mycroft 1.0 as Mycroft
import QtMultimedia
import Qt5Compat.GraphicalEffects
import "." as Local

Item {
    id: nowPlayingHomeBar
    property var mediaTitle: sessionData.title
    property var mediaArtist: sessionData.artist
    property var mediaArt: sessionData.image

    Rectangle {
        anchors.fill: parent
        color: Kirigami.Theme.backgroundColor
        opacity: 0.95

        RowLayout {
            anchors.fill: parent
            anchors.margins: Mycroft.Units.gridUnit
            spacing: Mycroft.Units.gridUnit

            Image {
                id: nowPlayingImage
                source: nowPlayingHomeBar.mediaArt
                Layout.fillHeight: true
                Layout.preferredWidth: nowPlayingImage.height
                fillMode: Image.PreserveAspectFit
                smooth: true
            }

            Controls.Label {
                id: nowPlayingLabel
                text: "Now Playing:"
                color: Kirigami.Theme.textColor
                Layout.fillHeight: true
                elide: Text.ElideRight
            }

            Controls.Label {
                id: nowPlayingTitle
                text: nowPlayingHomeBar.mediaTitle + " - " + nowPlayingHomeBar.mediaArtist
                color: Kirigami.Theme.textColor
                Layout.fillWidth: true                  
                Layout.fillHeight: true
                elide: Text.ElideRight
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: (mouse)=> {
            root.movePageRight()
        }
    }
}
