import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.0
import QtQuick.Templates 2.12 as T
import QtMultimedia 5.12

Mycroft.Delegate {
    id: root
    fillWidth: true
    skillBackgroundSource: sessionData.bg_image
    skillBackgroundColorOverlay: Qt.rgba(0, 0, 0, 0.85)
    leftPadding: 0
    topPadding: 0
    bottomPadding: 0
    rightPadding: 0

    property var thumbnail: sessionData.image
    property var title: sessionData.title
    property var author: sessionData.artist
    property var playerState: sessionData.status

    property var loopStatus: sessionData.loopStatus
    property var canResume: sessionData.canResume
    property var canNext: sessionData.canNext
    property var canPrev: sessionData.canPrev
    property var canRepeat: sessionData.canRepeat
    property var canShuffle: sessionData.canShuffle
    property var shuffleStatus: sessionData.shuffleStatus

    //Player Support Vertical / Horizontal Layouts
    //property bool horizontalMode: width > height ? 1 : 0
    property bool horizontalMode: false

    //Support custom colors for text / seekbar background / seekbar forground
    property color textColor: sessionData.textColor ? sessionData.textColor : "white"

    function formatedDuration(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    function formatedPosition(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    Component.onCompleted: {
        root.forceActiveFocus()
    }

    KeyNavigation.down: repeatButton

    Connections {
        target: Window.window
        onVisibleChanged: {
            if(playerState === "Playing") {
                triggerGuiEvent("pause", {})
            }
        }
    }

    Image {
        id: imgbackground
        anchors.fill: parent
        source: root.thumbnail
    }

    FastBlur {
        anchors.fill: imgbackground
        radius: 64
        source: imgbackground
    }

    Rectangle {
        color: Qt.rgba(0, 0, 0, 0.5)
        radius: 5
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2

        GridLayout {
            anchors.top: parent.top
            anchors.bottom: innerBox.top
            anchors.left: parent.left
            anchors.right: parent.right
            rows: horizontalMode ? 2 : 1
            columns: horizontalMode ? 2 : 1

            Rectangle {
                id: rct1
                Layout.preferredWidth: horizontalMode ? img.width : parent.width
                Layout.preferredHeight:  horizontalMode ? parent.height : parent.height * 0.75
                color: "transparent"

                Image {
                    id: img
                    property bool rounded: true
                    property bool adapt: true
                    source: root.thumbnail
                    width: parent.height
                    anchors.horizontalCenter: parent.horizontalCenter
                    height: width
                    z: 20

                    layer.enabled: rounded
                    layer.effect: OpacityMask {
                        maskSource: Item {
                            width: img.width
                            height: img.height
                            Rectangle {
                                anchors.centerIn: parent
                                width: img.adapt ? img.width : Math.min(img.width, img.height)
                                height: img.adapt ? img.height : width
                                radius: 5
                            }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"

                ColumnLayout {
                    id: songTitleText
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.smallSpacing

                    Label {
                        id: authortitle
                        text: root.author
                        maximumLineCount: 1
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        font.bold: true
                        font.pixelSize: Math.round(height * 0.45)
                        fontSizeMode: Text.Fit
                        minimumPixelSize: Math.round(height * 0.25)
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        font.capitalization: Font.Capitalize
                        color: "white"
                        visible: true
                        enabled: true
                    }

                    Label {
                        id: songtitle
                        text: root.title
                        maximumLineCount: 1
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        font.pixelSize: Math.round(height * 0.45)
                        fontSizeMode: Text.Fit
                        minimumPixelSize: Math.round(height * 0.25)
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        font.capitalization: Font.Capitalize
                        color: "white"
                        visible: true
                        enabled: true
                    }
                }
            }
        }
        Rectangle {
            id: innerBox
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: horizontalMode ? parent.height * 0.25 : parent.height * 0.20
            color: Qt.rgba(0, 0, 0, 0.7)

            Item {
                id: gridBar
                anchors.fill: parent
                anchors.margins: Mycroft.Units.gridUnit
                z: 10

                Button {
                    id: repeatButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.right: prevButton.left
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.right: prevButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: root.loopStatus === "RepeatTrack" ? Qt.resolvedUrl("images/media-playlist-repeat.svg") : root.loopStatus === "None" ? Qt.resolvedUrl("images/media-playlist-repeat-track.svg") : Qt.resolvedUrl("images/media-playlist-repeat.svg")
                        color: root.loopStatus === "None" ? "white" : root.loopStatus === "RepeatTrack" ? "white" : "grey"
                    }

                    background: Rectangle {
                        radius: 5
                        color:  Qt.rgba(0.2, 0.2, 0.2, 5)
                        border.color: repeatButton.activeFocus ? "#a70f1b" : "transparent"
                    }
                }

                Button {
                    id: prevButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.right: playButton.left
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: repeatButton
                    KeyNavigation.right: playButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                        triggerGuiEvent("previous", {})
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit

                        source: Qt.resolvedUrl("images/media-skip-backward.svg")
                        color: root.canPrev === true ? "white" : "grey"
                    }

                    background: Rectangle {
                        radius: 5
                        color:  Qt.rgba(0.2, 0.2, 0.2, 5)
                        border.color: prevButton.activeFocus ? "#a70f1b" : "transparent"
                    }
                }

                Button {
                    id: playButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: prevButton
                    KeyNavigation.right: nextButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                        if (playerState === "Paused"){
                            playerState = "Playing"
                            triggerGuiEvent("resume", {})
                        } else {
                            playerState = "Paused"
                            triggerGuiEvent("pause", {})
                        }
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: playerState === "Playing" ? Qt.resolvedUrl("images/media-playback-pause.svg") : Qt.resolvedUrl("images/media-playback-start.svg")
                        color: root.canResume === true ? "white" : "grey"
                    }

                    background: Rectangle {
                        radius: 5
                        color:  Qt.rgba(0.2, 0.2, 0.2, 5)
                        border.color: playButton.activeFocus ? "#a70f1b" : "transparent"
                    }
                }

                Button {
                    id: nextButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.left: playButton.right
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: playButton
                    KeyNavigation.right: shuffleButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                        triggerGuiEvent("next", {})
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: Qt.resolvedUrl("images/media-skip-forward.svg")
                        color: root.canNext === true ? "white" : "grey"
                    }

                    background: Rectangle {
                        radius: 5
                        color:  Qt.rgba(0.2, 0.2, 0.2, 5)
                        border.color: nextButton.activeFocus ? "#a70f1b" : "transparent"
                    }
                }

                Button {
                    id: shuffleButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.left: nextButton.right
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: nextButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {

                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: Qt.resolvedUrl("images/media-playlist-shuffle.svg")
                        color: root.shuffleStatus === true ? "white" : "grey"
                    }

                    background: Rectangle {
                        radius: 5
                        color:  Qt.rgba(0.2, 0.2, 0.2, 5)
                        border.color: shuffleButton.activeFocus ? "#a70f1b" : "transparent"
                    }
                }
            }
        }
    }
}

