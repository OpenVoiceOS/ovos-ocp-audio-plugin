import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import QtQuick.Window 2.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import QtMultimedia 5.12
import "." as Local
import "code/helper.js" as HelperJS

Mycroft.Delegate {
    id: root
    skillBackgroundSource: "https://source.unsplash.com/1920x1080/?+music"
    property bool compactMode: parent.height >= 550 ? 0 : 1
    property bool displayBottomBar: sessionData.displayBottomBar ? sessionData.displayBottomBar : 0
    fillWidth: true
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0
    readonly property var mediaService: Mycroft.MediaService
    property var mediaStatus: mediaService.playbackState

    function movePageRight(){
        parent.parent.parent.currentIndex++
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }

    Item {
        id: topBarArea
        height: Mycroft.Units.gridUnit * 3
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right

        Rectangle {
            id: pageTitleIconArea
            width: Mycroft.Units.gridUnit * 3
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            color: Kirigami.Theme.highlightColor

            Kirigami.Icon {
                id: pageTitleIcon
                anchors.centerIn: parent
                width: Mycroft.Units.gridUnit * 1.8
                height: Mycroft.Units.gridUnit * 1.8
                source: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.resolvedUrl("images/ocp-dark.png") : Qt.resolvedUrl("images/ocp-light.png")
            }
        }

        Rectangle {
            id: topBarAreaCloseDashboardButton
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: Mycroft.Units.gridUnit * 4
            color: Kirigami.Theme.highlightColor

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

        Kirigami.Separator {
            id: topBarSeparator
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
        }
    }

    StackLayout {
        id: homescreenStackLayout
        anchors.top: topBarArea.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: displayBottomBar ? bottomBar.top : parent.bottom
        anchors.bottomMargin: displayBottomBar ? Mycroft.Units.gridUnit * 0.5 : 0
        anchors.margins: Mycroft.Units.gridUnit * 2
        clip: true
        currentIndex: sessionData.homepage_index ? sessionData.homepage_index : 0

        Search {
            id: search
            anchors.fill: parent
        }

        OCPSkillsView {
            id: ocpSkillsView
            anchors.fill: parent
        }
    }

    Rectangle {
        id: bottomBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: nowPlayingHomeBar.visible ? Mycroft.Units.gridUnit * 7 : Mycroft.Units.gridUnit * 4
        color: "transparent"
        visible: displayBottomBar
        enabled: displayBottomBar

        Kirigami.Separator {
            id: bottomBarSeparator
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
        }

        NowPlayingHomeBar {
            id: nowPlayingHomeBar
            anchors.top: bottomBarSeparator.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: Mycroft.Units.gridUnit * 3
            visible: root.mediaStatus === MediaPlayer.PlayingState ? 1 : 0
            enabled: root.mediaStatus === MediaPlayer.PlayingState ? 1 : 0
        }

        Kirigami.Separator {
            id: bottomBarSeparatorBarSept
            anchors.top: nowPlayingHomeBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
            visible: nowPlayingHomeBar.visible
            enabled: nowPlayingHomeBar.enabled
        }

        GridLayout {
            id: bottomBarLayout
            anchors.top: nowPlayingHomeBar.visible ? bottomBarSeparatorBarSept.bottom : bottomBarSeparator.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: Mycroft.Units.gridUnit * 0.5
            columns: 2
            columnSpacing: Mycroft.Units.gridUnit * 0.5
            rowSpacing: Mycroft.Units.gridUnit * 0.5

            Rectangle {
                id: homepageButtonTangle
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Kirigami.Theme.backgroundColor
                radius: 6

                Controls.Label {
                    id: homepageButtonLabel
                    anchors.centerIn: parent
                    text: "Home"
                    font.pixelSize: parent.height * 0.5
                    color: homescreenStackLayout.currentIndex == 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        homescreenStackLayout.currentIndex = 0
                    }
                    onPressed: {
                        homepageButtonTangle.color = Kirigami.Theme.highlightColor
                        homepageButtonLabel.color = Kirigami.Theme.backgroundColor
                    }
                    onReleased: {
                        homepageButtonTangle.color = Kirigami.Theme.backgroundColor
                        homepageButtonLabel.color = homescreenStackLayout.currentIndex == 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    }
                }
            }

            Rectangle {
                id: skillsViewButtonTangle
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Kirigami.Theme.backgroundColor
                radius: 6

                Controls.Label {
                    id: skillsViewButtonLabel
                    anchors.centerIn: parent
                    text: "Skills"
                    font.pixelSize: parent.height * 0.5
                    color: homescreenStackLayout.currentIndex == 1 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        homescreenStackLayout.currentIndex = 1
                    }
                    onPressed: {
                        skillsViewButtonTangle.color = Kirigami.Theme.highlightColor
                        skillsViewButtonLabel.color = Kirigami.Theme.backgroundColor
                    }
                    onReleased: {
                        skillsViewButtonTangle.color = Kirigami.Theme.backgroundColor
                        skillsViewButtonLabel.color = homescreenStackLayout.currentIndex == 1 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    }
                }
            }
        }
    }
}
