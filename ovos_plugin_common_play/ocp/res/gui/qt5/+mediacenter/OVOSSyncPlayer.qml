import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.0
import QtQuick.Templates 2.12 as T
import QtMultimedia 5.12
import "./code/helper.js" as HelperJS

Item {
    id: root

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

    onFocusChanged: {
        if (focus) {
            repeatButton.forceActiveFocus()   
        }
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
        color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.5)
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
                        color: Kirigami.Theme.textColor
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
                        color: Kirigami.Theme.textColor
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
            color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.7)

            RowLayout {
                id: gridBar
                anchors.fill: parent
                anchors.margins: Mycroft.Units.gridUnit
                spacing: root.horizontalMode ? Mycroft.Units.gridUnit * 0.5 : 1
                z: 10

                AudioPlayerControl {
                    id: repeatButton
                    controlIcon: root.loopStatus === "RepeatTrack" ? Qt.resolvedUrl("images/media-playlist-repeat.svg") : root.loopStatus === "None" ? Qt.resolvedUrl("images/media-playlist-repeat-track.svg") : Qt.resolvedUrl("images/media-playlist-repeat.svg")
                    controlIconColor: root.loopStatus === "None" ? Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.3) : Kirigami.Theme.highlightColor
                    horizontalMode: root.horizontalMode

                    KeyNavigation.right: prevButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    Keys.onLeftPressed: {
                        mainLoaderView.movePageLeft()
                    }

                    onClicked: {
                    }
                }

                AudioPlayerControl {
                    id: prevButton
                    controlIcon: Qt.resolvedUrl("images/media-skip-backward.svg")
                    controlIconColor: root.canPrev === true ? Kirigami.Theme.textColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4)
                    horizontalMode: root.horizontalMode

                    KeyNavigation.left: repeatButton
                    KeyNavigation.right: playButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                        triggerGuiEvent("previous", {})
                    }
                }

                AudioPlayerControl {
                    id: playButton
                    controlIcon: playerState === MediaPlayer.PlayingState ? Qt.resolvedUrl("images/media-playback-pause.svg") : Qt.resolvedUrl("images/media-playback-start.svg")
                    controlIconColor: root.canResume === true ? Kirigami.Theme.textColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4)
                    horizontalMode: root.horizontalMode

                    KeyNavigation.left: prevButton
                    KeyNavigation.right: stopButton
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
                }

                AudioPlayerControl {
                    id: stopButton
                    controlIcon: Qt.resolvedUrl("images/media-playback-stop.svg")
                    controlIconColor: Kirigami.Theme.textColor
                    horizontalMode: root.horizontalMode

                    KeyNavigation.left: playButton
                    KeyNavigation.right: nextButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                        if(playerState === "Playing") {
                            playerState = "Stopped"
                            triggerGuiEvent("stop", {})
                        }
                    }
                }

                AudioPlayerControl {
                    id: nextButton
                    controlIcon: Qt.resolvedUrl("images/media-skip-forward.svg")
                    controlIconColor: root.canNext === true ? Kirigami.Theme.textColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4)
                    horizontalMode: root.horizontalMode

                    KeyNavigation.left: stopButton
                    KeyNavigation.right: shuffleButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    onClicked: {
                        triggerGuiEvent("next", {})
                    }
                }

                AudioPlayerControl {
                    id: shuffleButton
                    controlIcon: Qt.resolvedUrl("images/media-playlist-shuffle.svg")
                    controlIconColor: root.shuffleStatus === false ? Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.3) : Kirigami.Theme.highlightColor
                    horizontalMode: root.horizontalMode

                    KeyNavigation.left: nextButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    Keys.onRightPressed: {
                        mainLoaderView.movePageRight()
                    }

                    onClicked: {}
                }
            }
        }
    }
}

